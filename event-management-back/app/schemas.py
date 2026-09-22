"""Schemas Pydantic usados para validação de entrada e serialização de saída."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from fastapi import Form
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Auth / User
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------
class EventStatus(str, Enum):
    FUTURE = "future"
    PAST = "past"
    FULL = "full"


class EventBase(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str | None = Field(default="", max_length=4000)
    date_time: datetime
    location: str = Field(min_length=2, max_length=255)
    capacity: int = Field(gt=0, le=1_000_000)


class EventCreate(EventBase):
    name: str = Field(min_length=2, max_length=180)
    description: str = Field(max_length=4000)
    date_time: datetime
    location: str = Field(min_length=2, max_length=255)
    capacity: int = Field(gt=0, le=1_000_000)


class EventUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=4000)
    date_time: datetime | None = None
    location: str | None = Field(default=None, min_length=2, max_length=255)
    capacity: int | None = Field(default=None, gt=0, le=1_000_000)

    @field_validator("capacity")
    @classmethod
    def capacity_positive(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("capacity deve ser maior que zero")
        return v


class EventOut(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organizer_id: str
    created_at: datetime
    updated_at: datetime
    participants_count: int = 0
    spots_left: int = 0
    status: EventStatus
    image_url: str | None = None
    has_image: bool = False
    
class EventListOut(BaseModel):
    total: int
    items: list[EventOut]


# ---------------------------------------------------------------------------
# Participant
# ---------------------------------------------------------------------------
class ParticipantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    email: EmailStr


class ParticipantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    event_id: str
    registered_at: datetime
