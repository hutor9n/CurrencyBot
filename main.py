import logging
import requests
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


def clear_webhook(bot):
    try:
        bot.remove_webhook()
    except Exception as e:
        logging.warning(f"Не удалось удалить webhook через TeleBot: {e}")

    try:
        webhook_info = bot.get_webhook_info()
        if getattr(webhook_info, 'url', ''):
            delete_url = f"https://api.telegram.org/bot{bot.token}/deleteWebhook"
            response = requests.post(delete_url, data={"drop_pending_updates": "true"}, timeout=10)
            response.raise_for_status()
            logging.info("Webhook был удалён через прямой вызов Telegram API")
    except Exception as e:
        logging.warning(f"Не удалось проверить или повторно удалить webhook: {e}")

def main():
    setup_logger()
    logging.warning("Запуск CurrencyBot...")
    try:
        bot = create_bot()
        register_all_controllers(bot)
        keep_alive()
        set_bot_commands(bot)

        clear_webhook(bot)
        logging.warning("Запуск в polling-режиме")
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        logging.warning("Работа бота завершена пользователем (Ctrl+C).")
    except ValueError as e:
        logging.error(f"Ошибка конфигурации: {e}")

if __name__ == "__main__":
    main()
