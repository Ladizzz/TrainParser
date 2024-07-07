from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from create_bot import user_dict
from keyboards.inline_kbs import back_home_kb, waiting_list_kb, search_details_kb, search_details_back_kb

list_router = Router()


@list_router.callback_query(F.data.startswith('waiting_list'))
async def get_waiting_list(call: CallbackQuery):
    ans_type_edit = call.data.replace('waiting_list', '')
    if call.from_user.id in user_dict and user_dict[call.from_user.id]:
        # print(user_dict[call.from_user.id])
        formatted_list = [
            f"{request['station_from']} - {request['station_to']} ({request['date']}) - {request['train_data']['train_number']}"
            for request in user_dict[call.from_user.id]
        ]
        if ans_type_edit:
            await call.message.edit_text(f'Лист ожидания', reply_markup=waiting_list_kb(formatted_list))
        else:
            await call.message.answer(f'Лист ожидания', reply_markup=waiting_list_kb(formatted_list))
    else:
        if ans_type_edit:
            await call.message.edit_text(
                text='Лист ожидания пуст', reply_markup=back_home_kb())
        else:
            await call.message.answer(
                text='Лист ожидания пуст', reply_markup=back_home_kb())
    await call.answer()


@list_router.callback_query(F.data.startswith('train_'))
async def get_train(call: CallbackQuery):
    train_id = int(call.data.replace('train_', ''))
    search_data = user_dict[call.from_user.id][train_id]
    await call.message.edit_text(
        text="Детали о поиске:\n\n"
             f"Станиция отправления: <b>{search_data['station_from']}</b>\n"
             f"Станиция назначения: <b>{search_data['station_to']}</b>\n"
             f"Дата: <b>{search_data['date']}</b>\n"
             f"Выбранный поезд: <b>{search_data['train_data']['train_number']} {search_data['train_data']['train_name']}</b>\n"
             f"Отправление: <b>{search_data['train_data']['train_departure']}</b>\n"
             f"Прибытие: <b>{search_data['train_data']['train_arrival']}</b>\n"
        ,
        reply_markup=search_details_kb(train_id)
    )
    await call.answer()


@list_router.callback_query(F.data.startswith('delete_'))
async def delete_train(call: CallbackQuery):
    train_id = int(call.data.replace('delete_', ''))
    search_data = user_dict[call.from_user.id].pop(train_id)
    await call.message.edit_text(
        text="Поиск отменен",
        reply_markup=search_details_back_kb()
    )
    await call.answer()
