"""Endpoints para /passageiros (usuários)."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.domain.dto import PassengerCreate, PassengerResponse, PassengerUpdate
from app.infra.db import get_db
from app.services import passenger_service

router = APIRouter(prefix="/passageiros", tags=["passageiros"])


@router.get("/", response_model=List[PassengerResponse])
async def list_passengers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos os passageiros."""
    passengers = passenger_service.list_passengers(db, skip=skip, limit=limit)
    return passengers


@router.post("/", response_model=PassengerResponse, status_code=status.HTTP_201_CREATED)
async def create_passenger(
    passenger_data: PassengerCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo passageiro."""
    try:
        passenger = passenger_service.create_passenger(db, passenger_data)
        return passenger
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{passenger_id}", response_model=PassengerResponse)
async def get_passenger(
    passenger_id: int,
    db: Session = Depends(get_db)
):
    """Obtém um passageiro específico."""
    passenger = passenger_service.get_passenger(db, passenger_id)
    if not passenger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passageiro com ID {passenger_id} não encontrado"
        )
    return passenger


@router.put("/{passenger_id}", response_model=PassengerResponse)
async def update_passenger(
    passenger_id: int,
    passenger_data: PassengerUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um passageiro."""
    try:
        passenger = passenger_service.update_passenger(db, passenger_id, passenger_data)
        if not passenger:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Passageiro com ID {passenger_id} não encontrado"
            )
        return passenger
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{passenger_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_passenger(
    passenger_id: int,
    db: Session = Depends(get_db)
):
    """Deleta um passageiro."""
    deleted = passenger_service.delete_passenger(db, passenger_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passageiro com ID {passenger_id} não encontrado"
        )

