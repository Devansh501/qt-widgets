from PyQt5.QtWidgets import QComboBox, QListView
from PyQt5.QtCore import Qt, QEvent, QSize, QRectF
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QPen, QPainterPath


class RoundedListView(QListView):
    

    def __init__(self, radius, colors, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.colors = colors
        self.setFrameShape(QListView.NoFrame)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setViewportMargins(2, 2, 2, 2)
        self.setStyleSheet(f"""
            QListView {{
                background: transparent;
                color: {self.colors["popup_text"]};
                selection-background-color: {self.colors["popup_hover"]};
                selection-color: {self.colors["popup_text"]};
                outline: none;
            }}
        """)

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(0, 0, -1, -1)

        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), self.radius, self.radius)

        painter.setClipPath(path)

        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        bg_color = QColor(self.colors["popup_bg"])
        border_color = QColor(self.colors["border"])

        grad.setColorAt(0, bg_color.lighter(120))
        grad.setColorAt(1, bg_color.darker(110))

        painter.fillPath(path, grad)

        pen = QPen(border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)

        super().paintEvent(event)


class ThemedSelector(QComboBox):
    SIZE_MAP = {
        "large": QSize(160, 48),
        "medium": QSize(120, 36),
        "small": QSize(90, 28)
    }

    FONT_MAP = {
        "large": 12,
        "medium": 10,
        "small": 8
    }

    DEFAULT_COLORS = {
        "primary": "#1a4d7a",
        "hover": "#246ca3",
        "pressed": "#153b60",
        "border": "#29618f",
        "disabled_bg": "#2f4f6f",
        "disabled_text": "#aaaaaa",
        "text": "#ffffff",
        "popup_bg": "#1a4d7a",
        "popup_text": "#ffffff",
        "popup_hover": "#246ca3"
    }

    def __init__(self, parent=None, size="medium"):
        super().__init__(parent)

        if isinstance(size, QSize):
            self.setFixedSize(size)
            font_size = 10
        elif size in self.SIZE_MAP:
            self.setFixedSize(self.SIZE_MAP[size])
            font_size = self.FONT_MAP[size]
        else:
            self.setFixedSize(self.SIZE_MAP["medium"])
            font_size = self.FONT_MAP["medium"]

        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)

        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent;")
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)

        self.hovered = False
        self.pressed_in = False

        self.colors = self.DEFAULT_COLORS.copy()

        # configure popup
        self.radius = int(min(self.width(), self.height()) * 0.15)
        self.view_widget = RoundedListView(self.radius, self.colors)
        self.view_widget.setFont(font)
        self.setView(self.view_widget)

    def resizeEvent(self, event):
        self.radius = int(min(self.width(), self.height()) * 0.15)
        self.view_widget.radius = self.radius
        self.view_widget.update()
        super().resizeEvent(event)

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed_in = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.pressed_in = False
        self.update()
        super().mouseReleaseEvent(event)

    def event(self, e):
        if e.type() == QEvent.TouchBegin:
            e.accept()
            self.pressed_in = True
            self.hovered = True
            self.update()
            return True

        elif e.type() == QEvent.TouchEnd:
            e.accept()
            self.pressed_in = False
            self.hovered = False
            self.update()
            return True

        return super().event(e)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)

        if self.pressed_in:
            rect = rect.adjusted(1, 1, -1, -1)

        if not self.isEnabled():
            bg_color = QColor(self.colors["disabled_bg"])
            text_color = QColor(self.colors["disabled_text"])
        elif self.pressed_in:
            bg_color = QColor(self.colors["pressed"])
            text_color = QColor(self.colors["text"])
        elif self.hovered:
            bg_color = QColor(self.colors["hover"])
            text_color = QColor(self.colors["text"])
        else:
            bg_color = QColor(self.colors["primary"])
            text_color = QColor(self.colors["text"])

        border_color = QColor(self.colors["border"])
        radius = self.radius

        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0, bg_color.lighter(120))
        grad.setColorAt(1, bg_color.darker(110))

        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        pen = QPen(border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, radius, radius)

        # Draw current text
        painter.setPen(text_color)
        text_rect = rect.adjusted(6, 0, -20, 0)
        text = self.currentText()
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, text)

        # Draw dropdown arrow
        arrow_x = rect.right() - 15
        arrow_y = rect.center().y()
        pen = QPen(text_color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(arrow_x - 5, arrow_y - 3, arrow_x, arrow_y + 3)
        painter.drawLine(arrow_x, arrow_y + 3, arrow_x + 5, arrow_y - 3)


