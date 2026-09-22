"""Endpoints de eventos: CRUD + listagem com filtros de status/data."""
from datetime import datetime
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import null
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, User
from app.schemas import EventCreate, EventListOut, EventOut, EventStatus, EventUpdate
from app.security import get_current_user
from app.services.event_service import filter_events, serialize_event

router = APIRouter(prefix="/events", tags=["events"])

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


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
    events = filter_events(db, status_filter, date)
    items = [serialize_event(db, e) for e in events]
    return EventListOut(total=len(items), items=items)


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: str, db: Session = Depends(get_db)) -> dict:
    event = _get_event_or_404(db, event_id)
    return serialize_event(db, event)


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(
    name: str = Form(...),
    description: str = Form(...),
    date_time: datetime = Form(...),
    location: str = Form(...),
    capacity: int = Form(...),
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:

    
    payload = EventCreate(
        name=name,
        description=description,
        date_time=date_time,
        location=location,
        capacity=capacity,
    )

    event = Event(**payload.model_dump(), organizer_id=current_user.id)

    if file is not None:
     contents = await file.read()

    if len(contents) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Imagem muito grande. O tamanho máximo permitido é 5 MB.",
        )

    if contents:
        event.image_data = contents
        event.image_content_type = file.content_type
        
    db.add(event)
    db.commit()
    db.refresh(event)
    return serialize_event(db, event)


@router.put("/{event_id}", response_model=EventOut)
async def update_event(
    event_id: str,
    name: str = Form(...),
    description: str = Form(...),
    date_time: datetime = Form(...),
    location: str = Form(...),
    capacity: int = Form(...),
    file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Atualiza um evento existente. Requer autenticação e ser o organizador."""

    payload = EventCreate(
        name=name,
        description=description,
        date_time=date_time,
        location=location,
        capacity=capacity,
    )

    event = _get_event_or_404(db, event_id)

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para editar este evento",
        )


    event.name = name
    event.description = description
    event.date_time = date_time
    event.location = location
    event.capacity = capacity
    
    if file is not None:
        contents = await file.read()

        if len(contents) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Imagem muito grande. O tamanho máximo permitido é 5 MB.",
            )

        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A imagem enviada está vazia.",
            )

        event.image_data = contents
        event.image_content_type = file.content_type


    db.commit()
    db.refresh(event)
    return serialize_event(db, event)

@router.get("/{event_id}/image")
def get_event_image(
    event_id: str,
    db: Session = Depends(get_db),
):
    event = db.get(Event, event_id)

    if not event or not event.image_data:
        raise HTTPException(
            status_code=404,
            detail="Imagem não encontrada",
        )

    return Response(
        content=event.image_data,
        media_type=event.image_content_type,
    )


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
