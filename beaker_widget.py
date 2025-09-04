from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush,
    QLinearGradient, QFont, QPainterPath
)
import sys
import random


class BeakerWidget(QWidget):
    def __init__(
        self,
        fill_color=QColor("#3498db"),
        background_color=QColor("#111"),
        border_color=QColor("#888"),
        parent=None
    ):
        super().__init__(parent)

        self._fill_color = fill_color
        self._background_color = background_color
        self._border_color = border_color

        self._current_percent = 0
        self._target_percent = 0
        self._animation_step = 1

        self._beaker_width = 120
        self._beaker_height = 180
        self.setFixedSize(self._beaker_width + 40, self._beaker_height + 80)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.animate_fill)

        self.setStyleSheet("background-color: #1e1e1e;")

    def setFillPercent(self, percent: int):
        """Animate to a new percentage."""
        self._target_percent = max(0, min(100, percent))
        if not self._timer.isActive():
            self._timer.start(10)

    def setFillColorAndAnimate(self, color: QColor):
        """Change the fill color but keep the current percentage."""
        self._fill_color = color
        self._target_percent = self._current_percent  # Keep the same percent
        self._current_percent = 0
        if not self._timer.isActive():
            self._timer.start(10)
        self.update()

    def animate_fill(self):
        if self._current_percent < self._target_percent:
            self._current_percent += self._animation_step
        elif self._current_percent > self._target_percent:
            self._current_percent -= self._animation_step
        else:
            self._timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        margin = 20
        padding = 6
        radius = 20

        beaker_rect = QRectF(margin, margin, self._beaker_width, self._beaker_height)
        left = beaker_rect.left()
        right = beaker_rect.right()
        top = beaker_rect.top()
        bottom = beaker_rect.bottom()

        # Create beaker shape with rounded top and rounded bottom
        beaker_path = QPainterPath()
        beaker_path.moveTo(left + radius, top)
        beaker_path.lineTo(right - radius, top)
        beaker_path.quadTo(right, top, right, top + radius)
        beaker_path.lineTo(right, bottom - radius)
        beaker_path.quadTo(right, bottom, right - radius, bottom)
        beaker_path.lineTo(left + radius, bottom)
        beaker_path.quadTo(left, bottom, left, bottom - radius)
        beaker_path.lineTo(left, top + radius)
        beaker_path.quadTo(left, top, left + radius, top)

        # Draw beaker background
        painter.setBrush(self._background_color)
        painter.setPen(Qt.NoPen)
        painter.drawPath(beaker_path)

        # Calculate fill level
        inner_rect = beaker_rect.adjusted(padding, padding, -padding, -padding)
        inner_radius = radius - 2
        fill_height = inner_rect.height() * (self._current_percent / 100.0)
        fill_top = inner_rect.bottom() - fill_height

        # Fill path (with rounded bottom)
        fill_path = QPainterPath()
        if self._current_percent >= 98:
            fill_path = beaker_path  # Use full shape if nearly full
        else:
            fill_rect = QRectF(inner_rect.left(), fill_top, inner_rect.width(), fill_height)
            if fill_height > inner_radius:
                # Rounded bottom corners for fill
                fill_path.moveTo(fill_rect.left(), fill_rect.top())
                fill_path.lineTo(fill_rect.right(), fill_rect.top())
                fill_path.lineTo(fill_rect.right(), fill_rect.bottom() - inner_radius)
                fill_path.quadTo(
                    fill_rect.right(), fill_rect.bottom(),
                    fill_rect.right() - inner_radius, fill_rect.bottom()
                )
                fill_path.lineTo(fill_rect.left() + inner_radius, fill_rect.bottom())
                fill_path.quadTo(
                    fill_rect.left(), fill_rect.bottom(),
                    fill_rect.left(), fill_rect.bottom() - inner_radius
                )
                fill_path.lineTo(fill_rect.left(), fill_rect.top())
            else:
                fill_path.addRect(fill_rect)

        # Fill gradient
        if fill_height > 1:
            gradient = QLinearGradient(0, fill_top, 0, beaker_rect.bottom())
            gradient.setColorAt(0.0, self._fill_color.lighter(120))
            gradient.setColorAt(1.0, self._fill_color.darker(130))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawPath(fill_path.intersected(beaker_path))

        # Draw beaker border
        painter.setPen(QPen(self._border_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(beaker_path)

        # Percentage text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 10)
        font.setBold(True)
        painter.setFont(font)
        text = f"{int(self._current_percent)}%"
        text_rect = QRectF(0, bottom + 8, self.width(), 20)
        painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, text)


# --- Demo usage ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)

    beaker = BeakerWidget(
        fill_color=QColor("#FFAA5C"),
        background_color=QColor("#fff"),
        border_color=QColor("#ccc")
    )
    layout.addWidget(beaker, alignment=Qt.AlignCenter)

    # Button to change fill percentage
    button = QPushButton("Random Fill")
    button.clicked.connect(lambda: beaker.setFillPercent(random.randint(0, 100)))
    layout.addWidget(button, alignment=Qt.AlignCenter)

    # Button to change color but keep current percentage
    color_button = QPushButton("Change Color (Keep %)")
    color_button.clicked.connect(lambda: beaker.setFillColorAndAnimate(
        QColor(random.choice(["#FFAA5C", "#4CAF50", "#3498DB", "#E74C3C", "#9B59B6"]))
    ))
    layout.addWidget(color_button, alignment=Qt.AlignCenter)

    window.setStyleSheet("background-color: #6BAED6; color: white;")
    window.setWindowTitle("Beaker Widget - Keep % on Color Change")
    window.show()
    sys.exit(app.exec_())
