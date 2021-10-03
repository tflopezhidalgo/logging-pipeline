from multiprocessing import Process, Value

SENTINEL = (None, None)

class Responser(Process):
    def __init__(self, incoming_queue):
        super().__init__()

        self._alive = Value("b", False)
        self._incoming_q = incoming_queue

    def run(self):
        self._alive.value = True

        while self._alive.value:
            (sock, result) = self._incoming_q.get()

            if sock is None:
                break

            result = str(result)

            print(f"[RESPONSER] Responding to {sock.getpeername()}")

            msg = f"{len(result)}/{result}"
            sock.sendall(msg.encode("utf8"))

            sock.close()

    def stop(self):
        self._alive.value = False
        self._incoming_q.put(SENTINEL)
        self.join()
