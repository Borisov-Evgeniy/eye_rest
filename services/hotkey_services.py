from pynput import keyboard
from PySide6.QtCore import QObject, Signal, QThread
import time


class HotkeyWorker(QObject):
    triggered = Signal()

    def __init__(self, hotkey_str: str):
        super().__init__()
        self.hotkey_str = hotkey_str
        self.listener = None
        self._running = True

    def run(self):
        try:
            pynput_hotkey = self._format_hotkey(self.hotkey_str)
            self.listener = keyboard.GlobalHotKeys({
                pynput_hotkey: self.on_activate
            })
            self.listener.start()
            print(f"[Hotkey] Слушатель запущен: {pynput_hotkey}")

            while self._running and getattr(self.listener, 'running', True):
                time.sleep(0.1)

        except Exception as e:
            print(f"[Hotkey] Ошибка запуска: {e}")

    def on_activate(self):
        self.triggered.emit()

    def stop(self):
        self._running = False
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
            self.listener = None

    def _format_hotkey(self, hotkey_str: str) -> str:
        parts = [p.strip().lower() for p in hotkey_str.split('+')]
        mapping = {
            'ctrl': '<ctrl>', 'control': '<ctrl>',
            'alt': '<alt>',
            'shift': '<shift>',
            'win': '<win>', 'super': '<win>',
            'cmd': '<cmd>', 'command': '<cmd>',
        }
        formatted = [mapping.get(p, p) for p in parts]
        return '+'.join(formatted)


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
        print(f"[HotkeyService] Зарегистрирован: {hotkey}")

    def unregister(self):
        if self.worker:
            self.worker.stop()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(1000)

        self.thread = None
        self.worker = None
        self.current_hotkey = None