from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QMessageBox, QCheckBox,QKeySequenceEdit)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence

from core.scheduler import Scheduler
from core.app_state import AppState
from services.hotkey_services import HotkeyService
from services.service_settings import SettingsService
from core.autostart import AutoStart
from ui.break_window import BreakWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsService.load()

        self.setWindowTitle("Eye Rest")
        self.setFixedSize(580, 700)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.scheduler = None
        self.break_window = None
        self.hotkeys = HotkeyService()
        self.state = AppState.STOPPED

        self._drag_pos = None

        self._build_ui()
        self._apply_styles()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
            event.accept()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = self._create_header()
        main_layout.addWidget(header)

        settings_card = self._create_settings_card()
        main_layout.addWidget(settings_card)

        status_card = self._create_status_card()
        main_layout.addWidget(status_card, stretch=1)

        footer = self._create_footer()
        main_layout.addWidget(footer)

    def _create_header(self):
        header = QFrame()
        header.setObjectName("header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("👁️ Eye Rest")
        title.setObjectName("appTitle")

        close_btn = QPushButton("✕")
        close_btn.setObjectName("iconButton")
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.hide_window)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(close_btn)
        return header

    def _create_settings_card(self):
        card = QFrame()
        card.setObjectName("settingsCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        label1 = QLabel("Интервал работы (мин)")
        label1.setObjectName("inputLabel")
        self.interval_entry = QLineEdit()
        self.interval_entry.setObjectName("inputField")
        self.interval_entry.setText(str(self.settings.interval_minutes))

        label2 = QLabel("Перерыв (мин)")
        label2.setObjectName("inputLabel")
        self.break_entry = QLineEdit()
        self.break_entry.setObjectName("inputField")
        self.break_entry.setText(str(self.settings.break_time))

        label3 = QLabel("Горячая клавиша")
        label3.setObjectName("inputLabel")
        self.hotkey_entry = QKeySequenceEdit()
        self.hotkey_entry.setObjectName("hotkeyField")
        self.hotkey_entry.setMaximumSequenceLength(1)
        self.hotkey_entry.setKeySequence(QKeySequence(self.settings.hotkey))

        self.autostart_checkbox = QCheckBox("Запускать при старте системы")
        self.autostart_checkbox.setObjectName("web3Checkbox")
        self.autostart_checkbox.setChecked(AutoStart.is_enabled())

        save_btn = QPushButton("💾 Сохранить настройки")
        save_btn.setObjectName("saveButton")
        save_btn.clicked.connect(self.save_settings)

        layout.addWidget(label1)
        layout.addWidget(self.interval_entry)
        layout.addSpacing(4)
        layout.addWidget(label2)
        layout.addWidget(self.break_entry)
        layout.addSpacing(4)
        layout.addWidget(label3)
        layout.addWidget(self.hotkey_entry)
        layout.addSpacing(4)
        layout.addWidget(self.autostart_checkbox)
        layout.addWidget(save_btn)

        return card

    def _create_status_card(self):
        card = QFrame()
        card.setObjectName("statusCard")
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        self.status_label = QLabel("ОСТАНОВЛЕНО")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.countdown_label = QLabel("--:--")
        self.countdown_label.setObjectName("countdownTimer")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.status_label)
        layout.addWidget(self.countdown_label)
        return card

    def _create_footer(self):
        footer = QFrame()
        footer.setObjectName("footer")
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(24, 16, 24, 24)
        layout.setSpacing(12)

        self.start_btn = QPushButton("▶ Старт")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.clicked.connect(self.start)

        self.stop_btn = QPushButton("⏹ Стоп")
        self.stop_btn.setObjectName("dangerButton")
        self.stop_btn.clicked.connect(self.stop)

        self.pause_btn = QPushButton("⏸ Пауза")
        self.pause_btn.setObjectName("secondaryButton")
        self.pause_btn.clicked.connect(self.pause_resume)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.pause_btn)
        return footer

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(15, 23, 42, 0.98);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 16px;
            }
            QFrame#header {
                background-color: transparent;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QLabel#appTitle {
                color: #F8FAFC;
                font-size: 18px;
                font-weight: 700;
            }
            QFrame#settingsCard {
                background-color: rgba(30, 41, 59, 0.6);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                margin: 16px 24px 0 24px;
            }
            QLabel#inputLabel {
                color: #94A3B8;
                font-size: 12px;
                font-weight: 600;
            }
            QLineEdit#inputField {
                background-color: rgba(15, 23, 42, 0.8);
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                min-height: 14px;
            }
            QKeySequenceEdit#hotkeyField {
                background-color: rgba(15, 23, 42, 0.8);
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                min-height: 14px;
            }
            QKeySequenceEdit#hotkeyField:focus {
                border: 1px solid #8B5CF6;
            }
            QLineEdit#inputField:focus {
                border: 1px solid #8B5CF6;
            }
            QCheckBox#web3Checkbox {
                color: #CBD5E1;
                font-size: 13px;
                font-weight: 500;
                spacing: 8px;
                margin-top: 2px;
            }
            QCheckBox#web3Checkbox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                background-color: rgba(15, 23, 42, 0.8);
            }
            QCheckBox#web3Checkbox::indicator:checked {
                background-color: #8B5CF6;
                border: 1px solid #8B5CF6;
            }
            QPushButton#saveButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #8B5CF6);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
                margin-top: 8px;
                min-height: 20px;
            }
            QPushButton#saveButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #60A5FA, stop:1 #A78BFA);
            }
            QFrame#statusCard {
                background-color: rgba(30, 41, 59, 0.6);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                margin: 16px 24px 0 24px;
            }
            QLabel#statusLabel {
                color: #94A3B8;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 1px;
            }
            QLabel#countdownTimer {
                color: #F8FAFC;
                font-size: 56px;
                font-weight: 800;
                font-family: 'JetBrains Mono', 'Courier New', monospace;
            }
            QPushButton#primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 #10B981);
            }
            QPushButton#dangerButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#dangerButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F87171, stop:1 #EF4444);
            }
            QPushButton#secondaryButton {
                background-color: rgba(255, 255, 255, 0.05);
                color: #CBD5E1;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#secondaryButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
            }
            QPushButton#iconButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton#iconButton:hover {
                background-color: rgba(239, 68, 68, 0.2);
                color: #EF4444;
            }
        """)

    def hide_window(self):
        self.hide()

    def show_window(self):
        self.show()
        self.activateWindow()
        self.raise_()

    def update_countdown(self, seconds: int):
        mins = seconds // 60
        secs = seconds % 60
        self.countdown_label.setText(f"{mins:02d}:{secs:02d}")

    def set_state(self, state: AppState):
        self.state = state

        if state == AppState.RUNNING:
            if not self.scheduler:
                self.scheduler = Scheduler(
                    interval_minutes=self.settings.interval_minutes,
                    on_break=self.show_break,
                    on_countdown_update=self.update_countdown
                )
                self.scheduler.start()
            else:
                self.scheduler.resume()

            self.hotkeys.register(self.settings.hotkey, self.close_break)

        elif state == AppState.PAUSED:
            if self.scheduler:
                self.scheduler.pause()
            self.hotkeys.unregister()

        elif state == AppState.STOPPED:
            if self.scheduler:
                self.scheduler.stop()
                self.scheduler = None
            self.countdown_label.setText("--:--")
            self.hotkeys.unregister()

        elif state == AppState.BREAK:
            self.hotkeys.register(self.settings.hotkey, self.close_break)

        self.render_state()

    def render_state(self):
        if self.state == AppState.RUNNING:
            self.status_label.setText("РАБОТАЕТ")
            self.status_label.setStyleSheet("color: #10B981;")
            self.pause_btn.setText("⏸ Пауза")
        elif self.state == AppState.PAUSED:
            self.status_label.setText("ПАУЗА")
            self.status_label.setStyleSheet("color: #F59E0B;")
            self.pause_btn.setText("▶ Продолжить")
        elif self.state == AppState.STOPPED:
            self.status_label.setText("ОСТАНОВЛЕНО")
            self.status_label.setStyleSheet("color: #94A3B8;")
        elif self.state == AppState.BREAK:
            self.status_label.setText("ПЕРЕРЫВ")
            self.status_label.setStyleSheet("color: #8B5CF6;")

    def show_break(self):
        if self.state != AppState.RUNNING:
            return

        self.set_state(AppState.BREAK)

        self.break_window = BreakWindow(
            parent=self,
            break_minutes=self.settings.break_time,
            on_finish=self.break_finished,
            hotkey_hint=self.settings.hotkey
        )
        self.break_window.show()

    def break_finished(self):
        if self.break_window:
            self.break_window = None

        if self.scheduler:
            self.scheduler.stop()
            self.scheduler = None

        self.scheduler = Scheduler(
            interval_minutes=self.settings.interval_minutes,
            on_break=self.show_break,
            on_countdown_update=self.update_countdown
        )
        self.scheduler.start()

        self.set_state(AppState.RUNNING)

    def close_break(self):
        """Вызывается по хоткею"""
        if self.break_window and not self.break_window._is_closing:
            self.break_window.force_close()

    def start(self):
        self.set_state(AppState.RUNNING)

    def stop(self):
        self.set_state(AppState.STOPPED)

    def pause_resume(self):
        if self.state == AppState.PAUSED:
            self.set_state(AppState.RUNNING)
        else:
            self.set_state(AppState.PAUSED)

    def save_settings(self):
        try:
            self.settings.interval_minutes = int(self.interval_entry.text())
            self.settings.break_time = int(self.break_entry.text())
            self.settings.hotkey = self.hotkey_entry.keySequence().toString(QKeySequence.SequenceFormat.PortableText)

            SettingsService.save(self.settings)

            if self.autostart_checkbox.isChecked():
                AutoStart.enable()
            else:
                AutoStart.disable()

            if self.state == AppState.RUNNING and self.scheduler:
                self.scheduler.stop()
                self.scheduler = Scheduler(
                    interval_minutes=self.settings.interval_minutes,
                    on_break=self.show_break,
                    on_countdown_update=self.update_countdown
                )
                self.scheduler.start()

            QMessageBox.information(self, "Успешно", "Настройки сохранены!")

        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Введите корректные числа!")