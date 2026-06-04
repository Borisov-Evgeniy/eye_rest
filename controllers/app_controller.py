from services.tray_service import TrayService
from ui.main_window import MainWindow


class AppController:

    def __init__(self):
        self.main_window = MainWindow()

        self.tray = TrayService(
            on_show=self.main_window.show_window,
            on_exit=self.exit
        )

    def exit(self, *args):
        self.main_window.stop()
        self.tray.stop()
        self.main_window.root.destroy()

    def run(self):
        self.tray.start()
        self.main_window.run()