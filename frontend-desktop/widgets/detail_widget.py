import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QTabWidget, QHeaderView, QApplication, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

class DatasetDetailWindow(QMainWindow):
    """Refined analysis dashboard for specific datasets."""
    
    def __init__(self, api_client, dataset, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.dataset = dataset
        self.analytics = None
        self.equipment = []
        self.stat_values = {}
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Construct the dashboard layout with high-density components."""
        self.setWindowTitle(f"Analysis - {self.dataset.get('filename')}")
        screen = QApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        self.setMinimumSize(950, 650)
        
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Header Section
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 5)
        
        title_vbox = QVBoxLayout()
        header_title = QLabel(self.dataset.get('filename', 'Dataset Analysis'))
        header_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #111827;")
        subtitle = QLabel(f"Dataset ID: {self.dataset.get('id', 'N/A')}")
        subtitle.setStyleSheet("font-size: 12px; color: #6B7280; font-weight: 400;")
        title_vbox.addWidget(header_title)
        title_vbox.addWidget(subtitle)
        
        header_layout.addLayout(title_vbox)
        header_layout.addStretch()
        
        close_btn = QPushButton("✖ Close")
        close_btn.setFixedWidth(100)
        close_btn.setStyleSheet("""
            QPushButton { background-color: #F3F4F6; color: #374151; border-radius: 6px; padding: 8px; font-weight: 600; border: 1px solid #E5E7EB; }
            QPushButton:hover { background-color: #E5E7EB; }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        main_layout.addWidget(header_widget)

        # Stat Summary Grid
        stats_frame = QFrame()
        stats_frame.setObjectName("StatsFrame")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        stats_layout.setSpacing(20)
        
        stats_config = [
            ("Total Equipment", "total", "#1E40AF"),
            ("Avg Flowrate", "flowrate", "#2563EB"),
            ("Avg Pressure", "pressure", "#3B82F6"),
            ("Avg Temperature", "temp", "#EA580C")
        ]
        
        for title, key, color in stats_config:
            card = QFrame()
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.setSpacing(2)
            
            title_lbl = QLabel(title.upper())
            title_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #6B7280; letter-spacing: 0.5px;")
            val_lbl = QLabel("-")
            val_lbl.setStyleSheet(f"font-size: 26px; font-weight: 800; color: {color};")
            
            card_layout.addWidget(title_lbl)
            card_layout.addWidget(val_lbl)
            self.stat_values[key] = val_lbl
            stats_layout.addWidget(card)
        
        main_layout.addWidget(stats_frame)
        
        # Tabs for Visualization and Data
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_charts_tab(), "📊 Visual Analytics")
        self.tabs.addTab(self.create_equipment_tab(), "📋 Data Explorer")
        main_layout.addWidget(self.tabs, 1)
        
        self.apply_stylesheet()

    def create_charts_tab(self):
        """Analytics visualization tab."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)
        
        pie_container = QFrame()
        pie_container.setStyleSheet("background-color: white; border: 1px solid #F3F4F6; border-radius: 10px;")
        pie_vbox = QVBoxLayout(pie_container)
        pie_title = QLabel("Equipment Distribution")
        pie_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #374151; margin-bottom: 5px;")
        pie_title.setAlignment(Qt.AlignCenter)
        pie_vbox.addWidget(pie_title)
        
        self.pie_figure = Figure(figsize=(5, 4), dpi=100, facecolor='white')
        self.pie_canvas = FigureCanvas(self.pie_figure)
        pie_vbox.addWidget(self.pie_canvas)
        layout.addWidget(pie_container, 0, 0)
        
        bar_container = QFrame()
        bar_container.setStyleSheet("background-color: white; border: 1px solid #F3F4F6; border-radius: 10px;")
        bar_vbox = QVBoxLayout(bar_container)
        bar_title = QLabel("Mean Parameters")
        bar_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #374151; margin-bottom: 5px;")
        bar_title.setAlignment(Qt.AlignCenter)
        bar_vbox.addWidget(bar_title)
        
        self.bar_figure = Figure(figsize=(5, 4), dpi=100, facecolor='white')
        self.bar_canvas = FigureCanvas(self.bar_figure)
        bar_vbox.addWidget(self.bar_canvas)
        layout.addWidget(bar_container, 0, 1)
        
        return widget

    def create_equipment_tab(self):
        """Equipment details table tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(6)
        self.equipment_table.setHorizontalHeaderLabels(["Name", "Type", "Flow (m³/h)", "Press (bar)", "Temp (°C)", "Condition"])
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.equipment_table.setShowGrid(False)
        self.equipment_table.verticalHeader().setVisible(False)
        layout.addWidget(self.equipment_table)
        return widget

    def apply_stylesheet(self):
        """Apply dashboard-specific styles."""
        self.setStyleSheet("""
            QMainWindow { background-color: #F9FAFB; }
            #StatsFrame { background-color: white; border: 1px solid #E5E7EB; border-radius: 12px; }
            QTabWidget::pane { border: 1px solid #E5E7EB; border-radius: 12px; background-color: white; }
            QTabBar::tab { padding: 10px 25px; margin: 5px; font-weight: 600; border-radius: 6px; }
            QTabBar::tab:selected { background-color: #EFF6FF; color: #2563EB; }
            QTableWidget { border: none; font-size: 13px; background-color: white; }
            QHeaderView::section { background-color: white; color: #4B5563; padding: 10px; border: none; border-bottom: 2px solid #F3F4F6; font-weight: 700; }
        """)

    def load_data(self):
        """Retrieve analytics and equipment details from API."""
        try:
            res_a = self.api_client.get_analytics(self.dataset["id"])
            if res_a["success"]:
                self.analytics = res_a["data"]
                self.update_stats()
                self.update_charts()
            
            res_e = self.api_client.get_equipment(self.dataset["id"])
            if res_e["success"]:
                self.equipment = res_e["data"]
                self.populate_table()
        except Exception as e:
            logger.error(f"UI Loading Error: {e}")

    def update_stats(self):
        """Update stat card labels with fetched analytics."""
        if self.analytics:
            self.stat_values['total'].setText(str(self.analytics.get('total_equipment', 0)))
            self.stat_values['flowrate'].setText(f"{self.analytics.get('avg_flowrate', 0):.1f}")
            self.stat_values['pressure'].setText(f"{self.analytics.get('avg_pressure', 0):.1f}")
            self.stat_values['temp'].setText(f"{self.analytics.get('avg_temperature', 0):.1f}°C")

    def update_charts(self):
        """Render visualization charts."""
        if not self.analytics: return
        colors = ['#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
        
        # Donut Distribution Chart
        dist = self.analytics.get("equipment_type_distribution", {})
        if dist:
            self.pie_figure.clear()
            ax = self.pie_figure.add_subplot(111)
            ax.pie(dist.values(), labels=dist.keys(), autopct='%1.0f%%', colors=colors, 
                   wedgeprops={'width': 0.4, 'edgecolor': 'w', 'linewidth': 3})
            self.pie_canvas.draw()
        
        # Mean Parameters Bar Chart
        self.bar_figure.clear()
        ax = self.bar_figure.add_subplot(111)
        params = ['Flow', 'Press', 'Temp']
        vals = [self.analytics.get('avg_flowrate', 0), self.analytics.get('avg_pressure', 0), self.analytics.get('avg_temperature', 0)]
        ax.bar(params, vals, color=['#3B82F6', '#60A5FA', '#93C5FD'], width=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.bar_canvas.draw()

    def populate_table(self):
        """Render detailed equipment list."""
        self.equipment_table.setRowCount(len(self.equipment))
        for row, eq in enumerate(self.equipment):
            self.equipment_table.setItem(row, 0, QTableWidgetItem(eq.get("equipment_name", "")))
            self.equipment_table.setItem(row, 1, QTableWidgetItem(eq.get("equipment_type", "")))
            for i, key in enumerate(['flowrate', 'pressure', 'temperature'], 2):
                item = QTableWidgetItem(f"{eq.get(key, 0):.2f}")
                item.setTextAlignment(Qt.AlignCenter)
                self.equipment_table.setItem(row, i, item)
            
            is_outlier = eq.get("is_pressure_outlier") or eq.get("is_temperature_outlier")
            status_item = QTableWidgetItem("⚠️ Outlier" if is_outlier else "✅ Normal")
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QColor("#DC2626" if is_outlier else "#16A34A"))
            self.equipment_table.setItem(row, 5, status_item)

DatasetDetailDialog = DatasetDetailWindow