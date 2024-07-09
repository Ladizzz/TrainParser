from aiogram import Router, F
from aiogram.types import CallbackQuery
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


@list_router.callback_query(F.data.startswith('train_'))
async def get_train(call: CallbackQuery):
    train_id = call.data.replace('train_', '')
    request = await db["requests"].find_one({"_id": ObjectId(train_id)})
    await call.message.edit_text(
        text="Детали о поиске:\n\n"
             f"Станиция отправления: <b>{request['station_from']}</b>\n"
             f"Станиция назначения: <b>{request['station_to']}</b>\n"
             f"Дата: <b>{request['date']}</b>\n"
             f"Выбранный поезд: <b>{request['train_data']['train_number']} {request['train_data']['train_name']}</b>\n"
             f"Отправление: <b>{request['train_data']['train_departure']}</b>\n"
             f"Прибытие: <b>{request['train_data']['train_arrival']}</b>\n\n"
             f"Состояние: <b>{status_mapping.get(request['status'], 'Не определено')}</b>\n"
             f"Дата создания: <b>{request.get('created_at', None)}</b>\n"
             f"Дата изменения: <b>{request.get('updated_at', None)}</b>\n"
        ,
        reply_markup=search_details_kb(train_id)
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
