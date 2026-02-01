import logging
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QDesktopWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

logger = logging.getLogger(__name__)

class LoginWindow(QWidget):
    """Industry-standard professional authentication interface."""
    login_successful = pyqtSignal(str)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("CEPV | Secure Access")
        self.setFixedSize(420, 520)
        self.setStyleSheet("background-color: #FFFFFF;")
        
        # Center Window
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - 420) // 2, (screen.height() - 520) // 2)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(45, 50, 45, 50)
        layout.setSpacing(0)

        # Brand Identity
        brand = QLabel("CEPV")
        brand.setAlignment(Qt.AlignCenter)
        brand.setStyleSheet("font-size: 34px; font-weight: 900; color: #0F172A; letter-spacing: -1.5px;")
        
        subtitle = QLabel("Industrial Parameter Visualizer")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #64748B; margin-bottom: 40px;")
        
        layout.addWidget(brand)
        layout.addWidget(subtitle)

        # Inputs
        field_style = """
            QLineEdit {
                padding: 12px;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #F8FAFC;
                color: #1E293B;
            }
            QLineEdit:focus { border: 2px solid #6366F1; background-color: #FFFFFF; }
        """
        
        self.u_input = QLineEdit(placeholderText="Username")
        self.u_input.setText("testuser")
        self.u_input.setStyleSheet(field_style)
        
        self.p_input = QLineEdit(placeholderText="Password")
        self.p_input.setEchoMode(QLineEdit.Password)
        self.p_input.setText("testpass123")
        self.p_input.setStyleSheet(field_style)
        self.p_input.returnPressed.connect(self.handle_login)

        layout.addWidget(self.u_input)
        layout.addSpacing(15)
        layout.addWidget(self.p_input)
        layout.addSpacing(30)
        
        # Login Button
        btn = QPushButton("Sign In")
        btn.setMinimumHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #4F46E5;
                color: white;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #4338CA; }
        """)
        btn.clicked.connect(self.handle_login)
        layout.addWidget(btn)
        
        # Demo Hint (Added as requested)
        hint = QLabel("Demo: testuser / testpass123")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #94A3B8; font-size: 11px; margin-top: 25px;")
        layout.addWidget(hint)
        
        layout.addStretch()

    def handle_login(self):
        user, pwd = self.u_input.text().strip(), self.p_input.text().strip()
        if not user or not pwd:
            return
            
        result = self.api_client.login(user, pwd)
        if result["success"]:
            self.login_successful.emit(user)
        else:
            QMessageBox.critical(self, "Error", result.get('error', 'Login Failed'))