import os
import time
import argparse

import logging_client

parser = argparse.ArgumentParser()

SERVER_ADDR = os.environ.get("CLI_SERVER_ADDRESS", "127.0.0.1")
SERVER_PORT = int(os.environ.get("CLI_SERVER_WRITE_PORT", "8000"))

def main(args) -> None:
    port = SERVER_PORT
    server_addr = SERVER_ADDR

    c = logging_client.Client(
        port=port,
        server_addr=server_addr,
        app_id=args.app,
        no_timestamp=args.no_timestamp
        )

    if args.read:
        c.read(
            pattern=args.pattern,
            tag=args.tag,
            filter_dates=args.filter_dates,
            repeat=args.repeat
            )
    else:
        c.write()


class Timer:
    """
    Small class to use as a context manager
    for measuring execution times.
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
        return self.start and self.stop and self.stop - self.start


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
