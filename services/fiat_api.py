import requests
import json
import logging
from core.config import API_KEYS
from services.cache_manager import get_cached_list, cache_list, get_cached_rate, cache_rate

# Змінна для зберігання індексу поточного ключа
current_key_index = 0
FAVORITES = ["UAH", "USD", "EUR", "PLN", "GBP", "CZK"]

def _make_request(endpoint_url: str):
    """Внутрішня функція яка автоматично перемикає ключі у разі помилки 104/101."""
    global current_key_index
    for _ in range(len(API_KEYS)):
        current_api_key = API_KEYS[current_key_index]
        url = endpoint_url.replace('{API_KEY}', current_api_key)
        try:
            res = requests.get(url)
            data = json.loads(res.text)
            if data.get('success', False):
                return data
            error_code = data.get('error', {}).get('code')
            if error_code in (101, 104):
                logging.warning(f"Ключ {current_api_key} недійсний/вичерпаний (код {error_code}). Змінюємо на наступний...")
                current_key_index = (current_key_index + 1) % len(API_KEYS)
            else:
                logging.error(f"Помилка API currencylayer: {data.get('error')}")
                return None
        except Exception as e:
            logging.error(f"Критична помилка запиту: {e}")
            return None
    logging.error("УСІ API КЛЮЧІ ВИЧЕРПАНО АБО НЕДІЙСНІ!")
    return None

def get_currency_list():
    """Повертає словник усіх валют."""
    cached = get_cached_list()
    if cached:
        return cached

    url = 'https://api.currencylayer.com/list?access_key={API_KEY}'
    data = _make_request(url)
    if data and 'currencies' in data:
        cache_list(data['currencies'])
        return data['currencies']
    return None

def get_sorted_currencies():
    """Возвращает список кортежей [(code, name), ...] отсортированный для пользователей из Украины."""
    raw_dict = get_currency_list()
    if not raw_dict:
        return []
    
    favs = [(k, raw_dict[k]) for k in FAVORITES if k in raw_dict]
    others = [(k, raw_dict[k]) for k in raw_dict if k not in FAVORITES]
    others.sort(key=lambda x: x[0])
    
    return favs + others

def convert_currency(from_currency: str, to_currency: str, amount: float):
    base_rate = get_cached_rate(from_currency, to_currency)
    if base_rate is not None:
        return base_rate * amount

    url = f'https://api.currencylayer.com/convert?access_key={{API_KEY}}&from={from_currency}&to={to_currency}&amount=1'
    data = _make_request(url)
    if data and 'result' in data:
        base_rate = data['result']
        cache_rate(from_currency, to_currency, base_rate)
        return base_rate * amount
    return None
