import os
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                             QFileDialog, QMessageBox, QHeaderView, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class PDFWorker(QThread):
    finished = pyqtSignal(bool, str)
    def __init__(self, api_client, d_id, path):
        super().__init__()
        self.api_client, self.d_id, self.path = api_client, d_id, path
    def run(self):
        res = self.api_client.download_pdf(self.d_id, self.path)
        self.finished.emit(res["success"], res.get("error", "Success"))

class DataLoadThread(QThread):
    finished = pyqtSignal(dict)
    def __init__(self, api_client):
        super().__init__(); self.api_client = api_client
    def run(self):
        self.finished.emit(self.api_client.get_datasets())

class MainWindow(QMainWindow):
    """Symmetrical Command Center Dashboard."""
    logout_requested = pyqtSignal()
    
    def __init__(self, api_client, username):
        super().__init__()
        self.api_client, self.username = api_client, username
        self.datasets, self.detail_windows = [], []
        self.init_ui()
        self.load_datasets()
        
    def init_ui(self):
        self.setWindowTitle("CEPV Dashboard")
        self.resize(1280, 800)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
# Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        # Updated background color and added a border for industrial depth
        sidebar.setStyleSheet("background-color: #1E293B; border-right: 1px solid #334155;")
        s_layout = QVBoxLayout(sidebar)
        s_layout.setContentsMargins(15, 30, 15, 30)
        
        brand = QLabel("CEPV SYSTEM")
        brand.setStyleSheet("color: white; font-size: 18px; font-weight: 900; margin-bottom: 40px; padding-left: 10px;")
        s_layout.addWidget(brand)
        
        # New industrial button style with hover effect
        btn_style = """
            QPushButton {
                text-align: left; padding: 14px 20px; background: transparent; 
                color: #F1F5F9; border: none; font-weight: 700; font-size: 12px;
                border-radius: 8px; margin-bottom: 5px;
            }
            QPushButton:hover { background: #334155; color: #6366F1; }
        """
        
        self.btn_up = QPushButton("  📁  UPLOAD NEW DATA")
        self.btn_up.setStyleSheet(btn_style)
        self.btn_up.setCursor(Qt.PointingHandCursor)
        self.btn_up.clicked.connect(self.handle_upload)
        s_layout.addWidget(self.btn_up)
        
        s_layout.addStretch()
        
        # Modernized logout button to match the theme
        self.lo_btn = QPushButton("Log Out")
        self.lo_btn.setMinimumHeight(40)
        self.lo_btn.setCursor(Qt.PointingHandCursor)
        self.lo_btn.setStyleSheet("""
            QPushButton {
                background: #EF4444; color: white; border-radius: 8px; 
                font-weight: 800; font-size: 13px; margin: 10px;
            }
            QPushButton:hover { background: #DC2626; }
        """)
        self.lo_btn.clicked.connect(self.handle_logout)
        s_layout.addWidget(self.lo_btn)
        layout.addWidget(sidebar)
        
        # Main Content
        content = QWidget()
        content.setStyleSheet("background-color: #F8FAFC;")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(35, 35, 35, 35)
        
        header = QHBoxLayout()
        header.addWidget(QLabel("Global Inventory", styleSheet="font-size: 24px; font-weight: 800; color: #1E293B;"))
        header.addStretch()
        
        ref_btn = QPushButton("Refresh")
        ref_btn.setFixedSize(100, 35)
        ref_btn.setStyleSheet("background: white; border: 1px solid #E2E8F0; border-radius: 6px; font-weight: 600;")
        ref_btn.clicked.connect(self.load_datasets)
        header.addWidget(ref_btn)
        c_layout.addLayout(header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Filename", "Units", "Timestamp", "Analytics", "Report"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableWidget { background: white; border: 1px solid #E2E8F0; border-radius: 10px; }")
        c_layout.addWidget(self.table)
        layout.addWidget(content, 1)

    def load_datasets(self):
        self.thread = DataLoadThread(self.api_client)
        self.thread.finished.connect(self.on_datasets_loaded)
        self.thread.start()

    def on_datasets_loaded(self, res):
        if res["success"]:
            self.datasets = res["data"]
            self.table.setRowCount(len(self.datasets))
            for i, d in enumerate(self.datasets):
                self.table.setItem(i, 0, QTableWidgetItem(d.get("filename", "")))
                self.table.setItem(i, 1, QTableWidgetItem(f"{d.get('total_equipment', 0)} Units"))
                self.table.setItem(i, 2, QTableWidgetItem(d.get("uploaded_at", "")[:16]))
                
                v_btn = QPushButton("View")
                v_btn.setStyleSheet("background: #6366F1; color: white; border-radius: 4px;")
                v_btn.clicked.connect(lambda _, det=d: self.view_details(det))
                self.table.setCellWidget(i, 3, v_btn)
                
                p_btn = QPushButton("PDF")
                p_btn.setStyleSheet("background: #10B981; color: white; border-radius: 4px;")
                p_btn.clicked.connect(lambda _, det=d: self.download_pdf(det))
                self.table.setCellWidget(i, 4, p_btn)

    def handle_upload(self):
        f, _ = QFileDialog.getOpenFileName(self, "Upload CSV", "", "CSV (*.csv)")
        if f and self.api_client.upload_csv(f)["success"]: self.load_datasets()

    def view_details(self, d):
        from widgets.detail_widget import DatasetDetailWindow
        win = DatasetDetailWindow(self.api_client, d, self)
        self.detail_windows.append(win)
        win.show()

    def download_pdf(self, d):
        p, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"{d['filename']}.pdf", "PDF (*.pdf)")
        if p:
            self.pdf_worker = PDFWorker(self.api_client, d["id"], p)
            self.pdf_worker.finished.connect(lambda success, msg: 
                QMessageBox.information(self, "PDF Status", "Download Complete") if success 
                else QMessageBox.warning(self, "Error", msg))
            self.pdf_worker.start()

    def handle_logout(self):
        if QMessageBox.question(self, "Logout", "Exit?") == QMessageBox.Yes: self.logout_requested.emit()