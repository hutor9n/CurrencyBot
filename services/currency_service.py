from models import fiat_api


def get_sorted_currencies():
    return fiat_api.get_sorted_currencies()


def normalize_currency_code(currency_code: str) -> str:
    return currency_code.strip().upper()


def normalize_amount(amount) -> float | None:
    try:
        normalized_amount = float(str(amount).replace(',', '.'))
    except (TypeError, ValueError):
        return None

    if normalized_amount <= 0:
        return None

    return normalized_amount


def convert_currency(from_currency: str, to_currency: str, amount) -> float | None:
    normalized_amount = normalize_amount(amount)
    if normalized_amount is None:
        return None

    normalized_from_currency = normalize_currency_code(from_currency)
    normalized_to_currency = normalize_currency_code(to_currency)
    return fiat_api.convert_currency(normalized_from_currency, normalized_to_currency, normalized_amount)


def convert_to_uah(currency_code: str, amount) -> float | None:
    return convert_currency(currency_code, 'UAH', amount)
