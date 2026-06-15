import multiprocessing

from src.common import logging


class _Responder(multiprocessing.Process):

    SENTINEL = (None, None)
    NAME = 'responder'

    def __init__(self, incoming_queue):
        super().__init__(name=self.NAME)

        self._incoming_q = incoming_queue

    def run(self):
        while True:
            conn_result = self._incoming_q.get()

            if conn_result == self.SENTINEL:
                break  # noqa

            (sock, result) = conn_result
            logging.info(f"Responding to {sock.getpeername()}")

            if not sock.send_msg({"result": result}):
                logging.info(
                    f"Failed to send result to client {sock.getpeername()}"
                )
            sock.close()

    def stop(self):
        logging.info('Stopping worker: %s' % self.NAME)

        self._incoming_q.put(self.SENTINEL)
        self.join()


class RespondersPool:
    def __init__(self, size, incoming_q):
        self._pool = [_Responder(incoming_q) for _ in range(size)]

    def start(self):
        for router in self._pool:
            router.start()

    def join(self):
        for router in self._pool:
            router.join()

    def stop(self):
        for router in self._pool:
            router.stop()
