import logging
from logging.handlers import RotatingFileHandler
import os


def _has_currencybot_handler(logger):
    for handler in logger.handlers:
        if getattr(handler, "_currencybot_handler", False):
            return True
    return False

def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger() # Корневой логгер
    logger.setLevel(logging.INFO)

    # Не очищаем существующие handlers, чтобы не ломать логирование зависимостей.
    if _has_currencybot_handler(logger):
        return

    # Формат: 'Время | Уровень | Модуль | Сообщение'
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(module)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Настраиваем запись в файл с ротацией (максимум 5мб, храним до 3 архивов)
    file_handler = RotatingFileHandler(
        'logs/bot.log', 
        maxBytes=5*1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler._currencybot_handler = True

    # Настраиваем вывод в терминал
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler._currencybot_handler = True

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

setup_logger()
