import json

from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR


class SocketWrapper:
    """
    Socket wrapper that handles both socket-related and
    protocol-related logic.
    """

    MSG_SEP = "/"
    CHUNK_SIZE = 10

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
        msg = f"{len(json_data)}{self.MSG_SEP}{json_data}"
        msg = msg.encode("utf8")

        return self._sock.sendall(msg)

    def recv_msg(self):
        size_buf = ""
        msg_buf = ""

        def chunk_has_msg_sep(chunk):
            return chunk.find(self.MSG_SEP) != -1

        done = False
        while not done:
            chunk = self._sock.recv(self.CHUNK_SIZE).decode()

            if chunk_has_msg_sep(chunk):
                size_part, msg_part = chunk.split(self.MSG_SEP, 1)
                done = True
            else:
                size_part, msg_part = chunk, ""

            size_buf += size_part
            msg_buf += msg_part

        pending_bytes_to_recv = int(size_buf) - len(msg_buf)

        while pending_bytes_to_recv:
            chunk = self._sock.recv(pending_bytes_to_recv).decode()
            pending_bytes_to_recv -= len(chunk)
            msg_buf += chunk

        return json.loads(msg_buf)

    def shutdown(self):
        return self._sock.shutdown(SHUT_RDWR)

    def getpeername(self):
        return self._sock.getpeername()

    def close(self):
        return self._sock.close()
