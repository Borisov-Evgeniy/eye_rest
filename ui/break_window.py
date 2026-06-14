from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class BreakWindow(QMainWindow):
    def __init__(self,parent,break_minutes: int, on_finish):
        super().__init__()
        self.parent_window = parent
        self.seconds = break_minutes * 60
        self.on_finish = on_finish

        self.setWindowTitle("Перерыв")
        self.setFixedSize(900, 400)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint |
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui()
        self._apply_styles()
        self._center_on_screen()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(24)

        title = QLabel("Сделай перерыв для глаз! 🧐")
        title.setObjectName("breakTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer_label = QLabel("20:00")
        self.timer_label.setObjectName("breakTimer")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hint = QLabel("Закройте глаза и расслабьтесь")
        hint.setObjectName("breakHint")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(self.timer_label)
        layout.addWidget(hint)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(15, 23, 42, 0.95);
                border: 2px solid rgba(139, 92, 246, 0.5); /* Яркая фиолетовая рамка */
                border-radius: 24px;
            }
            QLabel#breakTitle {
                color: #F8FAFC;
                font-size: 32px;
                font-weight: 700;
            }
            QLabel#breakTimer {
                color: transparent; /* Делаем сам текст прозрачным, чтобы виден был только фон-градиент */
                font-size: 96px;
                font-weight: 800;
                font-family: 'JetBrains Mono', 'Courier New', monospace;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #A855F7, stop:1 #EC4899);
                -webkit-background-clip: text; /* Магия Qt6: обрезает градиент по форме текста */
            }
            QLabel#breakHint {
                color: #94A3B8;
                font-size: 16px;
                font-style: italic;
            }
        """)

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()  # Получаем размеры основного монитора
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_timer(self):
        mins = self.seconds // 60
        secs = self.seconds % 60
        self.timer_label.setText(f"{mins:02d}:{secs:02d}")

        if self.seconds > 0:
            self.seconds -= 1
        else:
            self.force_close()

    def force_close(self):
        self.timer.stop()
        self.close()
        self.on_finish()

    def closeEvent(self, event):
        if self.seconds > 0:
            event.ignore()
        else:
            event.accept()