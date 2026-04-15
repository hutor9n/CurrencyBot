import unittest
from unittest.mock import MagicMock, patch

from models import fiat_api


class FiatApiTests(unittest.TestCase):
    def test_convert_currency_uses_cached_rate(self):
        with patch("models.fiat_api.get_cached_rate", return_value=2.5), patch(
            "models.fiat_api.requests.get"
        ) as mocked_get:
            result = fiat_api.convert_currency("USD", "EUR", 4)
            self.assertEqual(result, 10.0)
            mocked_get.assert_not_called()

    def test_make_request_rotates_key_and_succeeds(self):
        first_response = MagicMock()
        first_response.raise_for_status.return_value = None
        first_response.json.return_value = {"success": False, "error": {"code": 101}}

        second_response = MagicMock()
        second_response.raise_for_status.return_value = None
        second_response.json.return_value = {"success": True, "currencies": {"USD": "US Dollar"}}

        with patch("models.fiat_api.get_api_keys", return_value=["k1", "k2"]), patch(
            "models.fiat_api.requests.get", side_effect=[first_response, second_response]
        ) as mocked_get:
            result = fiat_api._make_request("https://api.currencylayer.com/list?access_key={API_KEY}")
            self.assertIsNotNone(result)
            self.assertEqual(mocked_get.call_count, 2)
            self.assertIn("k1", mocked_get.call_args_list[0].args[0])
            self.assertIn("k2", mocked_get.call_args_list[1].args[0])

    def test_make_request_returns_none_when_no_keys(self):
        with patch("models.fiat_api.get_api_keys", return_value=[]), patch(
            "models.fiat_api.requests.get"
        ) as mocked_get:
            result = fiat_api._make_request("https://api.currencylayer.com/list?access_key={API_KEY}")
            self.assertIsNone(result)
            mocked_get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
