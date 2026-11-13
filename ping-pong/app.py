import os
import signal
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pg8000.native

PORT = 3000
DB_SETTINGS = {
    "host": os.environ["DB_HOST"],
    "port": int(os.environ["DB_PORT"]),
    "database": os.environ["DB_NAME"],
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "timeout": 3,
}

# Set once the table exists, which needs the database to be reachable.
initialized = threading.Event()


def handle_sigterm(signum, frame):
    sys.exit(0)


def connect():
    return pg8000.native.Connection(**DB_SETTINGS)


def init_db():
    while True:
        try:
            conn = connect()
            try:
                conn.run("CREATE TABLE IF NOT EXISTS pongs (id integer PRIMARY KEY, count integer NOT NULL)")
                conn.run("INSERT INTO pongs (id, count) VALUES (1, 0) ON CONFLICT (id) DO NOTHING")
            finally:
                conn.close()
            initialized.set()
            return
        except Exception as e:
            print(f"Waiting for the database: {e}", flush=True)
            time.sleep(2)


def database_is_available():
    if not initialized.is_set():
        return False
    try:
        conn = connect()
        try:
            conn.run("SELECT 1")
        finally:
            conn.close()
        return True
    except Exception as e:
        print(f"Database not available: {e}", flush=True)
        return False


def next_pong():
    conn = connect()
    try:
        # RETURNING gives the new value, so subtract 1 to answer with the previous count.
        return conn.run("UPDATE pongs SET count = count + 1 WHERE id = 1 RETURNING count - 1")[0][0]
    finally:
        conn.close()


def get_pings():
    conn = connect()
    try:
        return conn.run("SELECT count FROM pongs WHERE id = 1")[0][0]
    finally:
        conn.close()


class Handler(BaseHTTPRequestHandler):
    def send_text(self, text, status=200):
        body = f"{text}\n".encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            if database_is_available():
                self.send_text("ok")
            else:
                self.send_text("database not available", 500)
            return
        if self.path not in ("/", "/pings"):
            self.send_error(404)
            return
        try:
            if self.path == "/":
                self.send_text(f"pong {next_pong()}")
            else:
                self.send_text(get_pings())
        except Exception as e:
            print(f"Database error: {e}", flush=True)
            self.send_error(500)

    def log_message(self, format, *args):
        # Probes call /healthz every few seconds; keep them out of the log.
        if self.path != "/healthz":
            super().log_message(format, *args)


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    threading.Thread(target=init_db, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
