import os
import signal
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 3000
LOG_FILE = "/usr/src/app/files/log.txt"
INFORMATION_FILE = "/usr/src/app/config/information.txt"
PINGPONG_URL = "http://ping-pong-svc:2346/pings"
MESSAGE = os.environ["MESSAGE"]


def handle_sigterm(signum, frame):
    sys.exit(0)


def read_log():
    try:
        with open(LOG_FILE) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def read_information():
    with open(INFORMATION_FILE) as f:
        return f.read().strip()


def read_pongs():
    with urllib.request.urlopen(PINGPONG_URL, timeout=5) as response:
        return response.read().decode().strip()


class Handler(BaseHTTPRequestHandler):
    def send_status(self, text, status):
        body = f"{text}\n".encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            try:
                read_pongs()
            except Exception as e:
                print(f"Ping-pong not available: {e}", flush=True)
                self.send_status("ping-pong not available", 500)
                return
            self.send_status("ok", 200)
            return
        try:
            pongs = read_pongs()
        except Exception as e:
            print(f"Could not get pongs: {e}", flush=True)
            self.send_error(502)
            return
        body = (
            f"file content: {read_information()}\n"
            f"env variable: MESSAGE={MESSAGE}\n"
            f"{read_log()}Ping / Pongs: {pongs}\n"
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
