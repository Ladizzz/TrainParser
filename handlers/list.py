from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from create_bot import user_dict
from keyboards.inline_kbs import back_home_kb, waiting_list_kb

list_router = Router()


@list_router.callback_query(F.data == 'waiting_list')
async def get_inline_btn_link(call: CallbackQuery):
    if call.from_user.id in user_dict:
        # print(user_dict[call.from_user.id])
        await call.message.answer(f'Лист ожидания {user_dict[call.from_user.id]}', reply_markup=waiting_list_kb())
    else:
        await call.message.answer(
            text='Лист ожидания пустой')
    await call.answer()
