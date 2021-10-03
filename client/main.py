import json
import time
import argparse
from datetime import datetime, timedelta
from socket import socket, AF_INET, SOCK_STREAM

parser = argparse.ArgumentParser()

# TODO: change this to container addr
# TODO: set these as env vars
SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 8000  # write port
SAMPLE_SIZE = 100
MSG_SEP = "/"


def build_read_msg(app_id):
    log_data = {
        "app_id": app_id or "testing_app_id",
        "from": "",
        "to": "",
        "tag": ["testing", "test"],
        "pattern": "",
    }

    json_data = json.dumps(log_data)

    return f"{len(json_data)}/{json_data}"


def build_log_msg(current_date, app_id):
    log_data = {
        "app_id": app_id or "testing_app_id",
        "message": "This is my first log.",
        "tags": ["testing", "test"],
        "timestamp": current_date.isoformat(),
    }

    json_data = json.dumps(log_data)

    return f"{len(json_data)}/{json_data}"


def send_msg(server_addr, port, log_data):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((server_addr, port))
    sock.sendall(log_data.encode("utf8"))

    done = False
    received = []

    while not done:
        c = sock.recv(1)
        c = c.decode()
        if c != "/":
            received.append(c)
        else:
            done = True
    msg = sock.recv(int("".join(received)))
    msg = msg.decode()

    sock.close()


def main(args) -> None:
    port = SERVER_PORT
    server_addr = SERVER_ADDR
    app_id = args.app

    if args.read:
        log_msg = build_read_msg(app_id)
        send_msg(server_addr, port + 1, log_msg)
    else:
        dates = [
            datetime.now() + d * timedelta(minutes=15) for d in range(SAMPLE_SIZE)
        ]

        for d in dates:
            log_msg = build_log_msg(d, app_id)
            send_msg(server_addr, port, log_msg)


if __name__ == "__main__":
    start = time.time()

    parser.add_argument(
        "--read", action="store_true", help="Use read operation flag"
    )
    parser.add_argument(
        "--app", type=str, help="Application's id"
    )
    args = parser.parse_args()
    main(args)

    stop = time.time()

    print(f"[{args.app}] Taken %s secs." % (stop - start))
