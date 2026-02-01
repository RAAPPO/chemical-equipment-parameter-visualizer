#!/usr/bin/env python3
"""
Chemical Equipment Parameter Visualizer - Desktop Application
Industry-grade PyQt5 application with proper lifecycle management
"""

import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from utils.api_client import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cepv_desktop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Application:
    """Main application controller managing window lifecycle."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Chemical Equipment Parameter Visualizer")
        self.app.setOrganizationName("FOSSEE")
        self.app.setOrganizationDomain("fossee.in")
        
        # Set application-wide font
        self.app.setFont(self.app.font())
        
        self.api_client = APIClient()
        self.login_window = None
        self.main_window = None
        
        logger.info("Application initialized")
    
    def show_login(self):
        """Show login window."""
        logger.info("Showing login window")
        
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        
        self.login_window = LoginWindow(self.api_client)
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self, username):
        """Handle successful login."""
        logger.info(f"Login successful for user: {username}")
        
        # Close login window
        if self.login_window:
            self.login_window.close()
            self.login_window = None
        
        # Show main window
        self.main_window = MainWindow(self.api_client, username)
        self.main_window.logout_requested.connect(self.on_logout)
        self.main_window.show()
    
    def on_logout(self):
        """Handle logout request."""
        logger.info("Logout requested")
        
        # Clear tokens
        self.api_client.logout()
        
        # Close main window
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        
        # Show login again
        self.show_login()
    
    def run(self):
        """Start the application."""
        self.show_login()
        return self.app.exec_()


def main():
    """Application entry point."""
    logger.info("=" * 60)
    logger.info("Chemical Equipment Parameter Visualizer - Desktop")
    logger.info("=" * 60)
    
    try:
        app = Application()
        sys.exit(app.run())
    except Exception as e:
        logger.exception("Fatal error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()