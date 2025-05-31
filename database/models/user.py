from typing import Dict

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import AlchemyBaseModel


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
        unique=True,
        nullable=False,
    )

    nickname: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    # Роли пользователя
    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )

    def dict(self) -> Dict[str, any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
        }

    def should_be_updated(self, username: str) -> bool:
        """
        Нужно ли обновить ему имя.

        :param username: Никнейм пользователя в бд.
        :return: Нужно ли поставить новый никнейм
        """
        return self.username != username

