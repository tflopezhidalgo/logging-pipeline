import os
import json
from multiprocessing import Value, Queue, Pool

WORKERS = int(os.environ.get('WORKERS', 3))
CONCURRENCY = int(os.environ.get('CONC', '1'))


def get_queue(app_id):
    return hash(app_id) % CONCURRENCY

class Router:
    def __init__(self, pending_queue: Queue, dispatch_queues: list[Queue]):
        super().__init__()

        self._alive = Value("b", False)
        self._pending_q = pending_queue
        self._dispatch_q = dispatch_queues

    def _handle_connection(self, sock) -> dict:
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

    def start(self):
        self._pool = Pool(WORKERS, self.run)

    def run(self):
        self._alive.value = True

        while self._alive.value:
            connection = self._pending_q.get()
            if connection is None:
                break

            operation = self._handle_connection(connection)
            print(f"router {os.getpid()} got {operation}")

            q = get_queue(operation["app_id"])

            print("Dispatching to %s" % q)

            self._dispatch_q[q].put((connection, operation))

    def stop(self):
        self._alive.value = False
        for i in range(WORKERS):
            self._pending_q.put(None)
        self._pool.close()
        self._pool.join()
