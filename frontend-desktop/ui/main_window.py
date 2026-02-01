import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QFileDialog, QMessageBox, QHeaderView, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

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

        # Replaced print with logger.info for consistency
        logger.info(f"MainWindow initialized for user: {username}")
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.show() 
        self.raise_()
        self.activateWindow()
        
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.setGeometry(100, 100, 1200, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
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
        
        central_widget.setLayout(main_layout)
        
        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f3f4f6;
            }
            QLabel#title {
                color: #1E3A8A;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#username {
                color: #6B7280;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1E3A8A;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1E40AF;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #D1D5DB;
                border-radius: 5px;
                gridline-color: #E5E7EB;
            }
            QHeaderView::section {
                background-color: #1E3A8A;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
    
    def create_header(self):
        """Create header section."""
        header_frame = QFrame()
        header_layout = QHBoxLayout()
        
        title = QLabel("Chemical Equipment Parameter Visualizer")
        title.setObjectName("title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        username_label = QLabel(f"Welcome, {self.username}")
        username_label.setObjectName("username")
        header_layout.addWidget(username_label)
        
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.handle_logout)
        logout_btn.setStyleSheet("background-color: #DC2626;")
        header_layout.addWidget(logout_btn)
        
        header_frame.setLayout(header_layout)
        return header_frame
    
    def create_toolbar(self):
        """Create toolbar with action buttons."""
        toolbar_frame = QFrame()
        toolbar_layout = QHBoxLayout()
        
        toolbar_label = QLabel("Datasets")
        toolbar_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #374151;")
        toolbar_layout.addWidget(toolbar_label)
        
        toolbar_layout.addStretch()
        
        upload_btn = QPushButton("📁 Upload CSV")
        upload_btn.clicked.connect(self.handle_upload)
        toolbar_layout.addWidget(upload_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_datasets)
        toolbar_layout.addWidget(refresh_btn)
        
        toolbar_frame.setLayout(toolbar_layout)
        return toolbar_frame
    
    def create_table(self):
        """Create datasets table."""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Filename", "Equipment Count", "Upload Date", "Actions", "PDF"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        return table
    
    def load_datasets(self):
        """Load datasets from API."""
        self.statusBar().showMessage("Loading datasets...")
        
        # Use thread for API call
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
            # Filename
            self.table.setItem(row, 0, QTableWidgetItem(dataset.get("filename", "")))
            
            # Equipment count
            count = dataset.get("total_equipment") or dataset.get("equipment_count", 0)
            self.table.setItem(row, 1, QTableWidgetItem(str(count)))
            
            # Upload date
            date_str = dataset.get("uploaded_at", "")
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime("%d %b %Y, %H:%M")
                    self.table.setItem(row, 2, QTableWidgetItem(formatted_date))
                except ValueError:
                    self.table.setItem(row, 2, QTableWidgetItem(date_str))
            
            # View Details button
            view_btn = QPushButton("View Details")
            view_btn.clicked.connect(lambda checked, d=dataset: self.view_details(d))
            self.table.setCellWidget(row, 3, view_btn)
            
            # Download PDF button
            pdf_btn = QPushButton("Download PDF")
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