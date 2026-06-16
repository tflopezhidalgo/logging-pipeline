import ctypes
import multiprocessing


class _DummyLock:
    """
    Fake lock given to those proccesses (mostly readers)
    who don't need access in a concurrent-safe way to files.
    """

    def __enter__(self, *args, **kwargs):
        pass  # noqa: E704

    def __exit__(self, *args, **kwargs):
        pass  # noqa: E704

    def acquire(self):
        pass  # noqa: E704

    def release(self):
        pass  # noqa: E704


class AccessManager:
    """
    Responsible for handling in a the read and write accesses to files.
    """

    def __init__(self):
        manager = multiprocessing.Manager()

        self.write_registry = manager.dict()
        self.lock = multiprocessing.Lock()

        self.reader_file = manager.Value(ctypes.c_wchar_p, "None")
        self.reader_lck = multiprocessing.Lock()

        self.writer_file = manager.Value(ctypes.c_wchar_p, "None")
        self.writer_lck = multiprocessing.Lock()

    def writing_lock(self, app_id, filename):
        with self.lock:
            # si el reader esta leyendo el archivo que
            # tenemos que escribir necesitamos tomar
            # ese lock.
            if self.reader_file.value == filename:
                return self.reader_lck

            # si no entonces no hay nadie (otros writers
            # no escriben el mismo archivo que nosotros).
            self.writer_file.value = filename

            # dejamos registro del ultimo que tocamos
            self.write_registry[app_id] = filename

            return self.writer_lck

    def reading_lock(self, app_id, filename):
        with self.lock:
            # si el writer esta escribiendo el archivo que necesitamos
            # entonces necesitamos su lock.
            if self.writer_file.value == filename:
                return self.writer_lck

            # si no lo esta escribiendo pero es el ultimo que toco
            # entonces tomamos nuestro lock.
            if self.write_registry.get(app_id) == filename:
                return self.reader_lck

            # si hay otros readers no nos importa.
            return _DummyLock()
