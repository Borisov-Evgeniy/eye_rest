import threading
import pystray
from PIL import Image, ImageDraw
from PySide6.QtCore import QObject, Signal

def create_image():
    from pathlib import Path
    icon_path = Path(__file__).parent.parent / "icon.png"
    if icon_path.exists():
        return Image.open(icon_path)
    else:
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([16, 16, 48, 48], fill='#10B981')
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