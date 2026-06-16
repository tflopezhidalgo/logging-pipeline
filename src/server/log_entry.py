import re
import datetime


class LogEntry:
    LOG_STRUCTURE_REGEX = r"\[(.*)\]\[(.*)\](.*)$"

    def __init__(self, date, tags, content):
        self._date = date
        self._tags = tags
        self._content = content
        self._raw = self.to_str()

    @classmethod
    def from_str(cls, str):
        result = re.search(cls.LOG_STRUCTURE_REGEX, str)

        if not (result and result.groups()):
            raise RuntimeError("Log entry doesn't match expected structure")

        date, tags, content = result.groups()

        date = datetime.datetime.fromisoformat(date)
        tags = tags.split("|")

        return cls(date, tags, content)

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

    @property
    def raw(self):
        return self._raw
