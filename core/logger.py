import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger() # Корневой логгер
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

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

    # Настраиваем вывод в терминал
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

setup_logger()
