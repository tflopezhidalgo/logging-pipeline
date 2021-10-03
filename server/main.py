from multiprocessing import Queue

from shared import Acceptor, Router, AccessManager
from reader import LogReader, RResponser
from writer import LogWriter, WResponser


# XXX: should be taken from environment
SERVER_PORT = 8100
SERVER_BACKLOG = 10


def start_reader_processes(server_port, access_manager):
    router_q = Queue()
    result_q = Queue()
    reader_q_1 = Queue()
    readers_queues = [reader_q_1]

    acceptor = Acceptor(router_q, server_port, SERVER_BACKLOG, result_q)
    router = Router(router_q, readers_queues)

    log_reader = LogReader(reader_q_1, result_q, access_manager)

    responser = RResponser(result_q)

    acceptor.start()
    router.start()
    log_reader.start()
    responser.start()

    return [acceptor, router, log_reader, responser]


def start_writer_processes(server_port, access_manager):
    router_q = Queue()
    result_q = Queue()
    writer_q_1 = Queue()
    writers_queues = [writer_q_1]

    acceptor = Acceptor(router_q, server_port, SERVER_BACKLOG, result_q)
    router = Router(router_q, writers_queues)

    log_writer = LogWriter(writer_q_1, result_q, access_manager)

    responser = WResponser(result_q)

    acceptor.start()
    router.start()
    log_writer.start()
    responser.start()

    return [acceptor, router, log_writer, responser]


def main(server_port):
    access_manager = AccessManager()

    writer_processes = start_writer_processes(server_port, access_manager)
    reader_processes = start_reader_processes(server_port + 1, access_manager)

    input()

    for p in writer_processes + reader_processes:
        p.stop()


if __name__ == "__main__":
    main(SERVER_PORT)
