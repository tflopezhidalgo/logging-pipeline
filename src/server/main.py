import os
import signal
import multiprocessing

from src.server.shared import Acceptor, AccessManager, RespondersPool
from src.server.reader import LogReader, ReaderRouterPool
from src.server.writer import LogWriter, WriterRouterPool
from src.common import logging


SERVER_PORT = int(os.environ.get("SERVER_PORT", '12345'))  # type: ignore
SERVER_BACKLOG_SIZE = int(os.environ.get("SERVER_LISTEN_BACKLOG", 500))  # type: ignore
FILE_WORKERS = int(os.environ.get("FILE_WORKERS", 3))  # type: ignore

ROUTER_POOL_SIZE = int(os.environ.get("ROUTER_P_SIZE", 3))  # type: ignore
RESPONDER_POOL_SIZE = int(os.environ.get("RESPONSER_P_SIZE", 3))  # type: ignore


def create_readers(access_managers):
    manager = multiprocessing.Manager()
    router_q = manager.Queue()
    result_q = multiprocessing.Queue()

    readers_queues = [multiprocessing.Queue() for _ in range(FILE_WORKERS)]

    readers_pool = [
        LogReader(q, result_q, am)
        for q, am in zip(readers_queues, access_managers)
    ]

    acceptor = Acceptor(router_q, SERVER_PORT + 1, SERVER_BACKLOG_SIZE)
    router = ReaderRouterPool(ROUTER_POOL_SIZE, router_q, readers_queues, result_q)
    responder = RespondersPool(RESPONDER_POOL_SIZE, result_q)

    return [acceptor, router, responder] + readers_pool


def create_writers(access_managers):
    manager = multiprocessing.Manager()
    router_q = manager.Queue()
    result_q = multiprocessing.Queue()

    writers_queues = [multiprocessing.Queue() for _ in range(FILE_WORKERS)]

    writers_pool = [
        LogWriter(q, result_q, am)
        for q, am in zip(writers_queues, access_managers)
    ]

    acceptor = Acceptor(router_q, SERVER_PORT, SERVER_BACKLOG_SIZE)
    router = WriterRouterPool(ROUTER_POOL_SIZE, router_q, writers_queues, result_q)
    responder = RespondersPool(RESPONDER_POOL_SIZE, result_q)

    return [acceptor, router, responder] + writers_pool


def shutdown(processes):
    for p in processes:
        p.stop()
        p.join()


def main():
    processes = []
    try:
        access_managers = [AccessManager() for _ in range(FILE_WORKERS)]

        processes += create_writers(access_managers)
        processes += create_readers(access_managers)

        for p in processes:
            p.start()

        logging.info(
            f"Started server, listening in port {SERVER_PORT} "
            f"using {FILE_WORKERS} as WORKERS for reading/writing "
            f"using {ROUTER_POOL_SIZE} as ROUTERS "
            f"using {RESPONDER_POOL_SIZE} as RESPONSERS "
        )

        signal.signal(signal.SIGTERM, lambda *_: shutdown(processes))

        should_stop = False

        while not should_stop:
            try:
                response = input()
            except Exception:
                response = None
            should_stop = response == "q"
    except Exception as e:
        logging.error("Error initializing server processes [%s]" % e)
        logging.error("Shutting down...")
    finally:
        shutdown(processes)


if __name__ == "__main__":
    main()
