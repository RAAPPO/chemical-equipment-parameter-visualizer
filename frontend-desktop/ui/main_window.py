import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QScrollArea, QFrame, 
                             QGridLayout, QFileDialog, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QCursor

# --- WORKER THREADS (Keep existing logic) ---
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

# --- NEW: DATASET CARD WIDGET (Matches DatasetCard.jsx) ---
class DatasetCardWidget(QFrame):
    def __init__(self, dataset, on_view, on_pdf):
        super().__init__()
        self.setStyleSheet("""
            DatasetCardWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
            DatasetCardWidget:hover {
                border: 1px solid #3B82F6;
            }
        """)
        self.setFixedSize(320, 200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header (Icon + Filename)
        h_layout = QHBoxLayout()
        icon = QLabel("📊")
        icon.setStyleSheet("font-size: 24px; border: none;")
        name = QLabel(dataset.get('filename', 'Unknown'))
        name.setStyleSheet("font-weight: bold; font-size: 14px; color: #1F2937; border: none;")
        name.setWordWrap(True)
        h_layout.addWidget(icon)
        h_layout.addWidget(name, 1)
        layout.addLayout(h_layout)
        
        # Date
        date_lbl = QLabel(f"Uploaded: {dataset.get('uploaded_at', '')[:10]}")
        date_lbl.setStyleSheet("color: #6B7280; font-size: 12px; border: none; margin-bottom: 10px;")
        layout.addWidget(date_lbl)
        
        # Stats Row
        stats_layout = QHBoxLayout()
        count_bg = QLabel(f" {dataset.get('total_equipment', 0)} Units ")
        count_bg.setStyleSheet("background: #EFF6FF; color: #1E40AF; border-radius: 4px; padding: 4px; font-size: 11px; font-weight: bold; border: none;")
        stats_layout.addWidget(count_bg)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        layout.addStretch()
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_view = QPushButton("View Analysis")
        btn_view.setCursor(Qt.PointingHandCursor)
        btn_view.setStyleSheet("""
            QPushButton { background: #1E3A8A; color: white; border-radius: 6px; padding: 6px; font-weight: bold; border: none; }
            QPushButton:hover { background: #1E40AF; }
        """)
        btn_view.clicked.connect(lambda: on_view(dataset))
        
        btn_pdf = QPushButton("PDF")
        btn_pdf.setFixedWidth(50)
        btn_pdf.setCursor(Qt.PointingHandCursor)
        btn_pdf.setStyleSheet("""
            QPushButton { background: #10B981; color: white; border-radius: 6px; padding: 6px; font-weight: bold; border: none; }
            QPushButton:hover { background: #059669; }
        """)
        btn_pdf.clicked.connect(lambda: on_pdf(dataset))
        
        btn_layout.addWidget(btn_view)
        btn_layout.addWidget(btn_pdf)
        layout.addLayout(btn_layout)

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()
    
    def __init__(self, api_client, username):
        super().__init__()
        self.api_client, self.username = api_client, username
        self.detail_windows = []
        self.init_ui()
        self.load_datasets()
        
    def init_ui(self):
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.resize(1280, 900)
        self.setStyleSheet("background-color: #F3F4F6;") # bg-gray-100
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- HEADER (Matches Dashboard.jsx Header) ---
        header = QFrame()
        header.setStyleSheet("background-color: #1E3A8A;") # Primary Blue
        header.setFixedHeight(70)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)
        
        title = QLabel("Chemical Equipment Parameter Visualizer")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold; border: none;")
        
        user_info = QLabel(f"Welcome, {self.username}")
        user_info.setStyleSheet("color: white; margin-right: 15px; border: none;")
        
        btn_logout = QPushButton("Logout")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton { background: #DC2626; color: white; padding: 6px 16px; border-radius: 6px; font-weight: bold; border: none; }
            QPushButton:hover { background: #B91C1C; }
        """)
        btn_logout.clicked.connect(self.handle_logout)
        
        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(user_info)
        h_layout.addWidget(btn_logout)
        main_layout.addWidget(header)
        
        # --- SCROLLABLE CONTENT ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(32, 32, 32, 32)
        
        # Page Title Row
        title_row = QHBoxLayout()
        pg_title = QLabel("Datasets")
        pg_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1F2937; border: none;")
        
        btn_upload = QPushButton("Upload CSV")
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.setFixedSize(120, 40)
        btn_upload.setStyleSheet("""
            QPushButton { background: #1E3A8A; color: white; border-radius: 6px; font-weight: bold; border: none; }
            QPushButton:hover { background: #1E40AF; }
        """)
        btn_upload.clicked.connect(self.handle_upload)
        
        title_row.addWidget(pg_title)
        title_row.addStretch()
        title_row.addWidget(btn_upload)
        self.content_layout.addLayout(title_row)
        self.content_layout.addSpacing(20)
        
        # Grid for Cards
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(24)
        self.content_layout.addLayout(self.grid_layout)
        self.content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def load_datasets(self):
        self.thread = DataLoadThread(self.api_client)
        self.thread.finished.connect(self.populate_grid)
        self.thread.start()

    def populate_grid(self, res):
        # Clear grid
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
            
        if res["success"]:
            datasets = res["data"]
            cols = 3
            for idx, d in enumerate(datasets):
                card = DatasetCardWidget(d, self.view_details, self.download_pdf)
                self.grid_layout.addWidget(card, idx // cols, idx % cols)
        else:
            # Show Error placeholder
            err = QLabel("Failed to load datasets")
            self.grid_layout.addWidget(err, 0, 0)

    def handle_upload(self):
        f, _ = QFileDialog.getOpenFileName(self, "Upload CSV", "", "CSV (*.csv)")
        if f:
            res = self.api_client.upload_csv(f)
            if res["success"]: 
                self.load_datasets()
            else:
                QMessageBox.warning(self, "Upload Failed", res.get("error", "Unknown error"))

    def view_details(self, d):
        from widgets.detail_widget import DatasetDetailWindow
        # Pass style matching window
        win = DatasetDetailWindow(self.api_client, d, self)
        self.detail_windows.append(win)
        win.show()

    def download_pdf(self, d):
        p, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"report_{d['filename'][:-4]}.pdf", "PDF (*.pdf)")
        if p:
            self.pdf_worker = PDFWorker(self.api_client, d["id"], p)
            self.pdf_worker.finished.connect(lambda s, m: QMessageBox.information(self, "Done", "Saved PDF") if s else QMessageBox.warning(self, "Error", m))
            self.pdf_worker.start()

    def handle_logout(self):
        if QMessageBox.question(self, "Logout", "Are you sure?") == QMessageBox.Yes:
            self.logout_requested.emit()