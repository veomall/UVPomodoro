import os
import random

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QDialog
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QUrl
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist

from UVtimer.settings_window import SettingsWindow
from UVtimer.utils import IconButton, load_stylesheet
from UVtimer.notifications import NotificationWindow, MicroRestNotification
from UVtimer.constants import MICRO_REST_MIN, MICRO_REST_MAX


class TimerWindow(QWidget):
    """
    This class represents the main timer window of the UVPomodoro application.
    It displays the timer, controls, and handles the timer logic.
    """

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setStyleSheet(load_stylesheet('style.qss'))
        
        # Set window properties
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        window_height = 140
        self.setFixedWidth(200)
        self.setFixedHeight(window_height)
        
        # Initialize background image variables
        self.background_image = None
        self.transparent_background = None

        # Set up the main layout
        self.layout = QVBoxLayout(self)

        # Create and style the time display label
        self.time_label = QLabel(f"{self.settings['run_time']:02d}:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 48px; color: #88C0D0;")
        self.layout.addWidget(self.time_label)

        # Add session counter if enabled in settings
        if self.settings['display_session_counter']:
            self.session_label = QLabel("Session: 1")
            self.session_label.setAlignment(Qt.AlignCenter)
            self.session_label.setStyleSheet("font-size: 14px; color: #D8DEE9;")
            self.layout.addWidget(self.session_label)
            window_height += 10
            self.setFixedHeight(window_height)

        # Add music controls if enabled in settings
        if self.settings['display_music_controller']:
            music_control_layout = QHBoxLayout()

            # Create volume slider
            self.volume_slider = QSlider(Qt.Horizontal)
            self.volume_slider.setRange(0, 100)
            self.volume_slider.setValue(50)
            self.volume_slider.setFixedWidth(150)  # Increased width for better usability
            self.volume_slider.valueChanged.connect(self.set_background_music_volume)
            music_control_layout.addWidget(self.volume_slider)

            self.layout.addLayout(music_control_layout)

            # Set up background music playlist and player
            self.background_playlist = QMediaPlaylist()
            self.load_background_music()
            self.background_playlist.setPlaybackMode(QMediaPlaylist.Loop)

            self.background_music = QMediaPlayer()
            self.background_music.setPlaylist(self.background_playlist)
            self.background_music.setVolume(50)
            self.background_music.play()

            window_height += 30
            self.setFixedHeight(window_height)
        
        # Set up background image if provided in settings
        if self.settings['background_image']:
            self.background_image = QImage(self.settings['background_image'])
            self.transparent_background = QPixmap(self.size())
            self.transparent_background.fill(Qt.transparent)
            painter = QPainter(self.transparent_background)
            painter.setOpacity(self.settings['background_opacity'])
            
            # Calculate image scaling to fit the window
            image_ratio = self.background_image.width() / self.background_image.height()
            window_ratio = self.width() / self.height()
            
            if image_ratio > window_ratio:
                new_width = self.width()
                new_height = int(new_width / image_ratio)
                x = 0
                y = (self.height() - new_height) // 2
            else:
                new_height = self.height()
                new_width = int(new_height * image_ratio)
                x = (self.width() - new_width) // 2
                y = 0

            target_rect = QRect(x, y, new_width, new_height)
            painter.drawImage(target_rect, self.background_image)
            painter.end()
        else:
            self.transparent_background = None

        # Create control buttons
        button_layout = QHBoxLayout()
        self.pause_button = IconButton("#5E81AC", "pause")
        self.pause_button.clicked.connect(self.toggle_pause)

        self.stop_button = IconButton("#BF616A", "stop")
        self.stop_button.clicked.connect(self.stop_timer)

        self.skip_button = IconButton("#EBCB8B", "skip")
        self.skip_button.clicked.connect(self.skip_session)

        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.skip_button)

        self.layout.addLayout(button_layout)

        # Set up main timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = self.settings['run_time'] * 60
        self.is_break = False
        self.session_count = 1

        # Set up micro-rest timer
        self.micro_rest_timer = QTimer(self)
        self.micro_rest_timer.timeout.connect(self.show_micro_rest)

        self.start_timer()

        # Initialize variables for window dragging
        self.moving = False
        self.offset = QPoint()

        # Set up notification sound
        self.notification_sound = QMediaPlayer()
        self.notification_sound.setMedia(QMediaContent(QUrl.fromLocalFile(self.settings['notification_sound'])))

    def paintEvent(self, event):
        """
        Handle the paint event to draw the background image or color.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.transparent_background:
            painter.drawPixmap(0, 0, self.transparent_background)
        else:
            background_color = QColor(46, 52, 64)
            background_color.setAlpha(int(255 * self.settings['background_opacity']))
            painter.setBrush(background_color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect(), 10, 10)

    def mousePressEvent(self, event):
        """
        Handle mouse press event for window dragging.
        """
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        """
        Handle mouse move event for window dragging.
        """
        if self.moving:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        """
        Handle mouse release event for window dragging.
        """
        if event.button() == Qt.LeftButton:
            self.moving = False

    def start_timer(self):
        """
        Start the main timer and update the display.
        """
        minutes, seconds = divmod(self.remaining_time, 60)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        self.timer.start(1000)
        if not self.is_break:
            self.start_micro_rest_timer()

    def update_timer(self):
        """
        Update the timer display and handle session completion.
        """
        self.remaining_time -= 1
        minutes, seconds = divmod(self.remaining_time, 60)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        if self.remaining_time <= 0:
            self.notification_sound.play()
            self.show_notification()

    def toggle_pause(self):
        """
        Toggle the pause state of the timer.
        If the timer is active, pause it and change the button icon to play.
        If the timer is paused, restart it and change the button icon to pause.
        """
        if self.timer.isActive():
            self.timer.stop()
            self.micro_rest_timer.stop()
            self.pause_button.icon_path = "play"
        else:
            self.start_timer()
            self.pause_button.icon_path = "pause"
        self.pause_button.update()

    def stop_timer(self):
        """
        Stop the timer and close the timer window.
        This method stops all timers, stops the background music if it's enabled,
        closes the current window, and opens the settings window.
        """
        self.timer.stop()
        self.micro_rest_timer.stop()
        if self.settings['display_music_controller']:
            self.background_music.stop()
        self.close()
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def skip_session(self):
        """
        Skip the current session, play notification sound, and show notification.
        """
        self.notification_sound.play()
        self.show_notification()

    def toggle_session(self):
        """
        Toggle between work and break sessions.
        """
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
        """
        Start the micro-rest timer if enabled in settings.
        """
        if self.settings['activate_micro_rest'] and not self.is_break:
            interval = random.randint(MICRO_REST_MIN, MICRO_REST_MAX) * 1000
            self.micro_rest_timer.start(interval)

    def show_micro_rest(self):
        """
        Show a micro-rest notification during work sessions.
        """
        if not self.is_break:
            self.timer.stop()
            self.micro_rest_timer.stop()
            micro_rest = MicroRestNotification(self)
            if micro_rest.exec_() == QDialog.Accepted:
                self.start_timer()

    def show_notification(self):
        """
        Show a notification when a session is completed.
        """
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

    def load_background_music(self):
        """
        Load background music files from the specified folder into the playlist.
        """
        music_dir = self.settings['background_music_folder']
        if os.path.exists(music_dir):
            for file in random.sample(os.listdir(music_dir), len(os.listdir(music_dir))):
                if file.endswith((".mp3", ".wav", ".ogg")):
                    self.background_playlist.addMedia(QMediaContent(QUrl.fromLocalFile(os.path.join(music_dir, file))))

    def toggle_background_music(self):
        """
        Toggle the play/pause state of the background music.
        If the music is playing, pause it. If it's paused, resume playback.
        """
        if self.background_music.state() == QMediaPlayer.PlayingState:
            self.background_music.pause()
        else:
            self.background_music.play()

    def set_background_music_volume(self, volume):
        """
        Set the volume of the background music.
        """
        self.background_music.setVolume(volume)
