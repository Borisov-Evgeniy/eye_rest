class Sheduler:

    def __init__(self,root,interval_minutes,on_break):
        self.root = root
        self.interval_ms = (interval_minutes * 60 * 1000)
        self.on_break = on_break
        self.job_id = None
        self.running = False

    def start(self):
        self.running = True
        self._sheduler_next()

    def stop(self):
        self.running = False

        if self.job_id:
            self.root.after_cancel(self.job_id)

    def _sheduler_next(self):
        if not self.running:
            return
        self.job_id = self.root.after(int(self.interval_ms), self._run)

    def _run(self):
        if not self.running:
            return
        self.on_break()

    def break_finished(self):
        self._sheduler_next()