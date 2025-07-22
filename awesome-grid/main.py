from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from button import ThemedButton
from dynamic_button import DynamicButton
from awesome_grid import ButtonGridWidget
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dump")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        # button = DynamicButton()
        # button = ThemedButton("Click Me")
        grid = ButtonGridWidget(12, 8)
        layout.addWidget(grid)
        # layout.addWidget(button)
        
        
        central_widget.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.showFullScreen()
    window.show()
    sys.exit(app.exec_())