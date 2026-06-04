import sys
import traceback
from pathlib import Path
from utils.single_instance import SingleInstance


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
        sys.exit()
    try:
        log("Step 1: import AppController")
        from controllers.app_controller import AppController
        log("OK")
        log("Step 2: create AppController")
        app = AppController()
        log("OK")
        log("Step 3: run app")
        app.run()
        log("App exited normally")

    except Exception as e:
        log("!!! CRITICAL ERROR !!!")
        log(str(e))
        log(traceback.format_exc())


if __name__ == "__main__":
    main()