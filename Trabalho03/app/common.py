import os
import pika

EXCHANGE = os.getenv("EXCHANGE_NAME", "logistica.direct")
RK_EXPEDICAO = os.getenv("ROUTING_EXPEDICAO", "expedicao")
RK_NOTIFICACAO = os.getenv("ROUTING_NOTIFICACAO", "notificacao")
RK_FATURAMENTO = os.getenv("ROUTING_FATURAMENTO", "faturamento")

def mq_params():
    """
    Conecta via URL do CloudAMQP (amqps://...).
    """
    url = os.getenv("CLOUDAMQP_URL") or os.getenv("AMQP_URL")
    if url:
        params = pika.URLParameters(url)
        params.heartbeat = 30
        params.blocked_connection_timeout = 300
        params.socket_timeout = 10
        return params

    # fallback (para testes locais)
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

def declare_topology(channel: pika.adapters.blocking_connection.BlockingChannel):
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    channel.queue_declare(queue="expedicao_queue", durable=True)
    channel.queue_declare(queue="notificacao_queue", durable=True)
    channel.queue_declare(queue="faturamento_queue", durable=True)
    channel.queue_bind(queue="expedicao_queue", exchange=EXCHANGE, routing_key=RK_EXPEDICAO)
    channel.queue_bind(queue="notificacao_queue", exchange=EXCHANGE, routing_key=RK_NOTIFICACAO)
    channel.queue_bind(queue="faturamento_queue", exchange=EXCHANGE, routing_key=RK_FATURAMENTO)
