"""
Serviço de eleição de coordenador entre nós distribuídos.

Implementação inspirada no Bully Algorithm, porém usando
UPTIME como critério de prioridade (maior uptime vence).

Fluxo:
- Cada nó envia heartbeats periódicos com seu uptime.
- Todos mantêm no DB a tabela `Servidor` com last_heartbeat e uptime.
- Quando um nó detecta que o coordenador falhou (timeout), inicia eleição.
- O worker_ajuda chama `handle_election_message` ao receber mensagens de ajuda.
"""

import datetime
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.infra.db import SessionLocal
from app.infra.models import Servidor
from infrastructure.common import publish_ajuda

from app.config import NODE_ID


# ---------------------------
# Parâmetros globais da eleição
# ---------------------------

HEARTBEAT_TIMEOUT = 5


# ---------------------------
# Funções auxiliares internas
# ---------------------------

def _get_all_nodes(db: Session):
    return db.query(Servidor).all()


def _get_current_coordinator(db: Session) -> Optional[Servidor]:
    return (
        db.query(Servidor)
        .filter(Servidor.is_coordenador == True)   # noqa: E712
        .first()
    )


def _mark_all_as_non_coordinator(db: Session):
    db.query(Servidor).update({Servidor.is_coordenador: False})
    db.commit()


def _select_best_node(nodes):
    """
    Critério principal: maior uptime (como descrito no relatório).
    Empate: maior node_id.
    """
    return sorted(
        nodes,
        key=lambda n: (n.uptime or 0, n.node_id),
        reverse=True
    )[0]


def _send_new_coordinator_event(node_id: str):
    """
    Notifica todo o cluster que há um novo coordenador.
    """
    msg = {
        "tipo": "COORDENADOR_ELEITO",
        "coordenador_id": node_id
    }
    # Mensagem vai pelo routing_key ajuda
    import asyncio
    asyncio.run(publish_ajuda(msg))


# ---------------------------
# API Pública — chamada pelo worker_ajuda
# ---------------------------

def handle_election_message(message: Dict):
    """
    Processa mensagens vindas do RabbitMQ (worker_ajuda).
    Pode ser chamada de forma síncrona.
    """

    tipo = message.get("tipo")

    if tipo == "ELEICAO_INICIADA":
        origin = message.get("origin")
        print(f"[election_service] Eleição iniciada por {origin}")
        return start_election()

    elif tipo == "COORDENADOR_ELEITO":
        eleito = message.get("coordenador_id")
        print(f"[election_service] Novo coordenador recebido: {eleito}")
        return register_new_coordinator(eleito)

    else:
        print(f"[election_service] Mensagem não reconhecida: {message}")
        return None


# ---------------------------
# Iniciar eleição
# ---------------------------

def start_election():
    """
    Inicia o processo global de eleição.

    Etapas:
    1. Verifica nós conhecidos
    2. Remove nós que não enviam heartbeat
    3. Seleciona nó com maior uptime
    4. Atualiza DB
    5. Emite evento COORDENADOR_ELEITO
    """
    db: Session = SessionLocal()

    print("[election_service] Iniciando eleição...")

    nodes = _get_all_nodes(db)
    if not nodes:
        print("[election_service] Nenhum nó cadastrado!")
        return None

    alive_nodes = []
    now = datetime.datetime.utcnow()

    for n in nodes:
        if not n.ultimo_heartbeat:
            continue
        diff = (now - n.ultimo_heartbeat).total_seconds()
        if diff <= HEARTBEAT_TIMEOUT:
            alive_nodes.append(n)

    if not alive_nodes:
        print("[election_service] Nenhum nó vivo suficiente para eleição!")
        return None

    winner = _select_best_node(alive_nodes)

    _mark_all_as_non_coordinator(db)

    winner.is_coordenador = True
    db.commit()

    print(f"[election_service] Novo coordenador eleito: {winner.node_id}")

    _send_new_coordinator_event(winner.node_id)

    return winner.node_id


# ---------------------------
# Registrar coordenador recebido via mensagem
# ---------------------------

def register_new_coordinator(coordinator_id: str):
    """
    Chamado quando recebemos COORDENADOR_ELEITO de outro nó.
    """
    db: Session = SessionLocal()

    print(f"[election_service] Registrando coordenador {coordinator_id}")

    nodes = _get_all_nodes(db)

    for n in nodes:
        n.is_coordenador = False

    chosen = (
        db.query(Servidor)
        .filter(Servidor.node_id == coordinator_id)
        .first()
    )

    if chosen:
        chosen.is_coordenador = True
        db.commit()
        print(f"[election_service] Coordenador {coordinator_id} registrado com sucesso.")
        return coordinator_id

    print("[election_service] Coordenador recebido não existe no banco.")
    return None
