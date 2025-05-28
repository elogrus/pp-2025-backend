from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from database import AlchemyBaseModel


# Ассоциативная таблица для связи многие-ко-многим между событиями и посетителями
class EventVisitor(AlchemyBaseModel):
    __tablename__ = "event_visitors"

    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("events.id"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("safe_users.user_id"),
        primary_key=True,
    )

    # Дополнительные поля ассоциативной таблицы (если нужно)
    # Например, дата записи на событие
    registration_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
