# app/dlq_consumer.py
import json

import pika
from common import Q_DLQ, declare_topology, mq_params


def on_msg(ch, method, props, body):
    try:
        data = json.loads(body.decode())
    except Exception:
        data = body.decode(errors="ignore")
    print(f"[DLQ] mensagem morta: message_id={props.message_id} headers={props.headers} body={data}")
    ch.basic_ack(method.delivery_tag)

def main():
    conn = pika.BlockingConnection(mq_params())
    ch = conn.channel()
    declare_topology(ch)
    ch.basic_qos(prefetch_count=16)
    ch.basic_consume(queue=Q_DLQ, on_message_callback=on_msg, auto_ack=False)
    print("[DLQ] esperando mensagens na dead_letter_queue…")
    ch.start_consuming()

if __name__ == "__main__":
    main()
