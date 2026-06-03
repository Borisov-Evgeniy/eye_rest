from datetime import datetime, timedelta


class Scheduler:

    def __init__(self, root, interval_minutes, on_break):
        self.root = root
        self.interval_minutes = interval_minutes
        self.interval_ms = interval_minutes * 60 * 1000
        self.on_break = on_break
        self.job_id = None
        self.running = False
        self.next_break_time = None

    def start(self):
        self.running = True
        self.next_break_time = (datetime.now() + timedelta(minutes=self.interval_minutes))
        self._scheduler_next()

    def stop(self):
        self.running = False

        if self.job_id:
            self.root.after_cancel(self.job_id)

    def _scheduler_next(self):
        if not self.running:
            return
        self.job_id = self.root.after(int(self.interval_ms), self._run)

    def _run(self):
        if not self.running:
            return
        self.on_break()

    def break_finished(self):
        self.next_break_time = (datetime.now() + timedelta(minutes=self.interval_minutes))
        self._scheduler_next()

    def get_remaining_seconds(self):
        if not self.running or self.next_break_time is None:
            return 0

        delta = self.next_break_time - datetime.now()

        return max(0,int(delta.total_seconds()))