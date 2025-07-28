from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy,QApplication
)
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation
from PyQt5.QtGui import QFont


class VirtualKeyboard(QWidget):
    _instance = None  # Singleton instance

    def __init__(self, target_input, app, theme="dark"):
        super().__init__()
        QApplication.instance().focusChanged.connect(self.on_focus_changed)
        self.target_input = target_input
        self.app = app
        self.caps = False
        self.theme = theme

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowTitle("Keyboard")

        self.screen_geom = self.app.primaryScreen().availableGeometry()
        self.screen_width = self.screen_geom.width()
        self.screen_height = self.screen_geom.height()

        self.is_small_screen = self.screen_width <= 1280

        if self.is_small_screen:
            self.kb_width = min(self.screen_width, int(self.screen_width * 0.95))
            self.kb_height = int(self.screen_height * 0.4)
            self.font_size = max(14, int(self.screen_height * 0.03))
        else:
            self.kb_width = min(self.screen_width, int(self.screen_width * 0.75))
            self.kb_height = int(self.screen_height * 0.3)
            self.font_size = max(12, int(self.screen_height * 0.02))

        self.init_ui()
        self.position_keyboard()
        self.apply_theme()
        self.fade_in()

    def init_ui(self):
        self.keys_layout = [
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'Enter'],
            ['_','z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
            ['*', '&', '!', '@', 'Space', '$', '%', '(', ')']
        ]

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.buttons = {}
        multiplier = 2

        for row_keys in self.keys_layout:
            hbox = QHBoxLayout()
            hbox.setSpacing(0)
            hbox.setContentsMargins(0, 0, 0, 0)

            for key in row_keys:
                display_text = key.replace("&", "&&")
                btn = QPushButton(display_text)
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setMinimumSize(40, 40)
                btn.setFont(QFont("Arial", self.font_size))
                btn.clicked.connect(lambda _, k=key: self.key_pressed(k))
                self.buttons[key] = btn

                hbox.addWidget(btn)

                if key == 'Space':
                    hbox.setStretchFactor(btn, int(4 * multiplier))
                elif key in ['Backspace', 'Enter', 'Caps', 'Tab']:
                    hbox.setStretchFactor(btn, int(2 * multiplier))
                else:
                    hbox.setStretchFactor(btn, int(1 * multiplier))

            self.layout.addLayout(hbox)

        self.setLayout(self.layout)

    def position_keyboard(self):
        if self.is_small_screen:
            kb_x = 0
        else:
            kb_x = (self.screen_width - self.kb_width) // 2

        kb_y = self.screen_height - self.kb_height
        self.setGeometry(QRect(kb_x, kb_y, self.kb_width, self.kb_height))

    def apply_theme(self):
        if self.theme == "dark":
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: #222;
                }}
                QPushButton {{
                    background-color: #444;
                    color: white;
                    border: 1px solid #333;
                    border-radius: 4px;
                    font-size: {self.font_size}px;
                    margin: 0px;
                    padding: 0px;
                }}
                QPushButton:pressed {{
                    background-color: #666;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: #eee;
                }}
                QPushButton {{
                    background-color: #ddd;
                    color: black;
                    border: 1px solid #bbb;
                    border-radius: 4px;
                    font-size: {self.font_size}px;
                    margin: 0px;
                    padding: 0px;
                }}
                QPushButton:pressed {{
                    background-color: #ccc;
                }}
            """)

    def update_keys_case(self):
        for key, btn in self.buttons.items():
            if key.lower() in "abcdefghijklmnopqrstuvwxyz":
                if self.caps:
                    btn.setText(key.upper())
                else:
                    btn.setText(key.lower())

    def key_pressed(self, key):
        if key == "Backspace":
            current_text = self.target_input.text()
            self.target_input.setText(current_text[:-1])
        elif key == "Enter":
            self.fade_out()
        elif key == "Space":
            self.target_input.insert(" ")
        elif key == "Tab":
            self.target_input.insert("  ")
        elif key == "Caps":
            self.caps = not self.caps
            self.update_keys_case()
        else:
            to_insert = key
            if len(key) == 1:
                to_insert = key.upper() if self.caps else key.lower()
            self.target_input.insert(to_insert)

    def fade_in(self):
        if self.isVisible():
            return
        self.setWindowOpacity(0)
        self.show()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def fade_out(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.close)
        self.animation.start()

    def on_focus_changed(self, old, new):
        # If new widget is NOT a child of this keyboard window
        if new is None or not self.isAncestorOf(new):
            print("Focus left the keyboard")
            self.fade_out()

    

    @staticmethod
    def show_for(target_input, theme="dark"):
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()

        if VirtualKeyboard._instance is None:
            vk = VirtualKeyboard(target_input, app, theme)
            VirtualKeyboard._instance = vk
        else:
            vk = VirtualKeyboard._instance
            vk.target_input = target_input
            

        vk.fade_in()
