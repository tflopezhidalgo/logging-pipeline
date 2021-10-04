from multiprocessing import Process

from utils import send_msg


class Responser(Process):

    SENTINEL = (None, None)

    def __init__(self, incoming_queue):
        super().__init__()
        self._incoming_q = incoming_queue

    def run(self):
        while True:
            pack = self._incoming_q.get()

            if pack == self.SENTINEL:
                break  # noqa

            (sock, result) = pack

            send_msg(sock, {"result": result})

            sock.close()

    def stop(self):
        self._incoming_q.put(self.SENTINEL)
        self.join()
