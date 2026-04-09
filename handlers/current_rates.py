from telebot import types
from telebot.types import Message, CallbackQuery
from core.config import bot
from core.translations import get_ru_name
import logging
from services.fiat_api import convert_currency, get_sorted_currencies

ITEMS_PER_PAGE = 15

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
        text += f"🔹 <b>{code}</b> — <i>{ru_name}</i>\n"
        
    return text, total_pages

def get_pagination_keyboard(page, total_pages):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    
    if page > 1:
        buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
    else:
        buttons.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
        
    buttons.append(types.InlineKeyboardButton(f"{page} / {total_pages}", callback_data="ignore"))
    
    if page < total_pages:
        buttons.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"page_{page+1}"))
    else:
        buttons.append(types.InlineKeyboardButton(" ", callback_data="ignore"))
        
    markup.add(*buttons)
    return markup

def register_current_rates_handlers():
    @bot.message_handler(commands=['rates'])
    @bot.message_handler(func=lambda msg: msg.text == '💱 Быстрые курсы')
    def currency_message(message: Message):
        logging.info(f"Пользователь {message.from_user.id} запросил меню /rates")
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton('USD', callback_data='USD')
        btn2 = types.InlineKeyboardButton('EUR', callback_data='EUR')
        btn3 = types.InlineKeyboardButton('GBP', callback_data='GBP')
        btn4 = types.InlineKeyboardButton('Другая валюта', callback_data='else')
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

    @bot.callback_query_handler(func=lambda call: call.data in ['USD', 'EUR', 'GBP', 'else'])
    def currency_callback(call: CallbackQuery):
        logging.info(f"Пользователь {call.from_user.id} выбрал быструю валюту: {call.data}")
        if call.data == 'else':
            bot.send_message(call.message.chat.id, 'Введите трехбуквенный код валюты (например, PLN):')
            bot.register_next_step_handler(call.message, user_currency)
            return
            
        result = convert_currency(call.data, 'UAH', 1)
        if result is not None:
            bot.send_message(call.message.chat.id, f'Текущий курс: <b>{result:.2f} UAH</b>', parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, 'Произошла ошибка при получении курса. Попробуйте позже.')
            
        bot.answer_callback_query(call.id)

    def user_currency(message: Message):
        code = message.text.upper()
        result = convert_currency(code, 'UAH', 1)
        if result is not None:
            bot.send_message(message.chat.id, f'Текущий курс {code}: <b>{result:.2f} UAH</b>', parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, 'Ошибка при получении курса. Проверьте правильность кода валюты.')

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
