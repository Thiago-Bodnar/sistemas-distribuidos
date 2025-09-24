import json, time
import pika
from common import mq_params, declare_topology

def on_message(ch, method, props, body):
    data = json.loads(body.decode())
    shipment_id = props.message_id or data.get("shipment_id")
    print(f"[worker_notificacao] notify shipment={shipment_id} status={data.get('status')}")
    time.sleep(0.2)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    conn = pika.BlockingConnection(mq_params())
    ch = conn.channel()
    declare_topology(ch)
    ch.basic_qos(prefetch_count=16)
    ch.basic_consume(queue="notificacao_queue", on_message_callback=on_message, auto_ack=False)
    print("[worker_notificacao] waiting on notificacao_queue...")
    ch.start_consuming()

if __name__ == "__main__":
    main()
