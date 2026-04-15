import logging
import os
from telebot.types import BotCommand
from telebot.apihelper import ApiTelegramException
from core.config import create_bot
from core.logger import setup_logger
from controllers import register_all_controllers
from core.keep_alive import build_webhook_url, start_keep_alive

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

        webhook_url = build_webhook_url()
        if webhook_url:
            logging.warning(f"Запуск в webhook-режиме: {webhook_url}")
            bot.remove_webhook()
            bot.set_webhook(url=webhook_url, drop_pending_updates=True)
            start_keep_alive(bot)
        else:
            logging.warning("Запуск в polling-режиме")
            start_keep_alive()
            bot.polling(none_stop=True)
    except KeyboardInterrupt:
        logging.warning("Работа бота завершена пользователем (Ctrl+C).")
    except ApiTelegramException as e:
        if getattr(e, "error_code", None) == 409:
            logging.error("Бот уже запущен в другом экземпляре. Остановите второй процесс и запустите только один polling для этого токена.")
        else:
            logging.error(f"Ошибка Telegram API: {e}")
    except ValueError as e:
        logging.error(f"Ошибка конфигурации: {e}")

if __name__ == "__main__":
    main()
