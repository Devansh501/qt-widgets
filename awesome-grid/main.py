import sys
import math
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton


class Loader(QWidget):
    def __init__(self):
        super().__init__()
 
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Damn!!")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
