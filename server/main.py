from time import sleep
from multiprocessing import Queue

from acceptor import Acceptor
from router import Router as WriterRouter
from log_writer import LogWriter
from write_responser import Responser


# XXX: should be taken from environment
SERVER_PORT = 8000
SERVER_BACKLOG = 10


def main(server_port):

    router_q = Queue()
    result_q = Queue()
    writer_queue_1 = Queue()
    writers_queues = [writer_queue_1]

    acceptor = Acceptor(router_q, SERVER_PORT, SERVER_BACKLOG, result_q)
    router = WriterRouter(router_q, writers_queues)
    log_writer = LogWriter(writer_queue_1, result_q)
    responser = Responser(result_q)

    acceptor.start()
    router.start()
    log_writer.start()
    responser.start()

    input()

    acceptor.stop()
    router.stop()
    log_writer.stop()
    responser.stop()


if __name__ == "__main__":
    main(SERVER_PORT)
