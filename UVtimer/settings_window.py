import os
import json

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QSlider, QPushButton, QCheckBox, QFileDialog)
from PyQt5.QtCore import Qt

from UVtimer.constants import *

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UVPomodoro Settings")
        self.setFixedSize(500, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.config = self.load_config()

        self.run_time_slider = self.create_slider_with_label("Run Time (minutes):", RUN_MIN, RUN_MAX, self.config.get('run_time', 25))
        self.rest_time_slider = self.create_slider_with_label("Rest Time (minutes):", REST_MIN, REST_MAX, self.config.get('rest_time', 5))
        self.long_rest_time_slider = self.create_slider_with_label("Long Rest Time (minutes):", LONG_REST_MIN, LONG_REST_MAX, self.config.get('long_rest_time', 15))
        self.sessions_before_long_rest_slider = self.create_slider_with_label("Sessions Before Long Rest:", 2, 10, self.config.get('sessions_before_long_rest', 4))

        button_layout = QHBoxLayout()
        
        self.advanced_settings_button = QPushButton("Advanced Settings")
        self.advanced_settings_button.clicked.connect(self.toggle_additional_settings)
        button_layout.addWidget(self.advanced_settings_button)

        self.reset_defaults_button = QPushButton("Reset to Defaults")
        self.reset_defaults_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_defaults_button)

        self.layout.addLayout(button_layout)

        self.additional_settings_widget = QWidget()
        additional_settings_layout = QVBoxLayout(self.additional_settings_widget)

        self.activate_micro_rest = QCheckBox("Activate Micro Rest")
        self.activate_micro_rest.setChecked(self.config.get('activate_micro_rest', False))
        self.display_session_counter = QCheckBox("Display Session Counter")
        self.display_session_counter.setChecked(self.config.get('display_session_counter', False))
        self.display_music_controller = QCheckBox("Display Music Controller")
        self.display_music_controller.setChecked(self.config.get('display_music_controller', False))

        self.notification_sound_layout = QHBoxLayout()
        self.notification_sound_label = QLabel("Notification Sound:")
        self.notification_sound_path = QLabel(self.config.get('notification_sound', "Default"))
        self.notification_sound_button = QPushButton("Choose File")
        self.notification_sound_button.clicked.connect(self.choose_notification_sound)
        
        self.notification_sound_layout.addWidget(self.notification_sound_label)
        self.notification_sound_layout.addWidget(self.notification_sound_path)
        self.notification_sound_layout.addWidget(self.notification_sound_button)

        self.background_music_layout = QHBoxLayout()
        self.background_music_label = QLabel("Background Music Folder:")
        self.background_music_path = QLabel(self.config.get('background_music_folder', "Default"))
        self.background_music_button = QPushButton("Choose Folder")
        self.background_music_button.clicked.connect(self.choose_background_music_folder)
        
        self.background_music_layout.addWidget(self.background_music_label)
        self.background_music_layout.addWidget(self.background_music_path)
        self.background_music_layout.addWidget(self.background_music_button)

        self.background_image_layout = QHBoxLayout()
        self.background_image_label = QLabel("Background Image:")
        self.background_image_path = QLabel(self.config.get('background_image', "Default"))
        self.background_image_button = QPushButton("Choose Image")
        self.background_image_button.clicked.connect(self.choose_background_image)
        
        self.background_image_layout.addWidget(self.background_image_label)
        self.background_image_layout.addWidget(self.background_image_path)
        self.background_image_layout.addWidget(self.background_image_button)

        additional_settings_layout.addWidget(self.activate_micro_rest)
        additional_settings_layout.addWidget(self.display_session_counter)
        additional_settings_layout.addWidget(self.display_music_controller)
        additional_settings_layout.addLayout(self.notification_sound_layout)
        additional_settings_layout.addLayout(self.background_music_layout)
        additional_settings_layout.addLayout(self.background_image_layout)
        
        self.background_opacity_layout = QHBoxLayout()
        self.background_opacity_label = QLabel("Background Opacity:")
        self.background_opacity_slider = QSlider(Qt.Horizontal)
        self.background_opacity_slider.setRange(0, 100)
        self.background_opacity_slider.setValue(int(self.config.get('background_opacity', 30)))
        self.background_opacity_value = QLabel(f"{self.background_opacity_slider.value()}%")
        
        self.background_opacity_slider.valueChanged.connect(self.update_opacity_value)
        
        self.background_opacity_layout.addWidget(self.background_opacity_label)
        self.background_opacity_layout.addWidget(self.background_opacity_slider)
        self.background_opacity_layout.addWidget(self.background_opacity_value)

        additional_settings_layout.addLayout(self.background_opacity_layout)

        self.additional_settings_widget.setVisible(False)
        self.layout.addWidget(self.additional_settings_widget)

        self.start_button = QPushButton("Start Timer")
        self.start_button.clicked.connect(self.start_timer)
        self.layout.addWidget(self.start_button)

        self.initial_height = self.height()
        self.additional_settings_height = self.additional_settings_widget.sizeHint().height()

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

    def update_opacity_value(self, value):
        self.background_opacity_value.setText(f"{value}%")

    def choose_notification_sound(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Notification Sound", "", "Sound Files (*.mp3 *.wav)")
        if file_name:
            self.notification_sound_path.setText(os.path.basename(file_name))
            self.notification_sound_file = file_name
        else:
            self.notification_sound_path.setText("Default")
            self.notification_sound_file = "notification.mp3"

    def toggle_additional_settings(self):
        is_visible = self.additional_settings_widget.isVisible()
        self.additional_settings_widget.setVisible(not is_visible)

        if is_visible:
            new_height = self.height() - self.additional_settings_height
            self.setFixedSize(self.width(), new_height)
        else:
            new_height = self.height() + self.additional_settings_height
            self.setFixedSize(self.width(), new_height)

    def choose_background_music_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Background Music Folder")
        if folder:
            self.background_music_path.setText(folder)
            self.background_music_folder = folder
        else:
            self.background_music_path.setText("Default")
            self.background_music_folder = "bg_music"

    def choose_background_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            self.background_image_path.setText(os.path.basename(file_name))
            self.background_image_file = file_name
        else:
            self.background_image_path.setText("Default")
            self.background_image_file = None

    def load_config(self):
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            return self.get_default_config()

    def save_config(self):
        config = {
            'run_time': self.run_time_slider.value(),
            'rest_time': self.rest_time_slider.value(),
            'long_rest_time': self.long_rest_time_slider.value(),
            'sessions_before_long_rest': self.sessions_before_long_rest_slider.value(),
            'activate_micro_rest': self.activate_micro_rest.isChecked(),
            'display_session_counter': self.display_session_counter.isChecked(),
            'display_music_controller': self.display_music_controller.isChecked(),
            'notification_sound': getattr(self, 'notification_sound_file', "notification.mp3"),
            'background_music_folder': getattr(self, 'background_music_folder', "bg_music"),
            'background_image': getattr(self, 'background_image_file', None),
            'background_opacity': self.background_opacity_slider.value(),
        }
        with open('config.json', 'w') as f:
            json.dump(config, f)

    def get_default_config(self):
        return {
            'run_time': 25,
            'rest_time': 5,
            'long_rest_time': 15,
            'sessions_before_long_rest': 4,
            'activate_micro_rest': False,
            'display_session_counter': False,
            'display_music_controller': False,
            'notification_sound': "notification.mp3",
            'background_music_folder': "bg_music",
            'background_image': None,
            'background_opacity': 30,
        }

    def reset_to_defaults(self):
        default_config = self.get_default_config()
        self.run_time_slider.setValue(default_config['run_time'])
        self.rest_time_slider.setValue(default_config['rest_time'])
        self.long_rest_time_slider.setValue(default_config['long_rest_time'])
        self.sessions_before_long_rest_slider.setValue(default_config['sessions_before_long_rest'])
        self.activate_micro_rest.setChecked(default_config['activate_micro_rest'])
        self.display_session_counter.setChecked(default_config['display_session_counter'])
        self.display_music_controller.setChecked(default_config['display_music_controller'])
        self.notification_sound_path.setText("Default")
        self.background_music_path.setText("Default")
        self.background_image_path.setText("Default")
        self.background_opacity_slider.setValue(default_config['background_opacity'])
        
        self.notification_sound_file = default_config['notification_sound']
        self.background_music_folder = default_config['background_music_folder']
        self.background_image_file = default_config['background_image']

    def start_timer(self):
        from UVtimer.timer_window import TimerWindow
        settings = {
            'run_time': self.run_time_slider.value(),
            'rest_time': self.rest_time_slider.value(),
            'long_rest_time': self.long_rest_time_slider.value(),
            'sessions_before_long_rest': self.sessions_before_long_rest_slider.value(),
            'activate_micro_rest': self.activate_micro_rest.isChecked(),
            'display_session_counter': self.display_session_counter.isChecked(),
            'display_music_controller': self.display_music_controller.isChecked(),
            'notification_sound': getattr(self, 'notification_sound_file', "notification.mp3"),
            'background_music_folder': getattr(self, 'background_music_folder', "bg_music"),
            'background_image': getattr(self, 'background_image_file', None),
            'background_opacity': self.background_opacity_slider.value() / 100,
        }
        self.save_config()
        self.timer_window = TimerWindow(settings)
        self.timer_window.show()
        self.hide()
