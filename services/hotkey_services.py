import threading
from pynput import keyboard
from PySide6.QtCore import QObject, Signal, Qt


class HotkeyWorker(QObject):
    triggered = Signal()

    def __init__(self, hotkey_str: str):
        super().__init__()
        self.hotkey_str = hotkey_str
        self.listener = None
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        try:
            pynput_hotkey = self._format_hotkey(self.hotkey_str)
            self.listener = keyboard.GlobalHotKeys({
                pynput_hotkey: self.on_activate
            })
            self.listener.start()
            print(f"[Hotkey] Слушатель запущен: {pynput_hotkey}")
            self.listener.join()
        except Exception as e:
            print(f"[Hotkey] Ошибка запуска: {e}")

    def on_activate(self):
        self.triggered.emit()

    def stop(self):
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None

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
        self.worker = None
        self.current_hotkey = None
        self._callback = None

    def register(self, hotkey: str, callback):
        if not hotkey or not hotkey.strip():
            self.unregister()
            return

        hotkey = hotkey.strip()

        if self.current_hotkey == hotkey and self.worker and self.worker.listener:
            return

        self.unregister()

        self.current_hotkey = hotkey
        self._callback = callback
        self.worker = HotkeyWorker(hotkey)
        self.worker.triggered.connect(callback, Qt.ConnectionType.QueuedConnection)
        self.worker.start()
        print(f"[HotkeyService] Зарегистрирован: {hotkey}")

    def unregister(self):
        if self.worker:
            self.worker.stop()
            if self._callback:
                try:
                    self.worker.triggered.disconnect(self._callback)
                except Exception:
                    pass
            self.worker = None
        self.current_hotkey = None
        self._callback = None