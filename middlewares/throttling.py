from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from cachetools import TTLCache

CACHE = TTLCache(maxsize=10_000, ttl=2)  # Максимальный размер кэша - 10000 ключей, а время жизни ключа - 2 секунды


class ThrottlingMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user: User = data.get('event_from_user')

        if user.id in CACHE:
            return

        CACHE[user.id] = True

        return await handler(event, data)
