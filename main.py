from ui.main_window import MainWindow
from core.single_instance import SingleInstance
from controllers.app_controller import AppController

def main():
    if not SingleInstance.acquire():

        raise SystemExit

    app = AppController()
    app.run()


if __name__ == "__main__":
    main()