from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import (
    pyqtSignal, Qt, QSize, QPoint, QTimer, QPointF, QEvent, QRectF
)
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QBrush, QPen, QLinearGradient, QFontMetrics, QPainterPath, QRegion
)


class RippleOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.radius = 0
        self.alpha = 150
        self.center = QPointF()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.hide()

    def start(self, center):
        self.radius = 0
        self.alpha = 150
        self.center = QPointF(center)
        self.show()
        self.timer.start(16)

    def animate(self):
        self.radius += 6
        self.alpha -= 5
        if self.alpha <= 0:
            self.timer.stop()
            self.hide()
        self.update()

    def paintEvent(self, event):
        if self.alpha <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(255, 255, 255, self.alpha)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.center, self.radius, self.radius)


class SelectorButton(QWidget):
    def __init__(self, text="", size=QSize(120, 36), parent=None):
        super().__init__(parent)
        self.setFixedSize(size)
        self.text = text
        self.hovered = False
        self.pressed_in = False
        self.popup_open = False
        self.border_radius = 6
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

    def setText(self, text):
        self.text = text
        self.update()

    def getText(self):
        return self.text

    def setPopupOpen(self, is_open: bool):
        self.popup_open = is_open
        self.update()

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

    def mouseReleaseEvent(self, event):
        if self.pressed_in:
            self.pressed_in = False
            self.update()
            self.clicked()

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
            self.clicked()
            return True
        return super().event(e)

    def clicked(self):
        self.parent().show_popup()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)
        if self.pressed_in:
            rect = rect.adjusted(2, 2, -2, -2)

        base = QColor("#1a4d7a")
        hover = QColor("#246ca3")
        press = QColor("#153b60")
        border = QColor("#29618f")
        text_color = QColor("#ffffff")

        if not self.isEnabled():
            bg = QColor("#2f4f6f")
            text_color = QColor("#aaaaaa")
        elif self.pressed_in:
            bg = press
        elif self.hovered:
            bg = hover
        else:
            bg = base

        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0, bg.lighter(120))
        grad.setColorAt(1, bg.darker(110))

        top_radius = self.border_radius
        bottom_radius = 0 if self.popup_open else self.border_radius

        path = QPainterPath()
        path.moveTo(rect.left() + top_radius, rect.top())
        path.lineTo(rect.right() - top_radius, rect.top())
        path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + top_radius)
        path.lineTo(rect.right(), rect.bottom() - bottom_radius)
        path.quadTo(rect.right(), rect.bottom(), rect.right() - bottom_radius, rect.bottom())
        path.lineTo(rect.left() + bottom_radius, rect.bottom())
        path.quadTo(rect.left(), rect.bottom(), rect.left(), rect.bottom() - bottom_radius)
        path.lineTo(rect.left(), rect.top() + top_radius)
        path.quadTo(rect.left(), rect.top(), rect.left() + top_radius, rect.top())

        painter.setBrush(Qt.NoBrush)
        painter.setPen(Qt.NoPen)
        painter.fillPath(path, grad)

        pen = QPen(border)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)

        font = self.font()
        fm = QFontMetrics(font)
        text = self.text or "Select"
        text_width = fm.horizontalAdvance(text)
        max_text_width = rect.width() * 0.8

        while text_width > max_text_width and font.pointSize() > 1:
            font.setPointSize(font.pointSize() - 1)
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(text)

        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignCenter, text)


class ThemedSelector(QWidget):
    currentIndexChanged = pyqtSignal(int)

    def __init__(self, parent=None, size="medium"):
        super().__init__(parent)

        self.items = []
        self.current_index = -1
        self.popup = None

        size_map = {
            "small": QSize(90, 28),
            "medium": QSize(120, 36),
            "large": QSize(160, 48)
        }

        self.button = SelectorButton("Select", size=size_map.get(size, size_map["medium"]), parent=self)
        self.setFixedSize(self.button.size())

        font = QFont()
        font.setPointSize(12 if size == "large" else 10 if size == "medium" else 9)
        self.button.setFont(font)

        self.ripple = RippleOverlay(self.button)
        self.ripple.resize(self.button.size())

    def apply_rounded_clip(self, widget, radius=6):
        path = QPainterPath()
        rect = QRectF(widget.rect())  # ✅ FIXED: convert QRect to QRectF
        path.addRoundedRect(rect, radius, radius)
        widget.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def show_popup(self):
        if not self.items:
            return

        self.popup = QDialog(self, Qt.Popup)
        layout = QVBoxLayout(self.popup)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        list_widget = QListWidget()
        list_widget.setFocusPolicy(Qt.NoFocus)
        list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        list_widget.setSpacing(0)
        list_widget.setContentsMargins(0, 0, 0, 0)

        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1a4d7a;
                border: 1px solid #2c5d8f;
                color: white;
                outline: none;
                padding: 0px;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QListWidget::item {
                padding: 10px 14px;
            }
            QListWidget::item:selected {
                background-color: #246ca3;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 4px 2px 4px 0;
            }
            QScrollBar::handle:vertical {
                background: #4e8ecb;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        for i, (text, _) in enumerate(self.items):
            item = QListWidgetItem(text)
            item.setSizeHint(QSize(self.width(), self.height()))
            list_widget.addItem(item)

        list_widget.itemClicked.connect(lambda item: self.select_item(list_widget.row(item)))
        layout.addWidget(list_widget)

        shadow = QGraphicsDropShadowEffect(self.popup)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 220))
        self.popup.setGraphicsEffect(shadow)

        self.button.setPopupOpen(True)

        item_height = self.height()
        popup_height = min(6, len(self.items)) * item_height
        self.popup.setFixedSize(self.width(), popup_height)

        button_pos = self.mapToGlobal(QPoint(0, self.height()))
        self.popup.move(button_pos)
        self.popup.show()
        self.popup.finished.connect(lambda: self.button.setPopupOpen(False))

        self.apply_rounded_clip(list_widget.viewport(), radius=6)

    def select_item(self, index):
        self.current_index = index
        self.button.setText(self.items[index][0])
        if self.popup:
            self.popup.close()
        self.currentIndexChanged.emit(index)

    def addItem(self, text, userData=None):
        self.items.append((text, userData))
        if self.current_index == -1:
            self.setCurrentIndex(0)

    def addItems(self, items):
        for item in items:
            if isinstance(item, tuple):
                self.addItem(item[0], item[1])
            else:
                self.addItem(item)

    def setCurrentIndex(self, index):
        if 0 <= index < len(self.items):
            self.current_index = index
            self.button.setText(self.items[index][0])
            self.currentIndexChanged.emit(index)

    def currentIndex(self):
        return self.current_index

    def currentText(self):
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index][0]
        return ""

    def currentData(self):
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index][1]
        return None
