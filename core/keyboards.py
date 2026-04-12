from telebot import types
from core.translations import get_ru_name

def get_currency_select_keyboard(
    items: list,
    page: int,
    page_prefix: str,
    make_callback_data,
    cancel_data: str,
    ignore_data: str,
    items_per_page: int = 10
):
    markup = types.InlineKeyboardMarkup(row_width=1)
    total_pages = max(1, (len(items) + items_per_page - 1) // items_per_page)
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_items = items[start_idx:end_idx]
    
    for code, original_name in page_items:
        ru_name = get_ru_name(code, original_name)
        btn_text = f"{code} — {ru_name}"
        # Добавляем больше невидимых символов (ljust), чтобы гарантированно прижать текст к левому краю
        btn_text = btn_text.ljust(45, '\u2800')
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=make_callback_data(code)))
        
    # Добавляем пустые кнопки-пустышки, чтобы высота меню не прыгала на последней странице
    missing_items = items_per_page - len(page_items)
    for _ in range(missing_items):
        markup.add(types.InlineKeyboardButton('\u2800' * 45, callback_data=ignore_data))
        
    nav_buttons = []
    if page > 1:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"{page_prefix}{page-1}"))
    else:
        nav_buttons.append(types.InlineKeyboardButton(" ", callback_data=ignore_data))
        
    nav_buttons.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data=ignore_data))
    
    if page < total_pages:
        nav_buttons.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"{page_prefix}{page+1}"))
    else:
        nav_buttons.append(types.InlineKeyboardButton(" ", callback_data=ignore_data))
        
    markup.row(*nav_buttons)
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data=cancel_data))
    return markup