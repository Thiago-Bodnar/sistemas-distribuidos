import json
import sys
import time

import pika
from common import DLQ_EXCHANGE, declare_topology, mq_params


def on_dlq_message(ch, method, props, body):
    """
    Processa mensagens que chegaram na Dead Letter Queue genérica.
    """
    data = json.loads(body.decode())
    shipment_id = props.message_id or data.get("shipment_id")
    
    # Determina a origem da mensagem baseado no payload
    source = data.get("source", "Unknown")
    original_queue = "Unknown"
    
    # Identifica a fila original baseado no conteúdo
    if "hub" in data or "CD" in str(data):
        original_queue = "expedicao_queue"
    elif "driver_id" in data or "gps" in data:
        original_queue = "notificacao_queue"
    elif "invoice_value" in data or "currency" in data:
        original_queue = "faturamento_queue"
    
    print(f"[DLQ_MONITOR] Dead letter received:")
    print(f"  - Shipment ID: {shipment_id}")
    print(f"  - Original Queue: {original_queue}")
    print(f"  - Source: {source}")
    print(f"  - Retry Count: {props.headers.get('x-retry-count', 0) if props.headers else 0}")
    print(f"  - Payload: {data}")
    print(f"  - Headers: {props.headers}")
    print(f"  - Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
    print("=" * 50)
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"[DLQ_MONITOR] Tentativa de conexão {attempt + 1}/{max_retries}")
            conn = pika.BlockingConnection(mq_params())
            ch = conn.channel()
            declare_topology(ch)
            
            # Consome da DLQ genérica
            ch.basic_qos(prefetch_count=10)
            
            # Monitora dead letter queue genérica
            ch.basic_consume(
                queue="dead_letter_queue", 
                on_message_callback=on_dlq_message, 
                auto_ack=False
            )
            
            print("[DLQ_MONITOR] ✅ Conectado! Monitorando dead letter queue...")
            print("  - dead_letter_queue (genérica)")
            ch.start_consuming()
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[DLQ_MONITOR] ❌ Erro de conexão: {e}")
            if attempt < max_retries - 1:
                print(f"[DLQ_MONITOR] ⏳ Aguardando {retry_delay}s antes da próxima tentativa...")
                time.sleep(retry_delay)
            else:
                print(f"[DLQ_MONITOR] 💥 Falha ao conectar após {max_retries} tentativas")
                sys.exit(1)
        except KeyboardInterrupt:
            print("[DLQ_MONITOR] 🛑 Interrompido pelo usuário")
            break
        except Exception as e:
            print(f"[DLQ_MONITOR] ❌ Erro inesperado: {e}")
            if attempt < max_retries - 1:
                print(f"[DLQ_MONITOR] ⏳ Aguardando {retry_delay}s antes da próxima tentativa...")
                time.sleep(retry_delay)
            else:
                print(f"[DLQ_MONITOR] 💥 Falha após {max_retries} tentativas")
                sys.exit(1)

if __name__ == "__main__":
    main()
