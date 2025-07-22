from PyQt5.QtWidgets import (
    QApplication, QWidget, QAbstractButton, QSizePolicy, QGridLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen


class DynamicButton(QAbstractButton):
    def __init__(self,x,y,onCheck,onUncheck, parent=None, diameter=None):
        super().__init__(parent)

        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)

        self.hovered = False
        self.diameter = diameter
        self.x = x
        self.y = y
        self.onCheck = onCheck
        self.onUncheck = onUncheck

        # Colors
        self.border_color = QColor("#222")
        self.fill_color = QColor("#0078d7")
        self.hover_border_color = QColor("#888")
        self.dot_color = QColor("#fff")

        if self.diameter:  # fixed size
            self.setFixedSize(self.diameter, self.diameter)
        else:  # expandable
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toggled.connect(self.on_toggled)

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        center = rect.center()
        side = min(rect.width(), rect.height())

        pen_width = max(2, int(side * 0.05))
        radius = side / 2 - pen_width / 2 - 1

        if self.isChecked():
            border = self.fill_color
        elif self.hovered:
            border = self.hover_border_color
        else:
            border = self.border_color

        pen = QPen(border, pen_width)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, radius, radius)

        if self.isChecked():
            inner_radius = radius * 0.5
            painter.setBrush(self.fill_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, inner_radius, inner_radius)

    def on_toggled(self, checked):
        if checked:
            self.onCheck(self)
        else:
            self.onUncheck(self)
