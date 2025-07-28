from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint
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

        # Transparent fullscreen overlay
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.screen_geom = self.app.primaryScreen().availableGeometry()
        self.screen_width = self.screen_geom.width()
        self.screen_height = self.screen_geom.height()

        self.kb_height = int(self.screen_height * 0.25)  # Smaller keyboard height
        self.font_size = max(10, int(self.screen_height * 0.018))  # Smaller font

        self.resize(self.screen_width, self.screen_height)

        self.init_ui()
        self.apply_theme()
        self.fade_in()

    def init_ui(self):
        self.keys_layout = [
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'Enter'],
            ['_', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
            ['*', '&', '!', '@', 'Space', '$', '%', '(', ')']
        ]

        self.keyboard_layout = QVBoxLayout()
        self.keyboard_layout.setSpacing(0)
        self.keyboard_layout.setContentsMargins(2, 2, 2, 2)

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
                btn.setMinimumSize(30, 30)
                btn.setFont(QFont("Arial", self.font_size))
                btn.clicked.connect(lambda _, k=key: self.key_pressed(k))
                self.buttons[key] = btn

                hbox.addWidget(btn)

                if key == 'Space':
                    hbox.setStretchFactor(btn, 6)
                elif key in ['Backspace', 'Enter', 'Caps', 'Tab']:
                    hbox.setStretchFactor(btn, 2)
                else:
                    hbox.setStretchFactor(btn, 1)

            self.keyboard_layout.addLayout(hbox)

        # Wrap keyboard layout in widget with fixed height
        self.keyboard_widget = QWidget()
        self.keyboard_widget.setFixedHeight(self.kb_height)
        self.keyboard_widget.setLayout(self.keyboard_layout)

        # Main layout: stretch above and keyboard at bottom
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addStretch(1)
        outer_layout.addWidget(self.keyboard_widget)
        self.setLayout(outer_layout)

    def apply_theme(self):
        style = {
            "dark": {
                "bg": "#222",
                "btn_bg": "#444",
                "btn_fg": "white",
                "btn_border": "#333",
                "btn_pressed": "#666"
            },
            "light": {
                "bg": "#eee",
                "btn_bg": "#ddd",
                "btn_fg": "black",
                "btn_border": "#bbb",
                "btn_pressed": "#ccc"
            }
        }[self.theme]

        self.keyboard_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {style['bg']};
            }}
            QPushButton {{
                background-color: {style['btn_bg']};
                color: {style['btn_fg']};
                border: 1px solid {style['btn_border']};
                border-radius: 4px;
                font-size: {self.font_size}px;
                margin: 1px;
                padding: 2px;
            }}
            QPushButton:pressed {{
                background-color: {style['btn_pressed']};
            }}
        """)

    def update_keys_case(self):
        for key, btn in self.buttons.items():
            if key.lower() in "abcdefghijklmnopqrstuvwxyz":
                btn.setText(key.upper() if self.caps else key.lower())

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
        self.raise_()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(250)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def fade_out(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.close)
        self.animation.start()

    def on_focus_changed(self, old, new):
        if new is None or not self.isAncestorOf(new):
            self.fade_out()

    def mousePressEvent(self, event):
        # If click is outside keyboard_widget, close
        if not self.keyboard_widget.geometry().contains(event.pos()):
            self.fade_out()

    @staticmethod
    def show_for(target_input, theme="dark"):
        app = QApplication.instance()
        if VirtualKeyboard._instance is None:
            vk = VirtualKeyboard(target_input, app, theme)
            VirtualKeyboard._instance = vk
        else:
            vk = VirtualKeyboard._instance
            vk.target_input = target_input

        vk.fade_in()
