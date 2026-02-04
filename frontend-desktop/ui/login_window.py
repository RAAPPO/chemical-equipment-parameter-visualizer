from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont

class LoginWindow(QWidget):
    login_successful = pyqtSignal(str, str)  # username, token

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login - CEPV System")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #F8FAFC;")  # Slate-50 background

        # Center Layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # --- LOGIN CARD ---
        card = QFrame()
        card.setFixedSize(400, 500) # Height adjusted for demo hint
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        
        # Shadow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        # 1. Header
        title = QLabel("Welcome Back")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B; border: none;")
        
        subtitle = QLabel("Enter your credentials to access the chemical analytics platform.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size: 13px; color: #64748B; margin-bottom: 10px; border: none;")

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)

        # 2. Inputs (Pre-filled for convenience)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setText("testuser") 
        self.username_input.setFixedHeight(45)
        self.username_input.setStyleSheet(self.input_style())

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setText("testpass123")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(45)
        self.password_input.setStyleSheet(self.input_style())

        card_layout.addWidget(self.username_input)
        card_layout.addWidget(self.password_input)

        # 3. Login Button
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setFixedHeight(45)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E3A8A; 
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QPushButton:pressed {
                background-color: #172554;
            }
        """)
        card_layout.addWidget(self.login_btn)

        # 4. Demo Hint (Visible Reference)
        demo_hint = QLabel("Demo: testuser / testpass123")
        demo_hint.setAlignment(Qt.AlignCenter)
        demo_hint.setStyleSheet("color: #64748B; font-size: 12px; font-weight: bold; background: #F1F5F9; border-radius: 4px; padding: 5px;")
        card_layout.addWidget(demo_hint)

        # 5. Footer
        footer = QLabel("Chemical Equipment Parameter Visualizer v2.0")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #94A3B8; font-size: 11px; margin-top: 5px; border: none;")
        card_layout.addWidget(footer)

        main_layout.addWidget(card)

    def input_style(self):
        return """
            QLineEdit {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding-left: 12px;
                font-size: 13px;
                color: #334155;
                background: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
            }
        """

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return

        self.login_btn.setText("Authenticating...")
        self.login_btn.setEnabled(False)
        
        try:
            res = self.api_client.login(username, password)
            if res["success"]:
                # FIXED: Correct path to the token in the response dictionary
                token = res["data"]["access"] 
                self.login_successful.emit(username, token)
            else:
                QMessageBox.critical(self, "Login Failed", res.get("error", "Invalid credentials"))
        except Exception as e:
            QMessageBox.critical(self, "System Error", f"An error occurred during login.\n{str(e)}")
        finally:
            self.login_btn.setText("Sign In")
            self.login_btn.setEnabled(True)