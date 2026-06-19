import time


class Timer:
    """
    Small class to use as a context manager
    for measuring execution times.
    """

    def __init__(self):
        self.start = None
        self.stop = None

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop = time.time()

    def get_elapsed(self):
        return self.start and self.stop and self.stop - self.start
