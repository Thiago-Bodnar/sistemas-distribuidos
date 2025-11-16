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
    # TODO: Adicionar outros campos conforme necessário


class DriverResponse(BaseModel):
    """DTO para resposta de motorista."""
    id: int
    nome: str
    email: str
    telefone: str
    localizacao_atual: Optional[str] = None
    # TODO: Adicionar outros campos conforme necessário


class DriverStatusUpdate(BaseModel):
    """DTO para atualização de status do motorista."""
    status: str
    localizacao_atual: Optional[str] = None


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
    origem: str
    destino: str
    status: str
    valor: Optional[float] = None
    tempo: Optional[int] = None
    distancia: Optional[float] = None
    # TODO: Adicionar outros campos conforme necessário


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

