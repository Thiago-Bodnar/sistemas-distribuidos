"""Endpoints para /servers, /status, etc."""
from fastapi import APIRouter

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get("/")
async def list_servers():
    """Lista todos os servidores."""
    # TODO: Implementar lógica
    return {"message": "List servers - placeholder"}


@router.get("/status")
async def get_status():
    """Obtém o status do sistema."""
    # TODO: Implementar lógica
    return {"message": "Get status - placeholder"}


@router.get("/{server_id}")
async def get_server(server_id: int):
    """Obtém um servidor específico."""
    # TODO: Implementar lógica
    return {"message": f"Get server {server_id} - placeholder"}

