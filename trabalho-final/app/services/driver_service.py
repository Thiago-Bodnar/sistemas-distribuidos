"""Lógica CRUD para motoristas."""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.dto import DriverCreate, DriverUpdate
from app.infra.models import Motorista
from app.services.passenger_service import hash_password, verify_password


def create_driver(db: Session, driver_data: DriverCreate) -> Motorista:
    """Cria um novo motorista."""
    # Verifica se email já existe
    existing = db.query(Motorista).filter(Motorista.email == driver_data.email).first()
    if existing:
        raise ValueError(f"Email {driver_data.email} já está em uso")
    
    # Verifica se telefone já existe
    existing = db.query(Motorista).filter(Motorista.telefone == driver_data.telefone).first()
    if existing:
        raise ValueError(f"Telefone {driver_data.telefone} já está em uso")
    
    # Verifica se nome já existe
    existing = db.query(Motorista).filter(Motorista.nome == driver_data.nome).first()
    if existing:
        raise ValueError(f"Nome {driver_data.nome} já está em uso")
    
    # Cria hash da senha
    senha_hash = hash_password(driver_data.senha)
    
    # Cria novo motorista
    db_driver = Motorista(
        nome=driver_data.nome,
        email=driver_data.email,
        telefone=driver_data.telefone,
        senha_hash=senha_hash,
        localizacao_atual=driver_data.localizacao_atual,
        id_veiculo=driver_data.id_veiculo,
        id_servidor=driver_data.id_servidor
    )
    
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver


def get_driver(db: Session, driver_id: int) -> Optional[Motorista]:
    """Obtém um motorista por ID."""
    return db.query(Motorista).filter(Motorista.id == driver_id).first()


def get_driver_by_email(db: Session, email: str) -> Optional[Motorista]:
    """Obtém um motorista por email."""
    return db.query(Motorista).filter(Motorista.email == email).first()


def list_drivers(db: Session, skip: int = 0, limit: int = 100) -> List[Motorista]:
    """Lista todos os motoristas."""
    return db.query(Motorista).offset(skip).limit(limit).all()


def update_driver(
    db: Session, 
    driver_id: int, 
    driver_data: DriverUpdate
) -> Optional[Motorista]:
    """Atualiza um motorista."""
    db_driver = get_driver(db, driver_id)
    if not db_driver:
        return None
    
    # Atualiza campos fornecidos
    update_data = driver_data.model_dump(exclude_unset=True)
    
    # Se senha foi fornecida, gera hash
    if 'senha' in update_data:
        update_data['senha_hash'] = hash_password(update_data.pop('senha'))
    
    # Verifica unicidade de email se estiver sendo atualizado
    if 'email' in update_data:
        existing = db.query(Motorista).filter(
            Motorista.email == update_data['email'],
            Motorista.id != driver_id
        ).first()
        if existing:
            raise ValueError(f"Email {update_data['email']} já está em uso")
    
    # Verifica unicidade de telefone se estiver sendo atualizado
    if 'telefone' in update_data:
        existing = db.query(Motorista).filter(
            Motorista.telefone == update_data['telefone'],
            Motorista.id != driver_id
        ).first()
        if existing:
            raise ValueError(f"Telefone {update_data['telefone']} já está em uso")
    
    # Verifica unicidade de nome se estiver sendo atualizado
    if 'nome' in update_data:
        existing = db.query(Motorista).filter(
            Motorista.nome == update_data['nome'],
            Motorista.id != driver_id
        ).first()
        if existing:
            raise ValueError(f"Nome {update_data['nome']} já está em uso")
    
    # Atualiza campos
    for field, value in update_data.items():
        setattr(db_driver, field, value)
    
    db.commit()
    db.refresh(db_driver)
    return db_driver


def delete_driver(db: Session, driver_id: int) -> bool:
    """Deleta um motorista."""
    db_driver = get_driver(db, driver_id)
    if not db_driver:
        return False
    
    db.delete(db_driver)
    db.commit()
    return True


def get_available_drivers(region: str = None):
    """Obtém motoristas disponíveis."""
    # TODO: Implementar lógica de disponibilidade
    pass
