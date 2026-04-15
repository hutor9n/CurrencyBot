# CurrencyBot

Telegram bot for viewing and converting fiat currency rates against UAH. The project uses `pyTelegramBotAPI`, a lightweight JSON cache, and the `currencylayer` API.

## What It Does

- Shows quick currency rates against UAH.
- Opens a paginated list of available currencies.
- Supports interactive currency conversion with inline keyboards.
- Caches currency lists and exchange rates to reduce external API calls.
- Exposes a small keep-alive HTTP server for hosted environments.

## Project Structure

```text
main.py
controllers/
core/
models/
services/
views/
tests/
data/
logs/
```

- `main.py` is the application entry point.
- `core/` contains configuration, logging, and keep-alive infrastructure.
- `controllers/` contains Telegram handlers and callback flows.
- `services/` contains application-level currency logic and validation.
- `models/` contains API integration and JSON cache persistence.
- `views/` contains user-facing messages, keyboards, and localization helpers.
- `tests/` contains unit tests for cache, API, service, and controller helpers.

## Requirements

- Python 3.13 or newer
- Telegram bot token
- Currencylayer API keys

## Environment Variables

Create a `.env` file in the project root with:

```env
BOT_TOKEN=your_telegram_bot_token
API_KEYS=key1,key2,key3
```

- `BOT_TOKEN` is required.
- `API_KEYS` is required for currencylayer requests.


## Local Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Bot

```bash
python main.py
```

The bot will:

- initialize logging,
- create the Telegram bot instance,
- register controllers,
- start the keep-alive server,
- clear any existing webhook,
- start long polling to receive Telegram updates.

## Tests

Run the unit tests with:

```bash
python -m unittest tests.test_cache_manager tests.test_fiat_api tests.test_currency_service tests.test_controller_common
```

## Docker

Build and run with Docker if you prefer a containerized deployment.

```bash
docker build -t currencybot .
docker run --rm --env-file .env -p 8080:8080 currencybot
```

## Runtime Behavior

- Logging is written to `logs/bot.log` and also printed to the console.
- Currency lists and rates are cached in `data/cache.json`.
- Cache writes are protected to avoid losing updates between list and rate refreshes.
- Inline menus are closed after selection where the UX expects it.

## Notes For Contributors

- Keep controllers focused on Telegram interaction.
- Put shared validation and currency logic in `services/`.
- Keep API and cache code in `models/`.
- Prefer adding small helpers in `controllers/common.py` or `views/messages.py` instead of duplicating logic.
- Preserve the existing unittest-based verification flow when making changes.
