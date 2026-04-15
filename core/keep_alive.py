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


def run_server():
    try:
        port = int(os.environ.get('PORT', 8080))
        server = HTTPServer(('0.0.0.0', port), SimpleHandler)
        logging.info(f"Сервер keep-alive запущен на порту {port}")
        server.serve_forever()
    except Exception as e:
        logging.error(f"Ошибка сервера keep-alive: {e}")


def keep_alive():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()
    return t