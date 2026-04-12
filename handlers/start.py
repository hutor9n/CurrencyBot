from telebot import types
from telebot.types import Message
from core.config import bot

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_rates = types.KeyboardButton('💱 Курс гривны')
    btn_convert = types.KeyboardButton('🔄 Конвертер')
    btn_list = types.KeyboardButton('📋 Список валют')
    # Добавляем кнопки: Быстрые курсы на весь первый ряд, остальные ниже
    markup.add(btn_rates)
    markup.add(btn_convert, btn_list)
    return markup

def register_start_handlers():
    @bot.message_handler(commands=['start'])
    def start(message: Message):
        import logging
        logging.info(f"Пользователь {message.from_user.id} открыл главное меню (/start)")
        text = (
            "Привет! Я твой помощник для отслеживания курсов валют. 💸\n\n"
            "Выбери нужную функцию в меню ниже или через синюю кнопку Menu:"
        )
        bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard())
