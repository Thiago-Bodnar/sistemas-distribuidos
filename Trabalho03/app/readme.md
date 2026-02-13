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
```

## Tecnologias
  - Python
  - Docker
  - RabbitMQ
  - Pika

## Mensageria
  - JSON

## 'Boas práticas'
  - ACK
  - Prefetch


## Estrutura
```
app/
  common.py              
  producer_pedidos.py    
  producer_centro.py     
  producer_motorista.py  
  worker_expedicao.py    
  worker_faturamento.py  
  worker_notificacao.py  
  worker_dlq_monitor.py  
config.py                
docker-compose.yml       
Dockerfile
```

## Responsabilidades dos arquivos
  - commmon.py -> conectar com o rabbitMQ e declarar topologia (DLQ e queues)
  - config.py -> centralizar parâmetros
  - producer_*.py -> publicar de eventos
  - worker_*.py -> consumir prefetch e ack
  - worker_dlq_monitor -> ler DLQ e printar diagnóstico

## Fluxo
  - producer_pedidos.py -> rk_expedicao
  - producer_motorista.py -> rk_notificacao.py
  - producer_centro.py -> rk_expedicao.py
  - worker_expedicao.py
    - consume(expedicao) + ACK
    - publish → rk_faturamento  ← encadeia estágio

  - worker_faturamento.py
    - consume(faturamento) + ACK (fim do pipeline)

  - worker_notificacao.py
    - consume(notificacao) + ACK (trilha paralela)

  - worker_dlq_monitor.py
    - consume(DLQ) → imprime shipment_id, headers (x-retry-count/x-death), payload

