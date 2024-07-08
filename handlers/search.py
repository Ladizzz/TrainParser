from datetime import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
from create_bot import bot, user_requests_queue
from keyboards.inline_kbs import go_home_kb, validate_train_kb
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from services.train_service import get_trains


class TrainSearch(StatesGroup):
    choosing_station_from = State()
    choosing_station_to = State()
    choosing_date = State()
    choosing_train = State()
    validating_search = State()
    finish_search = State()


search_router = Router()


@search_router.callback_query(F.data == 'new_search')
async def new_search(call: CallbackQuery, state: FSMContext):
    # Устанавливаем пользователю состояние "выбирает название"
    await call.message.answer('Введите пункт отправления', reply_markup=go_home_kb())
    await state.set_state(TrainSearch.choosing_station_from)
    await call.answer()


@search_router.message(
    TrainSearch.choosing_station_from
)
async def choose_station_to(message: Message, state: FSMContext):
    await state.update_data(station_from=message.text)
    await message.answer(
        text="Введите пункт назначения", reply_markup=go_home_kb()
    )
    await state.set_state(TrainSearch.choosing_station_to)


@search_router.message(
    TrainSearch.choosing_station_to
)
async def choose_date(message: Message, state: FSMContext):
    await state.update_data(station_to=message.text)
    await message.answer(
        text="Введите дату поездки в формате YYYY-MM-DD",
        reply_markup=go_home_kb()
    )
    await state.set_state(TrainSearch.choosing_date)


@search_router.message(
    TrainSearch.choosing_date
)
async def validate_search(message: Message, state: FSMContext):
    try:
        await state.update_data(date=message.text)
        await message.answer(text="Ожидайте, идет поиск поездов...")
        async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
            # await asyncio.sleep(3)
            search_data = await state.get_data()
            trains_list = await get_trains(search_data['station_from'], search_data['station_to'], search_data['date'])
            if trains_list is not None:
                if trains_list:
                    formatted_list = [
                        f"{train['index']}. {train['train_number']} {train['train_name']} {train['train_departure']} - {train['train_arrival']} ({train['train_duration']})"
                        for train in trains_list
                    ]
                    await state.update_data(trains_list=trains_list)
                    if len("\n\n".join(formatted_list)) < 4096:
                        await message.answer(text="Доступные поезда:\n\n" + "\n\n".join(formatted_list))
                    else:
                        half = len(formatted_list) // 2
                        await message.answer(text="Доступные поезда:\n\n" + "\n\n".join(formatted_list[:half]))
                        await message.answer(text="\n\n".join(formatted_list[half:]))
                    await message.answer(text="Введите порядковый номер поезда", reply_markup=go_home_kb())
                    await state.set_state(TrainSearch.validating_search)
                else:
                    await message.answer(text="Нет доступных поездов. Проверьте правильность ввода")
                    await state.clear()
            else:
                await message.answer(text="Произошла ошибка при получении")
                await state.clear()
    except Exception as error:
        # todo how to global except?
        await message.answer(text="Произошла ошибка")


@search_router.message(
    TrainSearch.validating_search
)
async def validate_search(message: Message, state: FSMContext):
    try:
        train_index = int(message.text)
        search_data = await state.get_data()
        train_data = search_data['trains_list'][train_index - 1]
        await state.update_data(train_data=train_data)
        await message.answer(text="Проверьте введенные данные:\n\n"
                                  f"Станиция отправления: <b>{search_data['station_from']}</b>\n"
                                  f"Станиция назначения: <b>{search_data['station_to']}</b>\n"
                                  f"Дата: <b>{search_data['date']}</b>\n"
                                  f"Выбранный поезд: <b>{train_data['train_number']} {train_data['train_name']}</b>\n"
                                  f"Отправление: <b>{train_data['train_departure']}</b>\n"
                                  f"Прибытие: <b>{train_data['train_arrival']}</b>\n"
                             ,
                             reply_markup=validate_train_kb()
                             )
        await state.update_data(trains_list=None)
    except Exception as error:
        print(error)
        await message.answer(text="Неверный номер")


@search_router.callback_query(F.data == 'start_search')
async def start_search(call: CallbackQuery, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    data['status'] = 'active'
    data['timestamp'] = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    # Используем setdefault для добавления данных
    user_requests_queue.setdefault(call.from_user.id, []).append(data)
    await call.message.edit_reply_markup()
    await call.message.answer('Спасибо! Ваш запрос принят.', reply_markup=go_home_kb())
    await state.clear()
    await call.answer()
