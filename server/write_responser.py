from multiprocessing import Process, Value


class Responser(Process):
    def __init__(self, incoming_queue):
        super().__init__()

        self._alive = Value("b", False)
        self._incoming_q = incoming_queue

    def run(self):
        self._alive.value = True

        while self._alive.value:
            try:
                (sock, result) = self._incoming_q.get(timeout=1)
                result = str(result)
                print(f"Found result operation {result}")
                msg = f"{len(result)}/{result}"
                sock.sendall(msg.encode("utf8"))
                sock.close()
            except Exception as e:
                pass

    def stop(self):
        self._alive.value = False
