import json

from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR

MSG_SEP = "/"


class SocketWrapper:
    """
    Socket wrapper that handles both socket-related and
    protocol-related logic.
    """

    def __init__(self, sock=None):
        if sock is None:
            sock = socket(AF_INET, SOCK_STREAM)

        self._sock = sock

    def bind_and_listen(self, port, listen_backlog):
        self._sock.bind(("0.0.0.0", port))
        self._sock.listen(listen_backlog)

    def connect(self, addr):
        return self._sock.connect(addr)

    def accept(self):
        c, addr = self._sock.accept()
        return SocketWrapper(sock=c), addr

    def send_msg(self, data):
        json_data = json.dumps(data)
        msg = f"{len(json_data)}{MSG_SEP}{json_data}"
        msg = msg.encode("utf8")

        return self._sock.sendall(msg)

    def recv_msg(self):
        size_buf = []

        done = False
        while not done:
            n = self._sock.recv(1).decode()
            if n != MSG_SEP:
                size_buf.append(n)
            else:
                done = True

        pending_bytes_to_recv = int("".join(size_buf))

        msg_buf = b""

        while pending_bytes_to_recv:
            chunk = self._sock.recv(pending_bytes_to_recv)
            pending_bytes_to_recv -= len(chunk)
            msg_buf += chunk

        return json.loads(msg_buf.decode("utf8"))

    def shutdown(self):
        return self._sock.shutdown(SHUT_RDWR)

    def getpeername(self):
        return self._sock.getpeername()

    def close(self):
        return self._sock.close()
