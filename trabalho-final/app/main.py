"""Cria a FastAPI, inclui routers, middlewares."""
from fastapi import FastAPI

from app.api import drivers, rides, servers
from app.infra.logging_config import setup_logging

# Configurar logging
setup_logging()

# Criar aplicação FastAPI
app = FastAPI(
    title="Corridas Distribuídas API",
    description="API para sistema de corridas distribuído",
    version="0.1.0"
)

# Incluir routers
app.include_router(rides.router)
app.include_router(drivers.router)
app.include_router(servers.router)


@app.get("/")
async def root():
    """Endpoint raiz."""
    return {"message": "Corridas Distribuídas API"}
