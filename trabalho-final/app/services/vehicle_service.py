"""Lógica CRUD para veículos."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.dto import VehicleCreate, VehicleUpdate
from app.infra.models import Veiculo


def create_vehicle(db: Session, vehicle_data: VehicleCreate) -> Veiculo:
    """Cria um novo veículo."""
    # Verifica se placa já existe
    existing = db.query(Veiculo).filter(Veiculo.placa == vehicle_data.placa).first()
    if existing:
        raise ValueError(f"Placa {vehicle_data.placa} já está em uso")
    
    # Cria novo veículo
    db_vehicle = Veiculo(
        placa=vehicle_data.placa,
        modelo=vehicle_data.modelo,
        cor=vehicle_data.cor
    )
    
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def get_vehicle(db: Session, vehicle_id: int) -> Optional[Veiculo]:
    """Obtém um veículo por ID."""
    return db.query(Veiculo).filter(Veiculo.id == vehicle_id).first()


def get_vehicle_by_placa(db: Session, placa: str) -> Optional[Veiculo]:
    """Obtém um veículo por placa."""
    return db.query(Veiculo).filter(Veiculo.placa == placa).first()


def list_vehicles(db: Session, skip: int = 0, limit: int = 100) -> List[Veiculo]:
    """Lista todos os veículos."""
    return db.query(Veiculo).offset(skip).limit(limit).all()


def update_vehicle(
    db: Session, 
    vehicle_id: int, 
    vehicle_data: VehicleUpdate
) -> Optional[Veiculo]:
    """Atualiza um veículo."""
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return None
    
    # Atualiza campos fornecidos
    update_data = vehicle_data.model_dump(exclude_unset=True)
    
    # Verifica unicidade de placa se estiver sendo atualizada
    if 'placa' in update_data:
        existing = db.query(Veiculo).filter(
            Veiculo.placa == update_data['placa'],
            Veiculo.id != vehicle_id
        ).first()
        if existing:
            raise ValueError(f"Placa {update_data['placa']} já está em uso")
    
    # Atualiza campos
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
    
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def delete_vehicle(db: Session, vehicle_id: int) -> bool:
    """Deleta um veículo."""
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return False
    
    db.delete(db_vehicle)
    db.commit()
    return True

