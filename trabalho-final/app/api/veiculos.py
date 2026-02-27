"""Endpoints para /veiculos."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.domain.dto import VehicleCreate, VehicleResponse, VehicleUpdate
from app.infra.db import get_db
from app.services import vehicle_service

router = APIRouter(prefix="/veiculos", tags=["veiculos"])


@router.get("/", response_model=List[VehicleResponse])
async def list_vehicles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos os veículos."""
    vehicles = vehicle_service.list_vehicles(db, skip=skip, limit=limit)
    return vehicles


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo veículo."""
    try:
        vehicle = vehicle_service.create_vehicle(db, vehicle_data)
        return vehicle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """Obtém um veículo específico."""
    vehicle = vehicle_service.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veículo com ID {vehicle_id} não encontrado"
        )
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um veículo."""
    try:
        vehicle = vehicle_service.update_vehicle(db, vehicle_id, vehicle_data)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Veículo com ID {vehicle_id} não encontrado"
            )
        return vehicle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db)
):
    """Deleta um veículo."""
    deleted = vehicle_service.delete_vehicle(db, vehicle_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veículo com ID {vehicle_id} não encontrado"
        )

