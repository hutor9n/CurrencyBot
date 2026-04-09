import telebot
import os
import logging
from dotenv import load_dotenv
import core.logger # Инициализация нашей новой системы логирования

# Завантажуємо змінні з .env файлу
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Не знайдено BOT_TOKEN у файлі .env")

API_KEYS_RAW = os.getenv('API_KEYS', '')

# Розбиваємо "key1,key2" на масив і прибираємо лапки/пробіли
API_KEYS = [k.strip().strip('"\'') for k in API_KEYS_RAW.split(',')] if API_KEYS_RAW else []

if not API_KEYS or not API_KEYS[0]:
    raise ValueError("Не знайдено API_KEYS у файлі .env")

bot = telebot.TeleBot(BOT_TOKEN)
