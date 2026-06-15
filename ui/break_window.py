from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QApplication, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from pathlib import Path


class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(380, 380)
        self._value = 100

        self.timer_label = QLabel(self)
        self.timer_label.setGeometry(0, 0, 380, 380)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 72px;
            font-weight: 800;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            background: transparent;
            text-shadow: 0px 0px 20px rgba(45, 212, 191, 0.6);
        """)
        self.timer_label.setText("20:00")

    def setValue(self, value):
        self._value = max(0, min(100, value))
        self.update()

    def setTimerText(self, text):
        self.timer_label.setText(text)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = (self.width() - 40) // 2

        rect = QRect(center_x - radius, center_y - radius, radius * 2, radius * 2)

        bg_pen = QPen(QColor(45, 212, 191, 25), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawEllipse(rect)

        progress_pen = QPen(QColor(45, 212, 191), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(progress_pen)

        span_angle = int(360 * (self._value / 100))
        painter.drawArc(rect, 90 * 16, -span_angle * 16)


class BreakWindow(QMainWindow):
    def __init__(self, parent, break_minutes: int, on_finish, hotkey_hint: str = ""):
        super().__init__(parent)

        self.parent_window = parent
        self.total_seconds = break_minutes * 60
        self.seconds = self.total_seconds
        self.on_finish = on_finish

        self._is_closing = False

        self.setWindowTitle("Перерыв")
        self.setFixedSize(1300, 650)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._build_ui()
        self._apply_styles()
        self._center_on_screen()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.bg_label = QLabel(central_widget)
        self.bg_label.setObjectName("backgroundLabel")
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()

        content_widget = QWidget()
        content_widget.setObjectName("glassCard")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.setSpacing(40)

        content_layout.addStretch(2)

        title = QLabel("Сделай перерыв для глаз")
        title.setObjectName("breakTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        circle_layout = QHBoxLayout()
        circle_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        circle_layout.addStretch(4)
        self.circular_progress = CircularProgressBar()
        circle_layout.addWidget(self.circular_progress)
        circle_layout.addStretch(2)

        hint = QLabel("Закройте глаза и расслабьтесь")
        hint.setObjectName("breakHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addWidget(title)
        content_layout.addLayout(circle_layout)
        content_layout.addWidget(hint)
        content_layout.addStretch(3)

        main_layout.addWidget(content_widget)
        self._load_background_image()

    def _load_background_image(self):
        base_dir = Path(__file__).resolve().parent.parent
        image_path = base_dir / "background.jpg"

        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.bg_label.setPixmap(scaled_pixmap)
            else:
                self._set_fallback_background()
        else:
            self._set_fallback_background()

    def _set_fallback_background(self):
        self.bg_label.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                stop:0 #0f172a, stop:0.5 #134e4a, stop:1 #0f172a);
            border-radius: 32px;
        """)

    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget#glassCard {
                background-color: rgba(0, 0, 0, 0.65);
                border-radius: 40px;
                border: 1px solid rgba(45, 212, 191, 0.15);
                margin: 60px;
            }
            QLabel#breakTitle {
                color: #FFFFFF;
                font-size: 42px;
                font-weight: 700;
                letter-spacing: 1.5px;
                text-shadow: 0px 4px 20px rgba(0, 0, 0, 0.9);
            }
            QLabel#breakHint {
                color: rgba(255, 255, 255, 0.75);
                font-size: 19px;
                font-style: italic;
                font-weight: 400;
                text-shadow: 0px 2px 10px rgba(0, 0, 0, 0.9);
            }
        """)

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_timer(self):
        if self._is_closing:
            return

        mins = self.seconds // 60
        secs = self.seconds % 60
        time_str = f"{mins:02d}:{secs:02d}"

        self.circular_progress.setTimerText(time_str)

        progress_percent = (self.seconds / self.total_seconds) * 100
        self.circular_progress.setValue(progress_percent)

        if self.seconds > 0:
            self.seconds -= 1
        else:
            self.force_close()

    def force_close(self):
        if self._is_closing:
            return

        self._is_closing = True
        self.timer.stop()

        if self.on_finish:
            self.on_finish()

        self.close()

    def keyPressEvent(self, event):
        if self._is_closing:
            return
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Space):
            event.accept()
            self.force_close()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        if self._is_closing or self.seconds == 0:
            event.accept()
        else:
            event.ignore()