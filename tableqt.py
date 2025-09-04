import sys
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QColor, QPainter, QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableView, QStyledItemDelegate,
    QHeaderView, QAbstractItemView, QStyle, QHBoxLayout
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class RippleEffect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._radius = 0
        self._opacity = 0
        self._pos = QPoint(0, 0)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.raise_()

    def start(self, pos):
        self._pos = pos
        self._radius = 0
        self._opacity = 150

        anim = QPropertyAnimation(self, b"radius")
        anim.setDuration(400)
        anim.setStartValue(0)
        anim.setEndValue(80)
        anim.start()

        anim2 = QPropertyAnimation(self, b"opacity")
        anim2.setDuration(400)
        anim2.setStartValue(150)
        anim2.setEndValue(0)
        anim2.start()

    def paintEvent(self, event):
        if self._opacity > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            color = QColor(33, 150, 243)
            color.setAlpha(self._opacity)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self._pos, self._radius, self._radius)

    def getRadius(self):
        return self._radius

    def setRadius(self, value):
        self._radius = value
        self.update()

    def getOpacity(self):
        return self._opacity

    def setOpacity(self, value):
        self._opacity = value
        self.update()

    radius = pyqtProperty(int, fget=getRadius, fset=setRadius)
    opacity = pyqtProperty(int, fget=getOpacity, fset=setOpacity)


class MaterialDelegate(QStyledItemDelegate):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme

    def paint(self, painter, option, index):
        painter.save()
        rect = option.rect

        # Colors based on theme
        if self.theme == "dark":
            text_color = QColor("#FFFFFF")
            hover_color = QColor(255, 255, 255, 20)
            select_color = QColor(33, 150, 243, 80)
        else:
            text_color = QColor("#000000")
            hover_color = QColor(0, 0, 0, 10)
            select_color = QColor(33, 150, 243, 60)

        # Background effects
        if option.state & QStyle.State_Selected:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(select_color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 8, 8)
        elif option.state & QStyle.State_MouseOver:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(hover_color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 8, 8)

        # Text
        painter.setPen(text_color)
        painter.setFont(QFont("Segoe UI", 10))
        text = str(index.data())
        painter.drawText(rect.adjusted(10, 0, -10, 0), Qt.AlignVCenter | Qt.AlignLeft, text)

        painter.restore()


class MaterialTableWidget(QWidget):
    def __init__(self, theme="light", headers=None, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.current_theme = theme
        self.setLayout(QVBoxLayout())

        # Table
        self.table = QTableView()
        self.table.setMouseTracking(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setItemDelegate(MaterialDelegate(self.theme, self.table))

        if self.theme == "dark":
            self.table.setStyleSheet("background-color: #121212; border: none; color: white;")
        else:
            self.table.setStyleSheet("background-color: #FFFFFF; border: none; color: black;")

        self.layout().addWidget(self.table)

        # Ripple effect
        self.ripple = RippleEffect(self.table.viewport())

        # Model
        self.model = QStandardItemModel(0, len(headers) if headers else 3)
        if headers:
            self.model.setHorizontalHeaderLabels(headers)
        self.table.setModel(self.model)

        # Floating delete button
        self.delete_btn = QPushButton("X", self.table.viewport())
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #fcfcfc;
                color: #000000;
                border-radius: 12px;
                font-size: 14px;
                width: 24px;
                height: 24px;
            }
        """)
        self.delete_btn.hide()
        self.delete_btn.clicked.connect(self.delete_selected_row)

        # Connections
        self.table.selectionModel().selectionChanged.connect(self.show_delete_button)

    # Public API Methods
    def get_model(self):
        return self.model

    def add_row(self, row_data=None):
        if row_data is None:
            row_data = ["New", "Data", "Row"]
        row = self.model.rowCount()
        self.model.insertRow(row)
        for col, value in enumerate(row_data):
            self.model.setItem(row, col, QStandardItem(value))

    def delete_selected_row(self):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            row = selected[0].row()
            self.model.removeRow(row)

            # Select next row if exists
            if row < self.model.rowCount():
                new_index = self.model.index(row, 0)
            elif self.model.rowCount() > 0:
                new_index = self.model.index(self.model.rowCount() - 1, 0)
            else:
                new_index = None

            if new_index:
                self.table.selectRow(new_index.row())
                self.show_delete_button()
            else:
                self.delete_btn.hide()
        else:
            self.delete_btn.hide()

    def switch_theme(self, theme=None):
        if theme:
            self.current_theme = theme
        else:
            self.current_theme = "light" if self.current_theme == "dark" else "dark"

        self.table.setItemDelegate(MaterialDelegate(self.current_theme, self.table))
        if self.current_theme == "dark":
            self.table.setStyleSheet("background-color: #121212; border: none; color: white;")
        else:
            self.table.setStyleSheet("background-color: #FFFFFF; border: none; color: black;")
        self.table.viewport().update()

    # Internal Methods
    def show_delete_button(self):
        selected = self.table.selectionModel().selectedRows()
        if selected:
            index = selected[0]
            rect = self.table.visualRect(index)
            x = rect.right() - 30
            y = rect.top() + (rect.height() - 24) // 2
            self.delete_btn.move(x, y)
            self.delete_btn.show()
        else:
            self.delete_btn.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)

    # Create material table widget
    table_widget = MaterialTableWidget(theme="light", headers=["Name", "Age", "City"])
    layout.addWidget(table_widget)

    # Buttons
    btn_layout = QHBoxLayout()
    add_btn = QPushButton("Add Row")
    theme_btn = QPushButton("Switch Theme")
    btn_layout.addWidget(add_btn)
    btn_layout.addWidget(theme_btn)
    layout.addLayout(btn_layout)

    # Sample Data
    for row in [["Alice", "24", "New York"], ["Bob", "30", "London"], ["Charlie", "28", "Paris"]]:
        table_widget.add_row(row)

    # Connect buttons
    add_btn.clicked.connect(lambda: table_widget.add_row(["User", "20", "City"]))
    theme_btn.clicked.connect(table_widget.switch_theme)

    window.show()
    sys.exit(app.exec_())
