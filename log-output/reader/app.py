import signal
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 3000
LOG_FILE = "/usr/src/app/files/log.txt"
PINGPONG_FILE = "/usr/src/app/pingpong/pingpong.txt"


def handle_sigterm(signum, frame):
    sys.exit(0)


def read_file(path, default):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return default


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        log = read_file(LOG_FILE, "")
        pongs = read_file(PINGPONG_FILE, "0").strip()
        body = f"{log}Ping / Pongs: {pongs}\n".encode()
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
