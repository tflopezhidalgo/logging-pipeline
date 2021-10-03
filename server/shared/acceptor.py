from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from multiprocessing import Process, Value

class Acceptor(Process):
    """
    Responsible for handling throttling operations.
    If the output queue is either full or its size is above some threshold
    then it'll avoid adding another operation to that queue, and instead it
    will add a message in responser's queue.
    """

    def __init__(self, dispatch_queue, port, listen_backlog, fallback_queue):
        super().__init__()

        self._alive = Value("b", False)
        self._dispatch_q = dispatch_queue
        self._fallback_q = fallback_queue

        self._socket = socket(AF_INET, SOCK_STREAM)
        print(f"Acceptor socket on {self._socket}")
        self._socket.bind(("", port))
        self._socket.listen(listen_backlog)

    def __handle_client_connection(self, client_sock):
        self._dispatch_q.put(client_sock)

    def __accept_new_connection(self):
        # Connection arrived
        c, addr = self._socket.accept()
        print("Got connection from {}".format(addr))
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
                print(e)

    def stop(self):
        self._alive.value = False
        # FIXME: shutdown
        try:
            self._socket.shutdown(SHUT_RDWR)
        except:
            print("Unable to shutdown socket")
        self._socket.close()
        self.terminate()
