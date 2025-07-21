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
        layout.addWidget(self.text_input)

        # Override mousePressEvent to show keyboard when clicked
        self.text_input.mousePressEvent = self.show_virtual_keyboard

    def show_virtual_keyboard(self, event):
        # Show the virtual keyboard on click
        VirtualKeyboard.show_for(self.text_input,theme="dev")
        # Still call original event
        QLineEdit.mousePressEvent(self.text_input, event)


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
