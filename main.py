import logging
from telebot.types import BotCommand
from core.config import create_bot
from core.logger import setup_logger
from controllers import register_all_controllers
from core.keep_alive import keep_alive

def set_bot_commands(bot):
    commands = [
        BotCommand("start", "Главное меню и перезапуск"),
        BotCommand("rates", "Курс валют к гривне"),
        BotCommand("list", "Список всех доступных валют"),
        BotCommand("convert", "Конвертер валют")
    ]
    bot.set_my_commands(commands)

def main():
    setup_logger()
    logging.warning("Запуск CurrencyBot...")
    try:
        bot = create_bot()
        register_all_controllers(bot)
        set_bot_commands(bot)

        keep_alive()
        bot.delete_webhook(drop_pending_updates=True)
        logging.warning("Запуск long polling")
        bot.infinity_polling(skip_pending=True)
    except KeyboardInterrupt:
        logging.warning("Работа бота завершена пользователем (Ctrl+C).")
    except ValueError as e:
        logging.error(f"Ошибка конфигурации: {e}")

if __name__ == "__main__":
    main()
