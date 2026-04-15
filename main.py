import logging
from telebot.types import BotCommand
from telebot.apihelper import ApiTelegramException
from core.config import create_bot
from core.logger import setup_logger
from controllers import register_all_controllers

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

        # Если webhook был активирован ранее, polling вернет ошибку 409.
        bot.remove_webhook(drop_pending_updates=False)
        logging.warning("Запуск в polling-режиме")
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
