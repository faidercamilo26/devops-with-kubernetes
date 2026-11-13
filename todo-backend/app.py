import json
import os
import signal
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ["PORT"])
todos = []


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/todos":
            self.send_json(200, todos)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/todos":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            todo = json.loads(self.rfile.read(length))["todo"]
            if not isinstance(todo, str) or not todo:
                raise ValueError("todo must be a non-empty string")
        except (ValueError, KeyError, TypeError):
            self.send_error(400)
            return
        todos.append(todo)
        self.send_json(201, {"todo": todo})


def handle_sigterm(signum, frame):
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server started in port {PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
