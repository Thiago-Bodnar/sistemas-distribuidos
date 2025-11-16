"""Classes de negócio: Driver, Passenger, Ride, Node."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Driver:
    """Entidade Motorista."""
    id: Optional[int] = None
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    localizacao_atual: Optional[str] = None
    id_veiculo: Optional[int] = None
    id_servidor: Optional[int] = None
    # TODO: Adicionar outros campos conforme necessário


@dataclass
class Passenger:
    """Entidade Passageiro."""
    id: Optional[int] = None
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    # TODO: Adicionar outros campos conforme necessário


@dataclass
class Ride:
    """Entidade Corrida."""
    id: Optional[int] = None
    id_motorista: Optional[int] = None
    id_passageiro: Optional[int] = None
    id_veiculo: Optional[int] = None
    id_servidor: Optional[int] = None
    origem: Optional[str] = None
    destino: Optional[str] = None
    status: Optional[str] = None
    valor: Optional[float] = None
    tempo: Optional[int] = None
    distancia: Optional[float] = None
    # TODO: Adicionar outros campos conforme necessário


@dataclass
class Node:
    """Entidade Nó/Servidor."""
    id: Optional[int] = None
    nome: Optional[str] = None
    regiao: Optional[str] = None
    uptime: Optional[int] = None
    is_coordenador: Optional[bool] = None
    ultimo_heartbeat: Optional[datetime] = None
    # TODO: Adicionar outros campos conforme necessário

