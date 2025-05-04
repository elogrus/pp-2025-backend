from typing import TYPE_CHECKING, Dict

from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import AlchemyBaseModel


if TYPE_CHECKING:
    from database.models.event import Event
    # Реализовать роли
    # from database.models.roles import Role


class User(AlchemyBaseModel):
    """Модель для хранения информации о пользователе."""

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        unique=True,
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    # Настроить рассылки на почту?
    login: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String,
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
        back_populates="list_of_visitors",
        lazy="selectin",
    )

    # # Роли пользователя
    # role: Mapped[list["Role"]] = relationship(
    #     secondary="users_to_roles",
    #     lazy="selectin",
    # )

    def dict(self) -> Dict[str, any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "login": self.login,
            "created_events": self.created_events,
            "visited_events": self.visited_events,
        }

    def should_be_updated(self, username: str) -> bool:
        """
        Нужно ли обновить ему имя.

        :param username: Никнейм пользователя в бд.
        :return: Нужно ли поставить новый никнейм
        """
        return self.username != username

