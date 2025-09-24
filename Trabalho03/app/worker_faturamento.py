import json, time
import pika
from common import mq_params, declare_topology

def on_message(ch, method, props, body):
    data = json.loads(body.decode())
    shipment_id = props.message_id or data.get("shipment_id")
    print(f"[worker_faturamento] faturando shipment={shipment_id} valor={data.get('invoice_value')} {data.get('currency')}")
    time.sleep(0.3)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    conn = pika.BlockingConnection(mq_params())
    ch = conn.channel()
    declare_topology(ch)
    ch.basic_qos(prefetch_count=8)
    ch.basic_consume(queue="faturamento_queue", on_message_callback=on_message, auto_ack=False)
    print("[worker_faturamento] waiting on faturamento_queue...")
    ch.start_consuming()

if __name__ == "__main__":
    main()
