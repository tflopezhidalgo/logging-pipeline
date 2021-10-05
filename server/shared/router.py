import os

from multiprocessing import Queue, Process

from utils import recv_msg, logging


class InvalidParams(RuntimeError):
    pass

class InvalidAppID(RuntimeError):
    pass


class Router(Process):

    SENTINEL = None

    def __init__(self, pending_q, dispatch_qs, fallback_queue):
        super().__init__()

        self._pending_q = pending_q
        self._dispatch_qs = dispatch_qs
        self._fallback_q = fallback_queue

    def _validate_params(self, data):
        raise NotImplementedError()

    def __ask_client_for_op(self, connection):
        return recv_msg(connection)

    def __compute_dispatch_queue_index(self, app_id):
        return hash(app_id) % len(self._dispatch_qs)

    def run(self):
        while True:
            connection = self._pending_q.get()
            if connection is self.SENTINEL:
                break

            operation_params = self.__ask_client_for_op(connection)

            logging.info(
                f"[ROUTER][{os.getpid()}] got message from {operation_params['app_id']}"
            )

            try:
                operation_params = self._validate_params(operation_params)
            except InvalidParams:
                self._fallback_q.put((connection, 'One of the params is invalid.'))
                continue

            except InvalidAppID:
                self._fallback_q.put((connection, "There're no logs for that app."))
                continue

            q_index = self.__compute_dispatch_queue_index(operation_params["app_id"])

            self._dispatch_qs[q_index].put((connection, operation_params))

    def stop(self):
        self._pending_q.put(self.SENTINEL)


class RouterPool:
    def __init__(
        self, size, pending_queue: Queue, dispatch_queues: list[Queue], fallback_queue, router_class
    ):
        self._pool = [
            router_class(pending_queue, dispatch_queues, fallback_queue) for _ in range(size)
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
