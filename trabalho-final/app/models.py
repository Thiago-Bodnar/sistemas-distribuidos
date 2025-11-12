from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


# Adicionar novas models aqui, e rodar o alembic para gerar a migration
class Motorista(Base):
    __tablename__ = "motoristas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String(100), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    localizacao_atual: Mapped[str] = mapped_column(String(255))
    id_veiculo: Mapped[int] = mapped_column(Integer, ForeignKey("veiculos.id"))
    id_servidor: Mapped[int] = mapped_column(Integer, ForeignKey("servidores.id"))

class Passageiro(Base):
    __tablename__ = "passageiros"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String(100), unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255))

class Veiculo(Base):
    __tablename__ = "veiculos"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    placa: Mapped[str] = mapped_column(String(100), unique=True)
    modelo: Mapped[str] = mapped_column(String(100))
    cor: Mapped[str] = mapped_column(String(100))

class Corrida(Base):
    __tablename__ = "corridas"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_motorista: Mapped[int] = mapped_column(Integer, ForeignKey("motoristas.id"))
    id_passageiro: Mapped[int] = mapped_column(Integer, ForeignKey("passageiros.id"))
    id_veiculo: Mapped[int] = mapped_column(Integer, ForeignKey("veiculos.id"))
    id_servidor: Mapped[int] = mapped_column(Integer, ForeignKey("servidores.id"))
    origem: Mapped[str] = mapped_column(String(255))
    destino: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(100))
    valor: Mapped[float] = mapped_column(Float)
    tempo: Mapped[int] = mapped_column(Integer)
    distancia: Mapped[float] = mapped_column(Float)

class Servidor(Base):
    __tablename__ = "servidores"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True)
    regiao: Mapped[str] = mapped_column(String(100))
    uptime: Mapped[int] = mapped_column(Integer)
    is_coordenador: Mapped[bool] = mapped_column(Boolean)
    ultimo_heartbeat: Mapped[datetime] = mapped_column(DateTime)
