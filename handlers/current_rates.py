from telebot import types
from telebot.types import Message, CallbackQuery
from core.config import bot
from core.translations import get_ru_name
import logging
from services.fiat_api import convert_currency, get_sorted_currencies

ITEMS_PER_PAGE = 15
RATE_ITEMS_PER_PAGE = 10

def get_currency_page_text(items, page):
    total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    if total_pages == 0:
         return "Нет доступных валют.", 1
    if page > total_pages:
        page = total_pages
        
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = items[start_idx:end_idx]
    
    text = f"📖 <b>Доступные валюты (Страница {page}/{total_pages})</b>\n\n"
    for code, original_name in page_items:
        ru_name = get_ru_name(code, original_name)
        text += f"<b>{code}</b> — {ru_name}\n"
        
    return text, total_pages

def get_pagination_keyboard(page, total_pages):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    if page > 1:
        buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
    else:
        buttons.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
        
    buttons.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages:
        buttons.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"page_{page+1}"))
    else:
        buttons.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
        
    markup.add(*buttons)
    return markup

def get_rates_select_keyboard(page, items):
    markup = types.InlineKeyboardMarkup(row_width=1)
    total_pages = (len(items) + RATE_ITEMS_PER_PAGE - 1) // RATE_ITEMS_PER_PAGE
    start_idx = (page - 1) * RATE_ITEMS_PER_PAGE
    end_idx = start_idx + RATE_ITEMS_PER_PAGE
    
    for code, original_name in items[start_idx:end_idx]:
        ru_name = get_ru_name(code, original_name)
        markup.add(types.InlineKeyboardButton(f"{code} — {ru_name}", callback_data=f"ratesel_{code}"))
        
    nav_buttons = []
    if page > 1:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"ratepage_{page-1}"))
    else:
        nav_buttons.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
        
    nav_buttons.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages:
        nav_buttons.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"ratepage_{page+1}"))
    else:
        nav_buttons.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
        
    markup.row(*nav_buttons)
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="rate_cancel"))
    return markup

def register_current_rates_handlers():
    @bot.message_handler(commands=['rates'])
    @bot.message_handler(func=lambda msg: msg.text == '💱 Быстрые курсы')
    def currency_message(message: Message):
        logging.info(f"Пользователь {message.from_user.id} запросил меню /rates")
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('USD', callback_data='rate_USD')
        btn2 = types.InlineKeyboardButton('EUR', callback_data='rate_EUR')
        btn3 = types.InlineKeyboardButton('GBP', callback_data='rate_GBP')
        btn4 = types.InlineKeyboardButton('Другая валюта', callback_data='rate_else')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, 'Узнать курс к гривне (UAH):', reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('page_') or call.data == 'ignore')
    def pagination_callback(call: CallbackQuery):
        if call.data == 'ignore':
            bot.answer_callback_query(call.id)
            return
            
        page = int(call.data.split('_')[1])
        items = get_sorted_currencies()
        
        if items:
            text, total_pages = get_currency_page_text(items, page)
            markup = get_pagination_keyboard(page, total_pages)
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=text,
                    parse_mode='HTML',
                    reply_markup=markup
                )
            except Exception:
                pass
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data in ['rate_USD', 'rate_EUR', 'rate_GBP', 'rate_else'])
    def currency_callback(call: CallbackQuery):
        logging.info(f"Пользователь {call.from_user.id} выбрал быструю валюту: {call.data}")
        currency_code = call.data.replace('rate_', '')
        if currency_code == 'else':
            items = get_sorted_currencies()
            if not items:
                bot.send_message(call.message.chat.id, "Сервис временно недоступен.")
                return
            markup = get_rates_select_keyboard(1, items)
            bot.edit_message_text("Выберите валюту из списка:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id)
            return
            
        result = convert_currency(currency_code, 'UAH', 1)
        if result is not None:
            bot.edit_message_text(f'Текущий курс {currency_code}: <b>{result:.2f} UAH</b>', chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')
        else:
            bot.edit_message_text('Произошла ошибка при получении курса. Попробуйте позже.', chat_id=call.message.chat.id, message_id=call.message.message_id)
            
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == 'rate_cancel')
    def rate_cancel_callback(call: CallbackQuery):
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('USD', callback_data='rate_USD')
        btn2 = types.InlineKeyboardButton('EUR', callback_data='rate_EUR')
        btn3 = types.InlineKeyboardButton('GBP', callback_data='rate_GBP')
        btn4 = types.InlineKeyboardButton('Другая валюта', callback_data='rate_else')
        markup.add(btn1, btn2, btn3, btn4)
        bot.edit_message_text('Узнать курс к гривне (UAH):', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('ratepage_'))
    def rate_page_callback(call: CallbackQuery):
        page = int(call.data.replace('ratepage_', ''))
        items = get_sorted_currencies()
        if items:
            markup = get_rates_select_keyboard(page, items)
            try:
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            except Exception:
                pass
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('ratesel_'))
    def rate_selected_callback(call: CallbackQuery):
        currency_code = call.data.replace('ratesel_', '')
        result = convert_currency(currency_code, 'UAH', 1)
        if result is not None:
            bot.edit_message_text(f'Текущий курс {currency_code}: <b>{result:.2f} UAH</b>', chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')
        else:
            bot.edit_message_text('Произошла ошибка при получении курса. Попробуйте позже.', chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)

    @bot.message_handler(commands=['list'])
    @bot.message_handler(func=lambda msg: msg.text == '📋 Список валют')
    def currencies_command(message: Message):
        logging.info(f"Пользователь {message.from_user.id} запросил /list (Список валют)")
        items = get_sorted_currencies()
        if items:
            page = 1
            text, total_pages = get_currency_page_text(items, page)
            markup = get_pagination_keyboard(page, total_pages)
            bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Не удалось получить список валют. Попробуйте позже.')
