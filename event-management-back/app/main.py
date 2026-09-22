"""Ponto de entrada da aplicação FastAPI."""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.database import Base, engine
from app.routers import auth, events, participants

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
)
logger = logging.getLogger("event_management")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Aplicação iniciada, tabelas garantidas no banco de dados")
    yield
    logger.info("Aplicação encerrada")


app = FastAPI(
    title=settings.app_name,
    description="API para gestão de eventos e inscrição de participantes.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "%s %s -> %s (%sms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(loc) for loc in err["loc"] if loc != "body"), "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Dados inválidos", "errors": errors},
    )


@app.get("/health", tags=["health"])
@app.get("/healthz", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}


@app.get("/", tags=["health"])
def root() -> dict:
    return {"message": "Event Management API", "docs": "/docs"}


app.include_router(auth.router)
app.include_router(events.router)
app.include_router(participants.router)
