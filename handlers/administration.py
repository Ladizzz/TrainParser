from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.inline_kbs import back_home_kb, administration_kb

admin_router = Router()


@admin_router.callback_query(F.data == 'administration')
async def administration(call: CallbackQuery):
    await call.message.edit_text('Администрирование', reply_markup=administration_kb())
    await call.answer()
