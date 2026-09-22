"""Fixtures compartilhadas de teste: banco SQLite isolado em memória por teste."""

import os

os.environ["DATABASE_URL"] = "sqlite:///./data/test_event_management.db"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

# StaticPool garante que todas as sessões de teste compartilhem a MESMA conexão
# em memória (por padrão, cada conexão sqlite:///:memory: cria um banco novo).
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _setup_database():
    """Cria as tabelas do zero antes de cada teste e derruba depois (isolamento total)."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """Registra um usuário, faz login e retorna os headers com o Bearer token."""
    client.post(
        "/auth/register",
        json={
            "name": "Organizador Teste",
            "email": "organizador@teste.com",
            "password": "senha123",
        },
    )
    response = client.post(
        "/auth/token",
        data={"username": "organizador@teste.com", "password": "senha123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
