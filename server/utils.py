import os
import json
import logging


MSG_SEP = "/"
LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL", "INFO")

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=LOGGING_LEVEL,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def build_filename(log_date):
    return f"{log_date.date().isoformat()}-{log_date.hour:0>2}.log"


def send_msg(sock, data):
    json_data = json.dumps(data)
    msg = f"{len(json_data)}{MSG_SEP}{json_data}"
    msg = msg.encode("utf8")

    sock.sendall(msg)


def recv_msg(sock):
    size_buf = []

    done = False
    while not done:
        n = sock.recv(1).decode()
        if n != MSG_SEP:
            size_buf.append(n)
        else:
            done = True

    msg_size = int("".join(size_buf))

    msg_buf = sock.recv(msg_size)
    return json.loads(msg_buf.decode("utf8"))
