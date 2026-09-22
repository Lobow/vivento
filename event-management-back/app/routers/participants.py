"""Endpoints de participantes: inscrição pública em eventos, respeitando o limite de vagas."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, Participant, User
from app.schemas import ParticipantCreate, ParticipantOut
from app.security import get_current_user
from app.services.event_service import count_participants

router = APIRouter(prefix="/events/{event_id}/participants", tags=["participants"])


def _get_event_or_404(db: Session, event_id: str) -> Event:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado")
    return event


@router.get("", response_model=list[ParticipantOut])
def list_participants(event_id: str, db: Session = Depends(get_db)) -> list[Participant]:
    _get_event_or_404(db, event_id)
    return db.query(Participant).filter(Participant.event_id == event_id).all()


@router.post("", response_model=ParticipantOut, status_code=status.HTTP_201_CREATED)
def register_participant(
    event_id: str, payload: ParticipantCreate, db: Session = Depends(get_db)
) -> Participant:
    """Inscreve um participante no evento, respeitando o limite de vagas.

    Endpoint público: qualquer pessoa pode se inscrever em um evento, sem
    necessidade de login — o cadastro de conta é apenas para organizadores.
    """
    event = _get_event_or_404(db, event_id)

    current_count = count_participants(db, event_id)
    if current_count >= event.capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este evento está lotado, não há mais vagas disponíveis",
        )

    participant = Participant(name=payload.name, email=payload.email, event_id=event_id)
    db.add(participant)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail já está inscrito neste evento",
        ) from exc
    db.refresh(participant)
    return participant


@router.delete("/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_participant(
    event_id: str,
    participant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove a inscrição de um participante. Requer autenticação (organizador do evento)."""
    event = _get_event_or_404(db, event_id)
    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para gerenciar participantes deste evento",
        )

    participant = (
        db.query(Participant)
        .filter(Participant.id == participant_id, Participant.event_id == event_id)
        .first()
    )
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participante não encontrado"
        )

    db.delete(participant)
    db.commit()
