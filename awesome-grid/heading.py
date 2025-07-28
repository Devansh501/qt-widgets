from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class HeadingWidget(QWidget):
    def __init__(self, text, alignment='left', stretchable=False, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(text)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.label.setFont(font)

        # Set alignment
        alignment = alignment.lower()
        if alignment == 'center':
            self.label.setAlignment(Qt.AlignCenter)
            layout.addStretch()
            layout.addWidget(self.label)
            layout.addStretch()
        elif alignment == 'right':
            self.label.setAlignment(Qt.AlignRight)
            layout.addStretch()
            layout.addWidget(self.label)
        else:  # default: left
            self.label.setAlignment(Qt.AlignLeft)
            layout.addWidget(self.label)
            layout.addStretch()

        # Size policy
        if stretchable:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        else:
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
