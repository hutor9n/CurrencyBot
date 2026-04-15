import logging
from telebot import TeleBot
from telebot.types import Message
from views import messages, keyboards

def register_start_controllers(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def start(message: Message):
        logging.info(f"Пользователь {message.from_user.id} открыл главное меню (/start)")
        bot.send_message(message.chat.id, messages.get_start_text(), reply_markup=keyboards.get_main_keyboard())
