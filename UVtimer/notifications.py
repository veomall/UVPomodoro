# Import necessary modules from PyQt5
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication
from PyQt5.QtCore import Qt, QTimer
# Import the micro rest duration constant
from UVtimer.constants import MICRO_REST_DURATION


class NotificationWindow(QDialog):
    """
    A class to create and manage a notification window that appears when a Pomodoro session ends.
    """
    def __init__(self, parent):
        # Initialize the dialog with specific Qt window flags
        super().__init__(parent, Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(300, 200)

        # Create the main layout for the dialog
        layout = QVBoxLayout(self)

        # Set the message based on whether it's break time or focus time
        message = "Time to focus!" if parent.is_break else "Break time!"
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 24px; color: #88C0D0;")

        # Create buttons for starting next session and stopping the timer
        self.start_button = QPushButton("Start Next Session")
        self.start_button.clicked.connect(self.accept)

        self.stop_button = QPushButton("Stop Timer")
        self.stop_button.clicked.connect(self.reject)

        # Add widgets to the layout
        layout.addWidget(self.message_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        # Center the dialog on the screen
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.center() - self.rect().center())


class MicroRestNotification(QDialog):
    """
    A class to create and manage a notification window for micro-rest breaks.
    """
    def __init__(self, parent):
        # Initialize the dialog with specific Qt window flags
        super().__init__(parent, Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(300, 200)

        # Create the main layout for the dialog
        layout = QVBoxLayout(self)

        # Create and style the message label
        self.message_label = QLabel("Take a break!")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 24px; color: #88C0D0;")

        # Create and style the timer label
        self.time_label = QLabel(str(MICRO_REST_DURATION))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 48px; color: #88C0D0;")

        # Create the continue button (initially disabled)
        self.continue_button = QPushButton("Continue")
        self.continue_button.setEnabled(False)
        self.continue_button.clicked.connect(self.accept)

        # Add widgets to the layout
        layout.addWidget(self.message_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.continue_button)

        # TODO: Uncomment this line if you want to apply a custom stylesheet
        # self.setStyleSheet(load_stylesheet('style.qss'))

        # Set up the timer for countdown
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = MICRO_REST_DURATION
        self.timer.start(1000)  # Update every 1000 ms (1 second)

        # Center the dialog on the screen
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.center() - self.rect().center())

    def update_timer(self):
        """
        Update the timer display and enable the continue button when time is up.
        """
        self.remaining_time -= 1
        self.time_label.setText(str(self.remaining_time))
        if self.remaining_time <= 0:
            self.timer.stop()
            self.continue_button.setEnabled(True)

