import os
import logging
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        logging.debug("keep_alive: " + format % args)

def _run_keep_alive_server():
    try:
        port = int(os.environ.get('PORT', 8080))
        server = HTTPServer(('0.0.0.0', port), SimpleHandler)
        logging.info(f"Сервер keep-alive запущен на порту {port}")
        server.serve_forever()
    except Exception as e:
        logging.error(f"Ошибка сервера keep-alive: {e}")

def start_keep_alive() -> Thread:
    t = Thread(target=_run_keep_alive_server, name="keep_alive_server")
    t.daemon = True
    t.start()
    logging.info("Поток keep-alive успешно запущен")
    return t