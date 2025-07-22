from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from button import ThemedButton
from dynamic_button import DynamicButton
from awesome_grid import ButtonGridWidget
from selector import ThemedSelector
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dump")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        button = ThemedButton("Click Me")
        grid = ButtonGridWidget(4,5)
        selector = ThemedSelector(size="large")
        selector.addItem("Option 1", userData=101)
        selector.addItem("Option 2", userData=202)
        selector.addItem("Option 3", userData=303)
        
        layout.addWidget(grid)
        layout.addWidget(button)
        layout.addWidget(selector)
        
        central_widget.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    # window.showFullScreen()
    window.show()
    sys.exit(app.exec_())