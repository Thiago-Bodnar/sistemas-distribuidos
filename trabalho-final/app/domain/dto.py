"""Schemas/Pydantic para requests/responses."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Driver DTOs
class DriverCreate(BaseModel):
    """DTO para criação de motorista."""
    nome: str
    email: str
    telefone: str
    senha: str
    localizacao_atual: Optional[str] = None
    id_veiculo: Optional[int] = None
    id_servidor: Optional[int] = None


class DriverUpdate(BaseModel):
    """DTO para atualização de motorista."""
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    senha: Optional[str] = None
    localizacao_atual: Optional[str] = None
    id_veiculo: Optional[int] = None
    id_servidor: Optional[int] = None


class DriverResponse(BaseModel):
    """DTO para resposta de motorista."""
    id: int
    nome: str
    email: str
    telefone: str
    localizacao_atual: Optional[str] = None
    id_veiculo: Optional[int] = None
    id_servidor: Optional[int] = None

    class Config:
        from_attributes = True


class DriverStatusUpdate(BaseModel):
    """DTO para atualização de status do motorista."""
    status: str
    localizacao_atual: Optional[str] = None


# Passenger/User DTOs
class PassengerCreate(BaseModel):
    """DTO para criação de passageiro/usuário."""
    nome: str
    email: str
    telefone: str
    senha: str


class PassengerUpdate(BaseModel):
    """DTO para atualização de passageiro/usuário."""
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    senha: Optional[str] = None


class PassengerResponse(BaseModel):
    """DTO para resposta de passageiro/usuário."""
    id: int
    nome: str
    email: str
    telefone: str

    class Config:
        from_attributes = True


# Ride DTOs
class RideCreate(BaseModel):
    """DTO para criação de corrida."""
    id_passageiro: int
    origem: str
    destino: str
    # TODO: Adicionar outros campos conforme necessário


class RideResponse(BaseModel):
    """DTO para resposta de corrida."""
    id: int
    id_motorista: Optional[int] = None
    id_passageiro: int
    id_veiculo: Optional[int] = None
    id_servidor: Optional[int] = None
    origem: str
    destino: str
    status: str
    valor: Optional[float] = None
    tempo: Optional[int] = None
    distancia: Optional[float] = None
    
    class Config:
        from_attributes = True


# Server/Node DTOs
class ServerResponse(BaseModel):
    """DTO para resposta de servidor."""
    id: int
    nome: str
    regiao: str
    uptime: int
    is_coordenador: bool
    ultimo_heartbeat: Optional[datetime] = None


class StatusResponse(BaseModel):
    """DTO para resposta de status do sistema."""
    node_id: str
    region: str
    is_coordenador: bool
    status: str
    # TODO: Adicionar outros campos conforme necessário


# Auth DTOs
class LoginRequest(BaseModel):
    """DTO para requisição de login."""
    email: str
    senha: str


class TokenResponse(BaseModel):
    """DTO para resposta de token."""
    access_token: str
    token_type: str
    user_id: int
    user_type: str  # "passenger" ou "driver"


# Vehicle DTOs
class VehicleCreate(BaseModel):
    """DTO para criação de veículo."""
    placa: str
    modelo: str
    cor: str


class VehicleUpdate(BaseModel):
    """DTO para atualização de veículo."""
    placa: Optional[str] = None
    modelo: Optional[str] = None
    cor: Optional[str] = None


class VehicleResponse(BaseModel):
    """DTO para resposta de veículo."""
    id: int
    placa: str
    modelo: str
    cor: str

    class Config:
        from_attributes = True

