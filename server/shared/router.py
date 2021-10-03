import os
import json
from multiprocessing import Value, Queue, Pool, Process, Manager

WORKERS = int(os.environ.get('WORKERS', 3))
CONCURRENCY = int(os.environ.get('CONC', '1'))


def get_queue(app_id):
    return hash(app_id) % CONCURRENCY


def handle_connection(sock):
    done = False
    buf = ""

    while not done:
        c = sock.recv(1)
        c = c.decode()
        if c != "/":
            buf += c
        else:
            done = True

    msg = sock.recv(int(buf))
    return json.loads(msg.decode())


def run(pending_q, dispatch_queues, alive):
    alive.value = True

    while True:
        connection = pending_q.get()
        if connection is None:
            break

        operation = handle_connection(connection)
        print(f"[ROUTER][{os.getpid()}] got message from {operation['app_id']}")

        q = get_queue(operation["app_id"])

        dispatch_queues[q].put((connection, operation))


class Router:
    def __init__(self, pending_queue: Queue, dispatch_queues: list[Queue]):
        self._alive = Value("b", False)
        self._pending_q = pending_queue
        self._dispatch_q = dispatch_queues

    def start(self):
        self._pool = [Process(target=run, args=(self._pending_q, self._dispatch_q, self._alive)) for _ in range(WORKERS)]
        for p in self._pool:
            p.start()

    def join(self):
        for p in self._pool:
            p.join()

    def stop(self):
        # self._alive.value = False
        for i in range(WORKERS):
            self._pending_q.put(None)
