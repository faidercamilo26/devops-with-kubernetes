import signal
import sys
import time
import uuid
from datetime import datetime, timezone

RANDOM_STRING = str(uuid.uuid4())
INTERVAL_SECONDS = 5


def handle_sigterm(signum, frame):
    sys.exit(0)


def iso_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    while True:
        print(f"{iso_now()}: {RANDOM_STRING}", flush=True)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
