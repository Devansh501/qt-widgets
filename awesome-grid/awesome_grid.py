from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5.QtCore import Qt, QPoint
from dynamic_button import DynamicButton


class ButtonGridWidget(QWidget):
    def __init__(self,rows,cols):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.layout = QGridLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.buttons = []
        for i in range(rows):
            row_Buttons = []
            for j in range(cols):
                button = DynamicButton()
                self.layout.addWidget(button, i, j)
                row_Buttons.append(button)
            self.buttons.append(row_Buttons)
        self.setLayout(self.layout)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("background: green;")
        self.setMinimumSize(300, 300)
from PyQt5.QtWidgets import QWidget, QGridLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QLinearGradient, QPainterPath
from dynamic_button import DynamicButton


class ButtonGridWidget(QWidget):
    def __init__(self, rows, cols):
        super().__init__()
        self.rows = rows
        self.cols = cols

        self.layout = QGridLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.buttons = []
        for i in range(rows):
            row_buttons = []
            for j in range(cols):
                button = DynamicButton()
                self.layout.addWidget(button, i, j)
                row_buttons.append(button)
            self.buttons.append(row_buttons)

        self.setLayout(self.layout)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self.setMinimumSize(300, 300)

        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(4, 4)
        self.setGraphicsEffect(shadow)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(5, 5, -5, -5)

        radius = 20

        
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, QColor("#e0e0e0"))  
        gradient.setColorAt(1, QColor("#c0c0c0"))

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), radius, radius)

        painter.fillPath(path, gradient)

        pen = QPen(QColor("#888"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)
