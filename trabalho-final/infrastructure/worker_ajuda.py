import json
import os
import sys
import pika
from app.services import heartbeat_service, election_service
from config import CLOUDAMQP_URL, NODE_ID

EXCHANGE = "corrida.direct"
AJUDA_QUEUE = "ajuda_queue"
ROUTING_KEY = "ajuda"


def _declare_topology(channel):
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    channel.queue_declare(queue=AJUDA_QUEUE, durable=True)
    channel.queue_bind(queue=AJUDA_QUEUE, exchange=EXCHANGE, routing_key=ROUTING_KEY)


def _on_message(channel, method, properties, body):
    try:
        data = json.loads(body)
    except Exception:
        print("[worker_ajuda] Erro parseando JSON")
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return

    tipo = data.get("tipo")

    print(f"[worker_ajuda][{NODE_ID}] Mensagem recebida:", data)

    try:
        if tipo == "HEARTBEAT":
            heartbeat_service.process_heartbeat(data["node_id"], data)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        if tipo == "CHECK_HEALTH":
            heartbeat_service.check_node_health()
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        if tipo in ("ELEICAO_INICIADA", "COORDENADOR_ELEITO"):
            election_service.handle_election_message(data)
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        print("[worker_ajuda] Mensagem desconhecida:", data)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as exc:
        print("[worker_ajuda] ERRO:", exc, file=sys.stderr)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    print(f"[worker_ajuda][{NODE_ID}] Iniciando consumidor...")

    conn = pika.BlockingConnection(pika.URLParameters(CLOUDAMQP_URL))
    channel = conn.channel()
    _declare_topology(channel)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=AJUDA_QUEUE, on_message_callback=_on_message)

    print(f"[worker_ajuda][{NODE_ID}] Aguardando mensagens...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Encerrando worker_ajuda...")

if __name__ == '__main__':
    main()
