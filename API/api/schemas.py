from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Extra, conint, conlist, field_validator


class Size(Enum):
    small = "small"
    medium = "medium"
    big = "big"


class Status(Enum):
    created = "created"
    paid = "paid"
    progress = "progress"
    cancelled = "cancelled"
    dispatched = "dispatched"
    delivered = "delivered"


class CreateEventSchema(BaseModel):
    title: str
    description: Optional[str]


class GetEventSchema(CreateEventSchema):
    id: UUID
    created: datetime
    date: datetime
    limit_visitors: int
    list_of_visitors: list


class UserRequest(BaseModel):
    username: str
    login: str

    """
    для валидации данных с помощью pydantic
    @field_validator("quantity")
    def quantity_non_nullable(cls, value):
        assert value is not None, "quantity may not be None"
        return value
    """


class UserCreateRequest(UserRequest):
    password: str


class EventCreateRequest(BaseModel):
    title: str
    date: datetime
    limit_visitors: int
    location: str


class EventCreateDescription(EventCreateRequest):
    description: Optional[str]


class OAuth2PasswordRequestSchema(BaseModel):
    login: str
    password: str
