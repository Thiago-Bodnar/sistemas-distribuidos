"""Enums: Status de motorista, status de corrida, etc."""
from enum import Enum


class DriverStatus(str, Enum):
    """Status do motorista."""
    DISPONIVEL = "disponivel"
    EM_CORRIDA = "em_corrida"
    OFFLINE = "offline"
    # TODO: Adicionar outros status conforme necessário


class RideStatus(str, Enum):
    """Status da corrida."""
    PENDENTE = "pendente"
    ACEITA = "aceita"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"
    # TODO: Adicionar outros status conforme necessário


class NodeStatus(str, Enum):
    """Status do nó/servidor."""
    ATIVO = "ativo"
    INATIVO = "inativo"
    COORDENADOR = "coordenador"
    # TODO: Adicionar outros status conforme necessário

