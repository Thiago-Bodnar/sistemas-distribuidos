"""Lógica CRUD para passageiros/usuários."""
from typing import List, Optional

import bcrypt
from sqlalchemy.orm import Session

from app.domain.dto import PassengerCreate, PassengerUpdate
from app.infra.models import Passageiro


def hash_password(password: str) -> str:
    """Gera hash da senha usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha está correta."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_passenger(db: Session, passenger_data: PassengerCreate) -> Passageiro:
    """Cria um novo passageiro."""
    # Verifica se email já existe
    existing = db.query(Passageiro).filter(Passageiro.email == passenger_data.email).first()
    if existing:
        raise ValueError(f"Email {passenger_data.email} já está em uso")
    
    # Verifica se telefone já existe
    existing = db.query(Passageiro).filter(Passageiro.telefone == passenger_data.telefone).first()
    if existing:
        raise ValueError(f"Telefone {passenger_data.telefone} já está em uso")
    
    # Verifica se nome já existe
    existing = db.query(Passageiro).filter(Passageiro.nome == passenger_data.nome).first()
    if existing:
        raise ValueError(f"Nome {passenger_data.nome} já está em uso")
    
    # Cria hash da senha
    senha_hash = hash_password(passenger_data.senha)
    
    # Cria novo passageiro
    db_passenger = Passageiro(
        nome=passenger_data.nome,
        email=passenger_data.email,
        telefone=passenger_data.telefone,
        senha_hash=senha_hash
    )
    
    db.add(db_passenger)
    db.commit()
    db.refresh(db_passenger)
    return db_passenger


def get_passenger(db: Session, passenger_id: int) -> Optional[Passageiro]:
    """Obtém um passageiro por ID."""
    return db.query(Passageiro).filter(Passageiro.id == passenger_id).first()


def get_passenger_by_email(db: Session, email: str) -> Optional[Passageiro]:
    """Obtém um passageiro por email."""
    return db.query(Passageiro).filter(Passageiro.email == email).first()


def list_passengers(db: Session, skip: int = 0, limit: int = 100) -> List[Passageiro]:
    """Lista todos os passageiros."""
    return db.query(Passageiro).offset(skip).limit(limit).all()


def update_passenger(
    db: Session, 
    passenger_id: int, 
    passenger_data: PassengerUpdate
) -> Optional[Passageiro]:
    """Atualiza um passageiro."""
    db_passenger = get_passenger(db, passenger_id)
    if not db_passenger:
        return None
    
    # Atualiza campos fornecidos
    update_data = passenger_data.model_dump(exclude_unset=True)
    
    # Se senha foi fornecida, gera hash
    if 'senha' in update_data:
        update_data['senha_hash'] = hash_password(update_data.pop('senha'))
    
    # Verifica unicidade de email se estiver sendo atualizado
    if 'email' in update_data:
        existing = db.query(Passageiro).filter(
            Passageiro.email == update_data['email'],
            Passageiro.id != passenger_id
        ).first()
        if existing:
            raise ValueError(f"Email {update_data['email']} já está em uso")
    
    # Verifica unicidade de telefone se estiver sendo atualizado
    if 'telefone' in update_data:
        existing = db.query(Passageiro).filter(
            Passageiro.telefone == update_data['telefone'],
            Passageiro.id != passenger_id
        ).first()
        if existing:
            raise ValueError(f"Telefone {update_data['telefone']} já está em uso")
    
    # Verifica unicidade de nome se estiver sendo atualizado
    if 'nome' in update_data:
        existing = db.query(Passageiro).filter(
            Passageiro.nome == update_data['nome'],
            Passageiro.id != passenger_id
        ).first()
        if existing:
            raise ValueError(f"Nome {update_data['nome']} já está em uso")
    
    # Atualiza campos
    for field, value in update_data.items():
        setattr(db_passenger, field, value)
    
    db.commit()
    db.refresh(db_passenger)
    return db_passenger


def delete_passenger(db: Session, passenger_id: int) -> bool:
    """Deleta um passageiro."""
    db_passenger = get_passenger(db, passenger_id)
    if not db_passenger:
        return False
    
    db.delete(db_passenger)
    db.commit()
    return True

