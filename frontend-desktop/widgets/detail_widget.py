"""
Dataset Detail Window - 3-Tab Layout with Full-Width Content
Tab 1: Overview (Stats)
Tab 2: Visual Analytics (Charts)  
Tab 3: Equipment Data (Table)
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QTabWidget, QGridLayout, QHeaderView, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import logging

logger = logging.getLogger(__name__)


class DatasetDetailWindow(QMainWindow):
    """Dataset detail window with 3 clean tabs."""
    
    def __init__(self, api_client, dataset, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.dataset = dataset
        self.analytics = None
        self.equipment = []
        
        # Screen info
        self.screen = QApplication.primaryScreen().geometry()
        
        # Stat labels
        self.stat_labels = {}
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize UI with 3-tab layout."""
        self.setWindowTitle(f"Dataset Analysis - {self.dataset.get('filename')}")
        
        # Window size (75% of screen)
        width = int(self.screen.width() * 0.75)
        height = int(self.screen.height() * 0.80)
        width = max(1000, min(width, 1500))
        height = max(700, min(height, 1000))
        
        self.resize(width, height)
        self.setMinimumSize(1000, 700)
        
        # Center
        x = (self.screen.width() - width) // 2
        y = (self.screen.height() - height) // 2
        self.move(x, y)
        
        # Main container
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Header
        header = QLabel(f"📊 {self.dataset.get('filename', 'Dataset Analysis')}")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E3A8A;")
        layout.addWidget(header)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #E5E7EB;
                border-radius: 12px;
                background-color: white;
                padding: 25px;
            }
            QTabBar::tab {
                background-color: #F3F4F6;
                color: #374151;
                padding: 16px 40px;
                border: none;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                margin-right: 8px;
                font-size: 16px;
                font-weight: 600;
                min-width: 180px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #1E3A8A;
                border-bottom: 4px solid #1E3A8A;
            }
            QTabBar::tab:hover:!selected {
                background-color: #E5E7EB;
            }
        """)
        
        # Tab 1: Overview (Stats)
        overview_tab = self.create_overview_tab()
        self.tabs.addTab(overview_tab, "📋 Overview")
        
        # Tab 2: Visual Analytics (Charts)
        charts_tab = self.create_charts_tab()
        self.tabs.addTab(charts_tab, "📊 Visual Analytics")
        
        # Tab 3: Equipment Data (Table)
        equipment_tab = self.create_equipment_tab()
        self.tabs.addTab(equipment_tab, "📈 Equipment Data")
        
        layout.addWidget(self.tabs, 1)
        
        # Close button
        close_btn = QPushButton("✖ Close Window")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                padding: 16px 32px;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                min-height: 50px;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        container.setLayout(layout)
        self.apply_stylesheet()
    
    def create_overview_tab(self):
        """Tab 1: Overview with stat cards."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Dataset Summary")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #374151; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Stats grid (2x2)
        grid = QGridLayout()
        grid.setSpacing(25)
        
        cards = [
            ("📊", "Total Equipment", "total"),
            ("💧", "Average Flowrate", "flowrate"),
            ("⚡", "Average Pressure", "pressure"),
            ("🌡️", "Average Temperature", "temp")
        ]
        
        for idx, (icon, title_text, key) in enumerate(cards):
            card = self.create_large_stat_card(icon, title_text, key)
            grid.addWidget(card, idx // 2, idx % 2)
        
        layout.addLayout(grid)
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_large_stat_card(self, icon, title, key):
        """Create a large stat card."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 2px solid #E5E7EB;
                border-radius: 15px;
                padding: 30px;
            }
        """)
        card.setMinimumHeight(150)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Icon + Title
        top_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 42px;")
        top_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; color: #6B7280; font-weight: 600;")
        top_layout.addWidget(title_label, 1)
        
        layout.addLayout(top_layout)
        
        # Value
        value_label = QLabel("-")
        value_label.setStyleSheet("font-size: 38px; font-weight: bold; color: #1E3A8A; margin-top: 10px;")
        layout.addWidget(value_label)
        
        layout.addStretch()
        card.setLayout(layout)
        
        self.stat_labels[key] = value_label
        return card
    
    def create_charts_tab(self):
        """Tab 2: Visual Analytics - FULL WIDTH, vertical stacking."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Visual Analytics")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #374151; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # PIE CHART (Full Width)
        pie_section = QFrame()
        pie_section.setStyleSheet("QFrame { background-color: #F9FAFB; border-radius: 12px; padding: 20px; }")
        pie_layout = QVBoxLayout()
        
        pie_title = QLabel("Equipment Type Distribution")
        pie_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #374151; margin-bottom: 15px;")
        pie_title.setAlignment(Qt.AlignCenter)
        pie_layout.addWidget(pie_title)
        
        self.pie_figure = Figure(figsize=(12, 6), dpi=100, facecolor='#F9FAFB')
        self.pie_canvas = FigureCanvas(self.pie_figure)
        self.pie_canvas.setMinimumHeight(400)
        pie_layout.addWidget(self.pie_canvas)
        
        pie_section.setLayout(pie_layout)
        layout.addWidget(pie_section)
        
        # BAR CHART (Full Width)
        bar_section = QFrame()
        bar_section.setStyleSheet("QFrame { background-color: #F9FAFB; border-radius: 12px; padding: 20px; }")
        bar_layout = QVBoxLayout()
        
        bar_title = QLabel("Average Parameters Comparison")
        bar_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #374151; margin-bottom: 15px;")
        bar_title.setAlignment(Qt.AlignCenter)
        bar_layout.addWidget(bar_title)
        
        self.bar_figure = Figure(figsize=(12, 6), dpi=100, facecolor='#F9FAFB')
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_canvas.setMinimumHeight(400)
        bar_layout.addWidget(self.bar_canvas)
        
        bar_section.setLayout(bar_layout)
        layout.addWidget(bar_section)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_equipment_tab(self):
        """Tab 3: Equipment Data - FULL WIDTH table."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Equipment Details")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #374151; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Table
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(6)
        self.equipment_table.setHorizontalHeaderLabels([
            "Equipment Name", "Type", "Flowrate", "Pressure", "Temperature", "Status"
        ])
        
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.equipment_table.verticalHeader().setDefaultSectionSize(55)
        self.equipment_table.setAlternatingRowColors(True)
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.equipment_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.equipment_table, 1)
        widget.setLayout(layout)
        return widget
    
    def apply_stylesheet(self):
        """Apply main stylesheet."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f9fafb;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                gridline-color: #F3F4F6;
                font-size: 15px;
            }
            QTableWidget::item {
                padding: 16px 12px;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E3A8A;
            }
            QHeaderView::section {
                background-color: #1E3A8A;
                color: white;
                padding: 18px 12px;
                border: none;
                font-weight: 700;
                font-size: 15px;
            }
        """)
    
    def load_data(self):
        """Load data from API."""
        try:
            # Analytics
            result = self.api_client.get_analytics(self.dataset["id"])
            if result["success"]:
                self.analytics = result["data"]
                self.update_stats()
                self.update_charts()
            
            # Equipment
            result = self.api_client.get_equipment(self.dataset["id"])
            if result["success"]:
                self.equipment = result["data"]
                self.populate_table()
            
            logger.info(f"Data loaded: {self.dataset.get('filename')}")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    def update_stats(self):
        """Update stat card values."""
        if self.analytics:
            self.stat_labels['total'].setText(str(self.analytics.get('total_equipment', 0)))
            self.stat_labels['flowrate'].setText(f"{self.analytics.get('avg_flowrate', 0):.2f}")
            self.stat_labels['pressure'].setText(f"{self.analytics.get('avg_pressure', 0):.2f}")
            self.stat_labels['temp'].setText(f"{self.analytics.get('avg_temperature', 0):.2f}°C")
    
    def update_charts(self):
        """Draw charts with full width."""
        if not self.analytics:
            return
        
        colors = ['#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE', '#F97316', '#FB923C', '#FDBA74']
        
        # PIE CHART - Centered, larger
        distribution = self.analytics.get("equipment_type_distribution", {})
        if distribution:
            self.pie_figure.clear()
            ax = self.pie_figure.add_subplot(111)
            ax.set_facecolor('#F9FAFB')
            
            wedges, texts, autotexts = ax.pie(
                list(distribution.values()),
                labels=list(distribution.keys()),
                autopct='%1.1f%%',
                colors=colors[:len(distribution)],
                startangle=90,
                textprops={'fontsize': 14, 'weight': 'bold'},
                wedgeprops={'edgecolor': 'white', 'linewidth': 3},
                pctdistance=0.85
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(13)
                autotext.set_weight('bold')
            
            for text in texts:
                text.set_fontsize(13)
                text.set_weight('bold')
            
            ax.axis('equal')
            self.pie_figure.tight_layout(pad=1)
            self.pie_canvas.draw()
        
        # BAR CHART - Full width
        self.bar_figure.clear()
        ax = self.bar_figure.add_subplot(111)
        ax.set_facecolor('#F9FAFB')
        self.bar_figure.patch.set_facecolor('#F9FAFB')
        
        params = ['Flowrate', 'Pressure', 'Temperature']
        values = [
            self.analytics.get('avg_flowrate', 0),
            self.analytics.get('avg_pressure', 0),
            self.analytics.get('avg_temperature', 0)
        ]
        
        bars = ax.bar(params, values, color=['#1E3A8A', '#3B82F6', '#60A5FA'], 
                     width=0.6, edgecolor='white', linewidth=3)
        
        ax.set_ylabel("Value", fontsize=15, weight='bold', color='#374151')
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1.5)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(2)
        ax.spines['bottom'].set_linewidth(2)
        ax.tick_params(labelsize=14, colors='#374151', width=2)
        
        # Value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (max(values) * 0.02),
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=15, weight='bold', color='#1F2937')
        
        self.bar_figure.tight_layout(pad=1)
        self.bar_canvas.draw()
    
    def populate_table(self):
        """Fill equipment table."""
        self.equipment_table.setRowCount(len(self.equipment))
        
        for row, eq in enumerate(self.equipment):
            # Name
            name_item = QTableWidgetItem(eq.get("equipment_name", ""))
            self.equipment_table.setItem(row, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem(eq.get("equipment_type", ""))
            self.equipment_table.setItem(row, 1, type_item)
            
            # Flowrate
            flow_item = QTableWidgetItem(f"{eq.get('flowrate', 0):.2f}")
            flow_item.setTextAlignment(Qt.AlignCenter)
            self.equipment_table.setItem(row, 2, flow_item)
            
            # Pressure
            pres_item = QTableWidgetItem(f"{eq.get('pressure', 0):.2f}")
            pres_item.setTextAlignment(Qt.AlignCenter)
            self.equipment_table.setItem(row, 3, pres_item)
            
            # Temperature
            temp_item = QTableWidgetItem(f"{eq.get('temperature', 0):.2f}")
            temp_item.setTextAlignment(Qt.AlignCenter)
            self.equipment_table.setItem(row, 4, temp_item)
            
            # Status
            is_outlier = eq.get("is_pressure_outlier") or eq.get("is_temperature_outlier")
            status = "⚠️ Outlier" if is_outlier else "✅ Normal"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            if is_outlier:
                status_item.setForeground(QColor("#DC2626"))
                font = QFont()
                font.setBold(True)
                font.setPointSize(13)
                status_item.setFont(font)
            
            self.equipment_table.setItem(row, 5, status_item)


# Backward compatibility
DatasetDetailDialog = DatasetDetailWindow