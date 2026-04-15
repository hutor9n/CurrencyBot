import os
import tempfile
import unittest
from unittest.mock import patch

from models import cache_manager


class CacheManagerTests(unittest.TestCase):
    def test_save_and_load_cache_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "cache.json")
            payload = {
                "list": {"updated_at": 1, "currencies": {"USD": "US Dollar"}},
                "rates": {"USD_UAH": {"updated_at": 1, "rate": 40.0}},
            }
            with patch.object(cache_manager, "CACHE_FILE", cache_file):
                cache_manager.save_cache(payload)
                loaded = cache_manager.load_cache()
                self.assertEqual(loaded, payload)

    def test_get_cached_rate_returns_none_when_expired(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = os.path.join(tmpdir, "cache.json")
            expired_payload = {
                "list": {},
                "rates": {
                    "USD_UAH": {
                        "updated_at": 1,
                        "rate": 40.0,
                    }
                },
            }
            with patch.object(cache_manager, "CACHE_FILE", cache_file):
                cache_manager.save_cache(expired_payload)
                with patch("models.cache_manager.time.time", return_value=1 + cache_manager.RATE_TTL + 1):
                    self.assertIsNone(cache_manager.get_cached_rate("USD", "UAH"))


if __name__ == "__main__":
    unittest.main()
