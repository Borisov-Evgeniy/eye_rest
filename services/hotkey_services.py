import keyboard


class HotkeyService:
    def __init__(self):
        self.current_hotkey = None

    def register(self,hotkey,callback):
        self.unrigister()

        keyboard.add_hotkey(hotkey,callback)

        self.current_hotkey = hotkey

    def unrigester(self):
        keyboard.clear_all_hotkeys()