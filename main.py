import logging
from telebot.types import BotCommand
from core.config import bot
from handlers import register_all_handlers

def set_bot_commands():
    commands = [
        BotCommand("start", "Главное меню и перезапуск"),
        BotCommand("rates", "Курс популярных валют"),
        BotCommand("list", "Список всех доступных валют"),
        BotCommand("convert", "Калькулятор-конвертер")
    ]
    bot.set_my_commands(commands)

def main():
    logging.warning("Запуск CurrencyBot...")
    register_all_handlers()
    try:
        set_bot_commands()
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        logging.warning("Работа бота завершена пользователем (Ctrl+C).")

if __name__ == "__main__":
    main()
