import signal
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 3000
FILE = "/usr/src/app/files/log.txt"


def handle_sigterm(signum, frame):
    sys.exit(0)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with open(FILE) as f:
                content = f.read()
        except FileNotFoundError:
            content = ""
        body = content.encode()
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
