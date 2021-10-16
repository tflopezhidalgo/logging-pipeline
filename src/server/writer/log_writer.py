import os

from socket import socket
from multiprocessing import Process, Queue

from src.common import build_filename, logging

Result = tuple[socket, str]


class LogWriter(Process):
    SENTINEL = None
    LOGS_FOLDER = "logs"
    SUCEEDED_MSG = "Success"
    FAILED_MSG = "Failed to write logs"

    def __init__(
        self,
        operation_q: Queue,
        result_q: "Queue[Result]",
        access_control_mgr,
    ):
        super().__init__()

        self._operation_q = operation_q
        self._result_q = result_q
        self._access_control_mgr = access_control_mgr

    def __build_log_data(self, params):
        timestamp = params.get("timestamp")
        tags = "|".join(params.get("tags"))
        message = params.get("message")

        return f"[{timestamp}][{tags}] {message}\n"

    def __ensure_app_id_folder_exists(self, app_id):
        available_folders = os.listdir(".")

        if self.LOGS_FOLDER not in available_folders:
            os.mkdir(self.LOGS_FOLDER)

        available_folders = os.listdir(self.LOGS_FOLDER)

        if app_id not in available_folders:
            os.mkdir(os.path.join(self.LOGS_FOLDER, app_id))

    def __process_operation(self, params):
        filename = build_filename(params.get("timestamp"))

        app_id = params.get("app_id")

        self.__ensure_app_id_folder_exists(app_id)

        with self._access_control_mgr.get_lock_for_writer(app_id, filename):
            logfile_path = os.path.join(self.LOGS_FOLDER, app_id, filename)

            with open(logfile_path, "a+") as logfile:
                log_data = self.__build_log_data(params)
                logfile.write(log_data)

        return self.SUCEEDED_MSG

    def run(self):
        while True:
            write_operation: tuple[socket, dict] = self._operation_q.get()

            if write_operation is self.SENTINEL:
                break  # noqa

            (sock, params) = write_operation

            try:
                logging.info(f"Found write operation with params = {params}")
                result = self.__process_operation(params)
            except Exception as e:
                logging.error(e)
                result = self.FAILED_MSG

            self._result_q.put((sock, result))

    def stop(self):
        self._alive.value = False
        self._operation_q.put(self.SENTINEL)
        self.join()
