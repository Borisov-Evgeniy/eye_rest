import sys
from pathlib import Path
import winreg
from core.config import APP_NAME


class AutoStart():
    if sys.platform == "win32":
        REG_PATH = (r"Software\Microsoft\Windows"
                    r"\CurrentVersion\Run")

    @classmethod
    def enable(cls) -> None:
        if sys.platform == "win32":
            cls._enable_windows()
        else:
            cls._enable_linux()

    @classmethod
    def disable(cls):
        if sys.platform == "win32":
            cls._disable_windows()
        else:
            cls._disable_linux()

    def is_enabled(cls):
        if sys.platform == "win32":
            return cls._is_enabled_winodws()
        else:
            return cls._is_enabled_linux()

# ============= Windows ========================== #
    @classmethod
    def _enable_windows(cls) -> None:
        if not getattr(sys, "frozen", False):
            return

        exe_path = sys.executable

        with cls.winreg.OpenKey(
                cls.winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                cls.winreg.KEY_SET_VALUE,
        ) as key: cls.winreg.SetValueEx(key, APP_NAME, 0, cls.winreg.REG_SZ, exe_path)

    @classmethod
    def _disable_windows(cls) -> None:
        try:
            with cls.winreg.OpenKey(
                    cls.winreg.HKEY_CURRENT_USER,
                    cls.REG_PATH,
                    0,
                    cls.winreg.KEY_SET_VALUE,
            ) as key: cls.winreg.DeleteValue(key,APP_NAME,)

        except FileNotFoundError:
            pass

    @classmethod
    def is_enabled_windows(cls) -> bool:
        try:
            with cls.winreg.OpenKey(
                cls.winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,) as key:
                cls.winreg.QueryValueEx(key,APP_NAME,)
            return True
        except FileNotFoundError:
            return False

# === === === === === Linux === === === === === #
    @classmethod
    def _enable_linux(cls) -> None:
        if not getattr(sys, "frozen", False):
            return

        exe_path = sys.executable

        autostart_dir = Path.home() /".congig" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)

        desktop_file = autostart_dir / "eye-rest.desktop"

        content = f"""[Desktop Entry]
        Type=Application
        Name={APP_NAME}
        Exec={exe_path}
        Hidden=false
        NoDisplay=false
        X-GNOME-Autostart-enabled=true
        Comment=Eye Rest Application
        """
        desktop_file.write_text(content)

    @classmethod
    def _disable_linux(cls) -> None:
        desktop_file = Path.home() / ".config" / "autostart" / "eye-rest.desktop"
        if desktop_file.exists():
            desktop_file.unlink()

    def is_enabled_linux(cls) -> bool:
        desktop_file = Path.home() / ".config" / "autostart" / "eye-rest.desktop"
        return desktop_file.exists()