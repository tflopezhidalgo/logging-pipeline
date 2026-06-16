import os
import socket
import multiprocessing

from src.common import build_filename, logging
from ..log_entry import LogEntry


class WriteError(RuntimeError):
    pass


class LogWriter(multiprocessing.Process):
    SENTINEL = None
    LOGS_FOLDER = "logs"
    BASE_PATH = "."
    SUCEEDED_MSG = "Success"
    FILE_OPENING_MODE = "a+"
    FAILED_MSG = "Failed to write logs"

    def __init__(self, operation_q, result_q, access_control_mgr):
        super().__init__()

        self._operation_q = operation_q
        self._result_q = result_q
        self._access_control_mgr = access_control_mgr

    def __build_log_data(self, params):
        timestamp = params.get("timestamp")
        tags = params.get("tags")
        message = params.get("message")

        return LogEntry(timestamp, tags, message)

    def __ensure_app_id_folder_exists(self, app_id):
        full_path_logs_folder = os.path.join(self.BASE_PATH, self.LOGS_FOLDER)

        if not os.path.isdir(full_path_logs_folder):
            os.mkdir(self.LOGS_FOLDER)

        app_id_logs_folder = os.path.join(full_path_logs_folder, app_id)

        if not os.path.isdir(app_id_logs_folder):
            os.mkdir(app_id_logs_folder)

    def __process_operation(self, params):
        filename = build_filename(params.get("timestamp"))

        app_id = params.get("app_id")

        self.__ensure_app_id_folder_exists(app_id)

        with self._access_control_mgr.writing_lock(app_id, filename):
            logfile_path = os.path.join(
                self.BASE_PATH, self.LOGS_FOLDER, app_id, filename
            )

            try:
                with open(logfile_path, self.FILE_OPENING_MODE) as logfile:

                    logging.info(f"Writing to file = {logfile_path}")
                    log_data = self.__build_log_data(params).to_str()

                    if len(log_data) != logfile.write(log_data):
                        raise WriteError()

            except Exception:
                raise WriteError()

        return self.SUCEEDED_MSG

    def run(self):
        while True:
            write_operation: tuple[socket.socket, dict] = self._operation_q.get()

            if write_operation is self.SENTINEL:
                break  # noqa

            (sock, params) = write_operation

            try:
                logging.info(f"Found write operation with params = {params}")
                result = self.__process_operation(params)
            except (WriteError, Exception) as e:
                logging.error(e)
                result = self.FAILED_MSG

            self._result_q.put((sock, result))

    def stop(self):
        logging.info('Stopping worker: %s' % self.__class__.__name__)

        self._operation_q.put(self.SENTINEL)
        self.join()
