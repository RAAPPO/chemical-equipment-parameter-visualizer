import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

# Initialize logger
logger = logging.getLogger(__name__)

class LoginWindow(QWidget):
    """Login window for authentication."""
    
    login_successful = pyqtSignal(str)  # Signal emitted on successful login
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("CEPV - Login")
        self.setFixedSize(400, 350)
        self.setStyleSheet("""
            QWidget {
                background-color: #f3f4f6;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 13px;
                background-color: white;
            }
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QLabel {
                color: #374151;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Title
        title = QLabel("CEPV")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1E3A8A;")
        layout.addWidget(title)

        subtitle = QLabel("Chemical Equipment Parameter Visualizer")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(9)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)
                
        layout.addSpacing(10)
        
        # Username
        username_label = QLabel("Username:")
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setText("testuser")  # Default for demo
        layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password:")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("testpass123")  # Default for demo
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(10)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setObjectName("loginBtn")
        login_btn.clicked.connect(self.handle_login)
        login_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(login_btn)
        
        # Demo credentials hint
        demo_label = QLabel("Demo: testuser / testpass123")
        demo_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        demo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(demo_label)
        
        self.setLayout(layout)
    
    def handle_login(self):
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        logger.info(f"Attempting login for user: {username}")
        
        # Attempt login via API client
        result = self.api_client.login(username, password)
        
        if result["success"]:
            logger.info("Login successful! Emitting signal...")
            self.login_successful.emit(username)
            # The controller will handle closing this widget and opening the MainWindow
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.warning(f"Login failed for {username}: {error_msg}")
            QMessageBox.critical(
                self, 
                "Login Failed", 
                f"Authentication failed:\n{error_msg}"
            )