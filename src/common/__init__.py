from .logging import logging  # noqa
from .network import SocketWrapper  # noqa


def build_filename(log_date):
    return f"{log_date.date().isoformat()}-{log_date.hour:0>2}.log"
