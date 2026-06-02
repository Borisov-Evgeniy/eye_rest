import ctypes


class SingleInstance:

    MUTEX_NAME = "EyeRestMutex"

    @classmethod
    def acquire(cls):

        mutex = ctypes.windll.kernel32.CreateMutexW(
            None,
            False,
            cls.MUTEX_NAME,
        )

        error = ctypes.windll.kernel32.GetLastError()

        ERROR_ALREADY_EXISTS = 183

        if error == ERROR_ALREADY_EXISTS:
            return False

        return True