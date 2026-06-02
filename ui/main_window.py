import tkinter as tk

from core.sheduler import Sheduler
from models.settings import Settings
from services.hotkey_services import HotkeyService
from services.service_settings import SettingsService
from ui.break_window import BreakWindow


class MainWindow:

    def __init__(self):
        self.settings = SettingsService.load()

        self.root = tk.Tk()
        self.root.title("Eye Rest")

        self.sheduler = None
        self.break_window = None

        self.hotkeys = HotkeyService()

        self.build()

    def build(self):
        tk.Label(self.root, text="Интервал работы").pack()

        self.interval_entry = tk.Entry(self.root)
        self.interval_entry.insert(0, str(self.settings.interval_minutes))
        self.interval_entry.pack()

        tk.Label(self.root, text="Перерыв").pack()

        self.break_entry = tk.Entry(self.root)
        self.break_entry.insert(0, str(self.settings.break_time))
        self.break_entry.pack()

        tk.Label(self.root, text="Горячая клавиша").pack()

        self.hotkey_entry = tk.Entry(self.root)
        self.hotkey_entry.insert(0, self.settings.hotkey)
        self.hotkey_entry.pack()

        tk.Button(
            self.root,
            text="Сохранить",
            command=self.save
        ).pack()

        tk.Button(
            self.root,
            text="Старт",
            command=self.start
        ).pack()

    def save(self):
        self.settings = Settings(
            interval_minutes=int(self.interval_entry.get()),
            break_time=int(self.break_entry.get()),
            hotkey=self.hotkey_entry.get(),
        )

        SettingsService.save(self.settings)

    def start(self):
        if self.sheduler:
            self.sheduler.stop()

        self.sheduler = Sheduler(
            root=self.root,
            interval_minutes=self.settings.interval_minutes,
            on_break=self.show_break,
        )

        self.sheduler.start()

    def show_break(self):
        if self.break_window:
            return

        self.break_window = BreakWindow(
            parent=self.root,
            break_minutes=self.settings.break_time,
            on_finish=self.break_finished,
        )

        self.hotkeys.register(
            self.settings.hotkey,
            self.close_break,
        )

    def close_break(self):
        if not self.break_window:
            return

        self.break_window.force_close()

    def break_finished(self):
        self.break_window = None
        self.sheduler.break_finished()

    def run(self):
        self.root.mainloop()