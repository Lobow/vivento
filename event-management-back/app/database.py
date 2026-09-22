"""
Configuração do SQLAlchemy: engine, sessão e base declarativa.

Usamos SQLite localmente por padrão (arquivo em ./data), mas a URL de
conexão vem inteiramente da variável de ambiente DATABASE_URL, então
trocar para Postgres em produção é apenas uma questão de configuração,
sem alterar código.
"""
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

connect_args = {}
if settings.database_url.startswith("sqlite"):
    # Necessário para permitir uso do mesmo arquivo SQLite por múltiplas threads
    # (o TestClient do FastAPI/uvicorn usa threads distintas).
    connect_args = {"check_same_thread": False}

    # Garante que o diretório do arquivo SQLite exista antes de conectar.
    db_path = settings.database_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa para todos os models do SQLAlchemy."""


def get_db() -> Generator[Session, None, None]:
    """Dependency do FastAPI que fornece uma sessão de banco por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
