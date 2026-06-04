import tkinter as tk
from tkinter import messagebox
import ctypes
from core.scheduler import Scheduler
from core.app_state import AppState
from services.hotkey_services import HotkeyService
from services.service_settings import SettingsService
from ui.break_window import BreakWindow


class MainWindow:
    def __init__(self):
        self.settings = SettingsService.load()
        self.root = tk.Tk()
        self.root.title("Eye Rest")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        self.scheduler = None
        self.break_window = None
        self.hotkeys = HotkeyService()
        self.state = AppState.STOPPED
        self.build()
        self.setup_window_events()

    def setup_window_events(self):
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

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

        tk.Label(self.root, text="Интервал работы (мин)", font=("Arial", 10)).pack(pady=(20, 0))

        self.interval_entry = tk.Entry(self.root, width=15, font=("Arial", 11))
        self.interval_entry.insert(0, str(self.settings.interval_minutes))
        self.interval_entry.pack(pady=5)

        tk.Label(self.root, text="Перерыв (мин)", font=("Arial", 10)).pack(pady=(10, 0))

        self.break_entry = tk.Entry(self.root, width=15, font=("Arial", 11))
        self.break_entry.insert(0, str(self.settings.break_time))
        self.break_entry.pack(pady=5)

        tk.Label(self.root, text="Горячая клавиша", font=("Arial", 10)).pack(pady=(10, 0))

        self.hotkey_entry = tk.Entry(self.root, width=15, font=("Arial", 11))
        self.hotkey_entry.insert(0, self.settings.hotkey)
        self.hotkey_entry.pack(pady=5)

        tk.Button(self.root, text="Сохранить настройки",
                  command=self.save_settings,
                  bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(pady=15)

        self.status_label = tk.Label(self.root, text="Остановлено",
                                     font=("Arial", 12, "bold"), fg="gray")
        self.status_label.pack(pady=(10, 0))

        self.countdown_label = tk.Label(self.root,
                                        text="До перерыва: --:--",
                                        font=("Arial", 16, "bold"), fg="#00ff88")
        self.countdown_label.pack(pady=8)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Старт", command=self.start,
                  bg="#4CAF50", fg="white", width=12, font=("Arial", 10, "bold")).pack(side="left", padx=8)

        tk.Button(btn_frame, text="Стоп", command=self.stop,
                  bg="#f44336", fg="white", width=12, font=("Arial", 10, "bold")).pack(side="left", padx=8)

        self.pause_button = tk.Button(btn_frame, text="Пауза", command=self.pause_resume,
                                      bg="#ff9800", fg="white", width=12, font=("Arial", 10, "bold"))
        self.pause_button.pack(side="left", padx=8)

    def update_countdown(self, seconds: int):
        mins = seconds // 60
        secs = seconds % 60
        self.countdown_label.config(text=f"До перерыва: {mins:02d}:{secs:02d}")

    def set_state(self, state: AppState):
        self.state = state

        if state == AppState.RUNNING:
            if not self.scheduler:
                self.scheduler = Scheduler(
                    root=self.root,
                    interval_minutes=self.settings.interval_minutes,
                    on_break=self.show_break,
                    on_countdown_update=self.update_countdown)
                self.scheduler.start()
            else:
                self.scheduler.resume()

            self.hotkeys.register(self.settings.hotkey, self.close_break)

        elif state == AppState.PAUSED:
            if self.scheduler:
                self.scheduler.pause()

        elif state == AppState.STOPPED:
            if self.scheduler:
                self.scheduler.stop()
                self.scheduler = None
            self.countdown_label.config(text="До перерыва: --:--")
            self.hotkeys.unregister()

        elif state == AppState.BREAK:
            self.status_label.config(text="Перерыв")

        self.render_state()

    def render_state(self):
        if self.state == AppState.RUNNING:
            self.status_label.config(text="Работает")
            self.pause_button.config(text="Пауза")
        elif self.state == AppState.PAUSED:
            self.status_label.config(text="Пауза")
            self.pause_button.config(text="Продолжить")
        elif self.state == AppState.STOPPED:
            self.status_label.config(text="Остановлено")

    def start(self):
        self.set_state(AppState.RUNNING)

    def stop(self):
        self.set_state(AppState.STOPPED)

    def pause_resume(self):
        if self.state == AppState.PAUSED:
            self.set_state(AppState.RUNNING)
        else:
            self.set_state(AppState.PAUSED)

    def show_break(self):
        if self.state != AppState.RUNNING:
            return
        self.set_state(AppState.BREAK)
        self.break_window = BreakWindow(parent=self.root, break_minutes=self.settings.break_time,
                                        on_finish=self.break_finished)

    def break_finished(self):
        self.break_window = None
        self.set_state(AppState.RUNNING)

    def close_break(self):
        if self.break_window:
            self.break_window.force_close()

    def save_settings(self):
        try:
            self.settings.interval_minutes = int(self.interval_entry.get())
            self.settings.break_time = int(self.break_entry.get())
            self.settings.hotkey = self.hotkey_entry.get().strip()

            SettingsService.save(self.settings)

            if self.state == AppState.RUNNING and self.scheduler:
                self.scheduler.stop()
                self.scheduler = Scheduler(
                    root=self.root,
                    interval_minutes=self.settings.interval_minutes,
                    on_break=self.show_break
                )
                self.scheduler.start()

            tk.messagebox.showinfo("Успешно", "Настройки сохранены!")

        except ValueError:
            tk.messagebox.showerror("Ошибка", "Введите корректные числа!")

    def run(self):
        self.root.mainloop()
