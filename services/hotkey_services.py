from PySide6.QtCore import QObject, Signal, QThread, QTimer
import keyboard
import time


class HotkeyWorker(QObject):
    triggered = Signal()

    def __init__(self, hotkey_str: str):
        super().__init__()
        self.hotkey_str = hotkey_str
        self._running = True
        self._hook = None
        self._re_register_timer = None

    def run(self):
        try:
            self._register_hotkey()

            # Таймер для периодической перерегистрации (защита от сна)
            self._re_register_timer = QTimer()
            self._re_register_timer.timeout.connect(self._register_hotkey)
            self._re_register_timer.start(45000)  # каждые 45 секунд

            while self._running:
                time.sleep(0.1)

        except Exception as e:
            print(f"[Hotkey] Критическая ошибка: {e}")

    def _register_hotkey(self):
        """Безопасная (пере)регистрация"""
        try:
            if self._hook is not None:
                keyboard.remove_hotkey(self._hook)

            def on_press():
                print(f"[Hotkey] 🔥 СРАБОТАЛ: {self.hotkey_str}")
                self.triggered.emit()

            self._hook = keyboard.add_hotkey(
                self.hotkey_str.lower(),
                on_press,
                suppress=False
            )
            print(f"[Hotkey] ✓ Пере/зарегистрирован: {self.hotkey_str}")
        except Exception as e:
            print(f"[Hotkey] Ошибка регистрации: {e}")

    def stop(self):
        self._running = False
        if self._re_register_timer:
            self._re_register_timer.stop()
        if self._hook:
            try:
                keyboard.remove_hotkey(self._hook)
            except:
                pass
            self._hook = None


class HotkeyService(QObject):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None
        self.current_hotkey = None

    def register(self, hotkey: str, callback):
        if not hotkey or not hotkey.strip():
            self.unregister()
            return

        hotkey = hotkey.strip()
        if self.current_hotkey == hotkey and self.thread and self.thread.isRunning():
            return

        self.unregister()

        self.current_hotkey = hotkey
        self.worker = HotkeyWorker(hotkey)
        self.thread = QThread()

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.triggered.connect(callback)

        self.thread.start()
        print(f"[HotkeyService] Запущена регистрация: {hotkey}")

    def unregister(self):
        if self.worker:
            self.worker.stop()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(1200)

        self.thread = None
        self.worker = None
        self.current_hotkey = None