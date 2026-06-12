from datetime import datetime, timedelta
from PySide6 import QTimer, QObject


class Scheduler(QObject):
    def __init__(self, interval_minutes: int, on_break, on_countdown_update=None):
        super().__init__()
        self.interval_seconds = interval_minutes * 60
        self.on_break = on_break
        self.on_countdown_update = on_countdown_update

        self.break_timer = QTimer(self)
        self.break_timer.setSingleShot(True)
        self.break_timer.timeout.connect(self._run_break)

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._update_countdown)

        self.end_time = None
        self.paused = False
        self.remaining_seconds = 0

    def start(self):
        self.end_time = datetime.now() + timedelta(seconds=self.interval_seconds)
        self.paused = False
        self._schedule_break()
        self._start_countdown()

    def stop(self):
        self.break_timer.stop()
        self.countdown_timer.stop()
        self.end_time = None
        self.paused = False
        self.remaining_seconds = 0

    def pause(self):
        if not self.end_time:
            return

        self.remaining_seconds = self.get_remaining_seconds()
        self.paused = True
        self.break_timer.stop()
        self.countdown_timer.stop()

    def resume(self):
        if self.remaining_seconds <= 0:
            self.remaining_seconds = self.interval_seconds
        self.end_time = datetime.now() + timedelta(seconds=self.remaining_seconds)
        self.paused = False
        self._schedule_break()
        self._start_countdown()

    def _schedule_break(self):
        if not self.end_time:
            return

        remaining = self.get_remaining_seconds()
        delay_ms = int(remaining*1000)

        self.break_timer.start(delay_ms)

    def _run_break(self):
        self.break_timer.stop()
        self.countdown_timer.stop()

        self.on_break()

    def _start_countdow(self):
        self.countdown_timer.start(1000)
        self._update_countdown()

    def _update_countdown(self):
        if self.paused or not self.end_time:
            return

        remaining = self.get_remaining_seconds()

        if self.on_countdown_update:
            self.on_countdown_update(remaining)

        if remaining <= 0:
            self.countdown_timer.stop()

    def get_remaining_seconds(self):
        if not self.end_time or self.paused:
            return  self.remaining_seconds

        delta = self.end_time - datetime.now()
        return max(0, int(delta.total_seconds()))