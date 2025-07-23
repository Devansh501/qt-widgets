from PyQt5.QtWidgets import QWidget, QListView, QStyledItemDelegate, QApplication
from PyQt5.QtCore import (
    Qt, QSize, QEvent, QPropertyAnimation, pyqtSignal, QStringListModel, QRectF, pyqtProperty
)
from PyQt5.QtGui import (
    QPainter, QColor, QLinearGradient, QPen, QPainterPath
)


class ThemedItemDelegate(QStyledItemDelegate):
   
    def __init__(self, parent=None, divider_color=QColor(255, 255, 255, 30)):
        super().__init__(parent)
        self.divider_color = divider_color

    def paint(self, painter, option, index):
        super().paint(painter, option, index)

        if index.row() < index.model().rowCount() - 1:
            painter.save()
            pen = QPen(self.divider_color)
            pen.setWidth(1)
            painter.setPen(pen)
            y = option.rect.bottom()
            painter.drawLine(option.rect.left(), y, option.rect.right(), y)
            painter.restore()


class ThemedSelector(QWidget):
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
        "selection": "#246ca3"
    }

    currentIndexChanged = pyqtSignal(int)

    def __init__(self, parent=None, size="medium"):
        super().__init__(parent)

        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

        if isinstance(size, QSize):
            self.setFixedSize(size)
            font_size = 10
        else:
            self.setFixedSize(self.SIZE_MAP.get(size, self.SIZE_MAP["medium"]))
            font_size = self.FONT_MAP.get(size, self.FONT_MAP["medium"])

        self.colors = self.DEFAULT_COLORS.copy()
        self.radius = int(min(self.width(), self.height()) * 0.15)

        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)

        self.items = []  # (text, userData)
        self.current_index = -1
        self.hovered = False
        self.pressed_in = False
        self._hover_progress = 0.0
        self.popup_open = False

        self.hover_anim = QPropertyAnimation(self, b"hoverProgress", self)
        self.hover_anim.setDuration(200)

        self.view = QListView()
        self.view.setWindowFlags(Qt.Popup)
        self.view.setEditTriggers(QListView.NoEditTriggers)
        self.view.setSelectionMode(QListView.SingleSelection)
        self.view.setMouseTracking(True)
        self.view.setFont(font)
        self.view.setFrameShape(QListView.NoFrame)

        self.model = QStringListModel()
        self.view.setModel(self.model)
        self.view.clicked.connect(self.on_item_selected)

        self.view.setStyleSheet(f"""
        QListView {{
            background: transparent;
            outline: none;
            color: {self.colors["text"]};
            padding-top: 4px;
            padding-bottom: 4px;
        }}
        QListView::item {{
            padding: 4px 6px;
        }}
        QListView::item:selected {{
            background: {self.colors["selection"]};
            color: {self.colors["text"]};
        }}
        """)

        self.view.setItemDelegate(ThemedItemDelegate(
            self.view, divider_color=QColor(255, 255, 255, 30)))

        self.view.installEventFilter(self)

    def enterEvent(self, event):
        self.hovered = True
        self.animateHover(True)

    def leaveEvent(self, event):
        self.hovered = False
        self.animateHover(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed_in = True
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed_in = False
            self.show_popup()
            self.update()

    def animateHover(self, enter):
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self._hover_progress)
        self.hover_anim.setEndValue(1.0 if enter else 0.0)
        self.hover_anim.start()

    def getHoverProgress(self):
        return self._hover_progress

    def setHoverProgress(self, value):
        self._hover_progress = value
        self.update()

    hoverProgress = pyqtProperty(float, getHoverProgress, setHoverProgress)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)
        if self.pressed_in:
            rect = rect.adjusted(2, 2, -2, -2)

        if not self.isEnabled():
            base = QColor(self.colors["disabled_bg"])
            text_color = QColor(self.colors["disabled_text"])
        elif self.pressed_in:
            base = QColor(self.colors["pressed"])
            text_color = QColor(self.colors["text"])
        else:
            base_primary = QColor(self.colors["primary"])
            hover_color = QColor(self.colors["hover"])
            base = QColor(
                int(base_primary.red() + (hover_color.red() - base_primary.red()) * self._hover_progress),
                int(base_primary.green() + (hover_color.green() - base_primary.green()) * self._hover_progress),
                int(base_primary.blue() + (hover_color.blue() - base_primary.blue()) * self._hover_progress)
            )
            text_color = QColor(self.colors["text"])

        border_color = QColor(self.colors["border"])

        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0, base.lighter(120))
        grad.setColorAt(1, base.darker(110))

        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, self.radius, self.radius)

        pen = QPen(border_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, self.radius, self.radius)

        painter.setPen(text_color)
        text_rect = rect.adjusted(6, 0, -20, 0)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.currentText())

        arrow_x = rect.right() - 15
        arrow_y = rect.center().y()
        pen.setWidth(2)
        painter.setPen(text_color)
        painter.drawLine(arrow_x - 5, arrow_y - 3, arrow_x, arrow_y + 3)
        painter.drawLine(arrow_x, arrow_y + 3, arrow_x + 5, arrow_y - 3)

    def show_popup(self):
        if not self.items:
            return

        popup_height = min(200, len(self.items) * self.height())
        popup_width = self.width()
        button_pos = self.mapToGlobal(self.rect().bottomLeft())
        button_top = self.mapToGlobal(self.rect().topLeft())

        screen = QApplication.screenAt(button_pos) or QApplication.primaryScreen()
        screen_geom = screen.availableGeometry()

        space_below = screen_geom.bottom() - button_pos.y()
        space_above = button_top.y() - screen_geom.top()

        if space_below >= popup_height or space_below >= space_above:
            pos = button_pos
        else:
            pos = button_top
            pos.setY(pos.y() - popup_height)

        self.view.setMinimumWidth(popup_width)
        self.view.setFixedHeight(popup_height)
        self.view.move(pos)
        self.view.show()
        self.view.setFocus(Qt.PopupFocusReason)

        if not self.popup_open:
            QApplication.instance().installEventFilter(self)
            self.popup_open = True

    def eventFilter(self, obj, e):
        if obj == self.view.viewport() and e.type() == QEvent.Paint:
            painter = QPainter(self.view.viewport())
            painter.setRenderHint(QPainter.Antialiasing)

            rect = self.view.viewport().rect().adjusted(0, 0, -1, -1)
            path = QPainterPath()
            path.addRoundedRect(QRectF(rect), self.radius, self.radius)
            painter.setClipPath(path)

            bg_color = QColor(self.colors["primary"])
            border_color = QColor(self.colors["border"])

            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0, bg_color.lighter(130))
            grad.setColorAt(1, bg_color.darker(110))

            painter.fillPath(path, grad)

            pen = QPen(border_color)
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawPath(path)

        if self.popup_open:
            if e.type() in (QEvent.MouseButtonPress, QEvent.TouchBegin):
                if obj not in (self.view, self.view.viewport()) and not self.view.geometry().contains(e.globalPos()):
                    self.view.hide()
                    QApplication.instance().removeEventFilter(self)
                    self.popup_open = False

            if obj == self.view and e.type() in (QEvent.FocusOut, QEvent.WindowDeactivate):
                self.view.hide()
                QApplication.instance().removeEventFilter(self)
                self.popup_open = False

        return super().eventFilter(obj, e)

    def on_item_selected(self, index):
        self.current_index = index.row()
        self.currentIndexChanged.emit(self.current_index)
        self.view.hide()
        if self.popup_open:
            QApplication.instance().removeEventFilter(self)
            self.popup_open = False
        self.update()

    # API
    def addItem(self, text, userData=None):
        self.items.append((text, userData))
        self.model.setStringList([i[0] for i in self.items])
        if self.current_index == -1:
            self.setCurrentIndex(0)

    def addItems(self, items):
        for item in items:
            if isinstance(item, tuple):
                self.addItem(item[0], item[1])
            else:
                self.addItem(item)

    def currentText(self):
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index][0]
        return ""

    def currentData(self):
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index][1]
        return None

    def setCurrentIndex(self, index):
        if 0 <= index < len(self.items):
            self.current_index = index
            self.update()

    def currentIndex(self):
        return self.current_index
