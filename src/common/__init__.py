import os
import logging

from .log_entry import LogEntry  # noqa
from .socket_wrapper import SocketWrapper  # noqa


LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=LOGGING_LEVEL,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def build_filename(log_date):
    return f"{log_date.date().isoformat()}-{log_date.hour:0>2}.log"
