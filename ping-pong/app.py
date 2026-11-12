import os
import signal
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 3000
FILE = "/usr/src/app/files/pingpong.txt"
TMP_FILE = FILE + ".tmp"
counter = 0


def handle_sigterm(signum, frame):
    sys.exit(0)


def save_requests(count):
    with open(TMP_FILE, "w") as f:
        f.write(str(count))
    os.replace(TMP_FILE, FILE)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global counter
        if self.path != "/pingpong":
            self.send_error(404)
            return
        body = f"pong {counter}\n".encode()
        counter += 1
        save_requests(counter)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
