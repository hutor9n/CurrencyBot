import telebot
import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env файлу
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

API_KEYS_RAW = os.getenv('API_KEYS', '')

# Розбиваємо "key1,key2" на масив і прибираємо лапки/пробіли
API_KEYS = [k.strip().strip('"\'') for k in API_KEYS_RAW.split(',')] if API_KEYS_RAW else []

def get_bot_token(required: bool = True) -> str | None:
    if required and not BOT_TOKEN:
        raise ValueError("Не найден BOT_TOKEN в .env")
    return BOT_TOKEN


def get_api_keys(required: bool = True) -> list[str]:
    keys = [k for k in API_KEYS if k]
    if required and not keys:
        raise ValueError("Не найдены API_KEYS в .env")
    return keys


def create_bot(token: str | None = None) -> telebot.TeleBot:
    bot_token = token or get_bot_token(required=True)
    return telebot.TeleBot(bot_token)
