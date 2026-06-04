from datetime import datetime, timedelta
import tkinter as tk


class Scheduler:
    def __init__(self, root: tk.Tk, interval_minutes: int, on_break, on_countdown_update=None):
        self.root = root
        self.interval_seconds = interval_minutes * 60
        self.on_break = on_break
        self.on_countdown_update = on_countdown_update  # ← Новый параметр!

        self.job_id = None
        self.update_job = None
        self.end_time = None
        self.paused = False
        self.remaining_seconds = 0

    def start(self):
        self.end_time = datetime.now() + timedelta(seconds=self.interval_seconds)
        self.paused = False
        self._schedule()
        self._start_countdown_update()

    def stop(self):
        self._cancel_all_jobs()
        self.end_time = None
        self.paused = False

    def pause(self):
        if not self.end_time:
            return
        self.remaining_seconds = self.get_remaining_seconds()
        self.paused = True
        self._cancel_all_jobs()

    def resume(self):
        if self.remaining_seconds <= 0:
            self.remaining_seconds = self.interval_seconds
        self.end_time = datetime.now() + timedelta(seconds=self.remaining_seconds)
        self.paused = False
        self._schedule()
        self._start_countdown_update()

    def _cancel_all_jobs(self):
        if self.job_id:
            self.root.after_cancel(self.job_id)
            self.job_id = None
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None

    def _schedule(self):
        if not self.end_time:
            return
        delay = int(self.get_remaining_seconds() * 1000)
        self.job_id = self.root.after(delay, self._run)

    def _run(self):
        self.job_id = None
        self.on_break()

    def _start_countdown_update(self):
        self._update_countdown()

    def _update_countdown(self):
        if self.paused or not self.end_time:
            return

        remaining = self.get_remaining_seconds()

        if self.on_countdown_update:
            self.on_countdown_update(remaining)

        if remaining > 0:
            self.update_job = self.root.after(1000, self._update_countdown)
        else:
            self.update_job = None

    def get_remaining_seconds(self) -> int:
        if not self.end_time or self.paused:
            return self.remaining_seconds
        delta = self.end_time - datetime.now()
        return max(0, int(delta.total_seconds()))