from telebot import types
from views.translations import get_ru_name

MENU_BUTTONS = ['💱 Курс к гривне', '🔁 Конвертер', '📘 Список валют']

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_rates = types.KeyboardButton('💱 Курс к гривне')
    btn_convert = types.KeyboardButton('🔁 Конвертер')
    btn_list = types.KeyboardButton('📘 Список валют')
    markup.add(btn_rates)
    markup.add(btn_convert, btn_list)
    return markup

def get_fast_rates_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=3)
    btn1 = types.InlineKeyboardButton('USD', callback_data='USD')
    btn2 = types.InlineKeyboardButton('EUR', callback_data='EUR')
    btn3 = types.InlineKeyboardButton('GBP', callback_data='GBP')
    btn4 = types.InlineKeyboardButton('🌍 Другие валюты', callback_data='else')
    markup.add(btn1, btn2, btn3, btn4)
    return markup


def get_rates_picker_keyboard(page: int, total_pages: int, items: list, items_per_page=10):
    markup = types.InlineKeyboardMarkup(row_width=1)
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_items = items[start_idx:end_idx]

    for code, original_name in page_items:
        ru_name = get_ru_name(code, original_name)
        btn_text = f"{code} - {ru_name}"
        btn_text = btn_text.ljust(45, '\u2800')
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"rate_{code}"))

    nav_buttons = []
    if page > 1:
        nav_buttons.append(types.InlineKeyboardButton("Назад", callback_data=f"ratep_{page-1}"))
    else:
        nav_buttons.append(types.InlineKeyboardButton(" ", callback_data="rate_ignore"))

    nav_buttons.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="rate_ignore"))

    if page < total_pages:
        nav_buttons.append(types.InlineKeyboardButton("Вперед", callback_data=f"ratep_{page+1}"))
    else:
        nav_buttons.append(types.InlineKeyboardButton(" ", callback_data="rate_ignore"))

    markup.row(*nav_buttons)
    return markup

def get_pagination_keyboard(page: int, total_pages: int, prefix="page_", ignore_data="ignore"):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    if page > 1:
        buttons.append(types.InlineKeyboardButton("Назад", callback_data=f"{prefix}{page-1}"))
    else:
        buttons.append(types.InlineKeyboardButton(" ", callback_data=ignore_data))
        
    buttons.append(types.InlineKeyboardButton(f"{page} / {total_pages}", callback_data=ignore_data))
    
    if page < total_pages:
        buttons.append(types.InlineKeyboardButton("Вперед", callback_data=f"{prefix}{page+1}"))
    else:
        buttons.append(types.InlineKeyboardButton(" ", callback_data=ignore_data))
        
    markup.add(*buttons)
    return markup

def get_convert_keyboard(prefix: str, page: int, total_pages: int, items: list, make_callback_data, items_per_page=10):
    markup = types.InlineKeyboardMarkup(row_width=1)
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_items = items[start_idx:end_idx]
    
    for code, original_name in page_items:
        ru_name = get_ru_name(code, original_name)
        btn_text = f"{code} — {ru_name}"
        btn_text = btn_text.ljust(45, '\u2800')
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=make_callback_data(code)))
        
    missing_items = items_per_page - len(page_items)
    for _ in range(missing_items):
        markup.add(types.InlineKeyboardButton('\u2800' * 45, callback_data="conv_ignore"))
        
    nav_buttons = []
    if page > 1:
        nav_buttons.append(types.InlineKeyboardButton("Назад", callback_data=f"{prefix}{page-1}"))
    else:
        nav_buttons.append(types.InlineKeyboardButton(" ", callback_data="conv_ignore"))
        
    nav_buttons.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="conv_ignore"))
    
    if page < total_pages:
        nav_buttons.append(types.InlineKeyboardButton("Вперед", callback_data=f"{prefix}{page+1}"))
    else:
        nav_buttons.append(types.InlineKeyboardButton(" ", callback_data="conv_ignore"))
        
    markup.row(*nav_buttons)
    markup.add(types.InlineKeyboardButton("✖️ Отмена", callback_data="conv_cancel"))
    return markup
