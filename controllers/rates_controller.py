import logging
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from views import messages, keyboards
from models import fiat_api

ITEMS_PER_PAGE = 15
RATES_PICKER_ITEMS_PER_PAGE = 10

def register_rates_controllers(bot: TeleBot):
    @bot.message_handler(commands=['rates'])
    @bot.message_handler(func=lambda msg: msg.text == '💱 Курс к гривне')
    def currency_message(message: Message):
        logging.info(f"Пользователь {message.from_user.id} запросил меню /rates")
        bot.send_message(message.chat.id, messages.get_rates_menu_text(), reply_markup=keyboards.get_fast_rates_keyboard())

    @bot.callback_query_handler(func=lambda call: call.data in ['USD', 'EUR', 'GBP', 'else'])
    def currency_callback(call: CallbackQuery):
        logging.info(f"Пользователь {call.from_user.id} выбрал валюту в разделе /rates: {call.data}")
        if call.data == 'else':
            items = fiat_api.get_sorted_currencies()
            if not items:
                bot.send_message(call.message.chat.id, 'Не удалось получить список валют. Попробуйте позже.')
                bot.answer_callback_query(call.id)
                return

            total_pages = (len(items) + RATES_PICKER_ITEMS_PER_PAGE - 1) // RATES_PICKER_ITEMS_PER_PAGE
            markup = keyboards.get_rates_picker_keyboard(
                page=1,
                total_pages=total_pages,
                items=items,
                items_per_page=RATES_PICKER_ITEMS_PER_PAGE,
            )
            bot.edit_message_text(
                "💱 Выберите валюту для просмотра курса к гривне (UAH):",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup,
            )
            bot.answer_callback_query(call.id)
            return
            
        result = fiat_api.convert_currency(call.data, 'UAH', 1)
        if result is not None:
            text = f'💱 Текущий курс: <b>{result:.2f} UAH</b>'
            bot.send_message(call.message.chat.id, text, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, 'Произошла ошибка при получении курса. Попробуйте позже.')
            
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('ratep_') or call.data == 'rate_ignore')
    def rate_picker_pagination(call: CallbackQuery):
        if call.data == 'rate_ignore':
            bot.answer_callback_query(call.id)
            return

        page = int(call.data.replace('ratep_', ''))
        items = fiat_api.get_sorted_currencies()
        if not items:
            bot.answer_callback_query(call.id, 'Список валют временно недоступен.')
            return

        total_pages = (len(items) + RATES_PICKER_ITEMS_PER_PAGE - 1) // RATES_PICKER_ITEMS_PER_PAGE
        markup = keyboards.get_rates_picker_keyboard(
            page=page,
            total_pages=total_pages,
            items=items,
            items_per_page=RATES_PICKER_ITEMS_PER_PAGE,
        )

        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup,
            )
        except Exception as e:
            logging.warning(f"Не удалось обновить страницу выбора валюты в /rates: {e}")

        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('rate_'))
    def rate_picker_selected(call: CallbackQuery):
        code = call.data.replace('rate_', '')
        result = fiat_api.convert_currency(code, 'UAH', 1)
        if result is not None:
            text = f'💱 Текущий курс {code}: <b>{result:.2f} UAH</b>'
            bot.send_message(call.message.chat.id, text, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, 'Произошла ошибка при получении курса. Попробуйте позже.')

        bot.answer_callback_query(call.id)

    @bot.message_handler(commands=['list'])
    @bot.message_handler(func=lambda msg: msg.text == '📘 Список валют')
    def currencies_command(message: Message):
        logging.info(f"Пользователь {message.from_user.id} запросил список валют (/list)")
        items = fiat_api.get_sorted_currencies()
        if items:
            text, total_pages = messages.get_list_page_text(items, page=1, items_per_page=ITEMS_PER_PAGE)
            markup = keyboards.get_pagination_keyboard(page=1, total_pages=total_pages)
            bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Не удалось получить список валют. Попробуйте позже.')

    @bot.callback_query_handler(func=lambda call: call.data.startswith('page_') or call.data == 'ignore')
    def pagination_callback(call: CallbackQuery):
        if call.data == 'ignore':
            bot.answer_callback_query(call.id)
            return
            
        page = int(call.data.split('_')[1])
        items = fiat_api.get_sorted_currencies()
        
        if items:
            text, total_pages = messages.get_list_page_text(items, page, ITEMS_PER_PAGE)
            markup = keyboards.get_pagination_keyboard(page, total_pages)
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=text,
                    parse_mode='HTML',
                    reply_markup=markup
                )
            except Exception as e:
                logging.warning(f"Не удалось обновить страницу списка валют: {e}")
        bot.answer_callback_query(call.id)
