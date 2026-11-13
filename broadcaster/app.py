import asyncio
import json
import os
import signal
import urllib.request

import nats

NATS_URL = os.environ["NATS_URL"]
NATS_SUBJECT = os.environ["NATS_SUBJECT"]
NATS_QUEUE = os.environ["NATS_QUEUE"]
# Without a webhook (as in staging) the messages are only logged, never forwarded.
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")


def describe(event):
    todo = event["todo"]
    if event["event"] == "created":
        return f'A todo was created: "{todo["todo"]}"'
    state = "done" if todo["done"] else "not done"
    return f'A todo was marked as {state}: "{todo["todo"]}"'


def send(message):
    body = json.dumps({"user": "bot", "message": message}).encode()
    request = urllib.request.Request(
        WEBHOOK_URL, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(request, timeout=5):
        pass


async def on_message(msg):
    try:
        message = describe(json.loads(msg.data))
    except Exception as e:
        print(f"Ignoring a message that could not be read: {e}", flush=True)
        return
    if not WEBHOOK_URL:
        print(f"Not forwarded, no webhook configured: {message}", flush=True)
        return
    # A message that fails to be delivered is dropped on purpose: a missing message is
    # acceptable, a duplicated one is not, so there is no retry.
    try:
        await asyncio.to_thread(send, message)
        print(f"Forwarded: {message}", flush=True)
    except Exception as e:
        print(f"Could not forward the message, dropped: {e}", flush=True)


async def main():
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, stop.set)

    while True:
        try:
            nc = await nats.connect(NATS_URL, max_reconnect_attempts=-1, connect_timeout=2)
            break
        except Exception as e:
            print(f"Waiting for NATS: {e}", flush=True)
            await asyncio.sleep(2)
    print(f"Connected to NATS, subscribed to {NATS_SUBJECT} in queue group {NATS_QUEUE}", flush=True)
    await nc.subscribe(NATS_SUBJECT, queue=NATS_QUEUE, cb=on_message)

    await stop.wait()
    await nc.drain()


if __name__ == "__main__":
    asyncio.run(main())
