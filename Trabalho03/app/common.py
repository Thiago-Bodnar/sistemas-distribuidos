import json
import os
import time

import pika

EXCHANGE = os.getenv("EXCHANGE_NAME", "logistica.direct")
RK_EXPEDICAO = os.getenv("ROUTING_EXPEDICAO", "expedicao")
RK_NOTIFICACAO = os.getenv("ROUTING_NOTIFICACAO", "notificacao")
RK_FATURAMENTO = os.getenv("ROUTING_FATURAMENTO", "faturamento")

# DLQ Configuration
DLQ_EXCHANGE = os.getenv("DLQ_EXCHANGE", "logistica.dlq")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY_BASE = int(os.getenv("RETRY_DELAY_BASE", "1000"))  # milisegundos

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

def calculate_retry_delay(retry_count: int) -> int:
    """
    Calcula o delay para retry usando exponential backoff.
    """
    return RETRY_DELAY_BASE * (2 ** retry_count)

def get_retry_count(props: pika.BasicProperties) -> int:
    """
    Extrai o número de tentativas de retry dos headers da mensagem.
    """
    if props.headers and 'x-retry-count' in props.headers:
        return props.headers['x-retry-count']
    return 0

def increment_retry_count(props: pika.BasicProperties) -> dict:
    """
    Incrementa o contador de retry nos headers da mensagem.
    """
    headers = props.headers.copy() if props.headers else {}
    headers['x-retry-count'] = get_retry_count(props) + 1
    headers['x-retry-timestamp'] = int(time.time() * 1000)
    return headers

def should_retry(props: pika.BasicProperties) -> bool:
    """
    Verifica se a mensagem ainda pode ser reprocessada.
    """
    return get_retry_count(props) < MAX_RETRIES

def declare_topology(channel: pika.adapters.blocking_connection.BlockingChannel):
    # Exchange principal
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="direct", durable=True)
    
    # DLQ Exchange
    channel.exchange_declare(exchange=DLQ_EXCHANGE, exchange_type="direct", durable=True)
    
    # Queues principais com DLQ configurado (todas apontam para a mesma DLQ)
    channel.queue_declare(
        queue="expedicao_queue", 
        durable=True,
        arguments={
            'x-dead-letter-exchange': DLQ_EXCHANGE,
            'x-dead-letter-routing-key': 'dead.letter'
        }
    )
    channel.queue_declare(
        queue="notificacao_queue", 
        durable=True,
        arguments={
            'x-dead-letter-exchange': DLQ_EXCHANGE,
            'x-dead-letter-routing-key': 'dead.letter'
        }
    )
    channel.queue_declare(
        queue="faturamento_queue", 
        durable=True,
        arguments={
            'x-dead-letter-exchange': DLQ_EXCHANGE,
            'x-dead-letter-routing-key': 'dead.letter'
        }
    )
    
    # DLQ genérica
    channel.queue_declare(queue="dead_letter_queue", durable=True)
    
    # Bindings principais
    channel.queue_bind(queue="expedicao_queue", exchange=EXCHANGE, routing_key=RK_EXPEDICAO)
    channel.queue_bind(queue="notificacao_queue", exchange=EXCHANGE, routing_key=RK_NOTIFICACAO)
    channel.queue_bind(queue="faturamento_queue", exchange=EXCHANGE, routing_key=RK_FATURAMENTO)
    
    # DLQ Binding
    channel.queue_bind(queue="dead_letter_queue", exchange=DLQ_EXCHANGE, routing_key="dead.letter")
