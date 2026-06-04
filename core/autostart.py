import sys
import winreg

from core.config import APP_NAME


class AutoStart():
    REG_PATH = (
        r"Software\Microsoft\Windows"
        r"\CurrentVersion\Run"
    )

    @classmethod
    def enable(cls) -> None:
        if not getattr(sys, "frozen", False):
            return

        exe_path = sys.executable

        with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(
                    key,
                    APP_NAME,
                    0,
                    winreg.REG_SZ,
                    exe_path,)

    @classmethod
    def disable(cls) -> None:
        try:
            with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    cls.REG_PATH,
                    0,
                    winreg.KEY_SET_VALUE,
            ) as key:
                winreg.DeleteValue(
                    key,
                    APP_NAME,
                )

        except FileNotFoundError:
            pass

    @classmethod
    def is_enabled(cls) -> bool:
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,) as key:
                winreg.QueryValueEx(key,APP_NAME,)
            return True
        except FileNotFoundError:
            return False