import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QFileDialog, QMessageBox, QHeaderView, QFrame,
                             QApplication, QDesktopWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

logger = logging.getLogger(__name__)

class DataLoadThread(QThread):
    """Background thread for loading dataset list from the API."""
    finished = pyqtSignal(dict)
    
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
    
    def run(self):
        result = self.api_client.get_datasets()
        self.finished.emit(result)

class MainWindow(QMainWindow):
    """Integrated dashboard main window."""
    
    logout_requested = pyqtSignal() # Notify controller for session termination
    
    def __init__(self, api_client, username):
        super().__init__()
        self.api_client = api_client
        self.username = username
        self.datasets = []
        self.detail_windows = []
        self.init_ui()
        self.load_datasets()
        
    def init_ui(self):
        """Initialize UI with optimized vertical spacing."""
        self.setWindowTitle("CEPV Dashboard")
        screen = QDesktopWidget().screenGeometry()
        self.resize(int(screen.width() * 0.75), int(screen.height() * 0.75))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)
        
        # 1. Global Navigation Bar
        nav_frame = QFrame()
        nav_frame.setStyleSheet("background-color: #1E3A8A; border-radius: 8px;")
        nav_frame.setFixedHeight(60)
        nav_layout = QHBoxLayout(nav_frame)
        
        title = QLabel("🧪 CEPV SYSTEM")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: 800; padding-left: 10px;")
        nav_layout.addWidget(title)
        
        nav_layout.addStretch()
        
        user_info = QLabel(f"Logged in as: {self.username}")
        user_info.setStyleSheet("color: #BFDBFE; font-size: 13px; font-weight: 500; margin-right: 15px;")
        nav_layout.addWidget(user_info)
        
        logout_btn = QPushButton("Sign Out")
        logout_btn.setFixedSize(90, 32)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton { background-color: #EF4444; color: white; border-radius: 4px; font-weight: 700; font-size: 11px; }
            QPushButton:hover { background-color: #DC2626; }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        nav_layout.addWidget(logout_btn)
        
        main_layout.addWidget(nav_frame)
        
        # 2. Dataset Toolbar
        tool_layout = QHBoxLayout()
        
        table_title = QLabel("Available Datasets")
        table_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #374151;")
        tool_layout.addWidget(table_title)
        
        tool_layout.addStretch()
        
        upload_btn = QPushButton("⊕ Upload CSV")
        upload_btn.setFixedSize(130, 36)
        upload_btn.clicked.connect(self.handle_upload)
        tool_layout.addWidget(upload_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedSize(100, 36)
        refresh_btn.setObjectName("refreshBtn")
        refresh_btn.clicked.connect(self.load_datasets)
        tool_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(tool_layout)
        
        # 3. Main Data Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Filename", "Equipment", "Date Uploaded", "Analytics", "Report"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        main_layout.addWidget(self.table)
        
        self.statusBar().showMessage("System Ready")
        self.apply_global_styles()

    def apply_global_styles(self):
        """Apply unified component styling."""
        self.setStyleSheet("""
            QMainWindow { background-color: #F9FAFB; }
            QPushButton {
                background-color: #3B82F6; color: white; border-radius: 6px;
                font-weight: 600; font-size: 13px; border: none;
            }
            QPushButton:hover { background-color: #2563EB; }
            #refreshBtn { background-color: white; color: #374151; border: 1px solid #E5E7EB; }
            #refreshBtn:hover { background-color: #F3F4F6; }
            
            QTableWidget {
                background-color: white; border: 1px solid #E5E7EB;
                border-radius: 10px; font-size: 13px;
            }
            QHeaderView::section {
                background-color: white; color: #6B7280; padding: 12px;
                border: none; border-bottom: 2px solid #F3F4F6; font-weight: 700;
            }
        """)

    def handle_upload(self):
        """Process local CSV upload."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.statusBar().showMessage(f"Uploading {os.path.basename(file_path)}...")
            result = self.api_client.upload_csv(file_path)
            if result["success"]:
                QMessageBox.information(self, "Success", "Dataset uploaded successfully!")
                self.load_datasets()
            else:
                QMessageBox.critical(self, "Upload Failed", result.get('error', 'Unknown error'))
                self.statusBar().showMessage("Upload failed.")

    def view_details(self, dataset):
        """Open specialized analysis window."""
        from widgets.detail_widget import DatasetDetailWindow
        
        detail_window = DatasetDetailWindow(self.api_client, dataset, self)
        self.detail_windows.append(detail_window)
        detail_window.destroyed.connect(
            lambda: self.detail_windows.remove(detail_window) if detail_window in self.detail_windows else None
        )
        detail_window.show()
        detail_window.raise_()
        detail_window.activateWindow()

    def download_pdf(self, dataset):
        """Export analysis report to PDF."""
        clean_name = dataset.get('filename', 'dataset').replace('.csv', '')
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Report", f"Report_{clean_name}.pdf", "PDF Files (*.pdf)"
        )
        if save_path:
            self.statusBar().showMessage("Downloading PDF report...")
            result = self.api_client.download_pdf(dataset["id"], save_path)
            if result["success"]:
                QMessageBox.information(self, "Success", f"PDF saved to:\n{save_path}")
                self.statusBar().showMessage("PDF Downloaded")
            else:
                QMessageBox.critical(self, "Download Failed", result.get('error', 'Unknown error'))

    def handle_logout(self):
        """Handle session logout request."""
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to sign out?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()

    def load_datasets(self):
        """Trigger background data synchronization."""
        self.statusBar().showMessage("Syncing data...")
        self.load_thread = DataLoadThread(self.api_client)
        self.load_thread.finished.connect(self.on_datasets_loaded)
        self.load_thread.start()

    def on_datasets_loaded(self, result):
        """Update dashboard UI with new dataset information."""
        if result["success"]:
            self.datasets = result["data"]
            self.populate_table()
            self.statusBar().showMessage(f"Dashboard updated: {len(self.datasets)} datasets.")
        else:
            QMessageBox.critical(self, "Sync Error", result.get('error', 'Could not refresh data.'))

    def populate_table(self):
        """Render dataset rows in the main table."""
        self.table.setRowCount(len(self.datasets))
        for row, dataset in enumerate(self.datasets):
            self.table.setItem(row, 0, QTableWidgetItem(dataset.get("filename", "")))
            
            count = dataset.get("total_equipment") or dataset.get("equipment_count", 0)
            item_count = QTableWidgetItem(str(count))
            item_count.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, item_count)
            
            date_str = dataset.get("uploaded_at", "N/A")
            self.table.setItem(row, 2, QTableWidgetItem(date_str[:16].replace('T', ' ')))
            
            view_btn = QPushButton("View")
            view_btn.setFixedSize(80, 28)
            view_btn.clicked.connect(lambda checked, d=dataset: self.view_details(d))
            self.table.setCellWidget(row, 3, view_btn)
            
            pdf_btn = QPushButton("PDF")
            pdf_btn.setFixedSize(80, 28)
            pdf_btn.setStyleSheet("background-color: #10B981;")
            pdf_btn.clicked.connect(lambda checked, d=dataset: self.download_pdf(d))
            self.table.setCellWidget(row, 4, pdf_btn)