import os
import re

from multiprocessing import Process

from src.common import logging, build_filename, LogEntry


class _LineFilter:
    def __init__(self, params):
        self.params = params

    def line_matches_filters(self, line):
        log_entry = LogEntry.from_str(line)

        if self.params.get("from") and self.params.get("to"):
            from_date = self.params.get("from")
            to_date = self.params.get("to")

            matches_dates = (
                log_entry.date >= from_date and log_entry.date <= to_date
            )
        else:
            matches_dates = True

        if self.params.get("tag"):
            tag_to_find = f"{self.params.get('tag')}"

            matches_tag = tag_to_find in log_entry.tags
        else:
            matches_tag = True

        if self.params.get("pattern"):
            pattern = self.params["pattern"]
            pattern = re.compile(pattern)
            matches_pattern = bool(pattern.match(log_entry.raw))
        else:
            matches_pattern = True

        return matches_tag and matches_dates and matches_pattern


class LogReader(Process):
    SENTINEL = (None, None)
    LOGS_FOLDER = "logs"
    BASE_PATH = "/"
    FAILED_MSG = "Failed to read files"
    FILE_OPENING_MODE = "r"

    def __init__(self, operation_q, result_q, access_manager):
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

    def __get_filenames_to_read(self, params):
        app_id = params.get("app_id")

        logs_path = os.path.join(self.BASE_PATH, self.LOGS_FOLDER, app_id)

        if not os.path.exists(logs_path):
            logging.error(f"There is no log folder for app = {app_id}")
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
        app_id = params["app_id"]

        line_filter = _LineFilter(params)

        data = []

        for logfile in self.__get_filenames_to_read(params):
            filepath = os.path.join(
                self.BASE_PATH, self.LOGS_FOLDER, app_id, logfile
            )

            with self._access_manager.get_lock_for_reader(app_id, logfile):
                with open(filepath, self.FILE_OPENING_MODE) as logfile:
                    data += list(
                        filter(
                            line_filter.line_matches_filters,
                            logfile,
                        )
                    )

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
                result = self.FAILED_MSG

            self._result_q.put((sock, result))

    def stop(self):
        self._operation_q.put(self.SENTINEL)
        self.join()
