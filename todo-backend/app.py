import json
import os
import signal
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pg8000.native

PORT = int(os.environ["PORT"])
DB_SETTINGS = {
    "host": os.environ["DB_HOST"],
    "port": int(os.environ["DB_PORT"]),
    "database": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
}


def connect():
    return pg8000.native.Connection(**DB_SETTINGS)


def init_db():
    while True:
        try:
            conn = connect()
            try:
                conn.run("CREATE TABLE IF NOT EXISTS todos (id serial PRIMARY KEY, todo text NOT NULL)")
            finally:
                conn.close()
            return
        except Exception as e:
            print(f"Waiting for the database: {e}", flush=True)
            time.sleep(2)


def get_todos():
    conn = connect()
    try:
        return [row[0] for row in conn.run("SELECT todo FROM todos ORDER BY id")]
    finally:
        conn.close()


def add_todo(todo):
    conn = connect()
    try:
        conn.run("INSERT INTO todos (todo) VALUES (:todo)", todo=todo)
    finally:
        conn.close()


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/todos":
            self.send_error(404)
            return
        try:
            self.send_json(200, get_todos())
        except Exception as e:
            print(f"Database error: {e}", flush=True)
            self.send_error(500)

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
        try:
            add_todo(todo)
        except Exception as e:
            print(f"Database error: {e}", flush=True)
            self.send_error(500)
            return
        self.send_json(201, {"todo": todo})


def handle_sigterm(signum, frame):
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    init_db()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server started in port {PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
