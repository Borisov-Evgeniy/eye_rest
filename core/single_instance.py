import sys
import ctypes
from ctypes import wintypes
from pathlib import Path


class SingleInstance:
    def __init__(self, name: str = "EyeRest"):
        self.name = name
        self.lock_file = None
        self.lock_fd = None

    def acquire(self) -> bool:
        if sys.platform == "win32":
            return self._acquire_windows()
        else:
            return self._acquire_unix()

    def _acquire_windows(self):
        self._kernel32 = ctypes.windll.kernel32
        self._kernel32.CreateMutexW.restype = wintypes.HANDLE
        self._kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]

        self._kernel32.GetLastError.restype = wintypes.DWORD

        self._kernel32.CloseHandle.restype = wintypes.BOOL
        self._kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

        self.lock_file = self._kernel32.CreateMutexW(None, False, self.name)

        if not self.lock_file:
            return False

        last_error = self._kernel32.GetLastError()

        if last_error == 183:
            self._kernel32.CloseHandle(self.lock_file)
            self.lock_file = None
            return False
        return True

    def _acquire_unix(self):
        import os
        import fcntl

        lock_dir = Path.home() / ".cache" / "eye_rest"
        lock_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file = lock_dir / "lock"

        try:
            self.lock_fd = open(self.lock_file, 'w')
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lock_fd.write(str(os.getpid()))
            self.lock_fd.flush()
            return True
        except (IOError, OSError):
            if self.lock_fd:
                self.lock_fd.close()
            return False

    def release(self):
        if sys.platform == "win32":
            if self.lock_file:
                self._kernel32.CloseHandle(self.lock_file)
                self.lock_file = None
        else:
            # ИСПРАВЛЕНИЕ: Импортируем fcntl здесь на случай, если метод вызван в Linux
            import fcntl

            if self.lock_fd:
                try:
                    fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
                    self.lock_fd.close()
                    self.lock_fd = None

                    if self.lock_file and self.lock_file.exists():
                        self.lock_file.unlink()
                except Exception:
                    pass