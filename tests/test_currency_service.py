import unittest
from unittest.mock import patch

from services import currency_service


class CurrencyServiceTests(unittest.TestCase):
    def test_normalize_amount_returns_float_for_comma_decimal(self):
        self.assertEqual(currency_service.normalize_amount("10,5"), 10.5)

    def test_normalize_amount_rejects_non_positive_values(self):
        self.assertIsNone(currency_service.normalize_amount(0))
        self.assertIsNone(currency_service.normalize_amount(-1))

    def test_convert_currency_normalizes_inputs_before_delegating(self):
        with patch("services.currency_service.fiat_api.convert_currency", return_value=42.0) as mocked_convert:
            result = currency_service.convert_currency(" usd ", "uah", "2,5")

        self.assertEqual(result, 42.0)
        mocked_convert.assert_called_once_with("USD", "UAH", 2.5)

    def test_convert_currency_rejects_invalid_amounts(self):
        with patch("services.currency_service.fiat_api.convert_currency") as mocked_convert:
            result = currency_service.convert_currency("USD", "UAH", "abc")

        self.assertIsNone(result)
        mocked_convert.assert_not_called()


if __name__ == "__main__":
    unittest.main()