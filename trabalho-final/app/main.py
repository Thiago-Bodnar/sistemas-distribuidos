"""Cria a FastAPI, inclui routers, middlewares."""
import asyncio
from fastapi import FastAPI

from app.api import (auth, corridas, motoristas, passageiros, servidores,
                     veiculos)
from app.infra.logging_config import setup_logging
from app.services import heartbeat_service

setup_logging()

app = FastAPI(
    title="Corridas Distribuídas API",
    description="API para sistema de corridas distribuído",
    version="0.1.0"
)

app.include_router(auth.router)
app.include_router(passageiros.router)
app.include_router(corridas.router)
app.include_router(motoristas.router)
app.include_router(servidores.router)
app.include_router(veiculos.router)


@app.on_event("startup")
async def start_heartbeat_task():
    async def loop():
        while True:
            heartbeat_service.send_heartbeat()
            await asyncio.sleep(2)

    asyncio.create_task(loop())

@app.get("/")
async def root():
    """Endpoint raiz."""
    return {"message": "Corridas Distribuídas API"}
