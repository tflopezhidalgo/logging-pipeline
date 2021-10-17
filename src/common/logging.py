import os
import logging

LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=LOGGING_LEVEL,
    datefmt="%Y-%m-%d %H:%M:%S",
)
