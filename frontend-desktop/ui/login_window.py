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
        self.setFixedSize(450, 380)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Title
        title = QLabel("CEPV")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1E3A8A; margin-bottom: 5px;")
        layout.addWidget(title)

        # Subtitle split into 2 lines
        subtitle = QLabel("Chemical Equipment\nParameter Visualizer")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(11)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #6B7280; line-height: 1.4;")
        layout.addWidget(subtitle)
                
        layout.addSpacing(10)
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setText("testuser")  # Default for demo
        self.username_input.setMinimumHeight(40)
        layout.addWidget(self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("testpass123")  # Default for demo
        self.password_input.setMinimumHeight(40)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(10)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setObjectName("loginBtn")
        login_btn.setMinimumHeight(45)
        login_btn.clicked.connect(self.handle_login)
        login_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(login_btn)
        
        # Demo credentials hint
        demo_label = QLabel("Demo: testuser / testpass123")
        demo_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        demo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(demo_label)
        
        self.setLayout(layout)
        
        # Apply modern stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #f9fafb;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #E5E7EB;
                border-radius: 6px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #1E3A8A;
                background-color: #FFFFFF;
            }
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QPushButton:pressed {
                background-color: #1E3A8A;
            }
            QLabel {
                color: #374151;
            }
        """)
    
    def handle_login(self):
        """Handle login button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        logger.info(f"Attempting login for user: {username}")
        
        result = self.api_client.login(username, password)
        
        if result["success"]:
            logger.info("Login successful! Emitting signal...")
            self.login_successful.emit(username)
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.warning(f"Login failed for {username}: {error_msg}")
            QMessageBox.critical(
                self, 
                "Login Failed", 
                f"Authentication failed:\n{error_msg}"
            )