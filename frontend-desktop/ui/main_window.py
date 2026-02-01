import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QFileDialog, QMessageBox, QHeaderView, QFrame,
                             QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QCloseEvent, QKeyEvent

# Initialize logger
logger = logging.getLogger(__name__)

class DataLoadThread(QThread):
    """Thread for loading data from API."""
    finished = pyqtSignal(dict)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    def run(self):
        result = self.api_client.get_datasets()
        self.finished.emit(result)


class MainWindow(QMainWindow):
    """Main application window."""
    
    # Signal to notify the application controller to handle logout
    logout_requested = pyqtSignal()
    
    def __init__(self, api_client, username):
        super().__init__()
        self.api_client = api_client
        self.username = username
        self.datasets = []
        self.init_ui()
        self.load_datasets()

        logger.info(f"MainWindow initialized for user: {username}")
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.show() 
        self.raise_()
        self.activateWindow()
        
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.setGeometry(100, 100, 1400, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(25)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Datasets table
        self.table = self.create_table()
        main_layout.addWidget(self.table)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Menu bar
        self.create_menu_bar()

        central_widget.setLayout(main_layout)
        
        # Apply modern stylesheet with better spacing
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f9fafb;
            }
            QLabel#title {
                color: #1E3A8A;
                font-size: 22px;
                font-weight: bold;
                line-height: 1.4;
            }
            QLabel#username {
                color: #6B7280;
                font-size: 15px;
                padding: 5px 10px;
            }
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #1E40AF;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #1E3A8A;
            }
            QPushButton:disabled {
                background-color: #9CA3AF;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                gridline-color: #F3F4F6;
                font-size: 13px;
                padding: 5px;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #F3F4F6;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E3A8A;
            }
            QTableWidget::item:hover {
                background-color: #F9FAFB;
            }
            QHeaderView::section {
                background-color: #1E3A8A;
                color: white;
                padding: 15px 10px;
                border: none;
                font-weight: 700;
                font-size: 14px;
            }
            QStatusBar {
                background-color: #F9FAFB;
                color: #6B7280;
                border-top: 1px solid #E5E7EB;
                padding: 8px;
                font-size: 13px;
            }
            QMenuBar {
                background-color: white;
                border-bottom: 1px solid #E5E7EB;
                padding: 8px;
                font-size: 13px;
            }
            QMenuBar::item {
                padding: 10px 15px;
                background-color: transparent;
                border-radius: 6px;
            }
            QMenuBar::item:selected {
                background-color: #F3F4F6;
            }
            QMenu {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 8px;
            }
            QMenu::item {
                padding: 10px 35px 10px 25px;
                border-radius: 6px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #DBEAFE;
                color: #1E3A8A;
            }
            QFrame {
                background-color: transparent;
            }
        """)

    def create_menu_bar(self):
        """Create professional menu bar with keyboard shortcuts."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('&File')
        
        upload_action = file_menu.addAction('📁 Upload CSV')
        upload_action.setShortcut('Ctrl+O')
        upload_action.setStatusTip('Upload a new CSV dataset')
        upload_action.triggered.connect(self.handle_upload)
        
        refresh_action = file_menu.addAction('🔄 Refresh')
        refresh_action.setShortcut('Ctrl+R')
        refresh_action.setStatusTip('Refresh dataset list')
        refresh_action.triggered.connect(self.load_datasets)
        
        file_menu.addSeparator()
        
        logout_action = file_menu.addAction('🚪 Logout')
        logout_action.setShortcut('Ctrl+L')
        logout_action.setStatusTip('Logout and return to login screen')
        logout_action.triggered.connect(self.handle_logout)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('❌ Exit')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.handle_exit)
        
        # View Menu
        view_menu = menubar.addMenu('&View')
        status_bar_action = view_menu.addAction('Status Bar')
        status_bar_action.setCheckable(True)
        status_bar_action.setChecked(True)
        status_bar_action.triggered.connect(self.toggle_status_bar)
        
        # Help Menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = help_menu.addAction('ℹ️ About')
        about_action.setShortcut('F1')
        about_action.triggered.connect(self.show_about)
        
        docs_action = help_menu.addAction('📖 Documentation')
        docs_action.triggered.connect(self.show_documentation)
        
        return menubar
    
    def create_header(self):
        """Create header section."""
        header_frame = QFrame()
        header_frame.setMinimumHeight(80)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("Chemical Equipment\nParameter Visualizer")
        title.setObjectName("title")
        title.setStyleSheet("""
            color: #1E3A8A;
            font-size: 22px;
            font-weight: bold;
            line-height: 1.3;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        username_label = QLabel(f"👤 {self.username}")
        username_label.setObjectName("username")
        username_label.setStyleSheet("color: #6B7280; font-size: 15px;")
        header_layout.addWidget(username_label)
        
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setToolTip("Logout and return to login screen (Ctrl+L)")
        logout_btn.setMinimumHeight(40)
        logout_btn.setMinimumWidth(120)
        logout_btn.clicked.connect(self.handle_logout)
        logout_btn.setStyleSheet("""
            background-color: #DC2626;
            padding: 10px 20px;
            font-size: 14px;
        """)
        header_layout.addWidget(logout_btn)
        
        header_frame.setLayout(header_layout)
        return header_frame
    
    def create_toolbar(self):
        """Create toolbar with action buttons."""
        toolbar_frame = QFrame()
        toolbar_frame.setMinimumHeight(60)
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        
        toolbar_label = QLabel("📊 Datasets")
        toolbar_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #374151;
        """)
        toolbar_layout.addWidget(toolbar_label)
        
        toolbar_layout.addStretch()
        
        upload_btn = QPushButton("📁 Upload CSV")
        upload_btn.setToolTip("Upload a new CSV dataset (Ctrl+O)")
        upload_btn.setMinimumHeight(42)
        upload_btn.setMinimumWidth(150)
        upload_btn.clicked.connect(self.handle_upload)
        toolbar_layout.addWidget(upload_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setToolTip("Refresh dataset list (Ctrl+R)")
        refresh_btn.setMinimumHeight(42)
        refresh_btn.setMinimumWidth(130)
        refresh_btn.clicked.connect(self.load_datasets)
        toolbar_layout.addWidget(refresh_btn)
        
        toolbar_frame.setLayout(toolbar_layout)
        return toolbar_frame
    
    def create_table(self):
        """Create datasets table."""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "📄 Filename",
            "📊 Equipment Count",
            "📅 Upload Date",
            "🔍 Actions",
            "📥 PDF"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setDefaultSectionSize(60)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setShowGrid(True)
        table.setMinimumHeight(400)
        return table
    
    def load_datasets(self):
        """Load datasets from API."""
        self.statusBar().showMessage("Loading datasets...")
        
        self.load_thread = DataLoadThread(self.api_client)
        self.load_thread.finished.connect(self.on_datasets_loaded)
        self.load_thread.start()
    
    def on_datasets_loaded(self, result):
        """Handle datasets loaded from API."""
        if result["success"]:
            self.datasets = result["data"]
            self.populate_table()
            self.statusBar().showMessage(f"Loaded {len(self.datasets)} datasets")
        else:
            QMessageBox.critical(self, "Error", f"Failed to load datasets:\n{result.get('error')}")
            self.statusBar().showMessage("Error loading datasets")
    
    def populate_table(self):
        """Populate table with datasets."""
        self.table.setRowCount(len(self.datasets))
        
        for row, dataset in enumerate(self.datasets):
            self.table.setItem(row, 0, QTableWidgetItem(dataset.get("filename", "")))
            
            count = dataset.get("total_equipment") or dataset.get("equipment_count", 0)
            self.table.setItem(row, 1, QTableWidgetItem(str(count)))
            
            date_str = dataset.get("uploaded_at", "")
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime("%d %b %Y, %H:%M")
                    self.table.setItem(row, 2, QTableWidgetItem(formatted_date))
                except ValueError:
                    self.table.setItem(row, 2, QTableWidgetItem(date_str))
            
            view_btn = QPushButton("🔍 View Details")
            view_btn.setMinimumHeight(35)
            view_btn.clicked.connect(lambda checked, d=dataset: self.view_details(d))
            self.table.setCellWidget(row, 3, view_btn)
            
            pdf_btn = QPushButton("📥 Download PDF")
            pdf_btn.setMinimumHeight(35)
            pdf_btn.setStyleSheet("background-color: #059669;")
            pdf_btn.clicked.connect(lambda checked, d=dataset: self.download_pdf(d))
            self.table.setCellWidget(row, 4, pdf_btn)
    
    def handle_upload(self):
        """Handle CSV upload."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            self.statusBar().showMessage("Uploading CSV...")
            result = self.api_client.upload_csv(file_path)
            
            if result["success"]:
                QMessageBox.information(self, "Success", "CSV uploaded successfully!")
                self.load_datasets()
            else:
                QMessageBox.critical(self, "Error", f"Upload failed:\n{result.get('error')}")
                self.statusBar().showMessage("Upload failed")
    
    def view_details(self, dataset):
        """View dataset details."""
        from widgets.detail_widget import DatasetDetailDialog
        dialog = DatasetDetailDialog(self.api_client, dataset, self)
        dialog.exec_()
    
    def download_pdf(self, dataset):
        """Download PDF report."""
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            f"report_{dataset.get('filename', 'dataset').replace('.csv', '')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if save_path:
            self.statusBar().showMessage("Downloading PDF...")
            result = self.api_client.download_pdf(dataset["id"], save_path)
            
            if result["success"]:
                QMessageBox.information(self, "Success", f"PDF saved to:\n{save_path}")
                self.statusBar().showMessage("PDF downloaded")
            else:
                QMessageBox.critical(self, "Error", f"Download failed:\n{result.get('error')}")
                self.statusBar().showMessage("Download failed")
    
    def handle_logout(self):
        """Handle logout."""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info(f"User {self.username} logged out")
            self.logout_requested.emit()

    def toggle_status_bar(self, checked):
        """Toggle status bar visibility."""
        if checked:
            self.statusBar().show()
        else:
            self.statusBar().hide()

    def handle_exit(self):
        """Handle application exit."""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit the application?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("Application exit requested by user")
            QApplication.quit()

    def show_about(self):
        """Show About dialog."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        from PyQt5.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle("About CEPV")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        title = QLabel("🧪 Chemical Equipment Parameter Visualizer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E3A8A;")
        layout.addWidget(title)
        
        version = QLabel("Version 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("font-size: 12px; color: #6B7280;")
        layout.addWidget(version)
        
        desc = QLabel(
            "A professional desktop application for analyzing\n"
            "and visualizing chemical equipment parameters.\n\n"
            "Built with PyQt5, Django REST Framework,\n"
            "and industry-best practices."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("font-size: 11px; color: #374151;")
        layout.addWidget(desc)
        
        credits = QLabel(
            "Developed by: RAAPPO\n"
            "FOSSEE Internship 2026"
        )
        credits.setAlignment(Qt.AlignCenter)
        credits.setStyleSheet("font-size: 10px; color: #6B7280; margin-top: 20px;")
        layout.addWidget(credits)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def show_documentation(self):
        """Show documentation link."""
        QMessageBox.information(
            self,
            "Documentation",
            "Documentation is available at:\n\n"
            "https://github.com/RAAPPO/chemical-equipment-parameter-visualizer\n\n"
            "For support, please open an issue on GitHub."
        )

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Escape:
            self.statusBar().showMessage("Press Ctrl+Q to exit or Ctrl+L to logout", 3000)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event (X button or Alt+F4)."""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to close the application?\n"
            "Click 'Logout' if you want to return to login screen.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("Application closed via window close button")
            event.accept()
            QApplication.quit()
        else:
            event.ignore()