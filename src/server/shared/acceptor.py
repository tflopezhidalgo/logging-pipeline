from multiprocessing import Process, Value

from src.common import logging, SocketWrapper


class Acceptor(Process):
    """
    Responsible for handling throttling operations.
    If the output queue is either full or its size is above some threshold
    then it'll avoid adding another operation to that queue, and instead it
    will add a message in responser's queue.
    """

    # If there're more than THROTTLING_THRESHOLD items enqueued
    # start to throttling
    THROTTLING_THRESHOLD = 100

    def __init__(self, dispatch_queue, port, listen_backlog):
        super().__init__()

        self._alive = Value("b", False)
        self._dispatch_q = dispatch_queue

        self._socket = SocketWrapper()
        self._socket.bind_and_listen(port, listen_backlog)

    def __handle_client_connection(self, client_sock):
        if self._dispatch_q.qsize() >= self.THROTTLING_THRESHOLD:
            try:
                logging.info(
                    f"Making client {client_sock.getpeername()} aware of"
                    " throttling"
                )
                client_sock.send_msg(
                    {
                        "result": (
                            "Server is not available now. Please try again"
                            " later."
                        )
                    }
                )
            except Exception:
                logging.error(
                    "Failed to send message to client. Closing connection"
                )
            return client_sock.close()

        return self._dispatch_q.put(client_sock)

    def __accept_new_connection(self):
        # Connection arrived
        c, addr = self._socket.accept()
        logging.info("Got connection from {}".format(addr))
        return c

    def run(self):
        self._alive.value = True

        while self._alive.value:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
                # Clean the previous connection as fast as we can
                client_sock = None
            except (Exception, OSError) as e:
                logging.error(e)

    def stop(self):
        try:
            self._socket.shutdown()
        except OSError:
            logging.error("Unable to shutdown socket")
        self._socket.close()
