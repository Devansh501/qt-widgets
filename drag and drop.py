import sys
from PyQt5.QtWidgets import (
    QApplication, QLabel, QListWidget, QListWidgetItem,
    QWidget, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QPainter


class DraggableLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
            QLabel {
                background: #3498db;
                color: white;
                padding: 8px;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        self.setFixedWidth(120)

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return

        # --- create drag object ---
        drag = QDrag(self)

        # store text in mime data
        mime_data = QMimeData()
        mime_data.setText(self.text())
        drag.setMimeData(mime_data)

        # --- create visual preview (pixmap) ---
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        self.render(painter)
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())  # cursor position inside pixmap

        drag.exec_(Qt.CopyAction)


class DropList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QListWidget {
                background: #2ecc71;
                color: white;
                padding: 8px;
                border-radius: 8px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 6px;
            }
        """)
        self.setSpacing(4)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            text = event.mimeData().text()
            self.addItem(QListWidgetItem(text))  # stack items
            event.acceptProposedAction()


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag & Drop Demo")

        layout = QHBoxLayout(self)

        # --- Left side: draggable items ---
        left_layout = QVBoxLayout()
        left_layout.addWidget(DraggableLabel("Apple"))
        left_layout.addWidget(DraggableLabel("Banana"))
        left_layout.addWidget(DraggableLabel("Orange"))
        left_layout.addWidget(DraggableLabel("Mango"))
        left_layout.addStretch()

        # --- Right side: drop area (stack) ---
        self.drop_area = DropList()

        layout.addLayout(left_layout, 1)
        layout.addWidget(self.drop_area, 2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.resize(600, 400)
    win.show()
    sys.exit(app.exec_())
