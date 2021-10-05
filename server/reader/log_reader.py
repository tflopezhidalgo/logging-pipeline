import os
import re

from socket import socket
from multiprocessing import Process, Queue

from utils import logging, build_filename

Result = tuple[socket, str]


class LogReader(Process):
    SENTINEL = (None, None)
    LOGS_FOLDER = "logs"

    def __init__(
        self, operation_q: Queue, result_q: "Queue[Result]", access_manager
    ):
        super().__init__()

        self._operation_q = operation_q
        self._result_q = result_q
        self._access_manager = access_manager

    def __filter_filenames_between_dates(self, from_, to, filenames):
        from_filename = build_filename(from_)
        to_filename = build_filename(to)

        filtered = list(
            filter(
                lambda filename: (
                    filename >= from_filename and filename <= to_filename
                ),
                filenames,
            )
        )
        return filtered

    def __apply_filters_to_line(self, line, params):
        result = re.search(r"\[(.*)\]\[(.*)\].*$", line)

        if params.get("from") and params.get("to"):
            from_date = f"{params.get('from')}"
            to_date = f"{params.get('to')}"

            log_date = result.groups() and result.groups()[0] or ""

            matches_dates = log_date >= from_date and log_date <= to_date
        else:
            matches_dates = True

        if params.get("tag"):
            tag_to_find = f"{params.get('tag')}"
            log_tags = result.groups() and result.groups()[1] or ""

            matches_tag = log_tags.find(tag_to_find) != -1
        else:
            matches_tag = True

        if params.get("pattern"):
            pattern = params["pattern"]
            pattern = re.compile(pattern)
            matches_pattern = bool(pattern.match(line))
        else:
            matches_pattern = True

        return matches_tag and matches_dates and matches_pattern

    def _get_filenames_to_read(self, params):
        app_id = params.get("app_id")

        logs_path = os.path.join("./logs", app_id)

        if not os.path.exists(logs_path):
            logging.error(f"No existe log {logs_path}")
            return []

        logs = os.listdir(logs_path)

        logs.sort()

        from_date = params.get("from")
        to_date = params.get("to")

        if from_date and to_date:
            logs = self.__filter_filenames_between_dates(
                from_date, to_date, logs
            )

        return logs

    def __perform_operation(self, params):
        logs = list(self._get_filenames_to_read(params))

        app_id = params.get("app_id")

        data = []
        for logfile in logs:

            filepath = os.path.join(self.LOGS_FOLDER, app_id, logfile)

            with self._access_manager.get_lock_for_reader(app_id, logfile):
                if not os.path.isfile(filepath):
                    continue

                with open(filepath, "r") as logfile:
                    content = list(
                        filter(
                            lambda line: self.__apply_filters_to_line(
                                line, params
                            ),
                            logfile,
                        )
                    )
                    data += content

        return "".join(data)

    def run(self):
        while True:
            (sock, operation_params) = self._operation_q.get()

            if (sock, operation_params) == self.SENTINEL:
                break  # noqa

            try:
                logging.info(
                    f"Found read operation with params {operation_params}"
                )
                result = self.__perform_operation(operation_params)
            except Exception as e:
                logging.error(e)
                result = "Failed to read files."

            self._result_q.put((sock, result))

    def stop(self):
        self._operation_q.put(self.SENTINEL)
        self.join()
