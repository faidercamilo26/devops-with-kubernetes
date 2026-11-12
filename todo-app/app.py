import os
import signal
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "3000"))
IMAGE_URL = "https://picsum.photos/1200"
IMAGE_FILE = "/usr/src/app/files/image.jpg"
TMP_FILE = IMAGE_FILE + ".tmp"
CACHE_SECONDS = 600

HTML = b"""<!DOCTYPE html>
<html>
<head><title>Todo app</title></head>
<body>
<h1>Todo app</h1>
<img src="/image" alt="Random image" style="max-width:100%">
</body>
</html>
"""

fetch_lock = threading.Lock()


def download_image():
    request = urllib.request.Request(IMAGE_URL, headers={"User-Agent": "todo-app"})
    with urllib.request.urlopen(request, timeout=15) as response:
        data = response.read()
    # Write to a temp file and rename, so a crash mid-download never leaves a broken image.
    with open(TMP_FILE, "wb") as f:
        f.write(data)
    os.replace(TMP_FILE, IMAGE_FILE)


def refresh_in_background():
    if not fetch_lock.acquire(blocking=False):
        return

    def run():
        try:
            download_image()
        except Exception as e:
            print(f"Image refresh failed: {e}", flush=True)
        finally:
            fetch_lock.release()

    threading.Thread(target=run, daemon=True).start()


def get_image():
    """Return the cached image bytes, fetching a first one if none exists.

    When the cached image is older than CACHE_SECONDS it is served one more time
    and a new one is fetched, so the next request gets the new image.
    """
    if not os.path.exists(IMAGE_FILE):
        with fetch_lock:
            if not os.path.exists(IMAGE_FILE):
                download_image()
    with open(IMAGE_FILE, "rb") as f:
        data = f.read()
    if time.time() - os.path.getmtime(IMAGE_FILE) >= CACHE_SECONDS:
        refresh_in_background()
    return data


class Handler(BaseHTTPRequestHandler):
    def send_body(self, status, content_type, body, extra_headers=()):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in extra_headers:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.send_body(200, "text/html; charset=utf-8", HTML)
        elif self.path == "/image":
            try:
                data = get_image()
            except Exception as e:
                print(f"Image fetch failed: {e}", flush=True)
                self.send_error(502)
                return
            self.send_body(200, "image/jpeg", data, [("Cache-Control", "no-store")])
        else:
            self.send_error(404)


def handle_sigterm(signum, frame):
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server started in port {PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
