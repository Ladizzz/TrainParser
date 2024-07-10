import logging
from aiogram import Router
from aiogram.types import Message, ErrorEvent

from create_bot import dp, db

error_router = Router()


@error_router.message()
async def universal_answer(message: Message):
    await message.answer(f'Команда не распознана')


@dp.errors()
async def errors_handler(event: ErrorEvent):
    logger = logging.getLogger("errors_handler")
    if event.update.callback_query:
        await event.update.callback_query.answer(text="Ошибка сервера")
    if event.update.message:
        await event.update.message.answer(f"Ошибка сервера")
        user = await db["users"].find_one({"id": event.update.message.from_user.id})
        if user['debug_mode']:
            await event.update.message.answer(f"{event.exception}")
    logger.error("Error caught: %r while processing %r", event.exception, event.update)
