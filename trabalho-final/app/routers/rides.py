from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import RideCreate, RideOut

router = APIRouter(
    prefix="/corridas",
    tags=["corridas"],
)


def _selecionar_motorista_disponivel(db: Session) -> models.Motorista | None:
    """
    Por enquanto: pega o primeiro motorista com status DISPONIVEL.
    Depois podemos refinar (região, menos corridas, etc.).
    """
    return (
        db.query(models.Motorista)
        .filter(models.Motorista.status == "DISPONIVEL")
        .first()
    )


@router.post("/", response_model=RideOut, status_code=status.HTTP_201_CREATED)
def criar_corrida_local(
    payload: RideCreate,
    db: Session = Depends(get_db),
):
    passageiro = (
        db.query(models.Passageiro)
        .filter(models.Passageiro.id == payload.passageiro_id)
        .first()
    )
    if not passageiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passageiro não encontrado",
        )

    motorista = _selecionar_motorista_disponivel(db)
    if not motorista:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nenhum motorista disponível neste servidor",
        )

    distancia_km = 5.0
    tempo_min = 10
    valor = 15.0

    corrida = models.Corrida(
        passageiro_id=payload.passageiro_id,
        motorista_id=motorista.id,
        origem=payload.origem,
        destino=payload.destino,
        status="EM_ANDAMENTO",
        valor=valor,
        tempo=tempo_min,
        distancia=distancia_km,
    )

    db.add(corrida)

    motorista.status = "EM_CORRIDA"

    db.commit()
    db.refresh(corrida)

    return corrida


@router.get("/", response_model=list[RideOut])
def listar_corridas(db: Session = Depends(get_db)):
    """
    Endpoint simples para listar corridas e ajudar na demo.
    """
    corridas = db.query(models.Corrida).all()
    return corridas
