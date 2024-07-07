from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from create_bot import admins


def start_kb(user_telegram_id: int):
    inline_kb_list = [
        [InlineKeyboardButton(text="📝 Новый поиск", callback_data="new_search")],
        [InlineKeyboardButton(text="📚 Лист ожидания", callback_data='waiting_list')]
    ]
    if user_telegram_id in admins:
        inline_kb_list.append([InlineKeyboardButton(text="⚙️ Администрирование", callback_data='admin_panel')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def back_home_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="На главную", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def search_details_kb(train_id):
    inline_kb_list = [
        [InlineKeyboardButton(text="❌ Удалить", callback_data=f'delete_{train_id}')],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='waiting_list_back')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def search_details_back_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data='waiting_list_back')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def waiting_list_kb(items=[]):
    inline_kb_list = [
        [InlineKeyboardButton(text=item, callback_data=f'train_{i}')] for i, item in enumerate(items)
    ]
    inline_kb_list.append([InlineKeyboardButton(text="На главную", callback_data='back_home')])
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def validate_train_kb():
    inline_kb_list = [
        [InlineKeyboardButton(text="🔍 Начать поиск", callback_data='start_search')],
        [InlineKeyboardButton(text="❌ Отмена", callback_data='back_home')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
