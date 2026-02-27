"""Endpoints para /motoristas."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.domain.dto import (DriverCreate, DriverResponse, DriverStatusUpdate,
                            DriverUpdate)
from app.infra.db import get_db
from app.services import driver_service

router = APIRouter(prefix="/motoristas", tags=["motoristas"])


@router.get("/", response_model=List[DriverResponse])
async def list_drivers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos os motoristas."""
    drivers = driver_service.list_drivers(db, skip=skip, limit=limit)
    return drivers


@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(
    driver_data: DriverCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo motorista."""
    try:
        driver = driver_service.create_driver(db, driver_data)
        return driver
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: int,
    db: Session = Depends(get_db)
):
    """Obtém um motorista específico."""
    driver = driver_service.get_driver(db, driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Motorista com ID {driver_id} não encontrado"
        )
    return driver


@router.put("/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: int,
    driver_data: DriverUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza um motorista."""
    try:
        driver = driver_service.update_driver(db, driver_id, driver_data)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Motorista com ID {driver_id} não encontrado"
            )
        return driver
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(
    driver_id: int,
    db: Session = Depends(get_db)
):
    """Deleta um motorista."""
    deleted = driver_service.delete_driver(db, driver_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Motorista com ID {driver_id} não encontrado"
        )


@router.put("/{driver_id}/status", response_model=DriverResponse)
async def update_driver_status(
    driver_id: int,
    status_data: DriverStatusUpdate,
    db: Session = Depends(get_db)
):
    """Atualiza o status e localização de um motorista."""
    driver = driver_service.get_driver(db, driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Motorista com ID {driver_id} não encontrado"
        )
    
    # Atualiza localização se fornecida
    if status_data.localizacao_atual:
        driver.localizacao_atual = status_data.localizacao_atual
    
    db.commit()
    db.refresh(driver)
    return driver

