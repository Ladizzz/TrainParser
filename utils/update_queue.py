from create_bot import user_requests_queue, bot
from services.train_service import get_trains


async def update_queue():
    for chat_id, user_requests in user_requests_queue.items():
        for request in user_requests:
            if request['status'] == 'active':
                try:
                    trains_list = await get_trains(request['station_from'], request['station_to'], request['date'], True)
                    if not trains_list:
                        raise Exception
                    matching_train = next((train for train in trains_list if train['train_number'] == request['train_data']['train_number'])
                                          , None)
                    if 'tickets' in matching_train and matching_train['tickets']:
                        request['status'] = 'finished'
                        ans = ""
                        for ticket in matching_train['tickets']:
                            if "type" in ticket:
                                ans += f"Тип: <b>{ticket['type']}</b>\n"
                            if "available_seats" in ticket:
                                ans += f"Доступно мест: <b>{ticket['available_seats']}</b>\n"
                            if "prices" in ticket:
                                ans += f"Стоимость: <b>{ticket['prices']}</b>\n\n"

                        await bot.send_message(chat_id=chat_id, text=f"🚨 Найдено\n\n{ans}")
                except Exception as e:
                    await bot.send_message(chat_id=chat_id, text=f"Ошибка при поиске по запросу")
                    raise e
