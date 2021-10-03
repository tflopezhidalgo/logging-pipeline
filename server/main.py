import os
import time
import signal

from multiprocessing import Queue, Manager

from shared import Acceptor, Router, AccessManager
from reader import LogReader, RResponser
from writer import LogWriter, WResponser


# XXX: should be taken from environment
SERVER_PORT = int(os.environ.get('SERVER_PORT'))
SERVER_BACKLOG = int(os.environ.get('SERVER_LISTEN_BACKLOG'))

# TODO: bad name
CONCURRENCY = int(os.environ.get('CONC', '1'))


def start_reader_processes(server_port, access_managers):
    manager = Manager()
    router_q = manager.Queue()
    result_q = Queue()

    readers_queues = [Queue() for _ in range(CONCURRENCY)]

    readers_pool = [LogReader(q, result_q, am) for q, am in zip(readers_queues, access_managers)]

    acceptor = Acceptor(router_q, server_port, SERVER_BACKLOG, result_q)

    router = Router(router_q, readers_queues)

    responser = RResponser(result_q)

    acceptor.start()
    router.start()

    for reader in readers_pool:
        reader.start()

    responser.start()

    return [acceptor, router, responser] + readers_pool


def start_writer_processes(server_port, access_managers):
    manager = Manager()
    router_q = manager.Queue()
    result_q = Queue()

    writers_queues = [Queue() for _ in range(CONCURRENCY)]

    acceptor = Acceptor(router_q, server_port, SERVER_BACKLOG, result_q)
    router = Router(router_q, writers_queues)

    writers_pool = [LogWriter(q, result_q, am) for q, am in zip(writers_queues, access_managers)]

    responser = WResponser(result_q)

    acceptor.start()
    router.start()

    for writer in writers_pool:
        writer.start()

    responser.start()

    return [acceptor, router, responser] + writers_pool


def shutdown(processes):
    print("i'm dying", flush=True)
    for p in processes + reader_processes:
        p.stop()
        p.join()


def main(server_port):
    access_managers = [AccessManager() for _ in range(CONCURRENCY)]

    writer_processes = start_writer_processes(server_port, access_managers)
    reader_processes = start_reader_processes(server_port + 1, access_managers)

    signal.signal(signal.SIGTERM, lambda: shutdown(writer_processes + reader_processes))

    stop = False
    while not stop:
        response = input()
        stop = (response == 'q')

    shutdown(writer_processes + reader_processes)


if __name__ == "__main__":
    main(SERVER_PORT)
