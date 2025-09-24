import json, time, os
import pika
from common import mq_params, declare_topology, EXCHANGE, RK_FATURAMENTO

def on_message(ch, method, props, body):
    data = json.loads(body.decode())
    shipment_id = props.message_id or data.get("shipment_id")
    print(f"[worker_expedicao] received shipment={shipment_id} payload={data}")
    time.sleep(0.5)
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

def main():
    conn = pika.BlockingConnection(mq_params())
    ch = conn.channel()
    declare_topology(ch)
    ch.basic_qos(prefetch_count=8)
    ch.basic_consume(queue="expedicao_queue", on_message_callback=on_message, auto_ack=False)
    print("[worker_expedicao] waiting on expedicao_queue...")
    ch.start_consuming()

if __name__ == "__main__":
    main()
