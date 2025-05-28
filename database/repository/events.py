from datetime import datetime, timezone
from typing import Optional, List
import sqlalchemy as sa
from database.models import Event, SafeUser
from database.repository.base_repo import BaseRepository


class EventRepository(BaseRepository):

    async def create_event(
            self,
            creator: SafeUser,
            title: str,
            date: datetime,
            limit_visitors: int,
            location: str,
            description: Optional[str] = None,
    ) -> Event:
        """
        Создаёт новый ивент в бд.
        :param creator: Модель юзера, который создаёт ивент.
        :param title: Краткое описание/Титульник.
        :param date: Время начала.
        :param limit_visitors: Лимит посетителей.
        :param location: Место/Адрес проведения мероприятия.
        :param description: Полное описание.
        :return Event: Модель ивента.
        """
        if date.tzinfo is not None:
            date = date.replace(tzinfo=None)

        event = Event(title=title,
                      description=description,
                      date=date,
                      created=datetime.utcnow().replace(tzinfo=None),
                      creator=creator,
                      creator_id=creator.user_id,
                      limit_visitors=limit_visitors,
                      location=location.lower()
                      )
        self._session.add(event)
        await self.commit()
        await self.refresh(event)
        return event

    async def get(self, event_id: int) -> Event:
        """
        Получить ивент по айдишнику
        :param event_id: Айдишник ивента
        :return Event: Модель ивента.
        """
        query = sa.select(Event).where(Event.id == event_id)
        return await self.scalar(query)

    async def get_all(self) -> List[Event]:
        """
        Получить все существующие ивенты из бд
        :return List[Event]: Список с ивентами.
        """
        query = sa.select(Event)
        return await self.scalars(query)

    async def get_by_title(self, event_title) -> List[Event]:
        """
        Получить все ивент из бд по краткому описанию/титульнику.
        :param event_title: Строка по которой будет проходить поиск.
        :return List[Event]: Список ивентов.
        """
        query = sa.select(Event).filter(Event.title.like(f"%{event_title.lower()}%")).all()
        return list(await self.scalars(query))


