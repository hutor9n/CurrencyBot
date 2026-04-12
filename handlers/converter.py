from telebot import types
from telebot.types import Message, CallbackQuery
from core.config import bot
from core.translations import get_ru_name
import logging
from services.fiat_api import convert_currency, get_sorted_currencies

MENU_BUTTONS = ['💱 Курс гривны', '🔄 Конвертер', '📋 Список валют']
ITEMS_PER_PAGE = 10

def get_convert_keyboard(prefix: str, page: int, total_pages: int, items: list, make_callback_data):
    markup = types.InlineKeyboardMarkup(row_width=1)
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = items[start_idx:end_idx]
    
    for code, original_name in page_items:
        ru_name = get_ru_name(code, original_name)
        markup.add(types.InlineKeyboardButton(f"{code} — {ru_name}", callback_data=make_callback_data(code)))
        
    nav_buttons = []
    if page > 1:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"{prefix}{page-1}"))
    else:
        nav_buttons.append(types.InlineKeyboardButton(" ", callback_data="conv_ignore"))
        
    nav_buttons.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="conv_ignore"))
    
    if page < total_pages:
        nav_buttons.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"{prefix}{page+1}"))
    else:
        nav_buttons.append(types.InlineKeyboardButton(" ", callback_data="conv_ignore"))
        
    markup.row(*nav_buttons)
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="conv_cancel"))
    return markup


def register_converter_handlers():
    @bot.message_handler(commands=['convert'])
    @bot.message_handler(func=lambda msg: msg.text == '🔄 Конвертер')
    def convert_start(message: Message):
        logging.info(f"Пользователь {message.from_user.id} запустил интерактивный /convert")
        items = get_sorted_currencies()
        if not items:
            bot.send_message(message.chat.id, "Сервис временно недоступен.")
            return
            
        total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        markup = get_convert_keyboard(
            prefix="cfp_", 
            page=1, 
            total_pages=total_pages, 
            items=items, 
            make_callback_data=lambda code: f"cf_{code}"
        )
        bot.send_message(message.chat.id, 'Выберите валюту <b>ИЗ</b> которой переводим:', parse_mode='HTML', reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'conv_cancel' or call.data == 'conv_ignore')
    def conv_generic_callback(call: CallbackQuery):
        if call.data == 'conv_cancel':
            bot.edit_message_text("Операция конвертации прервана. ❌", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('cfp_'))
    def conv_from_page_callback(call: CallbackQuery):
        page = int(call.data.replace('cfp_', ''))
        items = get_sorted_currencies()
        total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        markup = get_convert_keyboard(
            prefix="cfp_", 
            page=page, 
            total_pages=total_pages, 
            items=items, 
            make_callback_data=lambda code: f"cf_{code}"
        )
        
        try:
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except Exception:
            pass
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('cf_'))
    def conv_from_selected(call: CallbackQuery):
        from_code = call.data.replace('cf_', '')
        
        items = get_sorted_currencies()
        total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        markup = get_convert_keyboard(
            prefix=f"ctp_{from_code}_", 
            page=1, 
            total_pages=total_pages, 
            items=items, 
            make_callback_data=lambda code: f"ct_{from_code}_{code}"
        )
        
        text = f"Вы выбрали: <b>{from_code}</b>. Теперь выберите валюту <b>В</b> которую переводим:"
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('ctp_'))
    def conv_to_page_callback(call: CallbackQuery):
        parts = call.data.split('_')
        from_code = parts[1]
        page = int(parts[2])
        
        items = get_sorted_currencies()
        total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        markup = get_convert_keyboard(
            prefix=f"ctp_{from_code}_", 
            page=page, 
            total_pages=total_pages, 
            items=items, 
            make_callback_data=lambda code: f"ct_{from_code}_{code}"
        )
        
        try:
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except Exception:
            pass
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('ct_'))
    def conv_to_selected(call: CallbackQuery):
        parts = call.data.split('_')
        from_code = parts[1]
        to_code = parts[2]
        
        text = f"Перевод <b>{from_code} ➡️ {to_code}</b>.\nВведите сумму цифрами (например: 100):"
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, get_amount, from_code, to_code)
        bot.answer_callback_query(call.id)

    def get_amount(message: Message, from_code: str, to_code: str):
        try:
            if message.text in MENU_BUTTONS:
                bot.send_message(message.chat.id, 'Операция конвертации отменена.')
                return

            amount_str = message.text.replace(',', '.')
            amount = float(amount_str)
            logging.info(f"Пользователь {message.from_user.id} инициировал запрос перевода: {amount} {from_code}->{to_code}")
            result = convert_currency(from_code, to_code, amount)
            if result is not None:
                bot.send_message(message.chat.id, f'Конвертация <b>{amount} {from_code} ➡️ {to_code}</b>:\n✅ <b>{result:.2f}</b>', parse_mode='HTML')
                logging.info(f"Успешный перевод для {message.from_user.id}: {result:.2f}")
            else:
                logging.error(f"Юзер {message.from_user.id}: Ошибка при конвертации {from_code}->{to_code} (скорее всего недопустимая пара или ошибка API 106)")
                bot.send_message(message.chat.id, 'Произошла ошибка при расчете курса.')
        except ValueError:
            bot.send_message(message.chat.id, 'Пожалуйста, введите корректное число (используйте точку или запятую).')
        except Exception as e:
            logging.error(f"Ошибка в get_amount: {e}")
            bot.send_message(message.chat.id, 'Возникла непредвиденная ошибка.')
