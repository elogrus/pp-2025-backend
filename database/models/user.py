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

    # UUID!
    user_id: Mapped[str] = mapped_column(
        String,
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
        String(256),
        nullable=False
    )

    # events: Mapped[list["Event"]] = relationship(
    #     secondary="event",
    #     lazy="selectin",
    # )

    # # Роли пользователя
    # role: Mapped[list["Role"]] = relationship(
    #     secondary="users_to_roles",
    #     lazy="selectin",
    # )

    @property
    def dict(self) -> Dict[str, any]:
        return ...  # Доделать

    def should_be_updated(self, username: str) -> bool:
        """
        Нужно ли обновить ему имя.

        :param username: Никнейм пользователя в бд.
        :return: Нужно ли поставить новый никнейм
        """
        return self.username != username

