from socket import socket
from multiprocessing import Process, Value, Queue
from datetime import datetime

import os

SENTINEL = None

Result = tuple[socket, str]


def build_filename(params):
    timestamp = params.get("timestamp")
    log_date = datetime.fromisoformat(timestamp)

    return f"{log_date.date().isoformat()}-{log_date.hour:0>2}.log"


def build_log_data(params):
    return f'[{params.get("timestamp")}] {params.get("message")}\n'


class LogWriter(Process):
    """
    Handles opening and closing file-related operations.
    """

    def __init__(
        self, operation_q: Queue, result_q: "Queue[Result]", access_control_mgr
    ):
        super().__init__()

        self._alive = Value("b", False)
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
        self._alive.value = True

        while self._alive.value:
            write_operation: tuple[socket, dict] = self._operation_q.get()

            if write_operation is None:
                break

            result = self.__process_operation(write_operation)

            self._result_q.put(result)

    def stop(self):
        self._alive.value = False
        self._operation_q.put(SENTINEL)
        self.join()
