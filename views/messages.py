from views.translations import get_ru_name

def get_start_text() -> str:
    return (
        "Привет. Я помощник для отслеживания курсов валют 👋\n\n"
        "Выберите нужную функцию в меню ниже или через кнопку Menu."
    )

def get_rates_menu_text() -> str:
    return '💱 Выберите валюту для просмотра курса к гривне (UAH):'


def get_currency_list_unavailable_text() -> str:
    return 'Не удалось получить список валют. Попробуйте позже.'


def get_currency_list_temp_unavailable_text() -> str:
    return 'Список валют временно недоступен.'


def get_currency_rate_unavailable_text() -> str:
    return 'Произошла ошибка при получении курса. Попробуйте позже.'


def get_convert_unavailable_text() -> str:
    return 'Сервис временно недоступен.'


def get_convert_cancelled_text() -> str:
    return 'Операция конвертации отменена.'


def get_convert_invalid_amount_text() -> str:
    return 'Пожалуйста, введите корректное число (используйте точку или запятую).'


def get_convert_error_text() -> str:
    return 'Произошла ошибка при расчете курса.'


def get_convert_unexpected_error_text() -> str:
    return 'Возникла непредвиденная ошибка.'

def get_list_page_text(items, page, items_per_page=15):
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    if total_pages == 0:
         return "Нет доступных валют.", 1
    if page > total_pages:
        page = total_pages
        
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_items = items[start_idx:end_idx]
    
    text = f"📘 <b>Доступные валюты (страница {page}/{total_pages})</b>\n\n"
    for code, original_name in page_items:
        ru_name = get_ru_name(code, original_name)
        text += f"<b>{code}</b> — {ru_name}\n"
        
    return text, total_pages

def get_convert_start_text() -> str:
    return '🔁 Выберите валюту <b>из</b>, которой переводим:'

def get_convert_to_text(from_code: str) -> str:
    return f"🔁 Вы выбрали <b>{from_code}</b>. Теперь выберите валюту <b>в</b>, которую переводим:"

def get_convert_amount_text(from_code: str, to_code: str) -> str:
    return f"🔁 Перевод <b>{from_code} -> {to_code}</b>.\nВведите сумму числом (например: 100):"

def get_convert_result_text(amount: float, from_code: str, to_code: str, result: float) -> str:
    return f'✅ Конвертация <b>{amount} {from_code} -> {to_code}</b>:\n<b>{result:.2f}</b>'
