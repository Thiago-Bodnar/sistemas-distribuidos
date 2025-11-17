"""Cria a FastAPI, inclui routers, middlewares."""
from fastapi import FastAPI

from app.api import (auth, corridas, motoristas, passageiros, servidores,
                     veiculos)
from app.infra.logging_config import setup_logging

from app.api import corridas, motoristas, maps

# Configurar logging
setup_logging()

# Criar aplicação FastAPI
app = FastAPI(
    title="Corridas Distribuídas API",
    description="API para sistema de corridas distribuído",
    version="0.1.0"
)

# Incluir routers
app.include_router(auth.router)
app.include_router(passageiros.router)
app.include_router(corridas.router)
app.include_router(motoristas.router)
app.include_router(servidores.router)
app.include_router(veiculos.router)
app.include_router(maps.router, prefix="/maps", tags=["Maps"])

@app.get("/")
async def root():
    """Endpoint raiz."""
    return {"message": "Corridas Distribuídas API"}
