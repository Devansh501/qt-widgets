from PyQt5.QtWidgets import QWidget, QGridLayout, QGraphicsDropShadowEffect,QLabel,QSizePolicy
from PyQt5.QtCore import Qt, QRectF, QEvent
from PyQt5.QtGui import QColor, QPainter, QPen, QLinearGradient, QPainterPath
from widgets.dynamic_button import DynamicButton


class ButtonGridWidget(QWidget):
    def __init__(self, rows, cols):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.layout = QGridLayout(self)
        self.layout.setSpacing(3)  # Set your minimum gap here (in pixels)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.selected_buttons = set()

        # Add column labels (1, 2, 3, ...) with compact style and fixed height
        LABEL_SIZE = 32
        BUTTON_SIZE = 32
        for col in range(cols):
            label = QLabel(str(col + 1))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 13px;
                    color: #1a4d7a;
                    background: transparent; /* Changed to transparent for better visibility */
                    border-radius: 6px;
                    padding: 0px;
                    margin: 0px;
                }
            """)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            label.setFixedWidth(LABEL_SIZE)
            label.setFixedHeight(LABEL_SIZE)
            self.layout.addWidget(label, 0, col + 1)

        # Add row labels (A, B, C, ...) with compact style and fixed height
        for row in range(rows):
            label = QLabel(chr(65 + row))  # 65 is 'A'
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 13px;
                    color: #1a4d7a;
                    background: transparent; /* Changed to transparent for better visibility */
                    border-radius: 6px;
                    padding: 0px;
                    margin: 0px;
                }
            """)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            label.setFixedWidth(LABEL_SIZE)
            label.setFixedHeight(LABEL_SIZE)
            self.layout.addWidget(label, row + 1, 0)

        self.buttons = []
        for i in range(rows):
            row_buttons = []
            for j in range(cols):
                btn = DynamicButton(i + 1, j + 1, self.onChecked, self.onUnchecked)
                btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                btn.setFixedWidth(BUTTON_SIZE)
                btn.setFixedHeight(BUTTON_SIZE)
                self.layout.addWidget(btn, i + 1, j + 1)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        self.setLayout(self.layout)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        # gesture state
        self.dragging = False
        self.toggled_buttons = set()
        self.touch_start_pos = None
        self.tap_threshold = 10  # pixels

        # design elements
        # self.setMinimumSize(300, 300)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(4, 4)
        self.setGraphicsEffect(shadow)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)
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

    def mousePressEvent(self, event):
        self.dragging = True
        self.toggled_buttons.clear()
        self.toggle_button_at(event.pos()).set

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.toggle_button_at(event.pos())

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.toggled_buttons.clear()

    def event(self, e):
        if e.type() == QEvent.TouchBegin:
            e.accept()
            self.dragging = False
            self.toggled_buttons.clear()
            self.touch_start_pos = e.touchPoints()[0].pos().toPoint()
            return True

        elif e.type() == QEvent.TouchUpdate:
            e.accept()
            point = e.touchPoints()[0].pos().toPoint()
            dx = abs(point.x() - self.touch_start_pos.x())
            dy = abs(point.y() - self.touch_start_pos.y())
            if max(dx, dy) > self.tap_threshold:
                self.dragging = True
                self.toggle_button_at(point)
            return True

        elif e.type() == QEvent.TouchEnd:
            e.accept()
            end_pos = e.touchPoints()[0].pos().toPoint()
            # For Linux
            if not self.dragging:
                print("Single Tap")
                self.toggle_button_at(end_pos)
            # For Windows Comment out
            self.dragging = False
            self.toggled_buttons.clear()
            self.touch_start_pos = None
            return True

        return super().event(e)

    def toggle_button_at(self, pos):
        btn = self.childAt(pos)
        if isinstance(btn, DynamicButton) and btn not in self.toggled_buttons:
            btn.toggle()
            self.toggled_buttons.add(btn)
    
    def onChecked(self, btnObject):
        self.selected_buttons.add((btnObject.x, btnObject.y))
        print(self.selected_buttons)
        print("--------------------------------")
    
    def onUnchecked(self, btnObject):
        self.selected_buttons.discard((btnObject.x, btnObject.y))
        print(self.selected_buttons)
        print("--------------------------------")
