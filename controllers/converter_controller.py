import logging
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from views import messages, keyboards
from models import fiat_api

ITEMS_PER_PAGE = 10

def register_converter_controllers(bot: TeleBot):
    @bot.message_handler(commands=['convert'])
    @bot.message_handler(func=lambda msg: msg.text == '🔁 Конвертер')
    def convert_start(message: Message):
        logging.info(f"Пользователь {message.from_user.id} запустил интерактивный /convert")
        items = fiat_api.get_sorted_currencies()
        if not items:
            bot.send_message(message.chat.id, "Сервис временно недоступен.")
            return
            
        total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        markup = keyboards.get_convert_keyboard(
            prefix="cfp_", 
            page=1, 
            total_pages=total_pages, 
            items=items, 
            make_callback_data=lambda code: f"cf_{code}",
            items_per_page=ITEMS_PER_PAGE
        )
        bot.send_message(message.chat.id, messages.get_convert_start_text(), parse_mode='HTML', reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == 'conv_cancel' or call.data == 'conv_ignore')
    def conv_generic_callback(call: CallbackQuery):
        if call.data == 'conv_cancel':
            bot.edit_message_text("Операция конвертации прервана.", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('cfp_'))
    def conv_from_page_callback(call: CallbackQuery):
        page = int(call.data.replace('cfp_', ''))
        items = fiat_api.get_sorted_currencies()
        total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        markup = keyboards.get_convert_keyboard(
            prefix="cfp_", 
            page=page, 
            total_pages=total_pages, 
            items=items, 
            make_callback_data=lambda code: f"cf_{code}",
            items_per_page=ITEMS_PER_PAGE
        )
        try:
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except Exception as e:
            logging.warning(f"Не удалось обновить список валют ИЗ в конвертере: {e}")
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('cf_'))
    def conv_from_selected(call: CallbackQuery):
        from_code = call.data.replace('cf_', '')
        
        items = fiat_api.get_sorted_currencies()
        total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        markup = keyboards.get_convert_keyboard(
            prefix=f"ctp_{from_code}_", 
            page=1, 
            total_pages=total_pages, 
            items=items, 
            make_callback_data=lambda code: f"ct_{from_code}_{code}",
            items_per_page=ITEMS_PER_PAGE
        )
        
        bot.edit_message_text(messages.get_convert_to_text(from_code), chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML', reply_markup=markup)
        bot.answer_callback_query(call.id)
        
    @bot.callback_query_handler(func=lambda call: call.data.startswith('ctp_'))
    def conv_to_page_callback(call: CallbackQuery):
        parts = call.data.split('_')
        from_code = parts[1]
        page = int(parts[2])
        
        items = fiat_api.get_sorted_currencies()
        total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        
        markup = keyboards.get_convert_keyboard(
            prefix=f"ctp_{from_code}_", 
            page=page, 
            total_pages=total_pages, 
            items=items, 
            make_callback_data=lambda code: f"ct_{from_code}_{code}",
            items_per_page=ITEMS_PER_PAGE
        )
        
        try:
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except Exception as e:
            logging.warning(f"Не удалось обновить список валют В в конвертере: {e}")
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('ct_'))
    def conv_to_selected(call: CallbackQuery):
        parts = call.data.split('_')
        from_code = parts[1]
        to_code = parts[2]
        
        bot.edit_message_text(messages.get_convert_amount_text(from_code, to_code), chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, get_amount, from_code, to_code)
        bot.answer_callback_query(call.id)

    def get_amount(message: Message, from_code: str, to_code: str):
        try:
            if message.text in keyboards.MENU_BUTTONS:
                bot.send_message(message.chat.id, 'Операция конвертации отменена.')
                return

            amount_str = message.text.replace(',', '.')
            amount = float(amount_str)
            logging.info(f"Пользователь {message.from_user.id} инициировал запрос перевода: {amount} {from_code}->{to_code}")
            result = fiat_api.convert_currency(from_code, to_code, amount)
            if result is not None:
                bot.send_message(message.chat.id, messages.get_convert_result_text(amount, from_code, to_code, result), parse_mode='HTML')
                logging.info(f"Конвертация для пользователя {message.from_user.id} выполнена успешно: {result:.2f}")
            else:
                logging.error(
                    f"Ошибка конвертации для пользователя {message.from_user.id}: {from_code}->{to_code} (возможна недопустимая пара или ошибка API 106)"
                )
                bot.send_message(message.chat.id, 'Произошла ошибка при расчете курса.')
        except ValueError:
            bot.send_message(message.chat.id, 'Пожалуйста, введите корректное число (используйте точку или запятую).')
        except Exception as e:
            logging.error(f"Ошибка в get_amount: {e}")
            bot.send_message(message.chat.id, 'Возникла непредвиденная ошибка.')
