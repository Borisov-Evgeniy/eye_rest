from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    interval_minutes: int = 30
    break_time: int = 7
    hotkey: str = "ctrl+alt+B"
    