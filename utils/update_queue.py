from create_bot import user_dict, bot
from services.train_service import get_trains


async def update_queue():
    for chat_id, user_requests in user_dict.items():
        for request in user_requests:
            try:
                trains_list = await get_trains(request['station_from'], request['station_to'], request['date'])
                matching_train = next((train for train in trains_list if train['train_number'] == request['train_data']['train_number'])
                                      , None)
                await bot.send_message(chat_id=chat_id, text=f"Найдено: {matching_train}")
            except Exception as e:
                await bot.send_message(chat_id=chat_id, text=f"Ошибка при поиске по запросу {request}")
