import sys
import traceback
from pathlib import Path
from core.single_instance import SingleInstance


BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "startup_log.txt"


def log(msg: str):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def main():
    log("=" * 50)
    log("STARTUP BEGIN")
    log("=" * 50)
    instance = SingleInstance("EyeRestMutex")
    if not instance.acquire():
        log("Another instance is already running. Exiting.")
        sys.exit()
    try:
        log("Step 1: Creating QApplication")
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QFont

        app = QApplication(sys.argv)

        font = QFont("Inter", 10)
        if not font.exactMatch():
            font = QFont("Segoe UI", 10)

        app.setFont(font)

        log("Step 2: import AppController")
        from controllers.app_controller import AppController
        log("OK")

        log("Step 3: create AppController")
        controller = AppController()
        log("OK")

        log("Step 4: run app")
        controller.run()
        log("App exited normally")

    except Exception as e:
        log("!!! CRITICAL ERROR !!!")
        log(str(e))
        log(traceback.format_exc())


if __name__ == "__main__":
    main()