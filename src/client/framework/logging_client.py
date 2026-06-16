from datetime import datetime, timedelta
from typing import Tuple

from src.common import SocketWrapper

def build_read_msg(
    app_id, tag=None, to=None, from_=None, pattern=None
):
    read_msg = {"app_id": app_id or "testing_app_id"}

    if to:
        read_msg["to"] = to.isoformat()

    if from_:
        read_msg["from"] = from_.isoformat()

    if pattern:
        read_msg["pattern"] = pattern

    if tag:
        read_msg["tag"] = tag

    return read_msg


def build_write_msg(current_date, app_id, message, tags):
    return {
        "app_id": app_id or "testing_app_id",
        "message": message,
        "tags": tags,
        "timestamp": current_date.isoformat(),
    }

def build_random_date_filter(base_date: datetime) -> Tuple[datetime, datetime]:
    return (base_date + timedelta(hours=5), base_date + timedelta(hours=1))


class Client:
    """
    ...
    """

    def __init__(self, **kwargs) -> None:
        self.port: int = kwargs.get("port") or 12345
        self.server_addr = kwargs.get("server_addr")

        self.app_id = kwargs.get("app_id")
        self.no_timestamp = kwargs.get("no_timestamp")

        # Deprecado. Compatibilidad hacia atras.
        self.profile = kwargs.get("profile")

    def _send_log_data(self, server_addr, port, payload):
        sock = SocketWrapper()
        sock.connect((server_addr, port))

        if not sock.send_msg(payload):
            sock.close()
            return None

        response = sock.recv_msg()

        sock.close()

        print('Socket closed!')

        return response

    def read(self, pattern=None, tag=None, filter_dates=False) -> None:
        now = datetime(year=2021, month=10, day=5)
        (to, _from_) = (None, None)

        if filter_dates:
            to, _from_ = build_random_date_filter(now)

        read_msg = build_read_msg(
            self.app_id,
            to=to,
            from_=_from_,
            tag=tag,
            pattern=pattern,
        )

        # FIXME.
        # Solamente para forzar un error en el servidor y ver cómo se comporta el cliente.
        # if args.invalid_params:
        #     read_msg["app_id"] = ""

        result = self._send_log_data(self.server_addr, self.port + 1, read_msg)

        if not self.profile:
            print(
                f"Aplication ID = {self.app_id} Result: \n"
                f" {result.get('result')}"
           )

    def write(self, d, message, tags) -> None:
        msg = build_write_msg(d, self.app_id, message, tags)

        # Solamente para forzar un error en el servidor y ver cómo se comporta el cliente.
        if self.no_timestamp:
            msg.pop("timestamp")

        result = self._send_log_data(self.server_addr, self.port, msg)

        if not self.profile:
            print(
                f"Application ID = {self.app_id} Result: \n"
                f" {result.get('result')}"
            )


