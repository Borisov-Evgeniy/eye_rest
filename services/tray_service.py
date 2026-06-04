import threading
import pystray
from PIL import Image, ImageDraw

def create_image():
    image = Image.new("RGB", (64, 64), "white")
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 10, 54, 54), fill="red")
    return image

class TrayService:
    def __init__(self, on_show, on_exit):
        self.on_show = on_show
        self.on_exit = on_exit
        self.icon = None

    def _run_icon(self):
        self.icon.run()

    def start(self):
        menu = pystray.Menu(
            pystray.MenuItem("Открыть", lambda icon, item: self.on_show(), default=True),
            pystray.MenuItem("Выход", lambda icon, item: self.on_exit()))

        self.icon = pystray.Icon("eye_rest", create_image(), "Eye Rest", menu=menu)
        threading.Thread(target=self._run_icon, daemon=True).start()

    def stop(self):
        if self.icon:
            self.icon.stop()