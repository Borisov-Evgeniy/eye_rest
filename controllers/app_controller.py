import sys
from services.tray_service import TrayService
from ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication


class AppController:
    def __init__(self):
        self.main_window = MainWindow()

        self.tray = TrayService(on_show=self.main_window.show_window,
                                on_exit=self.exit)

    def exit(self, *args):
        self.main_window.stop()
        self.tray.stop()
        QApplication.quit()

    def run(self):
        self.tray.start()
        self.main_window.show()
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        app.exec_()