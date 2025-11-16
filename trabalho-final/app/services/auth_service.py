"""Serviço de autenticação e geração de tokens JWT."""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import (JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM,
                        JWT_SECRET_KEY)
from app.infra.models import Motorista, Passageiro
from app.services.passenger_service import verify_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def authenticate_passenger(db: Session, email: str, senha: str) -> Optional[Passageiro]:
    """Autentica um passageiro."""
    passenger = db.query(Passageiro).filter(Passageiro.email == email).first()
    if not passenger:
        return None
    
    if not verify_password(senha, passenger.senha_hash):
        return None
    
    return passenger


def authenticate_driver(db: Session, email: str, senha: str) -> Optional[Motorista]:
    """Autentica um motorista."""
    driver = db.query(Motorista).filter(Motorista.email == email).first()
    if not driver:
        return None
    
    if not verify_password(senha, driver.senha_hash):
        return None
    
    return driver


def verify_token(token: str) -> Optional[dict]:
    """Verifica e decodifica um token JWT."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

