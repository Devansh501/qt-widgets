from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame, QApplication, QHBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PyQt5.QtGui import QColor
import sys


class AnimatedSidebar(QWidget):
    """
    A reusable, animated sidebar widget with toggle functionality.
    Features smooth animations, gradient backgrounds, and modern styling.
    """
    
    def __init__(self, parent=None, expanded_width=300, collapsed_width=50):
        super().__init__(parent)
        self.expanded_width = expanded_width
        self.collapsed_width = collapsed_width
        self.is_expanded = True
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components"""
        self.setFixedWidth(self.expanded_width)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Toggle button with hamburger icon
        self.toggle_button = QPushButton("☰")
        self.toggle_button.setFixedHeight(50)
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #1e272e;
                color: #ffffff;
                border: none;
                font-size: 24px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #2d3436;
            }
            QPushButton:pressed {
                background-color: #0984e3;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        
        # Sidebar content frame
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d3436, stop:1 #1e272e);
                border-right: 2px solid #0984e3;
            }
        """)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(15, 20, 15, 20)
        self.sidebar_layout.setSpacing(15)
        
        # Add menu items
        self.menu_buttons = []
        menu_items = [
            ("🏠", "Home"),
            ("📊", "Dashboard"),
            ("⚙️", "Settings"),
            ("📁", "Projects"),
            ("👤", "Profile"),
            ("📝", "Documents")
        ]
        
        for icon, label in menu_items:
            btn = self.create_menu_button(icon, label)
            self.menu_buttons.append(btn)
            self.sidebar_layout.addWidget(btn)
        
        self.sidebar_layout.addStretch()
        
        # Add widgets to main layout
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.sidebar_frame)
        
        # Setup animations
        self.setup_animations()
    
    def create_menu_button(self, icon, text):
        """Create a styled menu button"""
        btn = QPushButton(f"{icon}  {text}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(45)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                color: #dfe6e9;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                text-align: left;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(9, 132, 227, 0.3);
                border: 1px solid #0984e3;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: rgba(9, 132, 227, 0.5);
            }
        """)
        return btn
    
    def setup_animations(self):
        """Setup smooth animations for sidebar toggle"""
        # Width animation
        self.width_animation = QPropertyAnimation(self, b"minimumWidth")
        self.width_animation.setDuration(400)
        self.width_animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.width_animation_max = QPropertyAnimation(self, b"maximumWidth")
        self.width_animation_max.setDuration(400)
        self.width_animation_max.setEasingCurve(QEasingCurve.InOutQuart)
    
    def toggle_sidebar(self):
        """Toggle the sidebar with smooth animation"""
        if self.is_expanded:
            # Collapse
            self.width_animation.setStartValue(self.expanded_width)
            self.width_animation.setEndValue(self.collapsed_width)
            self.width_animation_max.setStartValue(self.expanded_width)
            self.width_animation_max.setEndValue(self.collapsed_width)
            
            # Update button text
            self.toggle_button.setText("☰")
        else:
            # Expand
            self.width_animation.setStartValue(self.collapsed_width)
            self.width_animation.setEndValue(self.expanded_width)
            self.width_animation_max.setStartValue(self.collapsed_width)
            self.width_animation_max.setEndValue(self.expanded_width)
            
            # Update button text
            self.toggle_button.setText("✕")
        
        self.width_animation.start()
        self.width_animation_max.start()
        self.is_expanded = not self.is_expanded
    
    def add_menu_item(self, icon, text, callback=None):
        """Add a custom menu item to the sidebar"""
        btn = self.create_menu_button(icon, text)
        if callback:
            btn.clicked.connect(callback)
        self.menu_buttons.append(btn)
        self.sidebar_layout.insertWidget(len(self.menu_buttons) - 1, btn)
        return btn


# Test Application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Main window
    main_window = QWidget()
    main_window.setWindowTitle("Animated Sidebar - Test Application")
    main_window.resize(1200, 700)
    main_window.setStyleSheet("background-color: #ecf0f1;")
    
    # Main layout
    main_layout = QVBoxLayout(main_window)
    main_layout.setContentsMargins(0, 0, 0, 0)
    
    # Create horizontal layout for sidebar + content
    h_layout = QHBoxLayout()
    h_layout.setContentsMargins(0, 0, 0, 0)
    h_layout.setSpacing(0)
    
    # Create sidebar
    sidebar = AnimatedSidebar(expanded_width=280, collapsed_width=60)
    
    # Add custom menu item to test
    def on_custom_click():
        content_label.setText("Custom Item Clicked!\n\nYou can add dynamic callbacks to menu items.")
    
    sidebar.add_menu_item("⭐", "Custom Item", on_custom_click)
    
    # Create content area with multiple sections
    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    content_layout.setContentsMargins(30, 30, 30, 30)
    content_layout.setSpacing(20)
    
    # Title
    title = QLabel("Welcome to Animated Sidebar")
    title.setStyleSheet("""
        QLabel {
            color: #2d3436;
            font-size: 28px;
            font-weight: bold;
        }
    """)
    content_layout.addWidget(title)
    
    # Instructions
    instructions = QLabel(
        "Instructions:\n"
        "• Click the hamburger menu (☰) to toggle the sidebar\n"
        "• The sidebar smoothly animates with easing curves\n"
        "• Hover over menu items to see interactive effects\n"
        "• Click any menu item to trigger actions"
    )
    instructions.setStyleSheet("""
        QLabel {
            color: #34495e;
            font-size: 14px;
            line-height: 1.6;
            background-color: rgba(52, 152, 219, 0.1);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
    """)
    content_layout.addWidget(instructions)
    
    # Content area
    content_label = QLabel(
        "Main Content Area\n\n"
        "Click menu items in the sidebar to update this content.\n"
        "The sidebar features:\n"
        "✓ Smooth animations (400ms duration)\n"
        "✓ Gradient backgrounds\n"
        "✓ Hover effects with transparency\n"
        "✓ Responsive button states\n"
        "✓ Fully customizable and reusable"
    )
    content_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    content_label.setStyleSheet("""
        QLabel {
            background-color: #ffffff;
            color: #2d3436;
            font-size: 14px;
            padding: 30px;
            border-radius: 8px;
            border: 2px solid #ecf0f1;
            line-height: 1.8;
        }
    """)
    content_layout.addWidget(content_label)
    
    # Add stretch to push content to top
    content_layout.addStretch()
    
    # Create scroll area for content
    scroll_area = QScrollArea()
    scroll_area.setWidget(content_widget)
    scroll_area.setWidgetResizable(True)
    scroll_area.setStyleSheet("""
        QScrollArea {
            background-color: #ecf0f1;
            border: none;
        }
        QScrollBar:vertical {
            background-color: #ecf0f1;
            width: 10px;
        }
        QScrollBar::handle:vertical {
            background-color: #bdc3c7;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #95a5a6;
        }
    """)
    
    # Add sidebar and content to layout
    h_layout.addWidget(sidebar)
    h_layout.addWidget(scroll_area, stretch=1)
    
    main_layout.addLayout(h_layout)
    
    main_window.show()
    sys.exit(app.exec_())