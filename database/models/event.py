import datetime
import uuid
from typing import TYPE_CHECKING, Dict
from sqlalchemy import BigInteger, Boolean, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database.base import AlchemyBaseModel

if TYPE_CHECKING:
    from database.models.user import User


class Event(AlchemyBaseModel):
    """Модель для хранения информации о пользователе."""

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
        ForeignKey("users.user_id"),
        nullable=False,
    )

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_events",
        lazy="selectin",
    )

    limit_visitors: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    list_of_visitors: Mapped[list["User"]] = relationship(
        "User",
        secondary="event_visitors",
        back_populates="visited_events",
        lazy="selectin",
    )

    location: Mapped[str] = mapped_column(
        String,
        default="Улица Пушкина, дом Колотушкина",
        nullable=False,
    )


    @property
    def dict(self) -> Dict[str, any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            # тип/категория,
            "created": self.created,
            "date": self.date,
            "creator": self.creator,
            "limit_visitors": self.limit_visitors,
            "list_of_visitors": [visitor.dict() for visitor in self.list_of_visitors]
        }
