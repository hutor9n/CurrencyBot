import os
import json
import logging
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from telebot.types import Update


class BotRequestHandler(BaseHTTPRequestHandler):
    bot = None

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def do_POST(self):
        if self.bot is None:
            self.send_response(503)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', '0'))
        payload = self.rfile.read(content_length)

        try:
            update = Update.de_json(json.loads(payload.decode('utf-8')))
            self.bot.process_new_updates([update])
        except Exception as e:
            logging.error(f"Ошибка обработки webhook-update: {e}")
            self.send_response(500)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        logging.debug("keep_alive: " + format % args)

def _run_keep_alive_server(bot=None):
    try:
        port = int(os.environ.get('PORT', 8080))
        BotRequestHandler.bot = bot
        server = HTTPServer(('0.0.0.0', port), BotRequestHandler)
        logging.info(f"Сервер keep-alive запущен на порту {port}")
        server.serve_forever()
    except Exception as e:
        logging.error(f"Ошибка сервера keep-alive: {e}")

def start_keep_alive(bot=None) -> Thread:
    t = Thread(target=_run_keep_alive_server, args=(bot,), name="keep_alive_server")
    t.daemon = True
    t.start()
    logging.info("Поток keep-alive успешно запущен")
    return t


def build_webhook_url() -> str | None:
    webhook_url = os.environ.get('WEBHOOK_URL')
    if webhook_url:
        return webhook_url.rstrip('/')

    render_external_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_external_url:
        return f"{render_external_url.rstrip('/')}/webhook"

    return None