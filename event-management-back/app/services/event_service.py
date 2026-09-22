"""Regras de negócio relacionadas a eventos (mantidas fora dos routers)."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import Event, Participant
from app.schemas import EventStatus


def event_status(event: Event, participants_count: int, now: datetime | None = None) -> EventStatus:
    """Deriva o status do evento: lotado > passado > futuro (lotado tem prioridade)."""
    now = now or datetime.now(UTC)
    event_dt = event.date_time
    if event_dt.tzinfo is None:
        event_dt = event_dt.replace(tzinfo=UTC)

    if participants_count >= event.capacity:
        return EventStatus.FULL
    if event_dt < now:
        return EventStatus.PAST
    return EventStatus.FUTURE


def count_participants(db: Session, event_id: str) -> int:
    return db.query(Participant).filter(Participant.event_id == event_id).count()


def serialize_event(db: Session, event: Event) -> dict:
    """Monta o dicionário de saída de um evento com campos derivados."""
    count = count_participants(db, event.id)
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "date_time": event.date_time,
        "location": event.location,
        "capacity": event.capacity,
        "organizer_id": event.organizer_id,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
        "participants_count": count,
        "spots_left": max(event.capacity - count, 0),
        "status": event_status(event, count),
        "has_image": event.image_data is not None,
    }


def filter_events(db: Session, status_filter: EventStatus | None, date_filter: str | None):
    """Aplica filtros de status (future/past/full) e/ou data (YYYY-MM-DD) em memória.

    Como o status é derivado (depende da contagem de participantes), o filtro
    é aplicado em memória após carregar os eventos do banco, o que é aceitável
    para o volume de dados esperado neste desafio.
    """
    query = db.query(Event).order_by(Event.date_time.asc())

    if date_filter:
        try:
            target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
        except ValueError:
            target_date = None
        if target_date:
            query = query.filter(
                Event.date_time >= datetime.combine(target_date, datetime.min.time()),
                Event.date_time < datetime.combine(target_date, datetime.max.time()),
            )

    events = query.all()

    if status_filter:
        events = [
            e for e in events if event_status(e, count_participants(db, e.id)) == status_filter
        ]

    return events
