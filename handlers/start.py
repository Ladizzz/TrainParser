from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import CallbackQuery

from create_bot import db
from keyboards.inline_kbs import start_kb

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await db["users"].update_one(
        {'id': message.from_user.id},
        {'$setOnInsert': dict(message.from_user)},
        upsert=True
    )
    await message.answer(f'Добро пожаловать, {message.from_user.full_name}',
                         reply_markup=start_kb(message.from_user.id))


@start_router.callback_query(F.data == 'go_home')
async def cmd_home_answer(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(f'Добро пожаловать, {call.from_user.full_name}',
                              reply_markup=start_kb(call.from_user.id))
    await call.answer()


@start_router.callback_query(F.data == 'back_home')
async def cmd_home_edit_text(call: CallbackQuery):
    await call.message.edit_text(f'Добро пожаловать, {call.from_user.full_name}',
                              reply_markup=start_kb(call.from_user.id))
    await call.answer()