from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class LoginWindow(QDialog):
    """Login window for authentication."""
    
    login_successful = pyqtSignal(str)  # Signal emitted on successful login
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("CEPV - Login")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #f3f4f6;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 13px;
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
        """)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("CEPV")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        subtitle = QLabel("Chemical Equipment Parameter Visualizer")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)
                
        layout.addSpacing(20)
        
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
        layout.addWidget(login_btn)
        
        # Demo credentials hint
        demo_label = QLabel("Demo: testuser / testpass123")
        demo_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        demo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(demo_label)
        
        self.setLayout(layout)
    
    def handle_login(self):
        """Handle login button click."""
        print("🔐 Login button clicked")
        
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        print(f"📝 Username: {username}")
        print(f"📝 Password: {'*' * len(password)}")
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        print("🌐 Attempting API login...")
        # Attempt login
        result = self.api_client.login(username, password)
        
        print(f"📡 API Response: {result}")
        
        if result["success"]:
            print("✅ Login successful! Emitting signal...")
            self.login_successful.emit(username)
            print("✅ Signal emitted, accepting dialog...")
            self.accept()
            print("✅ Dialog accepted")
        else:
            print(f"❌ Login failed: {result.get('error')}")
            QMessageBox.critical(
                self, 
                "Login Failed", 
                f"Authentication failed:\n{result.get('error', 'Unknown error')}"
            )
