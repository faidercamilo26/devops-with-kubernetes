import os
import signal
import sys
import time
import uuid
from datetime import datetime, timezone

RANDOM_STRING = str(uuid.uuid4())
FILE = "/usr/src/app/files/log.txt"
TMP_FILE = FILE + ".tmp"
INTERVAL_SECONDS = 5


def handle_sigterm(signum, frame):
    sys.exit(0)


def iso_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    while True:
        with open(TMP_FILE, "w") as f:
            f.write(f"{iso_now()}: {RANDOM_STRING}\n")
        os.replace(TMP_FILE, FILE)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
