from aiogram import Router
from aiogram.types import Message

error_router = Router()


@error_router.message()
async def error(message: Message):
    await message.answer(f'Команда не распознана')