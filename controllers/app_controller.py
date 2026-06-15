import sys
from services.tray_service import TrayService
from ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication


class AppController:
    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        self.main_window = MainWindow()

        self.tray = TrayService(on_show=self.main_window.show_window)

        self.tray.exit_requested.connect(self.exit)

    def exit(self, *args):
        print("[AppController] Начинаем завершение работы...")

        self.main_window.stop()

        if hasattr(self.main_window, 'break_window') and self.main_window.break_window:
            self.main_window.break_window.force_close()
            self.main_window.break_window = None

        self.tray.stop()

        self.app.quit()

    def run(self):
        self.tray.start()
        self.main_window.show()

        sys.exit(self.app.exec())