import os
import datetime

from multiprocessing import Queue, Process

from utils import recv_msg, logging


def sanitize_data(data):
    sanitized = {}

    if data.get("app_id"):
        sanitized["app_id"] = data.get("app_id")
    if data.get("from"):
        sanitized["from"] = datetime.datetime.fromisoformat(data.get("from"))
    if data.get("to"):
        sanitized["to"] = datetime.datetime.fromisoformat(data.get("to"))
    if data.get("tag"):
        sanitized["tag"] = data.get("tag")
    if data.get("pattern"):
        sanitized["pattern"] = data.get("app_id")
    if data.get("timestamp"):
        sanitized["timestamp"] = datetime.datetime.fromisoformat(
            data.get("timestamp")
        )
    if data.get("tags"):
        sanitized["tags"] = data.get("tags")

    return sanitized


class _Router(Process):

    SENTINEL = None

    def __init__(self, pending_q, dispatch_qs):
        super().__init__()

        self._pending_q = pending_q
        self._dispatch_qs = dispatch_qs

    def __handle_conn(self, connection):
        data = recv_msg(connection)

        logging.info(
            f"[ROUTER][{os.getpid()}] got message from {data['app_id']}"
        )

        return sanitize_data(data)

    def __compute_dispatch_queue_index(self, app_id):
        return hash(app_id) % len(self._dispatch_qs)

    def run(self):
        while True:
            connection = self._pending_q.get()
            if connection is self.SENTINEL:
                break

            operation = self.__handle_conn(connection)

            q_index = self.__compute_dispatch_queue_index(operation["app_id"])

            self._dispatch_qs[q_index].put((connection, operation))

    def stop(self):
        self._pending_q.put(self.SENTINEL)


class RouterPool:
    def __init__(
        self, size, pending_queue: Queue, dispatch_queues: list[Queue]
    ):
        self._pool = [
            _Router(pending_queue, dispatch_queues) for _ in range(size)
        ]

    def start(self):
        for router in self._pool:
            router.start()

    def join(self):
        for router in self._pool:
            router.join()

    def stop(self):
        for router in self._pool:
            router.stop()
