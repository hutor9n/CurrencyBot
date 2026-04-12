import json
import os
import time
import threading
import logging

CACHE_FILE = 'data/cache.json'
RATE_TTL = 12 * 3600  # 12 годин у секундах
LIST_TTL = 7 * 24 * 3600  # 7 днів у секундах

cache_lock = threading.Lock()

def _ensure_data_dir():
    if not os.path.exists('data'):
        os.makedirs('data')

def load_cache():
    _ensure_data_dir()
    if not os.path.exists(CACHE_FILE):
        return {"list": {}, "rates": {}}
    try:
        with cache_lock:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Помилка читання кешу: {e}")
        return {"list": {}, "rates": {}}

def save_cache(cache_data):
    _ensure_data_dir()
    try:
        with cache_lock:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Помилка запису кешу: {e}")

def _is_cache_valid(cache_entry, ttl):
    if not cache_entry or 'updated_at' not in cache_entry:
        return False
    return (time.time() - cache_entry['updated_at']) <= ttl

def get_cached_list():
    cache = load_cache()
    list_cache = cache.get("list", {})
    if _is_cache_valid(list_cache, LIST_TTL):
        return list_cache.get("currencies")
    return None

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
    if _is_cache_valid(rate_cache, RATE_TTL):
        return rate_cache.get("rate")
    return None

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
