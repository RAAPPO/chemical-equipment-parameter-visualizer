"""
Dataset Detail Window - FIXED: Scrollable, Maximizable, Properly Sized
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QTabWidget, QGridLayout, QHeaderView, QApplication,
                             QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import logging

logger = logging.getLogger(__name__)


class DatasetDetailWindow(QMainWindow):
    """Dataset detail window - Scrollable and maximizable."""
    
    def __init__(self, api_client, dataset, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.dataset = dataset
        self.analytics = None
        self.equipment = []
        self.stat_labels = {}
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle(f"Dataset Analysis - {self.dataset.get('filename')}")
        
        # Get screen size
        screen = QApplication.primaryScreen().geometry()
        
        # Initial size (70% of screen)
        width = int(screen.width() * 0.70)
        height = int(screen.height() * 0.75)
        
        self.resize(width, height)
        
        # CRITICAL: Allow window to be resized AND maximized
        self.setMinimumSize(900, 650)  # Minimum size
        # Don't set maximum size - allows maximize!
        
        # Center window
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.move(x, y)
        
        # Main container
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel(f"📊 {self.dataset.get('filename', 'Dataset Analysis')}")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E3A8A;")
        header.setWordWrap(True)
        layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F3F4F6;
                color: #374151;
                padding: 14px 30px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 6px;
                font-size: 15px;
                font-weight: 600;
                min-width: 150px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #1E3A8A;
                border-bottom: 3px solid #1E3A8A;
            }
            QTabBar::tab:hover:!selected {
                background-color: #E5E7EB;
            }
        """)
        
        # Create tabs with scroll areas
        self.tabs.addTab(self.create_overview_tab(), "📋 Overview")
        self.tabs.addTab(self.create_charts_tab(), "📊 Visual Analytics")
        self.tabs.addTab(self.create_equipment_tab(), "📈 Equipment Data")
        
        layout.addWidget(self.tabs, 1)
        
        # Close button
        close_btn = QPushButton("✖ Close Window")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                padding: 14px 28px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                min-height: 45px;
                min-width: 140px;
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
        """Tab 1: Overview with scrollable stat cards."""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Dataset Summary")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #374151;")
        layout.addWidget(title)
        
        # Stats grid
        grid = QGridLayout()
        grid.setSpacing(20)
        
        cards = [
            ("📊", "Total\nEquipment", "total"),
            ("💧", "Average\nFlowrate", "flowrate"),
            ("⚡", "Average\nPressure", "pressure"),
            ("🌡️", "Average\nTemperature", "temp")
        ]
        
        for idx, (icon, title_text, key) in enumerate(cards):
            card = self.create_stat_card(icon, title_text, key)
            grid.addWidget(card, idx // 2, idx % 2)
        
        layout.addLayout(grid)
        layout.addStretch()
        
        content.setLayout(layout)
        scroll.setWidget(content)
        return scroll
    
    def create_stat_card(self, icon, title, key):
        """Create stat card with proper sizing."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E5E7EB;
                border-radius: 12px;
                padding: 25px;
            }
        """)
        card.setMinimumHeight(140)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Icon + Title
        top = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 36px;")
        icon_label.setFixedWidth(50)
        top.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #6B7280; font-weight: 600;")
        title_label.setWordWrap(True)
        top.addWidget(title_label, 1)
        
        layout.addLayout(top)
        
        # Value
        value = QLabel("-")
        value.setStyleSheet("font-size: 32px; font-weight: bold; color: #1E3A8A;")
        layout.addWidget(value)
        
        card.setLayout(layout)
        self.stat_labels[key] = value
        return card
    
    def create_charts_tab(self):
        """Tab 2: Charts with proper scrolling."""
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Visual Analytics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #374151;")
        layout.addWidget(title)
        
        # PIE CHART
        pie_frame = QFrame()
        pie_frame.setStyleSheet("QFrame { background-color: #F9FAFB; border-radius: 10px; padding: 15px; }")
        pie_layout = QVBoxLayout()
        
        pie_title = QLabel("Equipment Type Distribution")
        pie_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #374151;")
        pie_title.setAlignment(Qt.AlignCenter)
        pie_layout.addWidget(pie_title)
        
        # FIXED: Proper chart size
        self.pie_figure = Figure(figsize=(10, 6), dpi=80, facecolor='#F9FAFB')
        self.pie_canvas = FigureCanvas(self.pie_figure)
        self.pie_canvas.setMinimumSize(600, 400)
        self.pie_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pie_layout.addWidget(self.pie_canvas)
        
        pie_frame.setLayout(pie_layout)
        layout.addWidget(pie_frame)
        
        # BAR CHART
        bar_frame = QFrame()
        bar_frame.setStyleSheet("QFrame { background-color: #F9FAFB; border-radius: 10px; padding: 15px; }")
        bar_layout = QVBoxLayout()
        
        bar_title = QLabel("Average Parameters Comparison")
        bar_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #374151;")
        bar_title.setAlignment(Qt.AlignCenter)
        bar_layout.addWidget(bar_title)
        
        # FIXED: Proper chart size
        self.bar_figure = Figure(figsize=(10, 6), dpi=80, facecolor='#F9FAFB')
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_canvas.setMinimumSize(600, 400)
        self.bar_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        bar_layout.addWidget(self.bar_canvas)
        
        bar_frame.setLayout(bar_layout)
        layout.addWidget(bar_frame)
        
        layout.addStretch()
        content.setLayout(layout)
        scroll.setWidget(content)
        return scroll
    
    def create_equipment_tab(self):
        """Tab 3: Equipment table."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Equipment Details")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #374151;")
        layout.addWidget(title)
        
        # Table
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(6)
        self.equipment_table.setHorizontalHeaderLabels([
            "Equipment Name", "Type", "Flowrate", "Pressure", "Temperature", "Status"
        ])
        
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.equipment_table.verticalHeader().setDefaultSectionSize(50)
        self.equipment_table.setAlternatingRowColors(True)
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.equipment_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.equipment_table, 1)
        widget.setLayout(layout)
        return widget
    
    def apply_stylesheet(self):
        """Apply stylesheet."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f9fafb;
            }
            QScrollArea {
                border: none;
                background-color: white;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #F3F4F6;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 14px 10px;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E3A8A;
            }
            QHeaderView::section {
                background-color: #1E3A8A;
                color: white;
                padding: 16px 10px;
                border: none;
                font-weight: 700;
                font-size: 14px;
            }
        """)
    
    def load_data(self):
        """Load data."""
        try:
            result = self.api_client.get_analytics(self.dataset["id"])
            if result["success"]:
                self.analytics = result["data"]
                self.update_stats()
                self.update_charts()
            
            result = self.api_client.get_equipment(self.dataset["id"])
            if result["success"]:
                self.equipment = result["data"]
                self.populate_table()
            
            logger.info(f"Data loaded: {self.dataset.get('filename')}")
        except Exception as e:
            logger.error(f"Error: {e}")
    
    def update_stats(self):
        """Update stats."""
        if self.analytics:
            self.stat_labels['total'].setText(str(self.analytics.get('total_equipment', 0)))
            self.stat_labels['flowrate'].setText(f"{self.analytics.get('avg_flowrate', 0):.2f}")
            self.stat_labels['pressure'].setText(f"{self.analytics.get('avg_pressure', 0):.2f}")
            self.stat_labels['temp'].setText(f"{self.analytics.get('avg_temperature', 0):.2f}°C")
    
    def update_charts(self):
        """Draw charts."""
        if not self.analytics:
            return
        
        colors = ['#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE', '#F97316', '#FB923C']
        
        # PIE CHART
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
                textprops={'fontsize': 12, 'weight': 'bold'},
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(11)
            
            ax.axis('equal')
            self.pie_figure.tight_layout(pad=1.5)
            self.pie_canvas.draw()
        
        # BAR CHART
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
                     width=0.6, edgecolor='white', linewidth=2)
        
        ax.set_ylabel("Value", fontsize=13, weight='bold', color='#374151')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=12, colors='#374151')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=13, weight='bold')
        
        self.bar_figure.tight_layout(pad=1.5)
        self.bar_canvas.draw()
    
    def populate_table(self):
        """Fill table."""
        self.equipment_table.setRowCount(len(self.equipment))
        
        for row, eq in enumerate(self.equipment):
            self.equipment_table.setItem(row, 0, QTableWidgetItem(eq.get("equipment_name", "")))
            self.equipment_table.setItem(row, 1, QTableWidgetItem(eq.get("equipment_type", "")))
            
            flow = QTableWidgetItem(f"{eq.get('flowrate', 0):.2f}")
            flow.setTextAlignment(Qt.AlignCenter)
            self.equipment_table.setItem(row, 2, flow)
            
            pres = QTableWidgetItem(f"{eq.get('pressure', 0):.2f}")
            pres.setTextAlignment(Qt.AlignCenter)
            self.equipment_table.setItem(row, 3, pres)
            
            temp = QTableWidgetItem(f"{eq.get('temperature', 0):.2f}")
            temp.setTextAlignment(Qt.AlignCenter)
            self.equipment_table.setItem(row, 4, temp)
            
            is_outlier = eq.get("is_pressure_outlier") or eq.get("is_temperature_outlier")
            status = "⚠️ Outlier" if is_outlier else "✅ Normal"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            if is_outlier:
                status_item.setForeground(QColor("#DC2626"))
                font = QFont()
                font.setBold(True)
                status_item.setFont(font)
            
            self.equipment_table.setItem(row, 5, status_item)


# Backward compatibility
DatasetDetailDialog = DatasetDetailWindow