from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QRectF, QTimer, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QFont, QPainterPath
import sys
import random


class TestTubeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._fill_color = QColor("#2ecc71")  # Greenish fill
        self._background_color = QColor("#111111")
        self._border_color = QColor("#555555")

        self._current_percent = 0
        self._target_percent = 0

        # Fixed internal size to avoid scaling issues
        self._tube_width = 50
        self._tube_height = 200
        self.setFixedSize(self._tube_width + 40, self._tube_height + 80)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.animate_fill)
        self._animation_step = 1

        self.setStyleSheet("background-color: #1e1e1e;")

    def setFillPercent(self, percent):
        self._target_percent = max(0, min(100, percent))
        if not self._timer.isActive():
            self._timer.start(10)

    def animate_fill(self):
        if self._current_percent < self._target_percent:
            self._current_percent += self._animation_step
            if self._current_percent > self._target_percent:
                self._current_percent = self._target_percent
        elif self._current_percent > self._target_percent:
            self._current_percent -= self._animation_step
            if self._current_percent < self._target_percent:
                self._current_percent = self._target_percent
        else:
            self._timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        margin = 12
        padding = 3
        tube_rect = QRectF(margin, margin, self._tube_width, self._tube_height)
        border_radius = self._tube_width / 2

        # Inner rect (glass content area)
        inner_rect = tube_rect.adjusted(padding, padding, -padding, -padding)

        # Draw inner glass background
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._background_color)
        painter.drawRoundedRect(inner_rect, border_radius - 2, border_radius - 2)

        # Draw fill
        fill_height = inner_rect.height() * (self._current_percent / 100.0)
        fill_top = inner_rect.bottom() - fill_height
        fill_rect = QRectF(inner_rect.left(), fill_top, inner_rect.width(), fill_height)

        if fill_height > 1:
            gradient = QLinearGradient(fill_rect.topLeft(), fill_rect.bottomLeft())
            gradient.setColorAt(0.0, self._fill_color.lighter(130))
            gradient.setColorAt(1.0, self._fill_color.darker(130))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)

            # Create a fill path with rounded top and flat bottom
            path = QPainterPath()
            corner_radius = min(fill_rect.height(), fill_rect.width()) / 2

            left = fill_rect.left()
            right = fill_rect.right()
            top = fill_rect.top()
            bottom = fill_rect.bottom()

            path.moveTo(left, bottom)
            path.lineTo(right, bottom)
            path.lineTo(right, top + corner_radius)
            path.quadTo(right, top, right - corner_radius, top)
            path.lineTo(left + corner_radius, top)
            path.quadTo(left, top, left, top + corner_radius)
            path.lineTo(left, bottom)

            # Clip path to inner tube boundary
            clip_path = QPainterPath()
            clip_path.addRoundedRect(inner_rect, border_radius - 2, border_radius - 2)
            painter.drawPath(path.intersected(clip_path))

        # Draw glass tube outline
        painter.setPen(QPen(self._border_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(tube_rect, border_radius, border_radius)

        # Draw percentage label
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 10)
        font.setBold(True)
        painter.setFont(font)
        text = f"{int(self._current_percent)}%"
        text_rect = QRectF(0, tube_rect.bottom() + 8, self.width(), 20)
        painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, text)


# Demo window to show the widget in action
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Test Tube Widget")
    layout = QVBoxLayout(window)

    test_tube = TestTubeWidget()
    layout.addWidget(test_tube, alignment=Qt.AlignCenter)

    button = QPushButton("Random Fill")
    button.clicked.connect(lambda: test_tube.setFillPercent(random.randint(0, 100)))
    layout.addWidget(button, alignment=Qt.AlignCenter)

    window.setStyleSheet("background-color: #1e1e1e; color: white;")
    window.show()
    sys.exit(app.exec_())
