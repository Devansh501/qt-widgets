from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics, QLinearGradient, QPen


class ThemedButton(QPushButton):
    """
    A reusable, theme-aware button
    with support for custom colors and sizes (large, medium, small),
    rendered manually with paintEvent for smoothness and effects.
    """

    SIZE_MAP = {
        "large": QSize(160, 48),
        "medium": QSize(120, 36),
        "small": QSize(90, 28)
    }

    DEFAULT_COLORS = {
        "primary": "#1a4d7a",
        "hover": "#246ca3",
        "pressed": "#153b60",
        "border": "#29618f",
        "disabled_bg": "#2f4f6f",
        "disabled_text": "#aaaaaa",
        "text": "#ffffff"
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

        # Determine size
        if isinstance(size, QSize):
            self.setFixedSize(size)
        elif size in self.SIZE_MAP:
            self.setFixedSize(self.SIZE_MAP[size])
        else:
            self.setFixedSize(self.SIZE_MAP["medium"])

        # Determine colors
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)

        # adjust if pressed
        if self.pressed_in:
            rect = rect.adjusted(2, 2, -2, -2)

        # pick color
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

        # gradient for depth
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0, bg_color.lighter(120))
        grad.setColorAt(1, bg_color.darker(110))

        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        # border
        pen = QPen(border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, radius, radius)

        # text
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
