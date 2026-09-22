"""Endpoints de eventos: CRUD + listagem com filtros de status/data."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, User
from app.schemas import EventCreate, EventListOut, EventOut, EventStatus, EventUpdate
from app.security import get_current_user
from app.services.event_service import filter_events, serialize_event

router = APIRouter(prefix="/events", tags=["events"])


def _get_event_or_404(db: Session, event_id: str) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado")
    return event


@router.get("", response_model=EventListOut)
def list_events(
    status_filter: EventStatus | None = Query(default=None, alias="status"),
    date: str | None = Query(default=None, description="Filtra por data no formato YYYY-MM-DD"),
    db: Session = Depends(get_db),
) -> EventListOut:
    """Lista eventos, com filtros opcionais por status (future/past/full) e data."""
    events = filter_events(db, status_filter, date)
    items = [serialize_event(db, e) for e in events]
    return EventListOut(total=len(items), items=items)


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: str, db: Session = Depends(get_db)) -> dict:
    event = _get_event_or_404(db, event_id)
    return serialize_event(db, event)


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Cria um evento. Requer autenticação (Bearer token)."""
    event = Event(**payload.model_dump(), organizer_id=current_user.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return serialize_event(db, event)


@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: str,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Atualiza um evento existente. Requer autenticação e ser o organizador."""
    event = _get_event_or_404(db, event_id)
    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para editar este evento",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return serialize_event(db, event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove um evento. Requer autenticação e ser o organizador."""
    event = _get_event_or_404(db, event_id)
    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para remover este evento",
        )
    db.delete(event)
    db.commit()
