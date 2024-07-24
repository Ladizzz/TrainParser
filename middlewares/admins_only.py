import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from create_bot import admins


class AdminsOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        # ...
        # Здесь выполняется код на входе в middleware
        # ...
        user: User = data.get('event_from_user')
        if user is not None:
            if user.id not in admins:
                logger = logging.getLogger("AdminsOnlyMiddleware")
                logger.warning(f'The user {user.id} is not an admin, reject event')
                return

        return await handler(event, data)
        # ...
        # Здесь выполняется код на выходе из middleware
        # ...
