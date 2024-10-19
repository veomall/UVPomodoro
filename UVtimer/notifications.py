from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication
from PyQt5.QtCore import Qt, QTimer
from UVtimer.constants import MICRO_REST_DURATION


class NotificationWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent, Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)

        message = "Time to focus!" if parent.is_break else "Break time!"
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 24px; color: #88C0D0;")

        self.start_button = QPushButton("Start Next Session")
        self.start_button.clicked.connect(self.accept)

        self.stop_button = QPushButton("Stop Timer")
        self.stop_button.clicked.connect(self.reject)

        layout.addWidget(self.message_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        # self.setStyleSheet(load_stylesheet('style.qss'))

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.center() - self.rect().center())


class MicroRestNotification(QDialog):
    def __init__(self, parent):
        super().__init__(parent, Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)

        self.message_label = QLabel("Take a break!")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 24px; color: #88C0D0;")

        self.time_label = QLabel(str(MICRO_REST_DURATION))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 48px; color: #88C0D0;")

        self.continue_button = QPushButton("Continue")
        self.continue_button.setEnabled(False)
        self.continue_button.clicked.connect(self.accept)

        layout.addWidget(self.message_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.continue_button)

        # self.setStyleSheet(load_stylesheet('style.qss'))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = MICRO_REST_DURATION
        self.timer.start(1000)

        # Center the notification on the screen
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.center() - self.rect().center())

    def update_timer(self):
        self.remaining_time -= 1
        self.time_label.setText(str(self.remaining_time))
        if self.remaining_time <= 0:
            self.timer.stop()
            self.continue_button.setEnabled(True)
