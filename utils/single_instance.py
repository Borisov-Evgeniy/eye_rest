import ctypes
import threading


class SingleInstance:
    def __init__(self,name: str):
        self.name = name
        self.mutex = None

    def acquire(self) -> bool:
        self.mutex = ctypes.windll.kernel32.CreateMutex(None,False,self.name)
        return ctypes.windll.kernel32.GetLastError() != 183