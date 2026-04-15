import logging
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from controllers.common import close_inline_keyboard, get_total_pages, safe_edit_message_reply_markup, safe_edit_message_text
from views import messages, keyboards
from services.currency_service import convert_currency, get_sorted_currencies

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
            items = get_sorted_currencies()
            if not items:
                bot.send_message(call.message.chat.id, messages.get_currency_list_unavailable_text())
                bot.answer_callback_query(call.id)
                return

            total_pages = get_total_pages(items, RATES_PICKER_ITEMS_PER_PAGE)
            markup = keyboards.get_rates_picker_keyboard(
                page=1,
                total_pages=total_pages,
                items=items,
                items_per_page=RATES_PICKER_ITEMS_PER_PAGE,
            )
            safe_edit_message_text(
                bot,
                call.message,
                "💱 Выберите валюту для просмотра курса к гривне (UAH):",
                reply_markup=markup,
            )
            bot.answer_callback_query(call.id)
            return
            
        result = convert_currency(call.data, 'UAH', 1)
        if result is not None:
            text = f'💱 Текущий курс: <b>{result:.2f} UAH</b>'
            bot.send_message(call.message.chat.id, text, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, 'Произошла ошибка при получении курса. Попробуйте позже.')

        close_inline_keyboard(bot, call.message)
            
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('ratep_') or call.data == 'rate_ignore')
    def rate_picker_pagination(call: CallbackQuery):
        if call.data == 'rate_ignore':
            bot.answer_callback_query(call.id)
            return

        page = int(call.data.replace('ratep_', ''))
        items = get_sorted_currencies()
        if not items:
            bot.answer_callback_query(call.id, messages.get_currency_list_temp_unavailable_text())
            return

        total_pages = get_total_pages(items, RATES_PICKER_ITEMS_PER_PAGE)
        markup = keyboards.get_rates_picker_keyboard(
            page=page,
            total_pages=total_pages,
            items=items,
            items_per_page=RATES_PICKER_ITEMS_PER_PAGE,
        )

        if not safe_edit_message_reply_markup(bot, call.message, markup):
            logging.warning("Не удалось обновить страницу выбора валюты в /rates")

        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('rate_'))
    def rate_picker_selected(call: CallbackQuery):
        code = call.data.replace('rate_', '')
        result = convert_currency(code, 'UAH', 1)
        if result is not None:
            text = f'💱 Текущий курс {code}: <b>{result:.2f} UAH</b>'
            bot.send_message(call.message.chat.id, text, parse_mode='HTML')
        else:
            bot.send_message(call.message.chat.id, messages.get_currency_rate_unavailable_text())

        close_inline_keyboard(bot, call.message)

        bot.answer_callback_query(call.id)

    @bot.message_handler(commands=['list'])
    @bot.message_handler(func=lambda msg: msg.text == '📘 Список валют')
    def currencies_command(message: Message):
        logging.info(f"Пользователь {message.from_user.id} запросил список валют (/list)")
        items = get_sorted_currencies()
        if items:
            text, total_pages = messages.get_list_page_text(items, page=1, items_per_page=ITEMS_PER_PAGE)
            markup = keyboards.get_pagination_keyboard(page=1, total_pages=total_pages)
            bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, messages.get_currency_list_unavailable_text())

    @bot.callback_query_handler(func=lambda call: call.data.startswith('page_') or call.data == 'ignore')
    def pagination_callback(call: CallbackQuery):
        if call.data == 'ignore':
            bot.answer_callback_query(call.id)
            return
            
        page = int(call.data.split('_')[1])
        items = get_sorted_currencies()
        
        if items:
            text, total_pages = messages.get_list_page_text(items, page, ITEMS_PER_PAGE)
            markup = keyboards.get_pagination_keyboard(page, total_pages)
            if not safe_edit_message_text(bot, call.message, text, parse_mode='HTML', reply_markup=markup):
                logging.warning("Не удалось обновить страницу списка валют")
        bot.answer_callback_query(call.id)
