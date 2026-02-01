"""
Dataset Detail Window - Professional version matching web app design
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QTabWidget, QGridLayout, QHeaderView, QDesktopWidget, QSplitter)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor
import matplotlib
matplotlib.use('Qt5Agg')  # CRITICAL: Force Qt5 backend
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)


class DatasetDetailWindow(QMainWindow):
    """Professional dataset detail window with working charts."""
    
    def __init__(self, api_client, dataset, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.dataset = dataset
        self.analytics = None
        self.equipment = []
        
        # Stat value labels
        self.total_value = None
        self.flowrate_value = None
        self.pressure_value = None
        self.temp_value = None
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle(f"Dataset Analysis - {self.dataset.get('filename')}")
        
        # Screen-aware sizing
        screen = QDesktopWidget().screenGeometry()
        width = min(int(screen.width() * 0.80), 1300)
        height = min(int(screen.height() * 0.80), 900)
        
        self.resize(width, height)
        self.setMinimumSize(1100, 750)
        
        # Center window
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.move(x, y)
        
        # Main container
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header
        header_label = QLabel("📊 Dataset Analysis")
        header_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E3A8A;")
        layout.addWidget(header_label)
        
        filename_label = QLabel(self.dataset.get("filename", ""))
        filename_label.setStyleSheet("font-size: 16px; color: #6B7280; margin-bottom: 10px;")
        layout.addWidget(filename_label)
        
        # Stats grid - 4 cards in 2x2
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)
        
        # Create 4 stat cards
        card1 = self.create_stat_card("📊", "Total Equipment", "total")
        card2 = self.create_stat_card("💧", "Avg Flowrate", "flowrate")
        card3 = self.create_stat_card("⚡", "Avg Pressure", "pressure")
        card4 = self.create_stat_card("🌡️", "Avg Temperature", "temp")
        
        stats_grid.addWidget(card1, 0, 0)
        stats_grid.addWidget(card2, 0, 1)
        stats_grid.addWidget(card3, 1, 0)
        stats_grid.addWidget(card4, 1, 1)
        
        layout.addLayout(stats_grid)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                background-color: white;
                padding: 20px;
            }
            QTabBar::tab {
                background-color: #F3F4F6;
                color: #374151;
                padding: 15px 35px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 8px;
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
        
        # Charts tab
        charts_widget = self.create_charts_tab()
        tabs.addTab(charts_widget, "📈 Visual Analytics")
        
        # Equipment tab
        equipment_widget = self.create_equipment_tab()
        tabs.addTab(equipment_widget, "📋 Equipment Data")
        
        layout.addWidget(tabs, 1)  # Stretch factor 1
        
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
                min-width: 150px;
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
        
        # Main stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f9fafb;
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
    
    def create_stat_card(self, icon, title, value_key):
        """Create a single stat card."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #E5E7EB;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        card.setMinimumHeight(120)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Icon and title row
        top_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px;")
        top_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #6B7280; font-weight: 600;")
        top_layout.addWidget(title_label, 1)
        
        layout.addLayout(top_layout)
        
        # Value
        value_label = QLabel("-")
        value_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #1E3A8A; margin-top: 5px;")
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        
        # Store reference
        if value_key == "total":
            self.total_value = value_label
        elif value_key == "flowrate":
            self.flowrate_value = value_label
        elif value_key == "pressure":
            self.pressure_value = value_label
        elif value_key == "temp":
            self.temp_value = value_label
        
        return card
    
    def create_charts_tab(self):
        """Create charts tab with matplotlib figures."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Charts side-by-side
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(25)
        
        # PIE CHART
        pie_container = QFrame()
        pie_container.setStyleSheet("QFrame { background-color: #F9FAFB; border-radius: 10px; padding: 15px; }")
        pie_layout = QVBoxLayout()
        
        pie_title = QLabel("Equipment Type Distribution")
        pie_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #374151; margin-bottom: 10px;")
        pie_title.setAlignment(Qt.AlignCenter)
        pie_layout.addWidget(pie_title)
        
        # Create matplotlib figure for pie chart
        self.pie_figure = Figure(figsize=(6, 5), dpi=100, facecolor='#F9FAFB')
        self.pie_canvas = FigureCanvas(self.pie_figure)
        self.pie_canvas.setMinimumSize(450, 400)
        pie_layout.addWidget(self.pie_canvas)
        
        pie_container.setLayout(pie_layout)
        charts_layout.addWidget(pie_container)
        
        # BAR CHART
        bar_container = QFrame()
        bar_container.setStyleSheet("QFrame { background-color: #F9FAFB; border-radius: 10px; padding: 15px; }")
        bar_layout = QVBoxLayout()
        
        bar_title = QLabel("Average Parameters")
        bar_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #374151; margin-bottom: 10px;")
        bar_title.setAlignment(Qt.AlignCenter)
        bar_layout.addWidget(bar_title)
        
        # Create matplotlib figure for bar chart
        self.bar_figure = Figure(figsize=(6, 5), dpi=100, facecolor='#F9FAFB')
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_canvas.setMinimumSize(450, 400)
        bar_layout.addWidget(self.bar_canvas)
        
        bar_container.setLayout(bar_layout)
        charts_layout.addWidget(bar_container)
        
        layout.addLayout(charts_layout, 1)
        widget.setLayout(layout)
        return widget
    
    def create_equipment_tab(self):
        """Create equipment table tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("Equipment Details")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #374151; margin-bottom: 10px;")
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
            
            logger.info(f"Data loaded for: {self.dataset.get('filename')}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def update_stats(self):
        """Update stat card values."""
        if self.analytics and self.total_value:
            self.total_value.setText(str(self.analytics.get('total_equipment', 0)))
            self.flowrate_value.setText(f"{self.analytics.get('avg_flowrate', 0):.2f}")
            self.pressure_value.setText(f"{self.analytics.get('avg_pressure', 0):.2f}")
            self.temp_value.setText(f"{self.analytics.get('avg_temperature', 0):.2f}°C")
    
    def update_charts(self):
        """Draw matplotlib charts."""
        if not self.analytics:
            return
        
        # Professional color palette
        colors = ['#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE', '#F97316', '#FB923C', '#FDBA74']
        
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
                textprops={'fontsize': 11, 'weight': 'bold'},
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            
            # Style percentage text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(10)
                autotext.set_weight('bold')
            
            ax.axis('equal')
            self.pie_figure.tight_layout(pad=1)
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
        
        bars = ax.bar(params, values, color=['#1E3A8A', '#3B82F6', '#60A5FA'], width=0.5, edgecolor='white', linewidth=2)
        
        ax.set_ylabel("Value", fontsize=12, weight='bold', color='#374151')
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E5E7EB')
        ax.spines['bottom'].set_color('#E5E7EB')
        ax.tick_params(colors='#374151', labelsize=11)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + (max(values) * 0.02),
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=11, weight='bold', color='#1F2937')
        
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
                status_item.setFont(font)
            
            self.equipment_table.setItem(row, 5, status_item)


# Backward compatibility
DatasetDetailDialog = DatasetDetailWindow