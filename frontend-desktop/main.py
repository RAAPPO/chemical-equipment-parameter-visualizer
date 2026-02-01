#!/usr/bin/env python3
"""
Chemical Equipment Parameter Visualizer - Desktop Application
Credits @ ADITYA V J
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from utils.api_client import APIClient


def main():
    """Main application entry point."""
    print("=" * 60)
    print("🚀 CHEMICAL EQUIPMENT PARAMETER VISUALIZER - Desktop App")
    print("=" * 60)
    print()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Chemical Equipment Parameter Visualizer")
    app.setOrganizationName("FOSSEE")
    
    print("✅ QApplication created")
    
    # Create API client
    api_client = APIClient()
    print("✅ API Client created")
    
    # Show login window
    login_window = LoginWindow(api_client)
    print("✅ Login window created")
    
    def on_login_success(username):
        """Handle successful login."""
        print()
        print("=" * 60)
        print(f"🎉 LOGIN SUCCESSFUL! Username: {username}")
        print("=" * 60)
        print("📂 Creating main window...")
        global main_window
        main_window = MainWindow(api_client, username)
        print("✅ Main window created")
              
        
        print("✅ Main window visible:", main_window.isVisible())
        print("✅ Main window size:", main_window.size())
        print()
    
    login_window.login_successful.connect(on_login_success)
    print("✅ Login success signal connected")
    
    print("📱 Showing login window...")
    result = login_window.exec_()
    print(f"📱 Login window result: {result} (Accepted={LoginWindow.Accepted})")
    
    if result == LoginWindow.Accepted:
        print("✅ Starting main event loop...")
        sys.exit(app.exec_())
    else:
        print("❌ Login cancelled or failed")
        sys.exit(0)


if __name__ == "__main__":
    main()