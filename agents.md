# Agents Guide For CurrencyBot

This file describes how AI agents should work in this repository.

## Goals

- Keep changes small, focused, and behavior-preserving unless the task explicitly asks for a larger refactor.
- Preserve the current layering:
  - `controllers/` handles Telegram interaction.
  - `services/` handles application logic and validation.
  - `models/` handles API access and persistence.
  - `views/` handles user-facing text and keyboards.

## Working Rules

- Prefer `unittest` for verification. Use `python -m unittest ...` unless the project adds another test runner.
- Before editing, read the relevant files and understand the current call flow.
- Use `apply_patch` for file edits.
- Do not introduce destructive git commands.
- Do not add new dependencies unless they are clearly needed.
- Keep controller code thin. Move repeated or cross-cutting logic into `controllers/common.py`, `services/`, or `views/`.
- Keep user-facing strings in `views/messages.py` where practical.

## Current Architecture Summary

- `main.py` initializes logging, creates the bot, registers controllers, starts keep-alive, and begins polling.
- `core/config.py` loads environment variables and creates the bot instance.
- `core/logger.py` configures the root logger explicitly.
- `core/keep_alive.py` provides the HTTP keep-alive server entry point.
- `services/currency_service.py` normalizes currency codes and amounts before delegating to `models/fiat_api.py`.
- `models/fiat_api.py` handles currencylayer requests, API key rotation, and cache interaction.
- `models/cache_manager.py` persists cached data to `data/cache.json`.
- `controllers/common.py` contains shared controller helpers.

## Change Strategy

- When adding a new Telegram flow, first decide whether the code belongs in a controller, a service, or a view helper.
- If the same edit/response logic appears twice, extract a helper rather than duplicating it.
- If a change affects behavior, add or update a unit test in `tests/`.

## Verification Checklist

- Run the relevant unit tests.
- Check for syntax or import errors in edited files.
- Confirm the bot still starts with `python main.py`.

## Style Notes

- Keep functions short and explicit.
- Prefer clear names over clever abstractions.
- Preserve the existing simple, procedural style unless there is a strong reason to refactor further.
# Agents Guide For CurrencyBot

This file describes how AI agents should work in this repository.

## Goals

- Keep changes small, focused, and behavior-preserving unless the task explicitly asks for a larger refactor.
- Preserve the current layering:
  - `controllers/` handles Telegram interaction.
  - `services/` handles application logic and validation.
  - `models/` handles API access and persistence.
  - `views/` handles user-facing text and keyboards.

## Working Rules

- Prefer `unittest` for verification. Use `python -m unittest ...` unless the project adds another test runner.
- Before editing, read the relevant files and understand the current call flow.
- Use `apply_patch` for file edits.
- Do not introduce destructive git commands.
- Do not add new dependencies unless they are clearly needed.
- Keep controller code thin. Move repeated or cross-cutting logic into `controllers/common.py`, `services/`, or `views/`.
- Keep user-facing strings in `views/messages.py` where practical.

## Current Architecture Summary

- `main.py` initializes logging, creates the bot, registers controllers, starts keep-alive, and begins polling.
- `core/config.py` loads environment variables and creates the bot instance.
- `core/logger.py` configures the root logger explicitly.
- `core/keep_alive.py` provides the HTTP keep-alive server entry point.
- `services/currency_service.py` normalizes currency codes and amounts before delegating to `models/fiat_api.py`.
- `models/fiat_api.py` handles currencylayer requests, API key rotation, and cache interaction.
- `models/cache_manager.py` persists cached data to `data/cache.json`.
- `controllers/common.py` contains shared controller helpers.

## Change Strategy

- When adding a new Telegram flow, first decide whether the code belongs in a controller, a service, or a view helper.
- If the same edit/response logic appears twice, extract a helper rather than duplicating it.
- If a change affects behavior, add or update a unit test in `tests/`.

## Verification Checklist

- Run the relevant unit tests.
- Check for syntax or import errors in edited files.
- Confirm the bot still starts with `python main.py`.

## Style Notes

- Keep functions short and explicit.
- Prefer clear names over clever abstractions.
- Preserve the existing simple, procedural style unless there is a strong reason to refactor further.
