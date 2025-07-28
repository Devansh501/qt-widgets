from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize, Qt, QEvent
from PyQt5.QtGui import QPainter, QColor, QFontMetrics, QLinearGradient, QPen


class ThemedButton(QPushButton):
    SIZE_MAP = {
        "large": QSize(160, 48),
        "medium": QSize(120, 36),
        "small": QSize(90, 28)
    }

    DEFAULT_COLORS = {
    "primary": "#1e5d91",      # A step lighter than the background
    "hover": "#257bbf",        # A brighter hover blue
    "pressed": "#164569",      # Darker pressed tone
    "border": "#2c77b8",       # Slightly vivid border
    "disabled_bg": "#26425d",  # Muted gray-blue
    "disabled_text": "#a0aab5",
    "text": "#ffffff"          # White text for readability
    }


    def __init__(
        self,
        text="",
        parent=None,
        size="medium",
        primary_color=None,
        hover_color=None,
        pressed_color=None,
        border_color=None,
        text_color=None
    ):
        super().__init__(text, parent)

        if isinstance(size, QSize):
            self.setFixedSize(size)
        elif size in self.SIZE_MAP:
            self.setFixedSize(self.SIZE_MAP[size])
        else:
            self.setFixedSize(self.SIZE_MAP["medium"])

        self.colors = self.DEFAULT_COLORS.copy()
        if primary_color:
            self.colors["primary"] = primary_color
        if hover_color:
            self.colors["hover"] = hover_color
        if pressed_color:
            self.colors["pressed"] = pressed_color
        if border_color:
            self.colors["border"] = border_color
        if text_color:
            self.colors["text"] = text_color

        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)
        self.setStyleSheet("background: transparent;")
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)

        self.hovered = False
        self.pressed_in = False

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

        elif e.type() == QEvent.TouchUpdate:
            e.accept()
            # (optional: you could track position here if needed)
            return True

        elif e.type() == QEvent.TouchEnd:
            e.accept()
            self.pressed_in = False
            self.hovered = False
            self.update()
            # emit clicked() since QPushButton might not do it without mouse
            self.clicked.emit()
            return True

        return super().event(e)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)

        if self.pressed_in:
            rect = rect.adjusted(2, 2, -2, -2)

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
        radius = min(self.width(), self.height()) * 0.15

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

        font = self.font()
        fm = QFontMetrics(font)
        text = self.text()
        text_width = fm.horizontalAdvance(text)
        max_text_width = rect.width() * 0.8

        while text_width > max_text_width and font.pointSize() > 1:
            font.setPointSize(font.pointSize() - 1)
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(text)

        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignCenter, text)
