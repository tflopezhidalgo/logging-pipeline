from multiprocessing import Process

from utils import logging


class Responser(Process):

    SENTINEL = (None, None)

    def __init__(self, incoming_queue):
        super().__init__()

        self._incoming_q = incoming_queue

    def run(self):
        while True:
            popped = self._incoming_q.get()

            if popped == self.SENTINEL:
                break

            (sock, result) = popped

            result = str(result)

            result = {"result": result}

            logging.info(f"[RESPONSER] Responding to {sock.getpeername()}")

            msg = f"{len(result)}/{result}"
            sock.sendall(msg.encode("utf8"))

            sock.close()

    def stop(self):
        self._incoming_q.put(self.SENTINEL)
        self.join()
