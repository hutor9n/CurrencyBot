import json
import os
import time
import logging
from threading import Lock

CACHE_FILE = 'data/cache.json'
RATE_TTL = 12 * 3600  # 12 годин у секундах
LIST_TTL = 7 * 24 * 3600  # 7 днів у секундах
_cache_lock = Lock()


def _ensure_cache_dir():
    cache_dir = os.path.dirname(CACHE_FILE)
    if cache_dir and not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

def load_cache():
    _ensure_cache_dir()
    if not os.path.exists(CACHE_FILE):
        return {"list": {}, "rates": {}}
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Не удалось прочитать кэш из {CACHE_FILE}: {e}")
        return {"list": {}, "rates": {}}

def save_cache(cache_data):
    _ensure_cache_dir()
    try:
        temp_file = f"{CACHE_FILE}.tmp"
        with _cache_lock:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=4)
            os.replace(temp_file, CACHE_FILE)
    except Exception as e:
        logging.error(f"Не удалось сохранить кэш в {CACHE_FILE}: {e}")

def get_cached_list():
    cache = load_cache()
    list_cache = cache.get("list", {})
    if not list_cache or 'updated_at' not in list_cache:
        return None
        
    if time.time() - list_cache['updated_at'] > LIST_TTL:
        return None
        
    return list_cache.get("currencies")

def cache_list(currencies_dict):
    cache = load_cache()
    cache["list"] = {
        "updated_at": time.time(),
        "currencies": currencies_dict
    }
    save_cache(cache)

def get_cached_rate(from_curr: str, to_curr: str):
    cache = load_cache()
    key = f"{from_curr}_{to_curr}"
    rate_cache = cache.get("rates", {}).get(key)
    
    if not rate_cache or 'updated_at' not in rate_cache:
        return None
        
    if time.time() - rate_cache['updated_at'] > RATE_TTL:
        return None
        
    return rate_cache.get("rate")

def cache_rate(from_curr: str, to_curr: str, rate: float):
    cache = load_cache()
    key = f"{from_curr}_{to_curr}"
    if "rates" not in cache:
        cache["rates"] = {}
        
    cache["rates"][key] = {
        "updated_at": time.time(),
        "rate": rate
    }
    save_cache(cache)
