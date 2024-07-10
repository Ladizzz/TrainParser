from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from create_bot import admins


def start_kb(user_telegram_id: int):
    inline_kb_list = [
        [InlineKeyboardButton(text="📝 Новый поиск", callback_data="new_search")],
        [InlineKeyboardButton(text="📚 Лист ожидания", callback_data='waiting_list')]
    ]
    if user_telegram_id in admins:
        inline_kb_list.append([InlineKeyboardButton(text="⚙️ Администрирование", callback_data='administration')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def go_home_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="На главную", callback_data='go_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def back_home_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def search_details_kb(request_id, status="active"):
    inline_kb_list = [
        [InlineKeyboardButton(text="❌ Удалить", callback_data=f'delete_{request_id}')]
    ]

    if status != "active":
        inline_kb_list.append([InlineKeyboardButton(text="🔁 Повторить", callback_data=f'restart_{request_id}')])

    inline_kb_list.append([InlineKeyboardButton(text="⬅️ Назад", callback_data='waiting_list')])

    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def search_details_back_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='waiting_list')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def waiting_list_kb(requests=[]):
    inline_kb_list = [
        [InlineKeyboardButton(text=f"{request['station_from']} - {request['station_to']} ({request['date']}) - {request['train_data']['train_number']}", callback_data=f'request_{request["_id"]}')] for request in requests
    ]
    inline_kb_list.append([InlineKeyboardButton(text="На главную", callback_data='go_home')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def validate_train_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="🔍 Начать поиск", callback_data='start_search')],
        [InlineKeyboardButton(text="❌ Отмена", callback_data='go_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def administration_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="⚙️ Режим отладки", callback_data=f'debug_mode')],
        [InlineKeyboardButton(text="⏳ Интервал поиска", callback_data=f'search_interval')],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
