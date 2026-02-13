import json, uuid, time
import pika
from common import mq_params, declare_topology, EXCHANGE, RK_EXPEDICAO

def main():
    conn = pika.BlockingConnection(mq_params())
    ch = conn.channel()
    ch.confirm_delivery()
    declare_topology(ch)

    payload = {
        "shipment_id": str(uuid.uuid4()),
        "hub": "CD CURITIBA/PR",
        "status": "RECEBIDO_NO_CD",
        "created_at": int(time.time()),
        "source": "Centro de Distribuicao"
    }
    ch.basic_publish(
        exchange=EXCHANGE,
        routing_key=RK_EXPEDICAO,
        body=json.dumps(payload).encode("utf-8"),
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
            message_id=payload["shipment_id"]
        ),
        mandatory=True
    )
    print("[producer_centro] published:", payload["shipment_id"])
    conn.close()

if __name__ == "__main__":
    main()
