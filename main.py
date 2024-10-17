import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QSlider, QCheckBox, QPushButton, QLabel, QDialog)
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl, QSize
from PyQt5.QtGui import QColor, QPainter, QPainterPath
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
import os


# Constants
MICRO_REST_MIN = 120
MICRO_REST_MAX = 180
MICRO_REST_DURATION = 10

RUN_MIN = 10
RUN_MAX = 90
REST_MIN = 3
REST_MAX = 15
LONG_REST_MIN = 10
LONG_REST_MAX = 30


def load_stylesheet(file_path):
    with open(file_path, 'r') as f:
        return f.read()


class IconButton(QPushButton):
    def __init__(self, color, icon_path, parent=None):
        super().__init__(parent)
        self.color = color
        self.icon_path = icon_path
        self.setFixedSize(32, 32)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw button background
        painter.setBrush(QColor(self.color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.rect())

        # Draw icon
        painter.setBrush(Qt.white)
        painter.setPen(Qt.white)
        path = QPainterPath()

        if self.icon_path == "pause":
            path.addRect(8, 8, 6, 16)
            path.addRect(18, 8, 6, 16)
        elif self.icon_path == "play":
            path.moveTo(12, 8)
            path.lineTo(24, 16)
            path.lineTo(12, 24)
            path.closeSubpath()
        elif self.icon_path == "stop":
            path.addRect(8, 8, 16, 16)
        elif self.icon_path == "music":
            path.moveTo(8, 8)
            path.lineTo(8, 24)
            path.moveTo(14, 6)
            path.lineTo(14, 26)
            path.moveTo(20, 10)
            path.lineTo(20, 22)
            path.moveTo(26, 14)
            path.lineTo(26, 18)
        elif self.icon_path == "skip":
            path.moveTo(8, 8)
            path.lineTo(8, 24)
            path.lineTo(18, 16)
            path.closeSubpath()
            path.moveTo(18, 8)
            path.lineTo(18, 24)
            path.lineTo(28, 16)
            path.closeSubpath()

        painter.drawPath(path)

    def hitButton(self, pos):
        # Check if the click is within the circular area
        center = self.rect().center()
        distance = ((pos.x() - center.x()) ** 2 + (pos.y() - center.y()) ** 2) ** 0.5
        return distance <= self.width() / 2

    def sizeHint(self):
        return QSize(32, 32)

    def minimumSizeHint(self):
        return QSize(32, 32)


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer - Settings")
        self.setFixedSize(400, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.run_time_slider = self.create_slider_with_label("Run Time (minutes):", RUN_MIN, RUN_MAX, 25)
        self.rest_time_slider = self.create_slider_with_label("Rest Time (minutes):", REST_MIN, REST_MAX, 5)
        self.long_rest_time_slider = self.create_slider_with_label("Long Rest Time (minutes):", LONG_REST_MIN, LONG_REST_MAX, 15)
        self.sessions_before_long_rest_slider = self.create_slider_with_label("Sessions Before Long Rest:", 2, 10, 4)

        self.activate_micro_rest = QCheckBox("Activate Micro Rest")
        self.display_session_counter = QCheckBox("Display Session Counter")
        self.display_music_controller = QCheckBox("Display Music Controller")

        self.start_button = QPushButton("Start Timer")
        self.start_button.clicked.connect(self.start_timer)

        layout.addWidget(self.activate_micro_rest)
        layout.addWidget(self.display_session_counter)
        layout.addWidget(self.display_music_controller)
        layout.addWidget(self.start_button)

    def create_slider_with_label(self, label_text, min_value, max_value, default_value):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 0, 10, 0)

        label_container = QWidget()
        label_layout = QHBoxLayout(label_container)
        label_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        value_label = QLabel(str(default_value))
        
        label_layout.addWidget(label)
        label_layout.addStretch()
        label_layout.addWidget(value_label)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(default_value)

        slider.valueChanged.connect(lambda v: value_label.setText(str(v)))

        layout.addWidget(label_container)
        layout.addWidget(slider)

        self.centralWidget().layout().addWidget(container)
        return slider

    def start_timer(self):
        settings = {
            'run_time': self.run_time_slider.value(),
            'rest_time': self.rest_time_slider.value(),
            'long_rest_time': self.long_rest_time_slider.value(),
            'sessions_before_long_rest': self.sessions_before_long_rest_slider.value(),
            'activate_micro_rest': self.activate_micro_rest.isChecked(),
            'display_session_counter': self.display_session_counter.isChecked(),
            'display_music_controller': self.display_music_controller.isChecked()
        }
        self.timer_window = TimerWindow(settings)
        self.timer_window.show()
        self.hide()


class TimerWindow(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        window_height = 140
        self.setFixedWidth(200)
        self.setFixedHeight(window_height)

        self.layout = QVBoxLayout(self)

        self.time_label = QLabel(f"{self.settings['run_time']:02d}:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 48px; color: #88C0D0;")

        self.layout.addWidget(self.time_label)

        if self.settings['display_session_counter']:
            self.session_label = QLabel("Session: 1")
            self.session_label.setAlignment(Qt.AlignCenter)
            self.session_label.setStyleSheet("font-size: 14px; color: #D8DEE9;")
            self.layout.addWidget(self.session_label)

            window_height += 10
            self.setFixedHeight(window_height)

        if self.settings['display_music_controller']:
            music_control_layout = QHBoxLayout()

            self.music_toggle_button = IconButton("#A3BE8C", "music")
            self.music_toggle_button.clicked.connect(self.toggle_background_music)
            music_control_layout.addWidget(self.music_toggle_button)

            self.volume_slider = QSlider(Qt.Horizontal)
            self.volume_slider.setRange(0, 100)
            self.volume_slider.setValue(50)
            self.volume_slider.setFixedWidth(80)
            self.volume_slider.valueChanged.connect(self.set_background_music_volume)
            music_control_layout.addWidget(self.volume_slider)

            self.layout.addLayout(music_control_layout)

            self.background_playlist = QMediaPlaylist()
            self.load_background_music()
            self.background_playlist.setPlaybackMode(QMediaPlaylist.Loop)

            self.background_music = QMediaPlayer()
            self.background_music.setPlaylist(self.background_playlist)
            self.background_music.setVolume(50)
            self.background_music.play()

            window_height += 30
            self.setFixedHeight(window_height)

        button_layout = QHBoxLayout()
        self.pause_button = IconButton("#5E81AC", "pause")
        self.pause_button.clicked.connect(self.toggle_pause)

        self.stop_button = IconButton("#BF616A", "stop")
        self.stop_button.clicked.connect(self.stop_timer)

        self.skip_button = IconButton("#EBCB8B", "skip")  # New skip button
        self.skip_button.clicked.connect(self.skip_session)  # Connect to new method

        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.skip_button)  # Add skip button to layout

        self.layout.addLayout(button_layout)

        self.setStyleSheet(load_stylesheet('style.qss'))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = self.settings['run_time'] * 60
        self.is_break = False
        self.session_count = 1

        self.micro_rest_timer = QTimer(self)
        self.micro_rest_timer.timeout.connect(self.show_micro_rest)

        self.start_timer()

        # Mouse event tracking for window movement
        self.moving = False
        self.offset = QPoint()

        # Sound effects
        self.notification_sound = QMediaPlayer()
        self.notification_sound.setMedia(QMediaContent(QUrl.fromLocalFile("notification.mp3")))

    def load_background_music(self):
        music_dir = "bg_music"
        if os.path.exists(music_dir):
            for file in random.sample(os.listdir(music_dir), len(os.listdir(music_dir))):
                if file.endswith((".mp3", ".wav", ".ogg")):
                    self.background_playlist.addMedia(QMediaContent(QUrl.fromLocalFile(os.path.join(music_dir, file))))

    def skip_session(self):
        self.notification_sound.play()
        self.show_notification()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(46, 52, 64, 180))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.moving:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = False

    def start_timer(self):
        minutes, seconds = divmod(self.remaining_time, 60)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        self.timer.start(1000)
        if not self.is_break:
            self.start_micro_rest_timer()

    def update_timer(self):
        self.remaining_time -= 1
        minutes, seconds = divmod(self.remaining_time, 60)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        if self.remaining_time <= 0:
            self.notification_sound.play()
            self.show_notification()

    def show_notification(self):
        self.timer.stop()
        self.micro_rest_timer.stop()
        notification = NotificationWindow(self)
        if notification.exec_() == QDialog.Accepted:
            self.toggle_session()
            self.start_timer()
        else:
            self.close()
            self.settings_window = SettingsWindow()
            self.settings_window.show()

    def toggle_session(self):
        if self.is_break:
            self.is_break = False
            self.remaining_time = self.settings['run_time'] * 60
            self.session_count += 1
            if self.settings['display_session_counter']:
                self.session_label.setText(f"Session: {self.session_count}")
        else:
            self.is_break = True
            if self.session_count % self.settings['sessions_before_long_rest'] == 0:
                self.remaining_time = self.settings['long_rest_time'] * 60
            else:
                self.remaining_time = self.settings['rest_time'] * 60

    def start_micro_rest_timer(self):
        if self.settings['activate_micro_rest'] and not self.is_break:
            interval = random.randint(MICRO_REST_MIN, MICRO_REST_MAX) * 1000
            self.micro_rest_timer.start(interval)

    def show_micro_rest(self):
        if not self.is_break:
            self.timer.stop()
            self.micro_rest_timer.stop()
            micro_rest = MicroRestNotification(self)
            if micro_rest.exec_() == QDialog.Accepted:
                self.start_timer()

    def toggle_pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.micro_rest_timer.stop()
            self.pause_button.icon_path = "play"
        else:
            self.start_timer()
            self.pause_button.icon_path = "pause"
        self.pause_button.update()

    def stop_timer(self):
        self.timer.stop()
        self.micro_rest_timer.stop()
        if self.settings['display_music_controller']:
            self.background_music.stop()
        self.close()
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def toggle_background_music(self):
        if self.background_music.state() == QMediaPlayer.PlayingState:
            self.background_music.pause()
        else:
            self.background_music.play()

    def set_background_music_volume(self, volume):
        self.background_music.setVolume(volume)


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

        self.setStyleSheet(load_stylesheet('style.qss'))

        # Center the notification on the screen
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

        self.setStyleSheet(load_stylesheet('style.qss'))

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


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet('style.qss'))
    settings_window = SettingsWindow()
    settings_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
