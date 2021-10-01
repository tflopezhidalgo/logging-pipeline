import json
from multiprocessing import Process, Value, Queue


def get_queue(app_id):
    return 0


class Router(Process):
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

    def run(self):
        self._alive.value = True

        while self._alive.value:
            try:
                connection = self._pending_q.get(timeout=1)
                operation = self._handle_connection(connection)
                print(f"router got {operation}")

                self._dispatch_q[get_queue(operation["app_id"])].put(
                    (connection, operation)
                )
            except Exception:
                pass

    def stop(self):
        self._alive.value = False
