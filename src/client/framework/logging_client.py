import datetime

from src.common import SocketWrapper


class Client:
    """
    TBD.
    """

    def __init__(self, **kwargs) -> None:
        self.port: int = kwargs.get('port') or 12345
        self.server_addr = kwargs.get('server_addr')

        self.app_id = kwargs.get('app_id') or 'testing_app_id'
        self.no_timestamp = kwargs.get('no_timestamp')

        # Deprecado. Compatibilidad hacia atras.
        self.profile = kwargs.get('profile')

    def _send_operation(self, server_addr, port, payload):
        # We have to create it create so FD doesn't get
        # reused and closed by the OS before we can send the message.
        sock = SocketWrapper()
        sock.connect((server_addr, port))

        print('Connected to server!', (server_addr, port))

        if not sock.send(payload):
            sock.close()
            print("Couldn't send message to server. Socket closed.")
            return None

        response = sock.recv()
        sock.close()

        print('Socket closed gracefully!')

        return response

    def get_read_port(self):
        return self.port + 1

    def get_write_port(self):
        return self.port

    def _build_read_msg(self, tag=None, range_filter=(None, None), pattern=None):
        read_msg = {'app_id': self.app_id}

        (to, from_) = range_filter

        if to:
            read_msg['to'] = to.isoformat()

        if from_:
            read_msg['from'] = from_.isoformat()

        if pattern:
            read_msg['pattern'] = pattern

        if tag:
            read_msg['tag'] = tag

        return read_msg

    def _build_write_msg(self, date, message, tags):
        if not date or not message:
            raise ValueError('Date and message are required')

        return {
            'app_id': self.app_id,
            'message': message,
            'tags': tags,
            'timestamp': date.isoformat(),
        }

    def read(self, **kwargs) -> None:
        pattern = kwargs.get('pattern')
        tag = kwargs.get('tag')
        dates_filter = kwargs.get('dates_filter')

        read_msg = self._build_read_msg(
            range_filter=dates_filter if dates_filter else (None, None),
            tag=tag,
            pattern=pattern,
        )

        # FIXME.
        # Solamente para forzar un error en el servidor y ver cómo se comporta el cliente.
        # if args.invalid_params:
        #     read_msg["app_id"] = ""
        op_result = self._send_operation(
            self.server_addr, self.get_read_port(), read_msg
        )
        return op_result

    def write(self, message, tags) -> None:
        now = datetime.datetime.now()
        message = self._build_write_msg(now, message, tags)

        # Solamente para forzar un error en el servidor y ver cómo se comporta el cliente.
        if self.no_timestamp:
            message.pop('timestamp')

        op_result = self._send_operation(
            self.server_addr, self.get_write_port(), message
        )
        return op_result
