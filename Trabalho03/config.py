# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # carrega o .env da raiz

AMQP_URL = os.getenv("AMQP_URL")

AMQP_EXCHANGE = os.getenv("AMQP_EXCHANGE", "logistica.direct")
AMQP_EXCHANGE_TYPE = os.getenv("AMQP_EXCHANGE_TYPE", "direct")

QUEUE_FATURAMENTO = os.getenv("QUEUE_FATURAMENTO", "faturamento_queue")
QUEUE_EXPEDICAO = os.getenv("QUEUE_EXPEDICAO", "expedicao_queue")
QUEUE_RASTREAMENTO = os.getenv("QUEUE_RASTREAMENTO", "rastreamento_queue")
QUEUE_DLQ = os.getenv("QUEUE_DLQ", "dead_letter_queue")

RK_FATURAMENTO = os.getenv("RK_FATURAMENTO", "faturamento.criado")
RK_EXPEDICAO = os.getenv("RK_EXPEDICAO", "expedicao.criado")
RK_RASTREAMENTO = os.getenv("RK_RASTREAMENTO", "rastreamento.evento")

AMQP_PREFETCH = int(os.getenv("AMQP_PREFETCH", "10"))
RETRY_MAX = int(os.getenv("RETRY_MAX", "5"))
RETRY_DELAY_MS = int(os.getenv("RETRY_DELAY_MS", "5000"))
