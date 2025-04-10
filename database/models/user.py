from typing import TYPE_CHECKING, Dict

from sqlalchemy import BigInteger, Boolean, Integer, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import AlchemyBaseModel


if TYPE_CHECKING:
    from database.models.event import Event
    # Реализовать роли
    # from database.models.roles import Role


class User(AlchemyBaseModel):
    """Модель для хранения информации о пользователе."""

    __tablename__ = "users"

    # UUID!
    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        autoincrement=True,
        unique=True,
        nullable=False,
    )

    # Настроить рассылки на почту?
    login: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String(256),
        nullable=False
    )

    events: Mapped[list["Event"]] = relationship(
        secondary="event",
        lazy="selectin",
    )

    # # Роли пользователя
    # role: Mapped[list["Role"]] = relationship(
    #     secondary="users_to_roles",
    #     lazy="selectin",
    # )

    @property
    def dict(self) -> Dict[str, any]:
        return ...  # Доделать
