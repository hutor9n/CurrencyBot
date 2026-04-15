import requests
import json
import logging
from threading import Lock
from core.config import get_api_keys
from models.cache_manager import get_cached_list, cache_list, get_cached_rate, cache_rate

current_key_index = 0
FAVORITES = ["UAH", "USD", "EUR", "PLN", "GBP", "CZK"]
REQUEST_TIMEOUT_SECONDS = 10
_api_key_lock = Lock()


def _get_current_api_key(api_keys):
    with _api_key_lock:
        key_count = len(api_keys)
        if key_count == 0:
            return None, None
        safe_index = current_key_index % key_count
        return safe_index, api_keys[safe_index]


def _move_to_next_api_key(key_count):
    global current_key_index
    with _api_key_lock:
        current_key_index = (current_key_index + 1) % key_count
        return current_key_index

def _make_request(endpoint_url: str):
    api_keys = get_api_keys(required=False)
    if not api_keys:
        logging.error("API_KEYS не настроены: добавьте API_KEYS в .env")
        return None

    for _ in range(len(api_keys)):
        key_index, current_api_key = _get_current_api_key(api_keys)
        url = endpoint_url.replace('{API_KEY}', current_api_key)
        try:
            res = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            res.raise_for_status()
            data = res.json()
            if data.get('success', False):
                return data
            error_code = data.get('error', {}).get('code')
            if error_code in (101, 104):
                next_index = _move_to_next_api_key(len(api_keys))
                logging.warning(
                    f"API-ключ с индексом {key_index} недействителен/исчерпан (код {error_code}). Переключаемся на индекс {next_index}."
                )
            else:
                logging.error(f"Ошибка API currencylayer: {data.get('error')}")
                return None
        except requests.Timeout:
            logging.error("Таймаут при обращении к currencylayer API")
            return None
        except requests.RequestException as e:
            logging.error(f"HTTP ошибка при обращении к currencylayer API: {e}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Некорректный JSON в ответе currencylayer API: {e}")
            return None
        except Exception as e:
            logging.error(f"Критическая ошибка запроса к currencylayer API: {e}")
            return None
    logging.error("Все API-ключи недействительны или исчерпаны")
    return None

def get_currency_list():
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
