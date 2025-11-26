"""Configuração do projeto - leitura de variáveis de ambiente."""
import os
from typing import Optional

# Node configuration
NODE_ID: str = os.getenv("NODE_ID", "node-1")
REGION: str = os.getenv("REGION", "us-east-1")

# Database configuration
DB_URL: str = os.getenv(
    "DB_URL",
    "mariadb+pymysql://fastapi:super-senha@127.0.0.1:3307/fastapi"
)

# RabbitMQ configuration
RABBIT_URL: str = os.getenv("RABBIT_URL", "amqp://guest:guest@localhost:5672/")
CLOUDAMQP_URL: str = os.getenv("CLOUDAMQP_URL", os.getenv("AMQP_URL", RABBIT_URL))

# Maps API configuration (placeholder)
MAPS_API_KEY: Optional[str] = os.getenv("MAPS_API_KEY")
MAPS_API_URL: str = os.getenv("MAPS_API_URL", "https://api.maps.example.com")

# JWT configuration
JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "key-super-secreta")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas

