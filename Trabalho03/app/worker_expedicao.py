import json
import os
import sys
import time

import pika
from common import (EXCHANGE, RK_FATURAMENTO, calculate_retry_delay,
                    declare_topology, get_retry_count, increment_retry_count,
                    mq_params, should_retry)


def on_message(ch, method, props, body):
    data = json.loads(body.decode())
    shipment_id = props.message_id or data.get("shipment_id")
    retry_count = get_retry_count(props)
    
    print(f"[worker_expedicao] received shipment={shipment_id} payload={data} retry={retry_count}")
    
    try:
        # Simula processamento que pode falhar
        time.sleep(0.5)
        
        # Simula falha aleatória para demonstrar retry (remover em produção)
        import random
        if random.random() < 0.3:  # 30% chance de falha
            raise Exception("Simulated processing error")
        
        print(f"[worker_expedicao] expedicao concluida shipment={shipment_id}")

        faturamento = {
            "shipment_id": shipment_id,
            "invoice_value": 79.90,
            "currency": "BRL",
            "issued_at": int(time.time()),
            "source": "Serviço de Expedição"
        }
        ch.basic_publish(
            exchange=EXCHANGE,
            routing_key=os.getenv("ROUTING_FATURAMENTO", "faturamento"),
            body=json.dumps(faturamento).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
                message_id=shipment_id
            )
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"[worker_expedicao] error processing shipment={shipment_id}: {e}")
        
        if should_retry(props):
            # Retry com exponential backoff
            retry_delay = calculate_retry_delay(retry_count)
            print(f"[worker_expedicao] retrying shipment={shipment_id} in {retry_delay}ms (attempt {retry_count + 1})")
            
            # Rejeita a mensagem para que seja redelivered após o delay
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            # Simula delay (em produção, usar TTL ou delayed exchange)
            time.sleep(retry_delay / 1000.0)
        else:
            # Máximo de retries atingido, envia para DLQ
            print(f"[worker_expedicao] max retries exceeded for shipment={shipment_id}, sending to DLQ")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"[worker_expedicao] Tentativa de conexão {attempt + 1}/{max_retries}")
            conn = pika.BlockingConnection(mq_params())
            ch = conn.channel()
            declare_topology(ch)
            ch.basic_qos(prefetch_count=8)
            ch.basic_consume(queue="expedicao_queue", on_message_callback=on_message, auto_ack=False)
            print("[worker_expedicao] ✅ Conectado! Aguardando mensagens na expedicao_queue...")
            ch.start_consuming()
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[worker_expedicao] ❌ Erro de conexão: {e}")
            if attempt < max_retries - 1:
                print(f"[worker_expedicao] ⏳ Aguardando {retry_delay}s antes da próxima tentativa...")
                time.sleep(retry_delay)
            else:
                print(f"[worker_expedicao] 💥 Falha ao conectar após {max_retries} tentativas")
                sys.exit(1)
        except KeyboardInterrupt:
            print("[worker_expedicao] 🛑 Interrompido pelo usuário")
            break
        except Exception as e:
            print(f"[worker_expedicao] ❌ Erro inesperado: {e}")
            if attempt < max_retries - 1:
                print(f"[worker_expedicao] ⏳ Aguardando {retry_delay}s antes da próxima tentativa...")
                time.sleep(retry_delay)
            else:
                print(f"[worker_expedicao] 💥 Falha após {max_retries} tentativas")
                sys.exit(1)

if __name__ == "__main__":
    main()
