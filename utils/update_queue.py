import logging
from datetime import datetime
from aiogram.enums import ParseMode
from create_bot import bot, db
from services.train_service import get_trains


async def update_queue():
    logger = logging.getLogger("update_queue")
    requests = await db["requests"].find({"status": "active"}).to_list(None)
    for request in requests:
        logger.info(f"Active request found: {request}")
        try:
            trains_list = await get_trains(request['station_from'], request['station_to'], request['date'], True)
            if not trains_list:
                logger.error("trains_list is empty!")
                raise Exception
            matching_train = next(
                (train for train in trains_list if train['train_number'] == request['train_data']['train_number'])
                , None)
            if 'tickets' in matching_train and matching_train['tickets']:
                await db['requests'].update_one(
                    {'_id': request['_id']},
                    {'$set': {'status': 'finished', 'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
                )
                logger.info(f"Request {request['_id']} updated to finished")
                ans = ""
                for ticket in matching_train['tickets']:
                    if "type" in ticket:
                        ans += f"Тип: <b>{ticket['type']}</b>\n"
                    if "available_seats" in ticket:
                        ans += f"Доступно мест: <b>{ticket['available_seats']}</b>\n"
                    if "prices" in ticket:
                        ans += f"Стоимость: <b>{ticket['prices']}</b>\n\n"
                logger.info(f"Trying to send message...")
                await bot.send_message(chat_id=request['chat_id'], text=f"🚨 Найдено\n\n{ans}", parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error("Exception while updating queue")
            await bot.send_message(chat_id=request['chat_id'], text=f"Ошибка при поиске по запросу")
