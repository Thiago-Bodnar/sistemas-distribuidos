import json, uuid, time, random
import pika
from common import mq_params, declare_topology, EXCHANGE, RK_NOTIFICACAO

def main():
    conn = pika.BlockingConnection(mq_params())
    ch = conn.channel()
    ch.confirm_delivery()
    declare_topology(ch)

    payload = {
        "shipment_id": str(uuid.uuid4()),
        "driver_id": f"DRV-{random.randint(1000,9999)}",
        "status": "COLETADO",
        "gps": {"lat": -26.915, "lng": -49.071},
        "timestamp": int(time.time()),
        "source": "Motorista/App"
    }
    ch.basic_publish(
        exchange=EXCHANGE,
        routing_key=RK_NOTIFICACAO,
        body=json.dumps(payload).encode("utf-8"),
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
            message_id=payload["shipment_id"]
        ),
        mandatory=True
    )
    print("[producer_motorista] published:", payload["shipment_id"])
    conn.close()

if __name__ == "__main__":
    main()
