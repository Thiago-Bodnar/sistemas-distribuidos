"""Endpoints para /corridas."""
from fastapi import APIRouter

router = APIRouter(prefix="/corridas", tags=["rides"])


@router.get("/")
async def list_rides():
    """Lista todas as corridas."""
    # TODO: Implementar lógica
    return {"message": "List rides - placeholder"}


@router.post("/")
async def create_ride():
    """Cria uma nova corrida."""
    # TODO: Implementar lógica
    return {"message": "Create ride - placeholder"}


@router.get("/{ride_id}")
async def get_ride(ride_id: int):
    """Obtém uma corrida específica."""
    # TODO: Implementar lógica
    return {"message": f"Get ride {ride_id} - placeholder"}


@router.put("/{ride_id}")
async def update_ride(ride_id: int):
    """Atualiza uma corrida."""
    # TODO: Implementar lógica
    return {"message": f"Update ride {ride_id} - placeholder"}

