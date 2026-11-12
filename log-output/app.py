import signal
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

RANDOM_STRING = str(uuid.uuid4())
INTERVAL_SECONDS = 5
PORT = 3000


def handle_sigterm(signum, frame):
    sys.exit(0)


def iso_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def status():
    return f"{iso_now()}: {RANDOM_STRING}"


def log_loop():
    while True:
        print(status(), flush=True)
        time.sleep(INTERVAL_SECONDS)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = f"{status()}\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    threading.Thread(target=log_loop, daemon=True).start()
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
