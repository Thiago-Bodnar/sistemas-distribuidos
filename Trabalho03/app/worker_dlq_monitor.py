import json
import sys
import time

import pika
from common import DLQ_EXCHANGE, declare_topology, mq_params


def on_dlq_message(ch, method, props, body):
    """
    Processa mensagens que chegaram na Dead Letter Queue.
    """
    data = json.loads(body.decode())
    shipment_id = props.message_id or data.get("shipment_id")
    
    print(f"[DLQ_MONITOR] Dead letter received:")
    print(f"  - Shipment ID: {shipment_id}")
    print(f"  - Original Queue: {method.routing_key}")
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
            
            # Consome de todas as DLQs
            ch.basic_qos(prefetch_count=10)
            
            # Monitora expedicao DLQ
            ch.basic_consume(
                queue="expedicao_dlq", 
                on_message_callback=on_dlq_message, 
                auto_ack=False
            )
            
            # Monitora notificacao DLQ
            ch.basic_consume(
                queue="notificacao_dlq", 
                on_message_callback=on_dlq_message, 
                auto_ack=False
            )
            
            # Monitora faturamento DLQ
            ch.basic_consume(
                queue="faturamento_dlq", 
                on_message_callback=on_dlq_message, 
                auto_ack=False
            )
            
            print("[DLQ_MONITOR] ✅ Conectado! Monitorando dead letter queues...")
            print("  - expedicao_dlq")
            print("  - notificacao_dlq") 
            print("  - faturamento_dlq")
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
