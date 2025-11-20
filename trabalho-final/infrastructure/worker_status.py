import json
import sys

import pika
from sqlalchemy.orm import Session

from config import CLOUDAMQP_URL
from app.infra.db import SessionLocal
from app.infra.models import Corrida, Motorista
from app.domain.enums import RideStatus, DriverStatus


EXCHANGE = "corrida.direct"
STATUS_QUEUE = "status_queue"
ROUTING_KEY = "status"


def _declare_topology(channel):
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    channel.queue_declare(queue=STATUS_QUEUE, durable=True)
    channel.queue_bind(queue=STATUS_QUEUE, exchange=EXCHANGE, routing_key=ROUTING_KEY)


def _update_motorista(db: Session, motorista_id: int, novo_status: str):
    motorista = db.get(Motorista, motorista_id)
    if not motorista:
        return

    if novo_status in (RideStatus.ACEITA.value, RideStatus.EM_ANDAMENTO.value):
        motorista.status = DriverStatus.EM_CORRIDA.value
    elif novo_status in (RideStatus.CONCLUIDA.value, RideStatus.CANCELADA.value):
        motorista.status = DriverStatus.DISPONIVEL.value

    db.commit()


def _handle_status_update(db: Session, data: dict):
    corrida_id = data.get("corrida_id")
    novo_status = data.get("status")

    if corrida_id is None or novo_status is None:
        print("[worker_status] Mensagem inválida:", data)
        return

    corrida: Corrida = db.get(Corrida, corrida_id)
    if not corrida:
        print(f"[worker_status] Corrida {corrida_id} não encontrada.")
        return

    corrida.status = novo_status

    if "motorista_id" in data and data["motorista_id"] is not None:
        corrida.motorista_id = data["motorista_id"]
        _update_motorista(db, data["motorista_id"], novo_status)

    if "valor" in data:
        corrida.valor = data["valor"]
    if "tempo" in data:
        corrida.tempo = data["tempo"]
    if "distancia" in data:
        corrida.distancia = data["distancia"]

    db.commit()
    db.refresh(corrida)

    print(f"[worker_status] Atualizado status da corrida {corrida_id}: {novo_status}")

    # OPCIONAL (ativar se quiser)
    # from app.services.messaging_service import publish_status
    # if novo_status == RideStatus.ACEITA.value:
    #     asyncio.run(publish_status({"tipo": "CORRIDA_EM_ANDAMENTO", "corrida_id": corrida_id}))


def _on_message(channel, method, properties, body):
    try:
        data = json.loads(body)
    except Exception:
        print("[worker_status] Erro parseando JSON:", body)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    db = SessionLocal()
    try:
        _handle_status_update(db, data)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as exc:
        print("[worker_status] ERRO:", exc, file=sys.stderr)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    finally:
        db.close()


def main():
    print("[worker_status] Iniciando consumidor...")

    conn = pika.BlockingConnection(pika.URLParameters(CLOUDAMQP_URL))
    channel = conn.channel()
    _declare_topology(channel)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=STATUS_QUEUE, on_message_callback=_on_message)

    print("[worker_status] Aguardando mensagens...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Encerrando worker_status...")



if __name__ == '__main__':
    main()
