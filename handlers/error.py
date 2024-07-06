from aiogram import Router
from aiogram.types import Message

error_router = Router()


@error_router.message()
async def cmd_start(message: Message):
    await message.answer(f'Проверьте правильность ввода')