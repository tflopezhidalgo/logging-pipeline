from socket import socket
from multiprocessing import Process, Value, Queue


class LogWriter(Process):
    def __init__(self, operation_q: Queue, result_q: Queue):
        super().__init__()

        self._alive = Value("b", False)
        self._operation_q = operation_q
        self._result_q = result_q

    def __process_operation(self, write_operation: (socket, dict)) -> (socket, int):
        return (write_operation[0], 1)

    def run(self):
        self._alive.value = True

        while self._alive.value:
            try:
                write_operation: (socket, dict) = self._operation_q.get(timeout=1)
                print(f"Found write operation {write_operation}")
                result = self.__process_operation(write_operation)
                self._result_q.put(result)
            except Exception:
                pass

    def stop(self):
        self._alive.value = False
