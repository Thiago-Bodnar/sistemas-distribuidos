"""Tabelas (ORM): drivers, passengers, rides, nodes, heartbeats/logs."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infra.db import Base


# Adicionar novas models aqui, e rodar o alembic para gerar a migration
class Motorista(Base):
    """Modelo ORM para motoristas."""
    __tablename__ = "motoristas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String(100), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    localizacao_atual: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    id_veiculo: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("veiculos.id"), nullable=True)
    id_servidor: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("servidores.id"), nullable=True)


class Passageiro(Base):
    """Modelo ORM para passageiros."""
    __tablename__ = "passageiros"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String(100), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))


class Veiculo(Base):
    """Modelo ORM para veículos."""
    __tablename__ = "veiculos"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    placa: Mapped[str] = mapped_column(String(100), unique=True)
    modelo: Mapped[str] = mapped_column(String(100))
    cor: Mapped[str] = mapped_column(String(100))


class Corrida(Base):
    """Modelo ORM para corridas."""
    __tablename__ = "corridas"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_motorista: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("motoristas.id"), nullable=True)
    id_passageiro: Mapped[int] = mapped_column(Integer, ForeignKey("passageiros.id"))
    id_veiculo: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("veiculos.id"), nullable=True)
    id_servidor: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("servidores.id"), nullable=True)
    origem: Mapped[str] = mapped_column(String(255))
    destino: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(100))
    valor: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tempo: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    distancia: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class Servidor(Base):
    """Modelo ORM para servidores/nós."""
    __tablename__ = "servidores"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    node_id = Column(String(50), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    regiao: Mapped[str] = mapped_column(String(100))
    uptime: Mapped[int] = mapped_column(Integer)
    is_coordenador: Mapped[bool] = mapped_column(Boolean)
    ultimo_heartbeat: Mapped[datetime] = mapped_column(DateTime)

