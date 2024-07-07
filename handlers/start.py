from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from keyboards.inline_kbs import back_home_kb
from keyboards.inline_kbs import start_kb
from aiogram.types import CallbackQuery
from aiogram import html


start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f'Добро пожаловать, {html.quote(message.from_user.full_name)}',
                         reply_markup=start_kb(message.from_user.id))


@start_router.callback_query(F.data == 'back_home')
async def cmd_home(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(f'Добро пожаловать, {call.from_user.full_name}',
                         reply_markup=start_kb(call.from_user.id))
    await call.answer()


@start_router.callback_query(F.data == 'admin_panel')
async def get_inline_btn_link(call: CallbackQuery):
    await call.message.answer('Администрирование', reply_markup=back_home_kb())
    await call.answer()

