import json
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM


# TODO: change this to container addr
SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 8000  # write port
MSG_SEP = "/"


def main() -> None:
    log_data = {
        "app_id": "testing_app_id",
        "message": "This is my first log.",
        "tags": ["testing", "test"],
        "timestamp": datetime.now().isoformat(),
    }

    json_data = json.dumps(log_data)

    msg = f"{len(json_data)}/{json_data}"

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((SERVER_ADDR, SERVER_PORT))
    sock.sendall(msg.encode("utf8"))

    done = False
    buf = ""

    while not done:
        c = sock.recv(1)
        c = c.decode()
        if c != "/":
            buf += c
        else:
            done = True
    msg = sock.recv(int(buf))
    msg = msg.decode()

    sock.close()

    print(f"Recibido {msg}")


if __name__ == "__main__":
    main()
