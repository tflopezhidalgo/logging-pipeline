import json
import socket


class JSONEncoder:
    """
    TBD.
    """

    def serialize(self, data):
        return json.dumps(data)

    def deserialize(self, data):
        return json.loads(data)


class SocketWrapper:
    """
    Socket wrapper that handles both socket-related and
    protocol-related logic.
    """

    MSG_SEP = '/'

    def __init__(self, sock=None):
        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._sock = sock
        self.encoder = JSONEncoder()

    def bind_and_listen(self, port, listen_backlog):
        self._sock.bind(('0.0.0.0', port))
        self._sock.listen(listen_backlog)

    def connect(self, addr):
        return self._sock.connect(addr)

    def accept(self):
        c, addr = self._sock.accept()
        return SocketWrapper(sock=c), addr

    def getpeername(self):
        return self._sock.getpeername()

    def send_msg(self, data):
        try:
            encoded = self.encoder.serialize(data)
            msg = f'{len(encoded)}{self.MSG_SEP}{encoded}'

            self._sock.sendall(msg.encode('utf8'))
            return len(msg)
        except (Exception, OSError):
            return 0

    def recv_msg(self):
        size_buf = ''
        msg_buf = ''

        try:

            def chunk_has_msg_sep(c):
                return c.find(self.MSG_SEP) != -1

            done = False

            # Fetch an initial chunk of data. First comes the size of message
            # and then the message itself, separated by MSG_SEP. We need to loop until
            # we have the size of the message, which is required to know how many bytes we need to fetch
            while not done:
                try:
                    chunk = self._sock.recv(1).decode('utf8')

                    if chunk_has_msg_sep(chunk):
                        size_part, msg_part = chunk.split(self.MSG_SEP, 1)
                        done = True
                    else:
                        size_part, msg_part = chunk, ''

                    size_buf += size_part
                    msg_buf += msg_part

                except socket.timeout:
                    return None

            pending = int(size_buf) - len(msg_buf)

            # Now fetch the remaining bytes of the message until we have the full message
            while pending:
                chunk = self._sock.recv(pending).decode()
                pending -= len(chunk)
                msg_buf += chunk

            return self.encoder.deserialize(msg_buf)

        except (Exception, OSError):
            return None

    def close(self):
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            self._sock.close()
