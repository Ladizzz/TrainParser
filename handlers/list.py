from datetime import datetime
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram import html
from bson import ObjectId

from create_bot import db, logger
from keyboards.inline_kbs import waiting_list_kb, search_details_kb, search_details_back_kb, back_home_kb
from utils import status_mapping

list_router = Router()


@list_router.callback_query(F.data == 'waiting_list')
async def get_waiting_list(call: CallbackQuery):
    requests = await db["requests"].find({"chat_id": call.from_user.id}).to_list(None)
    if requests:
        logger.info(f"Find requests: {requests}")
        await call.message.edit_text(f'Лист ожидания', reply_markup=waiting_list_kb(requests))
    else:
        await call.message.edit_text(
            text='Лист ожидания пуст', reply_markup=back_home_kb())
    await call.answer()


@list_router.callback_query(F.data.startswith('restart_'))
async def restart_search(call: CallbackQuery):
    request_id = call.data.replace('restart_', '')
    await db['requests'].update_one(
        {'_id': ObjectId(request_id)},
        {'$set': {'status': 'active', 'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
    )
    # await call.message.edit_reply_markup()
    await call.answer("Статус обновлен")
    await get_request(call, request_id)


@list_router.callback_query(F.data.startswith('request_'))
async def get_request(call: CallbackQuery, request_id=None):
    if not request_id:
        request_id = call.data.replace('request_', '')
    request = await db["requests"].find_one({"_id": ObjectId(request_id)})
    await call.message.edit_text(
        text="Детали о поиске:\n\n"
             f"Станиция отправления: <b>{html.quote(request['station_from'])}</b>\n"
             f"Станиция назначения: <b>{html.quote(request['station_to'])}</b>\n"
             f"Дата: <b>{html.quote(request['date'])}</b>\n"
             f"Выбранный поезд: <b>{request['train_data']['train_number']} {request['train_data']['train_name']}</b>\n"
             f"Отправление: <b>{request['train_data']['train_departure']}</b>\n"
             f"Прибытие: <b>{request['train_data']['train_arrival']}</b>\n\n"
             f"Состояние: <b>{html.quote(status_mapping.get(request['status'], 'Не определено'))}</b>\n"
             f"Дата создания: <b>{request.get('created_at', None)}</b>\n"
             f"Дата изменения: <b>{request.get('updated_at', None)}</b>\n"
        ,
        reply_markup=search_details_kb(request_id, request['status']),
        parse_mode=ParseMode.HTML
    )
    await call.answer()


@list_router.callback_query(F.data.startswith('delete_'))
async def delete_train(call: CallbackQuery):
    train_id = call.data.replace('delete_', '')
    request = await db["requests"].find_one_and_delete({"_id": ObjectId(train_id)})
    await call.message.edit_text(
        text="Поиск отменен",
        reply_markup=search_details_back_kb()
    )
    await call.answer()
