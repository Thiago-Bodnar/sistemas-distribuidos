"""
Serviço de heartbeat entre nós distribuídos.

Responsabilidades:
- Enviar periodicamente heartbeats do nó atual para a fila de AJUDA.
- Atualizar/registrar nós na tabela Servidor com uptime e last_heartbeat.
- Verificar saúde do coordenador e disparar eleição quando necessário.

Formato de HEARTBEAT enviado:

{
    "tipo": "HEARTBEAT",
    "node_id": "<NODE_ID>",
    "uptime": 123.45,
    "timestamp": "2025-11-19T18:00:00Z"
}
"""

import datetime
from typing import Optional, Dict, Any

import asyncio
from sqlalchemy.orm import Session

from app.config import NODE_ID
from app.infra.db import SessionLocal
from app.infra.models import Servidor

from infrastructure.common import publish_ajuda

HEARTBEAT_TIMEOUT = 5


# --------------------------------------------------------------------
# Helpers internos
# --------------------------------------------------------------------

def _get_node(db: Session, node_id: str) -> Optional[Servidor]:
    return (
        db.query(Servidor)
        .filter(Servidor.node_id == node_id)
        .first()
    )


def _get_or_create_local_node(db: Session) -> Servidor:
    """
    Garante que exista um registro para o nó atual (NODE_ID) na tabela Servidor.
    """
    node = _get_node(db, NODE_ID)
    if node:
        return node

    now = datetime.datetime.utcnow()
    node = Servidor(
        node_id=NODE_ID,
        nome='a',
        regiao='b',
        uptime=0.0,
        ultimo_heartbeat=now,
        is_coordenador=False,
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def _get_current_coordinator(db: Session) -> Optional[Servidor]:
    return (
        db.query(Servidor)
        .filter(Servidor.is_coordenador == True)  # noqa: E712
        .first()
    )


# --------------------------------------------------------------------
# Envio de HEARTBEAT (chamado periodicamente por algum scheduler)
# --------------------------------------------------------------------


async def send_heartbeat() -> None:
    """
    Envia um heartbeat do nó atual (NODE_ID) para a fila de ajuda.

    Deve ser chamado periodicamente (ex.: a cada 2 ou 3 segundos)
    por um scheduler, background task do FastAPI, cron, etc.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.datetime.utcnow()

        node = _get_or_create_local_node(db)

        # calcula uptime incremental com base no tempo desde o último heartbeat
        if node.ultimo_heartbeat:
            delta = (now - node.ultimo_heartbeat).total_seconds()
            if delta < 0:
                delta = 0
        else:
            delta = 0

        node.uptime = (node.uptime or 0.0) + delta
        node.ultimo_heartbeat = now
        db.commit()
        db.refresh(node)

        msg: Dict[str, Any] = {
            "tipo": "HEARTBEAT",
            "node_id": NODE_ID,
            "uptime": float(node.uptime or 0.0),
            "timestamp": now.replace(tzinfo=datetime.timezone.utc).isoformat(),
        }

        print(f"[heartbeat_service] Enviando HEARTBEAT: {msg}")

        # publish_ajuda é async; aqui estamos num contexto síncrono,
        # então usamos asyncio.run. Se você for chamar de um lugar async,
        # prefira await publish_ajuda(msg) diretamente.
        await publish_ajuda(msg)


    finally:
        db.close()


# --------------------------------------------------------------------
# Processamento de HEARTBEAT recebidos (chamado pelo worker_ajuda)
# --------------------------------------------------------------------

def process_heartbeat(node_id: str, heartbeat_data: Dict[str, Any]) -> Optional[float]:
    """
    Atualiza o registro do nó que enviou heartbeat.

    Chamado pelo worker_ajuda quando chega uma mensagem do tipo HEARTBEAT.

    Retorna o uptime do nó, se conseguir processar.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.datetime.utcnow()

        node = _get_node(db, node_id)
        if not node:
            # se nó não existe, cria com base nos dados recebidos
            node = Servidor(
                node_id=node_id,
                uptime=float(heartbeat_data.get("uptime") or 0.0),
                ultimo_heartbeat=now,
                is_coordenador=False,
            )
            db.add(node)
        else:
            # se veio uptime explícito, confia nele
            if "uptime" in heartbeat_data and heartbeat_data["uptime"] is not None:
                node.uptime = float(heartbeat_data["uptime"])
            else:
                # caso contrário, incrementa com base no tempo
                if node.ultimo_heartbeat:
                    delta = (now - node.ultimo_heartbeat).total_seconds()
                    if delta < 0:
                        delta = 0
                else:
                    delta = 0
                node.uptime = (node.uptime or 0.0) + delta

            node.ultimo_heartbeat = now

        db.commit()
        db.refresh(node)

        print(f"[heartbeat_service] Atualizado heartbeat de {node_id} -> uptime={node.uptime}")
        return float(node.uptime or 0.0)
    finally:
        db.close()


# --------------------------------------------------------------------
# Verificação de saúde e disparo de eleição
# --------------------------------------------------------------------

def check_node_health() -> Dict[str, Any]:
    """
    Verifica a saúde do coordenador atual.

    - Se não houver coordenador, dispara eleição.
    - Se houver e estiver sem heartbeat há mais de HEARTBEAT_TIMEOUT,
      dispara eleição.
    - Caso contrário, retorna que está tudo OK.

    Chamado pelo worker_ajuda quando chega mensagem 'CHECK_HEALTH'
    ou por um endpoint de debug/monitoramento.
    """
    db: Session = SessionLocal()
    try:
        now = datetime.datetime.utcnow()
        coordinator = _get_current_coordinator(db)

        if coordinator is None:
            print("[heartbeat_service] Nenhum coordenador registrado. Iniciando eleição...")
            from app.services import election_service
            new_coord = election_service.start_election()
            return {
                "status": "election_started",
                "reason": "no_coordinator",
                "new_coordinator": new_coord,
            }

        if not coordinator.ultimo_heartbeat:
            diff = float("inf")
        else:
            diff = (now - coordinator.ultimo_heartbeat).total_seconds()

        if diff > HEARTBEAT_TIMEOUT:
            print("[heartbeat_service] Coordenador atual parece ter falhado. Iniciando eleição...")
            from app.services import election_service
            new_coord = election_service.start_election()
            return {
                "status": "election_started",
                "reason": "coordinator_timeout",
                "old_coordinator": coordinator.node_id,
                "new_coordinator": new_coord,
            }

        print(f"[heartbeat_service] Coordenador saudável: {coordinator.node_id}, diff={diff:.2f}s")
        return {
            "status": "ok",
            "coordinator": coordinator.node_id,
            "last_heartbeat_diff": diff,
        }

    finally:
        db.close()
