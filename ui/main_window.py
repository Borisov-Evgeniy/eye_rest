import ctypes
import tkinter as tk
from core.scheduler import Scheduler
from models.settings import Settings
from services.hotkey_services import HotkeyService
from services.service_settings import SettingsService
from ui.break_window import BreakWindow
from core.state import AppState


class MainWindow:
    def __init__(self):
        self.settings = SettingsService.load()
        self.root = tk.Tk()
        self.root.title("Eye Rest")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        self.sсheduler = None
        self.break_window = None
        self.hotkeys = HotkeyService()
        self.build()
        self.setup_window_events()
        self.state = AppState.WORKING

    def setup_window_events(self):
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window, )

    def hide_window(self):
        self.root.withdraw()

    def show_window(self):
        self.root.after(100, self._force_show)

    def _force_show(self):
        self.root.deiconify()
        self.root.geometry("600x450")
        self.root.update_idletasks()
        hwnd = self.root.winfo_id()
        ctypes.windll.user32.ShowWindow(hwnd, 5)
        ctypes.windll.user32.SetForegroundWindow(hwnd)

    def build(self):
        tk.Label(self.root, text="Интервал работы (мин)", ).pack(pady=(10, 0))

        self.interval_entry = tk.Entry(self.root)
        self.interval_entry.insert(0, str(self.settings.interval_minutes), )
        self.interval_entry.pack(pady=5)

        tk.Label(self.root, text="Перерыв (мин)", ).pack()

        self.break_entry = tk.Entry(self.root)
        self.break_entry.insert(0, str(self.settings.break_time), )
        self.break_entry.pack(pady=5)

        tk.Label(self.root, text="Горячая клавиша", ).pack()

        self.hotkey_entry = tk.Entry(self.root)
        self.hotkey_entry.insert(0, self.settings.hotkey, )
        self.hotkey_entry.pack(pady=5)
        self.countdown_label = tk.Label(self.root, text="До перерыва: --:--")
        self.countdown_label.pack(pady=10)
        self.status_label = tk.Label(self.root, text="Таймер остановлен")
        self.status_label.pack()
        tk.Button(self.root, text="Сохранить", command=self.save, ).pack(pady=10)

        tk.Button(self.root, text="Старт", command=self.start, bg="#d4edda", ).pack(pady=5)

        tk.Button(self.root, text="Стоп", command=self.stop, bg="#f8d7da", ).pack(pady=5)

    def save(self):
        self.settings = Settings(
            interval_minutes=int(self.interval_entry.get()),
            break_time=int(self.break_entry.get()),
            hotkey=self.hotkey_entry.get())

        SettingsService.save(self.settings)

    def start(self):
        if self.sсheduler:
            self.sсheduler.stop()
            self.sсheduler = None

        self.sсheduler = Scheduler(root=self.root,
                                   interval_minutes=self.settings.interval_minutes,
                                   on_break=self.show_break, )
        self.countdown_active = False
        self.sсheduler.start()
        self.hotkeys.register(self.settings.hotkey, self.close_break, )

        self.next_break_seconds = (self.settings.interval_minutes * 60)
        self.countdown_active = True
        self.status_label.config(text=f"Таймер запущен. "
                                      f"Следующий перерыв через "
                                      f"{self.settings.interval_minutes} мин.")
        self.update_countdown()

    def stop(self):
        if self.sсheduler:
            self.sсheduler.stop()
            self.sсheduler = None

        self.countdown_active = False
        self.countdown_label.config(text="До перерыва: --:--")
        self.status_label.config(text="Таймер остановлен")

    def update_countdown(self):
        if not self.countdown_active:
            return

        seconds = self.sсheduler.get_remaining_seconds()

        mins = seconds // 60
        secs = seconds % 60

        self.countdown_label.config(text=f"До перерыва: {mins:02}:{secs:02}")
        self.root.after(1000,self.update_countdown,)

    def show_break(self):
        if self.state != AppState.WORKING:
            return

        self.state = AppState.BREAK
        self.break_window = BreakWindow(parent=self.root,
                                        break_minutes=self.settings.break_time,
                                        on_finish=self.break_finished, )

    def close_break(self):
        if not self.break_window:
            return

        self.break_window.force_close()

    def break_finished(self):
        self.break_window = None
        self.state = AppState.WORKING
        self.next_break_seconds = (self.settings.interval_minutes * 60)
        self.countdown_active = True
        self.update_countdown()
        self.sсheduler.break_finished()

    def run(self):
        self.root.mainloop()
