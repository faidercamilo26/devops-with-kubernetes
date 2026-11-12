import signal
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 3000
counter = 0


def handle_sigterm(signum, frame):
    sys.exit(0)


class Handler(BaseHTTPRequestHandler):
    def send_text(self, text):
        body = f"{text}\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        global counter
        if self.path == "/pingpong":
            text = f"pong {counter}"
            counter += 1
            self.send_text(text)
        elif self.path == "/pings":
            self.send_text(counter)
        else:
            self.send_error(404)


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
