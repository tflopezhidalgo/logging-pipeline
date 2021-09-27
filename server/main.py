import time
import multiprocessing

# XXX: should be taken from environment
SERVER_PORT = 8000
SERVER_BACKLOG = 10


class Server:
    def __init__(self, q):
        self._q = q
        self._me = multiprocessing.Process(target=self.run)

    def start(self):
        self._me.start()
        print("Started!")

    def run(self):
        print("Hey, I'm running in another process!")
        print("I'm gonna sleep for 10 secs.")
        time.sleep(10)
        print("Alright I'm awaken")

    def stop(self):
        self._me.join()


def main(server_port):
    s = Server(None)
    s.start()
    for _ in range(0, 10):
        print("Hey!")
        time.sleep(1)

    s.stop()


if __name__ == "__main__":
    main(SERVER_PORT)
