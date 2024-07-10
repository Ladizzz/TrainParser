from aiogram import Router, F
from aiogram.types import CallbackQuery

from create_bot import db
from keyboards.inline_kbs import administration_kb, back_home_kb

admin_router = Router()


@admin_router.callback_query(F.data == 'administration')
async def administration(call: CallbackQuery):
    user = await db["users"].find_one({"id": call.from_user.id})
    await call.message.edit_text('Администрирование', reply_markup=administration_kb(debug_mode=user['debug_mode']))
    await call.answer()


@admin_router.callback_query(F.data.startswith('debug_mode_'))
async def debug_mode(call: CallbackQuery):
    switch_to = call.data.replace('debug_mode_', '')
    if switch_to == "on":
        await db["users"].update_one({"id": call.from_user.id}, {'$set': {'debug_mode': True}})
        await call.message.edit_text('Режим отладки установлен!', reply_markup=back_home_kb())
    else:
        await db["users"].update_one({"id": call.from_user.id}, {'$set': {'debug_mode': False}})
        await call.message.edit_text('Режим отладки отключен!', reply_markup=back_home_kb())
    await call.answer()
