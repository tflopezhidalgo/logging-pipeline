import os
import signal

from multiprocessing import Queue, Manager

from src.server.shared import Acceptor, AccessManager, ResponserPool
from src.server.reader import LogReader, ReaderRouterPool
from src.server.writer import LogWriter, WriterRouterPool
from src.common import logging


SERVER_PORT = int(os.environ.get("SERVER_PORT"))  # type: ignore
SERVER_BACKLOG = int(os.environ.get("SERVER_LISTEN_BACKLOG"))  # type: ignore
FILE_WORKERS = int(os.environ.get("FILE_WORKERS", 3))  # type: ignore
ROUTER_P_SIZE = int(os.environ.get("ROUTER_P_SIZE", 3))  # type: ignore
RESPONSER_P_SIZE = int(os.environ.get("RESPONSER_P_SIZE", 3))  # type: ignore


def start_reader_processes(access_managers):
    manager = Manager()
    router_q = manager.Queue()
    result_q = Queue()

    readers_queues = [Queue() for _ in range(FILE_WORKERS)]

    readers_pool = [
        LogReader(q, result_q, am)
        for q, am in zip(readers_queues, access_managers)
    ]

    acceptor = Acceptor(router_q, SERVER_PORT + 1, SERVER_BACKLOG)

    router = ReaderRouterPool(
        ROUTER_P_SIZE, router_q, readers_queues, result_q
    )

    responser = ResponserPool(RESPONSER_P_SIZE, result_q)

    acceptor.start()
    router.start()

    for reader in readers_pool:
        reader.start()

    responser.start()

    return [acceptor, router, responser] + readers_pool


def start_writer_processes(access_managers):
    manager = Manager()
    router_q = manager.Queue()
    result_q = Queue()

    writers_queues = [Queue() for _ in range(FILE_WORKERS)]

    acceptor = Acceptor(router_q, SERVER_PORT, SERVER_BACKLOG)
    router = WriterRouterPool(
        ROUTER_P_SIZE, router_q, writers_queues, result_q
    )

    writers_pool = [
        LogWriter(q, result_q, am)
        for q, am in zip(writers_queues, access_managers)
    ]

    responser = ResponserPool(RESPONSER_P_SIZE, result_q)

    acceptor.start()
    router.start()

    for writer in writers_pool:
        writer.start()

    responser.start()

    return [acceptor, router, responser] + writers_pool


def shutdown(processes):
    for p in processes:
        p.stop()
        p.join()


def main():
    access_managers = [AccessManager() for _ in range(FILE_WORKERS)]

    writer_processes = start_writer_processes(access_managers)
    reader_processes = start_reader_processes(access_managers)

    logging.info(
        f"Started server, listening in port {SERVER_PORT} "
        f"using {FILE_WORKERS} as WORKERS for reading/writing "
        f"using {ROUTER_P_SIZE} as ROUTERS "
        f"using {RESPONSER_P_SIZE} as RESPONSERS "
    )

    signal.signal(
        signal.SIGTERM, lambda: shutdown(writer_processes + reader_processes)
    )

    stop = False
    while not stop:
        try:
            response = input()
        except Exception:
            response = None
        stop = response == "q"

    shutdown(writer_processes + reader_processes)


if __name__ == "__main__":
    main()
