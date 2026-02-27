"""Endpoints de autenticação."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from app.domain.dto import LoginRequest, TokenResponse
from app.infra.db import get_db
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.post("/login/passageiro", response_model=TokenResponse)
async def login_passenger(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login para passageiros."""
    passenger = auth_service.authenticate_passenger(
        db, login_data.email, login_data.senha
    )
    
    if not passenger:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(passenger.id), "type": "passenger"},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": passenger.id,
        "user_type": "passenger"
    }


@router.post("/login/motorista", response_model=TokenResponse)
async def login_driver(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login para motoristas."""
    driver = auth_service.authenticate_driver(
        db, login_data.email, login_data.senha
    )
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(driver.id), "type": "driver"},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": driver.id,
        "user_type": "driver"
    }


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login genérico usando OAuth2 (compatível com Swagger UI).
    Tenta autenticar como passageiro primeiro, depois como motorista.
    """
    # Tenta autenticar como passageiro primeiro
    passenger = auth_service.authenticate_passenger(
        db, form_data.username, form_data.password
    )
    
    if passenger:
        access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": str(passenger.id), "type": "passenger"},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": passenger.id,
            "user_type": "passenger"
        }
    
    # Se não for passageiro, tenta como motorista
    driver = auth_service.authenticate_driver(
        db, form_data.username, form_data.password
    )
    
    if driver:
        access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": str(driver.id), "type": "driver"},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": driver.id,
            "user_type": "driver"
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email ou senha incorretos",
        headers={"WWW-Authenticate": "Bearer"},
    )

