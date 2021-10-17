import os
import time
import argparse
import random

from datetime import datetime, timedelta

from src.common import SocketWrapper

parser = argparse.ArgumentParser()

SERVER_ADDR = os.environ.get("CLI_SERVER_ADDRESS", "127.0.0.1")
SERVER_PORT = int(os.environ.get("CLI_SERVER_WRITE_PORT", "8000"))

SAMPLE_SIZE = 100

TAGS = ["test", "warning", "info", "debug", "unicorn"]

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
    current_date, app_id, tag=None, to=None, from_=None, pattern=None
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


def build_log_msg(current_date, app_id):
    return {
        "app_id": app_id or "testing_app_id",
        "message": random.choice(MESSAGES),
        "tags": [random.choice(TAGS)],
        "timestamp": current_date.isoformat(),
    }


def send_log_data(server_addr, port, log_data):
    sock = SocketWrapper()
    sock.connect((server_addr, port))

    sock.send_msg(log_data)

    response = sock.recv_msg()

    sock.close()

    return response


def main(args) -> None:
    port = SERVER_PORT
    server_addr = SERVER_ADDR
    app_id = args.app

    now = datetime(year=2021, month=10, day=5)

    if args.read:

        repeat_for = SAMPLE_SIZE if args.repeat else 1

        for i in range(repeat_for):
            to = None
            from_ = None

            if args.filter_dates:
                to = now + timedelta(hours=1)
                from_ = now + timedelta(hours=5)

            log_msg = build_read_msg(
                now,
                app_id,
                to=to,
                from_=from_,
                tag=args.tag,
                pattern=args.pattern,
            )

            if args.invalid_params:
                log_msg["app_id"] = ""

            result = send_log_data(server_addr, port + 1, log_msg)

            if not args.profile:
                print(
                    f"Aplication ID = {app_id} Result: \n"
                    f" {result.get('result')}"
                )
    else:
        dates = [now + d * timedelta(minutes=10) for d in range(SAMPLE_SIZE)]

        if args.no_timestamp:
            dates = [dates[0]]

        for d in dates:
            log_msg = build_log_msg(d, app_id)

            if args.no_timestamp:
                log_msg.pop("timestamp")

            result = send_log_data(server_addr, port, log_msg)

            if not args.profile:
                print(
                    f"Application ID = {app_id} Result: \n"
                    f" {result.get('result')}"
                )


class Timer:
    """
    Small class to use as a context manager
    for measure execution times.
    """

    def __init__(self):
        self.start = None
        self.stop = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop = time.time()

    def get_elapsed(self):
        return self.stop - self.start


if __name__ == "__main__":
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Show execution time after finishing",
    )
    parser.add_argument(
        "--read", action="store_true", help="Use read operation flag"
    )
    parser.add_argument(
        "--app", required=True, type=str, help="Application's id"
    )
    parser.add_argument("--tag", type=str, help="Tag to search for")
    parser.add_argument("--pattern", type=str, help="Pattern to search for")
    parser.add_argument(
        "--filter-dates",
        action="store_true",
        help="filter between two fixed dates",
    )
    parser.add_argument(
        "--invalid-params",
        action="store_true",
        help="Add invalid param to filter",
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Add invalid param to filter",
    )
    parser.add_argument(
        "--repeat",
        action="store_true",
        help="Add invalid param to filter",
    )

    args = parser.parse_args()

    timer = Timer()

    with timer:
        main(args)

    if args.profile:
        type = "reader" if args.read else "writer"
        print(
            f"[{type}][{args.app}] Time elapsed: %s secs."
            % (timer.get_elapsed())
        )
