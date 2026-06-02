import keyboard


class HotkeyService:

    def __init__(self):
        self.hotkey_handle = None

    def register(self, hotkey, callback):
        self.unregister()

        self.hotkey_handle = keyboard.add_hotkey(
            hotkey,
            callback
        )

    def unregister(self):
        if self.hotkey_handle:
            try:
                keyboard.remove_hotkey(self.hotkey_handle)
            except KeyError:
                pass

            self.hotkey_handle = None