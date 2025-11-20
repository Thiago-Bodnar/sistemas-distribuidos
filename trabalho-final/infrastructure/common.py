"""Publicar/consumir mensagens no RabbitMQ."""
import asyncio
import json
import os
from typing import Any, Awaitable, Callable

import pika

from app.config import RABBIT_URL

EXCHANGE = os.getenv("EXCHANGE_NAME", "corrida.direct")
RK_STATUS = os.getenv("ROUTING_STATUS", "status")
RK_AJUDA = os.getenv("ROUTING_AJUDA", "ajuda")

Q_STATUS = os.getenv("QUEUE_STATUS", "status_queue")
Q_AJUDA = os.getenv("QUEUE_AJUDA", "ajuda_queue")


def _mq_params() -> pika.ConnectionParameters:
    """Monta parâmetros de conexão a partir do RABBIT_URL ou variáveis simples."""
    url = os.getenv("CLOUDAMQP_URL") or os.getenv("AMQP_URL") or RABBIT_URL
    if url:
        params = pika.URLParameters(url)
        params.heartbeat = 30
        params.blocked_connection_timeout = 300
        params.socket_timeout = 10
        return params

    creds = pika.PlainCredentials(
        os.getenv("RABBITMQ_USER", "guest"),
        os.getenv("RABBITMQ_PASS", "guest"),
    )
    return pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        virtual_host=os.getenv("RABBITMQ_VHOST", "/"),
        credentials=creds,
        heartbeat=30,
        blocked_connection_timeout=300,
    )


def declare_topology(channel: pika.adapters.blocking_connection.BlockingChannel) -> None:
    """Declara exchange + filas + binds."""
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)

    channel.queue_declare(queue=Q_STATUS, durable=True)
    channel.queue_declare(queue=Q_AJUDA, durable=True)

    channel.queue_bind(queue=Q_STATUS, exchange=EXCHANGE, routing_key=RK_STATUS)
    channel.queue_bind(queue=Q_AJUDA, exchange=EXCHANGE, routing_key=RK_AJUDA)


# ---------------------------------------------------------------------------
# Producers
# ---------------------------------------------------------------------------

async def publish_message(exchange: str, routing_key: str, message: dict) -> None:
    """
    Publica uma mensagem no RabbitMQ.

    Obs.: usa conexão bloqueante do pika, então roda em thread via run_in_executor.
    Para este trabalho está ótimo.
    """
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _publish_blocking, exchange, routing_key, message)


def _publish_blocking(exchange: str, routing_key: str, message: dict) -> None:
    connection = pika.BlockingConnection(_mq_params())
    channel = connection.channel()
    declare_topology(channel)

    body = json.dumps(message).encode("utf-8")

    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=body,
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
        ),
    )
    connection.close()


async def publish_status(message: dict) -> None:
    """Helper específico para mensagens de status."""
    await publish_message(EXCHANGE, RK_STATUS, message)


async def publish_ajuda(message: dict) -> None:
    """Helper específico para mensagens de ajuda/eleição."""
    await publish_message(EXCHANGE, RK_AJUDA, message)


# ---------------------------------------------------------------------------
# Consumers (workers)
# ---------------------------------------------------------------------------

def _consume_blocking(queue: str, handler: Callable[[dict], None]) -> None:
    """Loop de consumo síncrono, pensado para rodar em script worker separado."""
    connection = pika.BlockingConnection(_mq_params())
    channel = connection.channel()
    declare_topology(channel)

    def _callback(ch, method, properties, body):
        data = json.loads(body.decode("utf-8"))
        handler(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=_callback)
    print(f"[x] Consumindo fila {queue} ...")
    channel.start_consuming()


async def consume_messages(queue: str, handler: Callable[[dict], Awaitable[None]] | Callable[[dict], None]) -> None:
    """
    Versão async-friendly para se você quiser chamar de dentro de algo async.

    Na prática, para os workers eu usaria diretamente `_consume_blocking`
    em um script separado (worker_status.py, worker_ajuda.py).
    """
    loop = asyncio.get_running_loop()

    def wrapper_sync(msg: dict):
        if asyncio.iscoroutinefunction(handler):
            asyncio.run_coroutine_threadsafe(handler(msg), loop)
        else:
            handler(msg)

    await loop.run_in_executor(None, _consume_blocking, queue, wrapper_sync)
