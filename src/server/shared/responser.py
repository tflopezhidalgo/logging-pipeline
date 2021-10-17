from multiprocessing import Process

from src.common import logging


class _Responser(Process):

    SENTINEL = (None, None)

    def __init__(self, incoming_queue):
        super().__init__()

        self._incoming_q = incoming_queue

    def run(self):
        while True:
            conn_result = self._incoming_q.get()

            if conn_result == self.SENTINEL:
                break  # noqa

            (sock, result) = conn_result
            try:
                logging.info(
                    f"Responding to {sock.getpeername()} with {result}"
                )

                sock.send_msg({"result": result})

            except (Exception, OSError) as e:
                logging.info(f"Failed to send result to client {e}")

            finally:
                sock.close()

    def stop(self):
        self._incoming_q.put(self.SENTINEL)
        self.join()


class ResponserPool:
    def __init__(self, size, incoming_q):
        self._pool = [_Responser(incoming_q) for _ in range(size)]

    def start(self):
        for router in self._pool:
            router.start()

    def join(self):
        for router in self._pool:
            router.join()

    def stop(self):
        for router in self._pool:
            router.stop()
