from socket import socket
from multiprocessing import Process, Value, Queue
import os

SENTINEL = None

Result = tuple[socket, str]


class LogReader(Process):
    """
    Handles opening and closing file-related operations.
    """

    def __init__(
        self, operation_q: Queue, result_q: "Queue[Result]", access_manager
    ):
        super().__init__()

        self._alive = Value("b", False)
        self._operation_q = operation_q
        self._result_q = result_q
        self.access_manager = access_manager

    def __process_operation(self, read_operation):
        (sock, params) = read_operation

        app_id = params.get("app_id")

        logs_path = os.path.join("logs", app_id)

        logs = os.listdir(logs_path)

        logs.sort()

        data = []

        for logfile in logs:
            with self.access_manager.get_lock_for_reader(app_id, logfile):
                with open(
                    os.path.join("logs", app_id, logfile), "r"
                ) as logfile:
                    print(f"Opening {logfile}")
                    data.append(logfile.read())

        return (sock, "".join(data))

    def run(self):
        self._alive.value = True

        while self._alive.value:
            write_operation: tuple[socket, dict] = self._operation_q.get()

            if write_operation is None:
                break

            print(f"Found read operation: {write_operation}")

            result = self.__process_operation(write_operation)

            self._result_q.put(result)

    def stop(self):
        self._operation_q.put(SENTINEL)
        self._alive.value = False
        self.join()
