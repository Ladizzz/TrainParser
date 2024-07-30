import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram import html

from create_bot import bot, db
from services.train_service import get_trains
from keyboards.inline_kbs import go_home_kb, validate_train_kb, price_filter_back_kb


class TrainSearch(StatesGroup):
    choosing_station_from = State()
    choosing_station_to = State()
    choosing_date = State()
    choosing_train = State()
    validating_train_number = State()
    validating_search = State()
    setting_price_filter_from = State()
    setting_price_filter_to = State()
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
async def choose_train(message: Message, state: FSMContext):
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
                    await state.set_state(TrainSearch.validating_train_number)
                else:
                    await message.answer(text="Нет доступных поездов. Проверьте правильность ввода")
                    await state.clear()
            else:
                await message.answer(text="Произошла ошибка при получении")
                await state.clear()
    except Exception as error:
        await message.answer(text="Произошла ошибка")
        user = await db["users"].find_one({"id": message.from_user.id})
        if user['debug_mode']:
            await message.answer(text=f"{error}")


@search_router.message(
    TrainSearch.validating_train_number
)
async def validating_train_number(message: Message, state: FSMContext):
    try:
        train_index = int(message.text)
        search_data = await state.get_data()
        train_data = search_data['trains_list'][train_index - 1]
        await state.update_data(train_data=train_data)
        await validate_search_message(message, state)
        await state.update_data(trains_list=None)
    except Exception:
        await message.answer(text="Неверный номер")


@search_router.message(
    TrainSearch.validating_search
)
async def validate_search_message(message: Message, state: FSMContext):
    search_data = await state.get_data()
    # check if search with price filter
    with_filter = 'price_from' in search_data
    response_text = await generate_response(search_data)
    await message.answer(text=response_text,
                         reply_markup=validate_train_kb(filter_exists=with_filter),
                         parse_mode=ParseMode.HTML)


@search_router.callback_query(F.data == 'back_to_validate_search')
async def validate_search_call(call: CallbackQuery, state: FSMContext):
    search_data = await state.get_data()
    # check if search with price filter
    with_filter = 'price_from' in search_data
    response_text = await generate_response(search_data)
    await call.message.answer(text=response_text,
                              reply_markup=validate_train_kb(filter_exists=with_filter),
                              parse_mode=ParseMode.HTML)
    await call.answer()


async def generate_response(search_data):
    logger = logging.getLogger("generate_response")
    try:
        response_text = (
            f"Проверьте введенные данные:\n\n"
            f"Станиция отправления: <b>{html.quote(search_data['station_from'])}</b>\n"
            f"Станиция назначения: <b>{html.quote(search_data['station_to'])}</b>\n"
            f"Дата: <b>{html.quote(search_data['date'])}</b>\n"
            f"Выбранный поезд: <b>{search_data['train_data']['train_number']} {search_data['train_data']['train_name']}</b>\n"
            f"Отправление: <b>{search_data['train_data']['train_departure']}</b>\n"
            f"Прибытие: <b>{search_data['train_data']['train_arrival']}</b>\n"
        )

        if 'price_from' in search_data:
            response_text += (
                f"Стоимость от: <b>{search_data['price_from']} BYN</b>\n"
            )

        if 'price_to' in search_data:
            response_text += (
                f"Стоимость до: <b>{search_data['price_to']} BYN</b>\n"
            )

        return response_text
    except Exception as error:
        logger.error(error)


@search_router.callback_query(F.data == 'start_search')
async def start_search(call: CallbackQuery, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    data['chat_id'] = call.from_user.id
    data['status'] = 'active'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['created_at'] = f'{timestamp}'
    data['updated_at'] = f'{timestamp}'
    # Используем setdefault для добавления данных
    await db["requests"].insert_one(data)
    await call.message.edit_reply_markup()
    await call.message.answer('Спасибо! Ваш запрос принят.', reply_markup=go_home_kb())
    await state.clear()
    await call.answer()


@search_router.callback_query(F.data == 'price_filter')
async def price_filter(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Введите стоимость от (BYN):', reply_markup=price_filter_back_kb())
    await state.set_state(TrainSearch.setting_price_filter_from)
    await call.answer()


@search_router.message(
    TrainSearch.setting_price_filter_from
)
async def price_filter(message: Message, state: FSMContext):
    await state.update_data(price_from=message.text)
    await message.answer('Введите стоимость до (BYN):', reply_markup=price_filter_back_kb())
    await state.set_state(TrainSearch.setting_price_filter_to)


@search_router.message(
    TrainSearch.setting_price_filter_to
)
async def price_filter(message: Message, state: FSMContext):
    await state.update_data(price_to=message.text)
    await validate_search_message(message, state)
