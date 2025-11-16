"""Endpoints para /motoristas."""
from fastapi import APIRouter

router = APIRouter(prefix="/motoristas", tags=["drivers"])


@router.get("/")
async def list_drivers():
    """Lista todos os motoristas."""
    # TODO: Implementar lógica
    return {"message": "List drivers - placeholder"}


@router.post("/")
async def create_driver():
    """Cria um novo motorista."""
    # TODO: Implementar lógica
    return {"message": "Create driver - placeholder"}


@router.get("/{driver_id}")
async def get_driver(driver_id: int):
    """Obtém um motorista específico."""
    # TODO: Implementar lógica
    return {"message": f"Get driver {driver_id} - placeholder"}


@router.put("/{driver_id}/status")
async def update_driver_status(driver_id: int):
    """Atualiza o status de um motorista."""
    # TODO: Implementar lógica
    return {"message": f"Update driver {driver_id} status - placeholder"}

