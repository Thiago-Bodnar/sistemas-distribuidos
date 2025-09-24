# Logística MQ (CloudAMQP + Docker + Python)

Este projeto conecta no **CloudAMQP** (RabbitMQ gerenciado).  
Não há serviço RabbitMQ local no compose; apenas o container da aplicação Python.

## Pré-requisitos
1. Crie uma instância em https://www.cloudamqp.com/ (planos gratuitos servem para testes).
2. Copie a **AMQP URL** (formato `amqps://USER:PASS@HOST/vhost`).
3. Cole em `.env` na variável `CLOUDAMQP_URL`.

## Subir
```bash
docker compose up -d --build

## Iniciar consumidores
docker compose exec app python worker_expedicao.py
docker compose exec app python worker_notificacao.py
docker compose exec app python worker_faturamento.py

#Publicar mensagens
docker compose exec app python producer_pedidos.py
docker compose exec app python producer_centro.py
docker compose exec app python producer_motorista.py


