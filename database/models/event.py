import datetime
from typing import TYPE_CHECKING, Dict

from sqlalchemy import BigInteger, Boolean, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database.base import AlchemyBaseModel

if TYPE_CHECKING:
    from database.models.user import User


class Event(AlchemyBaseModel):
    """Модель для хранения информации о пользователе."""

    __tablename__ = "events"

    # UUID?
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

    creator: Mapped["User"] = relationship(
        secondary="user",
        lazy="selectin",
    )

    limit_visitors: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    list_of_visitors: Mapped[list["User"]] = relationship(
        secondary='user',
        lazy="selectin"
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
