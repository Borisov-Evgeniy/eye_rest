from ui.main_window import MainWindow
from services.tray_service import TrayService

class AppController:
    def __init__(self):
        self.main_window = MainWindow()

        self.tray = TrayService(
            on_show=self.show_window,
            on_exit=self.exit
        )

    def show_window(self, *args):
        print("[DEBUG] Левый клик пойман! Передаем команду в Tkinter...")
        self.main_window.root.after(0, self.main_window.show_window)

    def hide_window(self):
        self.main_window.root.after(0, self.main_window.root.withdraw)

    def exit(self, *args):
        print("[DEBUG] Инициируем выход...")
        if self.main_window.sheduler:
            self.main_window.sheduler.stop()

        self.tray.stop()
        self.main_window.root.after(0, self.main_window.root.destroy)

    def run(self):
        self.tray.start()
        self.main_window.run()