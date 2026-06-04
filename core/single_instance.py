import ctypes
from ctypes import wintypes

class SingleInstance:
    def __init__(self, name: str = "EyeRest_SingleInstance"):
        self.name = name
        self.mutex = None
        self._kernel32 = ctypes.windll.kernel32
        self._kernel32.CreateMutexW.restype = wintypes.HANDLE
        self._kernel32.CreateMutexW.argtypes = [wintypes.LPVOID,wintypes.BOOL,wintypes.LPCWSTR]
        self._kernel32.GetLastError.restype = wintypes.DWORD
        self._kernel32.CloseHandle.restype = wintypes.BOOL
        self._kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

    def acquire(self) -> bool:
        if self.mutex is not None:
            return True  # уже захвачен

        self.mutex = self._kernel32.CreateMutexW(None, False, self.name)

        if not self.mutex:
            return False

        last_error = self._kernel32.GetLastError()

        if last_error == 183:  # ERROR_ALREADY_EXISTS
            # Уже запущен другой экземпляр
            self._kernel32.CloseHandle(self.mutex)
            self.mutex = None
            return False
        return True

    def release(self):
        if self.mutex:
            self._kernel32.CloseHandle(self.mutex)
            self.mutex = None