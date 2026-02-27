from pydantic import BaseModel
from typing import Optional


class RideCreate(BaseModel):
    passageiro_id: int
    origem: str
    destino: str


class RideOut(BaseModel):
    id: int
    passageiro_id: int
    motorista_id: Optional[int]
    origem: str
    destino: str
    status: str
    valor: Optional[float]
    tempo: Optional[int]
    distancia: Optional[float]

    class Config:
        from_attributes = True 
