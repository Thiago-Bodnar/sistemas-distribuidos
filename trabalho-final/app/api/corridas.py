"""Endpoints para /corridas."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.dto import RideResponse
from app.infra.db import get_db
from app.services import ride_service

router = APIRouter(prefix="/corridas", tags=["corridas"])


class AcceptRideRequest(BaseModel):
    """DTO para aceitar corrida."""
    id_motorista: int


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


@router.post("/{ride_id}/aceitar", response_model=RideResponse)
async def accept_ride(
    ride_id: int,
    request: AcceptRideRequest,
    db: Session = Depends(get_db)
):
    """Motorista aceita uma corrida."""
    try:
        ride = ride_service.accept_ride(db, ride_id, request.id_motorista)
        if not ride:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Corrida com ID {ride_id} não encontrada"
            )
        return ride
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{ride_id}/finalizar", response_model=RideResponse)
async def finalize_ride(
    ride_id: int,
    db: Session = Depends(get_db)
):
    """Finaliza uma corrida."""
    try:
        ride = ride_service.finalize_ride(db, ride_id)
        if not ride:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Corrida com ID {ride_id} não encontrada"
            )
        return ride
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

