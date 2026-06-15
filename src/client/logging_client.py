import os
import time
import argparse
import random

from datetime import datetime, timedelta

from src.common import SocketWrapper
from typing import Tuple

SAMPLE_SIZE = 100

TAGS = ["error", "warning", "info", "debug", "unicorn"]

MESSAGES = [
    "Hey",
    "random log!",
    "this is not a log",
    "why are we logging?",
    "Yeah, that went fine. Nop",
    "lorem ipsum?",
    "The application has died.",
]


def build_read_msg(
    app_id, tag=None, to=None, from_=None, pattern=None
):
    read_msg = {"app_id": app_id or "testing_app_id"}

    if to:
        to = to.isoformat()
        read_msg["to"] = to

    if from_:
        from_ = from_.isoformat()
        read_msg["from"] = from_

    if pattern:
        read_msg["pattern"] = pattern

    if tag:
        read_msg["tag"] = tag

    return read_msg


def build_write_msg(current_date, app_id):
    return {
        "app_id": app_id or "testing_app_id",
        "message": random.choice(MESSAGES),
        "tags": [random.choice(TAGS)],
        "timestamp": current_date.isoformat(),
    }

def build_random_date_filter(base_date: datetime) -> Tuple[datetime, datetime]:
    return (base_date + timedelta(hours=5), base_date + timedelta(hours=1))


class Client:

    def __init__(self, **kwargs) -> None:
        self.port: int = kwargs.get("port") or 12345
        self.server_addr = kwargs.get("server_addr")

        self.app_id = kwargs.get("app_id")
        self.no_timestamp = kwargs.get("no_timestamp")

    def _send_log_data(self, server_addr, port, payload):
        sock = SocketWrapper()
        sock.connect((server_addr, port))

        if not sock.send_msg(payload):
            return sock.close()

        response = sock.recv_msg()

        if response is None:
            pass

        sock.close()

        return response

    def read(self, pattern=None, tag=None, filter_dates=False, repeat=False) -> None:
        now = datetime(year=2021, month=10, day=5)

        repeat_for = SAMPLE_SIZE if repeat else 1

        for _ in range(repeat_for):
            (to, _from_) = (None, None)

            if filter_dates:
                to, _from_ = build_random_date_filter(now)

            read_msg = build_read_msg(
                self.app_id,
                to=to,
                from_=_from_,
                tag=tag,
                pattern=pattern,
            )

            # Solamente para forzar un error en el servidor y ver cómo se comporta el cliente.
            if args.invalid_params:
                read_msg["app_id"] = ""

            result = self._send_log_data(self.server_addr, self.port + 1, read_msg)

            if not args.profile:
                print(
                    f"Aplication ID = {self.app_id} Result: \n"
                    f" {result.get('result')}"
               )

    def write(self) -> None:
        now = datetime(year=2021, month=10, day=5)

        # Generate a list of timestamps to send.
        dates = [now + d * timedelta(minutes=10) for d in range(SAMPLE_SIZE)]

        if self.no_timestamp:
            dates = [dates[0]]

        for d in dates:
            write_msg = build_write_msg(d, self.app_id)

            # Solamente para forzar un error en el servidor y ver cómo se comporta el cliente.
            if args.no_timestamp:
                write_msg.pop("timestamp")

            result = self._send_log_data(self.server_addr, self.port, write_msg)

            if not args.profile:
                print(
                    f"Application ID = {self.app_id} Result: \n"
                    f" {result.get('result')}"
                )


