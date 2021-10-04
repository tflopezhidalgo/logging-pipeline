import os

from socket import socket
from multiprocessing import Process, Queue

Result = tuple[socket, str]


# TODO -> utils
def build_filename(params):
    log_date = params.get("timestamp")
    return f"{log_date.date().isoformat()}-{log_date.hour:0>2}.log"


def build_log_data(params):
    timestamp = params.get("timestamp")
    tags = "|".join(params.get("tags"))
    message = params.get("message")

    return f"[{timestamp}][{tags}] {message}\n"


class LogWriter(Process):
    """
    Handles opening and closing file-related operations.
    """

    SENTINEL = None

    def __init__(
        self, operation_q: Queue, result_q: "Queue[Result]", access_control_mgr
    ):
        super().__init__()

        self._operation_q = operation_q
        self._result_q = result_q
        self._access_control_mgr = access_control_mgr

    def __process_operation(self, write_operation):
        (sock, params) = write_operation

        filename = build_filename(params)

        app_id = params.get("app_id")

        available_folders = os.listdir(".")

        if "logs" not in available_folders:
            os.mkdir("logs")

        available_folders = os.listdir("logs")

        if app_id not in available_folders:
            os.mkdir("logs" + "/" + app_id)

        with self._access_control_mgr.get_lock_for_writer(app_id, filename):
            with open("logs" + "/" + app_id + "/" + filename, "a+") as logfile:
                log_data = build_log_data(params)
                logfile.write(log_data)

        return (sock, "OK")

    def run(self):
        while True:
            write_operation: tuple[socket, dict] = self._operation_q.get()

            if write_operation is self.SENTINEL:
                break

            result = self.__process_operation(write_operation)

            self._result_q.put(result)

    def stop(self):
        self._alive.value = False
        self._operation_q.put(self.SENTINEL)
        self.join()
