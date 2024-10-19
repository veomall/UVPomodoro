import sys

from PyQt5.QtWidgets import QApplication

from UVtimer.settings_window import SettingsWindow
from UVtimer.utils import load_stylesheet


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet('style.qss'))
    settings_window = SettingsWindow()
    settings_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
