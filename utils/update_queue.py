import logging
from datetime import datetime
from aiogram.enums import ParseMode
from create_bot import bot, db
from services.train_service import get_trains


async def update_queue():
    logger = logging.getLogger("update_queue")
    requests = await db["requests"].find({"status": "active"}).to_list(None)
    for request in requests:
        logger.info(f"Active request found: {request['_id']} {request['station_from']} {request['station_to']} {request['date']}")
        user = await db["users"].find_one({"id": request['chat_id']})
        try:
            trains_list = await get_trains(request['station_from'], request['station_to'], request['date'], True)
            if not trains_list:
                logger.error("trains_list is empty!")
                raise Exception
            matching_train = next(
                (train for train in trains_list if train['train_number'] == request['train_data']['train_number'])
                , None)
            if 'tickets' in matching_train and matching_train['tickets']:
                ans = ""
                finished = False
                for ticket in matching_train['tickets']:
                    if ("prices" not in ticket
                            or ("prices" in ticket
                                and ("price_from" not in request or ("price_from" in request and ticket['prices'] >= request['price_from']))
                                and ("price_to" not in request or ("price_to" in request and ticket['prices'] <= request['price_to'])))):
                        finished = True
                        if "type" in ticket:
                            ans += f"Тип: <b>{ticket['type']}</b>\n"
                        if "available_seats" in ticket:
                            ans += f"Доступно мест: <b>{ticket['available_seats']}</b>\n"
                        if "prices" in ticket:
                            ans += f"Стоимость: <b>{ticket['prices']}</b>\n\n"
                if finished:
                    await db['requests'].update_one(
                        {'_id': request['_id']},
                        {'$set': {'status': 'finished', 'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
                    )
                    logger.info(f"Request {request['_id']} updated to finished")
                    logger.info(f"Trying to send message...")
                    await bot.send_message(chat_id=request['chat_id'], text=f"🚨 Найдено\n\n{request['train_data']['train_name']} ({request['date']})\n\n{ans}", parse_mode=ParseMode.HTML)
            else:
                logger.info(f"No places found for request {request['_id']}")
                if user['debug_mode']:
                    await bot.send_message(chat_id=request['chat_id'], text=f"По запросу {request['_id']} {request['station_from']} {request['station_to']} {request['date']} мест нет")
        except Exception as e:
            logger.error(f"Exception while updating queue: {e}")
            if user['debug_mode']:
                await bot.send_message(chat_id=request['chat_id'], text=f"Ошибка при поиске по запросу: {e}")
