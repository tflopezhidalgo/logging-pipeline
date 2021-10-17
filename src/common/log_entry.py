import re


class LogEntry:

    LOG_STRUCTURE_REGEX = r"\[(.*)\]\[(.*)\].*$"

    def __init__(self, date, tags, content):
        self._date = date
        self._tags = tags
        self._content = content

    @classmethod
    def from_str(self, str):
        result = re.search(self.LOG_STRUCTURE_REGEX, str)

        if not result.groups():
            raise RuntimeError("Log entry doesn't match expected structure")

        self._date, self._tags, self._content = result

    def to_str(self):
        timestamp = self._date
        tags = "|".join(self._tags)
        message = self._content

        return f"[{timestamp}][{tags}] {message}\n"

    @property
    def date(self):
        return self._date

    @property
    def tags(self):
        return self._tags

    @property
    def content(self):
        return self._content
