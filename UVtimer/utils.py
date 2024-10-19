# Import necessary modules from PyQt5
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QColor, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QSize, pyqtProperty


def load_stylesheet(file_path):
    """
    Load and return the contents of a stylesheet file.

    Args:
        file_path (str): The path to the stylesheet file.

    Returns:
        str: The contents of the stylesheet file.
    """
    with open(file_path, 'r') as f:
        return f.read()

class IconButton(QPushButton):
    def __init__(self, color, icon_path, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.icon_path = icon_path
        self.setFixedSize(32, 32)

    @pyqtProperty(QColor)
    def iconColor(self):
        return self._color

    @iconColor.setter
    def iconColor(self, color):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw button background
        painter.setBrush(self._color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.rect())

        # Draw icon
        painter.setBrush(Qt.white)
        painter.setPen(Qt.white)
        path = QPainterPath()

        # Define icon paths based on the icon_path attribute
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
        """
        Determine if the button was clicked within its circular area.

        Args:
            pos (QPoint): The position of the click.

        Returns:
            bool: True if the click is within the button's circular area, False otherwise.
        """
        center = self.rect().center()
        distance = ((pos.x() - center.x()) ** 2 + (pos.y() - center.y()) ** 2) ** 0.5
        return distance <= self.width() / 2

    def sizeHint(self):
        """
        Provide a size hint for the button.

        Returns:
            QSize: The suggested size for the button.
        """
        return QSize(32, 32)

    def minimumSizeHint(self):
        """
        Provide a minimum size hint for the button.

        Returns:
            QSize: The minimum suggested size for the button.
        """
        return QSize(32, 32)

