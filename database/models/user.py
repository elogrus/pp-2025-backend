from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import UserRelatedModel

"""
Реализовать роли
if TYPE_CHECKING:
    from database.models.roles import Role
"""


class User(UserRelatedModel):
    """Модель для хранения информации о пользователе."""

    __tablename__ = "users"

    # UUID?
    id: Mapped[int] = mapped_column(
        Integer,
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
        String(64),
        nullable=False
    )

    # # Роли пользователя
    # roles: Mapped[list["Role"]] = relationship(
    #     secondary="users_to_roles",
    #     lazy="selectin",
    # )

    @property
    def short_info(self) -> str:
        """Краткая информация о пользователе."""
        return f"User(id={self.id}, login={self.login})"


