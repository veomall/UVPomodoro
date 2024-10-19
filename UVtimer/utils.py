from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QPainter, QColor, QPainterPath
from PyQt5.QtCore import Qt, QSize


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

