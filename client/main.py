import os
import time
import argparse

from datetime import datetime, timedelta
from socket import socket, AF_INET, SOCK_STREAM

from utils import send_msg, recv_msg

parser = argparse.ArgumentParser()

SERVER_ADDR = os.environ.get("CLI_SERVER_ADDRESS", "127.0.0.1")
SERVER_PORT = int(os.environ.get("CLI_SERVER_WRITE_PORT", "8000"))

SAMPLE_SIZE = 100
MSG_SEP = "/"


def build_read_msg(app_id):
    date1 = datetime(year=2021, month=10, day=4, hour=4, minute=30).isoformat()
    date2 = datetime(year=2021, month=10, day=4, hour=7, minute=30).isoformat()
    return {
        "app_id": app_id or "testing_app_id",
        #"from": date1,
        #"to": date2,
        #"tag": "falopini",
        "pattern": ".*None.*",
    }


def build_log_msg(current_date, app_id):
    return {
        "app_id": app_id or "testing_app_id",
        "message": "This is my first log.",
        "tags": ["testing", "test"],
        "timestamp": current_date.isoformat(),
    }


def send_log_data(server_addr, port, log_data):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((server_addr, port))

    send_msg(sock, log_data)

    response = recv_msg(sock)

    sock.close()

    return response


def main(args) -> None:
    port = SERVER_PORT
    server_addr = SERVER_ADDR
    app_id = args.app

    if args.read:
        log_msg = build_read_msg(app_id)
        result = send_log_data(server_addr, port + 1, log_msg)

        if not args.profile:
            print(f"result {result.get('result')}")
    else:
        dates = [
            datetime.now() + d * timedelta(minutes=15)
            for d in range(SAMPLE_SIZE)
        ]

        for d in dates:
            log_msg = build_log_msg(d, app_id)
            result = send_log_data(server_addr, port, log_msg)

            if not args.profile:
                print(f"result {result}")


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

    args = parser.parse_args()

    timer = Timer()

    with timer:
        main(args)

    if args.profile:
        print(f"[{args.app}] Took %s secs." % (timer.get_elapsed()))
