from typing import TYPE_CHECKING, Dict

from sqlalchemy import BigInteger, Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import AlchemyBaseModel


if TYPE_CHECKING:
    from database.models.event import Event


class SafeUser(AlchemyBaseModel):
    """Модель для хранения информации о пользователе."""

    __tablename__ = "safe_users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        primary_key=True,
        unique=True,
    )

    # Это логин!
    username: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    nickname: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    # Роли пользователя
    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )

    created_events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="creator",
        lazy="selectin",
    )

    # События, на которые пользователь записался (многие-ко-многим)
    visited_events: Mapped[list["Event"]] = relationship(
        "Event",
        secondary="event_visitors",
        back_populates="visitors",
        lazy="selectin",
    )

    def dict(self) -> Dict[str, any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "nickname": self.nickname,
            "role": self.role,
            "created_events": self.created_events,
            "visited_events": self.visited_events,
        }

    def dict_for_event(self) -> Dict[str, any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "nickname": self.nickname,
            "role": self.role,
        }
