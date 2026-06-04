from enum import Enum

class AppState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    BREAK = "break"