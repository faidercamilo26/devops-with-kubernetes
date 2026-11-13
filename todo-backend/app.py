import json
import os
import re
import signal
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pg8000.native

PORT = int(os.environ["PORT"])
MAX_TODO_LENGTH = int(os.environ["MAX_TODO_LENGTH"])
DB_SETTINGS = {
    "host": os.environ["DB_HOST"],
    "port": int(os.environ["DB_PORT"]),
    "database": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "timeout": 3,
}


def connect():
    return pg8000.native.Connection(**DB_SETTINGS)


def init_db():
    while True:
        try:
            conn = connect()
            try:
                conn.run("CREATE TABLE IF NOT EXISTS todos (id serial PRIMARY KEY, todo text NOT NULL)")
                conn.run("ALTER TABLE todos ADD COLUMN IF NOT EXISTS done boolean NOT NULL DEFAULT false")
            finally:
                conn.close()
            return
        except Exception as e:
            print(f"Waiting for the database: {e}", flush=True)
            time.sleep(2)


def check_database():
    conn = connect()
    try:
        conn.run("SELECT 1")
    finally:
        conn.close()


def to_dict(row):
    return {"id": row[0], "todo": row[1], "done": row[2]}


def get_todos():
    conn = connect()
    try:
        return [to_dict(row) for row in conn.run("SELECT id, todo, done FROM todos ORDER BY id")]
    finally:
        conn.close()


def add_todo(todo):
    conn = connect()
    try:
        row = conn.run("INSERT INTO todos (todo) VALUES (:todo) RETURNING id, todo, done", todo=todo)[0]
        return to_dict(row)
    finally:
        conn.close()


def set_done(todo_id, done):
    """Return the updated todo, or None if there is no todo with that id."""
    conn = connect()
    try:
        rows = conn.run(
            "UPDATE todos SET done = :done WHERE id = :id RETURNING id, todo, done", done=done, id=todo_id
        )
        return to_dict(rows[0]) if rows else None
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

    def log_message(self, format, *args):
        # Probes call /healthz every few seconds; keep them out of the log.
        if self.path != "/healthz":
            super().log_message(format, *args)

    def do_GET(self):
        if self.path == "/healthz":
            try:
                check_database()
            except Exception as e:
                print(f"Database not available: {e}", flush=True)
                self.send_error(500)
                return
            self.send_json(200, {"status": "ok"})
            return
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
            print("Todo rejected: invalid request", flush=True)
            self.send_error(400)
            return
        if len(todo) > MAX_TODO_LENGTH:
            print(
                f'Todo rejected: too long ({len(todo)} characters, max {MAX_TODO_LENGTH}): "{todo[:50]}..."',
                flush=True,
            )
            self.send_error(400, f"Todo must be at most {MAX_TODO_LENGTH} characters")
            return
        try:
            created = add_todo(todo)
        except Exception as e:
            print(f"Database error: {e}", flush=True)
            self.send_error(500)
            return
        print(f'Todo created: "{todo}"', flush=True)
        self.send_json(201, created)

    def do_PUT(self):
        match = re.fullmatch(r"/todos/(\d+)", self.path)
        if not match:
            self.send_error(404)
            return
        todo_id = int(match.group(1))
        try:
            length = int(self.headers.get("Content-Length", "0"))
            done = json.loads(self.rfile.read(length))["done"]
            if not isinstance(done, bool):
                raise ValueError("done must be true or false")
        except (ValueError, KeyError, TypeError):
            print(f"Todo {todo_id} update rejected: invalid request", flush=True)
            self.send_error(400)
            return
        try:
            updated = set_done(todo_id, done)
        except Exception as e:
            print(f"Database error: {e}", flush=True)
            self.send_error(500)
            return
        if updated is None:
            print(f"Todo {todo_id} update rejected: not found", flush=True)
            self.send_error(404)
            return
        print(f'Todo {todo_id} marked as {"done" if done else "not done"}: "{updated["todo"]}"', flush=True)
        self.send_json(200, updated)


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
