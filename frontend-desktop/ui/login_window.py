import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QDesktopWidget, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

logger = logging.getLogger(__name__)

class LoginWindow(QWidget):
    """Modernized Auth Card login window."""
    
    login_successful = pyqtSignal(str) # Signal emitted on successful login
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI with a clean card-based layout."""
        self.setWindowTitle("CEPV - Login")
        self.setFixedSize(400, 480)
        
        # Center window on screen
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - 400) // 2, (screen.height() - 480) // 2)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.setSpacing(0)

        # Brand Section
        title = QLabel("CEPV")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: 900; color: #1E3A8A; margin-bottom: 0px;")
        
        subtitle = QLabel("Chemical Equipment Visualizer")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #6B7280; font-weight: 500; margin-bottom: 30px;")
        
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Input Group
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setText("testuser") 
        self.username_input.setMinimumHeight(45)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("testpass123")
        self.password_input.setMinimumHeight(45)
        self.password_input.returnPressed.connect(self.handle_login)

        label_style = "font-weight: 600; color: #374151; font-size: 10px; letter-spacing: 0.5px;"
        
        header_label = QLabel("ACCOUNT LOGIN")
        header_label.setStyleSheet(label_style)
        layout.addWidget(header_label, 0, Qt.AlignLeft)
        
        layout.addSpacing(8)
        layout.addWidget(self.username_input)
        layout.addSpacing(15)
        layout.addWidget(self.password_input)
        layout.addSpacing(25)
        
        # Login button
        login_btn = QPushButton("Sign In")
        login_btn.setMinimumHeight(48)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)
        
        layout.addStretch()
        
        # Demo Footer
        demo_label = QLabel("Demo: testuser / testpass123")
        demo_label.setStyleSheet("color: #9CA3AF; font-size: 11px;")
        demo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(demo_label)
        
        self.setStyleSheet("""
            QWidget { background-color: white; }
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                font-size: 14px;
                background-color: #F9FAFB;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                background-color: white;
            }
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #1E40AF; }
        """)
    
    def handle_login(self):
        """Handle login authentication via API."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required.")
            return
        
        logger.info(f"Attempting login for user: {username}")
        result = self.api_client.login(username, password)
        
        if result["success"]:
            logger.info("Login successful.")
            self.login_successful.emit(username)
        else:
            error_msg = result.get('error', 'Authentication failed.')
            QMessageBox.critical(self, "Login Failed", error_msg)