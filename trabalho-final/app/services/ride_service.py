"""Lógica de criação de corrida, seleção de motorista."""
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.enums import RideStatus
from app.infra.models import Corrida, Motorista


async def create_ride(passenger_id: int, origin: str, destination: str):
    """Cria uma nova corrida."""
    # TODO: Implementar
    pass


async def select_driver(ride_id: int):
    """Seleciona um motorista para a corrida."""
    # TODO: Implementar
    pass


def get_ride(db: Session, ride_id: int) -> Optional[Corrida]:
    """Obtém uma corrida por ID."""
    return db.query(Corrida).filter(Corrida.id == ride_id).first()


def accept_ride(db: Session, ride_id: int, driver_id: int) -> Optional[Corrida]:
    """Motorista aceita uma corrida."""
    ride = get_ride(db, ride_id)
    if not ride:
        return None
    
    # Verifica se a corrida está pendente
    if ride.status != RideStatus.PENDENTE.value:
        raise ValueError(f"Corrida não pode ser aceita. Status atual: {ride.status}")
    
    # Verifica se o motorista existe
    driver = db.query(Motorista).filter(Motorista.id == driver_id).first()
    if not driver:
        raise ValueError(f"Motorista com ID {driver_id} não encontrado")
    
    # Verifica se o motorista está disponível
    # TODO: Adicionar verificação de status do motorista quando implementado
    
    # Atualiza a corrida
    ride.id_motorista = driver_id
    ride.id_veiculo = driver.id_veiculo
    ride.status = RideStatus.ACEITA.value
    
    db.commit()
    db.refresh(ride)
    return ride


def finalize_ride(db: Session, ride_id: int) -> Optional[Corrida]:
    """Finaliza uma corrida."""
    ride = get_ride(db, ride_id)
    if not ride:
        return None
    
    # Verifica se a corrida pode ser finalizada
    if ride.status not in [RideStatus.ACEITA.value, RideStatus.EM_ANDAMENTO.value]:
        raise ValueError(f"Corrida não pode ser finalizada. Status atual: {ride.status}")
    
    # Atualiza o status
    ride.status = RideStatus.CONCLUIDA.value
    
    # TODO: Atualizar status do motorista para disponível quando implementado
    
    db.commit()
    db.refresh(ride)
    return ride

