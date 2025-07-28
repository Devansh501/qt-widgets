import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QLabel
from virtual_keyboard import VirtualKeyboard


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Virtual Keyboard Demo")
        self.setGeometry(100, 100, 600, 200)
        self.showFullScreen()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        label = QLabel("Click in the input box to open the virtual keyboard:", self)
        layout.addWidget(label)

        self.text_input = QLineEdit(self)
        self.dummy_input = QLineEdit(self)
        layout.addWidget(self.text_input)
        layout.addWidget(self.dummy_input)

        # Assign per-widget mouse event handlers
        self.text_input.mousePressEvent = self.get_virtual_keyboard_callback(self.text_input)
        self.dummy_input.mousePressEvent = self.get_virtual_keyboard_callback(self.dummy_input)

    def get_virtual_keyboard_callback(self, target_input):
        def callback(event):
            VirtualKeyboard.show_for(target_input)
            QLineEdit.mousePressEvent(target_input, event)
        return callback


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()