import threading
import pystray
from PIL import Image, ImageDraw
from PySide6.QtCore import QObject, Signal

def create_image():
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 10, 54, 54), fill="red")
    return image

class TrayService(QObject):
    exit_requested = Signal()

    def __init__(self, on_show):
        super().__init__()
        self.on_show = on_show
        self.icon = None

    def _run_icon(self):
        self.icon.run()

    def start(self):
        menu = pystray.Menu(
            pystray.MenuItem("Открыть", lambda icon, item: self.on_show(), default=True),
            pystray.MenuItem("Выход", lambda icon, item: self.exit_requested.emit()))

        self.icon = pystray.Icon("eye_rest", create_image(), "Eye Rest", menu=menu)
        threading.Thread(target=self._run_icon, daemon=True).start()

    def stop(self):
        if self.icon:
            self.icon.stop()
            self.icon = None