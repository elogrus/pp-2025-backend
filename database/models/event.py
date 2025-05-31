from typing import TYPE_CHECKING, Dict
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from database.base import AlchemyBaseModel

if TYPE_CHECKING:
    from database.models.safe_user import SafeUser


class Event(AlchemyBaseModel):
    """Модель для хранения информации о мероприятиях."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        unique=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(256),
    )

    # Реализовать категории/тип меро

    created: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    creator_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("safe_users.user_id"),
        nullable=False,
    )

    creator: Mapped["SafeUser"] = relationship(
        "SafeUser",
        back_populates="created_events",
        lazy="selectin",
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    limit_visitors: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    visitors: Mapped[list["SafeUser"]] = relationship(
        "SafeUser",
        secondary="event_visitors",
        back_populates="visited_events",
        lazy="selectin",
    )

    location: Mapped[str] = mapped_column(
        String,
        default="Улица Пушкина, дом Колотушкина",
        nullable=False,
    )

    def dict(self) -> Dict[str, any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            # тип/категория,
            "created": self.created,
            "date": self.date,
            "creator_id": self.creator_id,
            "location": self.location,
            "limit_visitors": self.limit_visitors,
            "list_of_visitors": [visitor.dict_for_event() for visitor in self.visitors]
        }
