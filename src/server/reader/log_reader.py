import os
import re
import multiprocessing

from src.common import build_filename, logging
from ..log_entry import LogEntry


class Filter:
    """
    Base class for filters. Each filter should implement entry_matches_filter method
    """

    def entry_matches_filter(self, log_entry):
        raise NotImplementedError


class DateIntervalFilter(Filter):
    """
    Filter for log entries that checks if the date of the entry is between from and to dates
    """

    def __init__(self, from_date, to_date):
        self._from = from_date
        self._to = to_date

    def entry_matches_filter(self, log_entry):
        return log_entry.date >= self._from and log_entry.date <= self._to


class TagFilter(Filter):
    """
    Filter for log entries that checks if the entry has the specified tag
    """

    def __init__(self, tag):
        self._tag = tag

    def entry_matches_filter(self, log_entry):
        return self._tag in log_entry.tags


class PatternFilter(Filter):
    """
    Filter for log entries that checks if the raw log entry matches the specified pattern (regex)
    """

    def __init__(self, pattern):
        self._pattern = pattern

    def entry_matches_filter(self, log_entry):
        pattern = re.compile(self._pattern)
        return bool(pattern.match(log_entry.raw))


class Searcher:
    """
    TBD.
    """

    def __init__(self, params):
        self.filters = []

        from_date = params.get('from')
        to_date = params.get('to')

        if from_date and to_date:
            self.filters.append(DateIntervalFilter(from_date, to_date))

        tag_to_find = params.get('tag')

        if tag_to_find:
            self.filters.append(TagFilter(tag_to_find))

        pattern = params.get('pattern')

        if pattern:
            self.filters.append(PatternFilter(pattern))

    def is_match(self, line):
        entry = LogEntry.from_str(line)

        return all(
            map(
                lambda f: f.entry_matches_filter(entry),
                self.filters,
            )
        )


class LogReader(multiprocessing.Process):
    SENTINEL = (None, None)
    LOGS_FOLDER = 'logs'
    BASE_PATH = '.'
    FAILED_MSG = 'Failed to read files'
    FILE_OPENING_MODE = 'r'

    def __init__(
        self,
        operation_q: multiprocessing.Queue[tuple],
        result_q: multiprocessing.Queue[tuple],
        access_manager,
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
                lambda filename: filename >= from_filename and filename <= to_filename,
                filenames,
            )
        )
        return filtered

    def __get_filenames_to_read(self, params):
        app_id = params.get('app_id')

        logs_path = os.path.join(self.BASE_PATH, self.LOGS_FOLDER, app_id)

        if not os.path.exists(logs_path):
            logging.error(f'There is no log folder for app = {app_id}')
            return []

        logs = os.listdir(logs_path)

        logs.sort()

        from_date = params.get('from')
        to_date = params.get('to')

        if from_date and to_date:
            logs = self.__filter_filenames_between_dates(from_date, to_date, logs)

        return logs

    def __perform_operation(self, params) -> list[str]:
        app_id = params['app_id']

        s = Searcher(params)
        matching_lines: list[str] = []

        for logfile in self.__get_filenames_to_read(params):
            filepath = os.path.join(self.BASE_PATH, self.LOGS_FOLDER, app_id, logfile)

            with self._access_manager.reading_lock(app_id, logfile):
                with open(filepath, self.FILE_OPENING_MODE) as logfile:
                    matching_lines += list(filter(s.is_match, logfile))

        return matching_lines if len(matching_lines) > 0 else []

    def run(self):
        while True:
            (sock, operation_params) = self._operation_q.get()

            if (sock, operation_params) == self.SENTINEL:
                break  # noqa

            try:
                logging.info(f'Found read operation with params {operation_params}')
                result = self.__perform_operation(operation_params)
            except Exception as e:
                logging.error(e)
                result = self.FAILED_MSG

            self._result_q.put((sock, result))

    def stop(self):
        logging.info('Stopping worker: %s' % self.name)

        self._operation_q.put(self.SENTINEL)
        self.join()
