"""
Dataset Detail Window - Clean, working version with proper charts
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QTabWidget, QGridLayout, QHeaderView, QDesktopWidget,
                             QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)


class DatasetDetailWindow(QMainWindow):
    """Dataset detail window with charts and equipment table."""
    
    def __init__(self, api_client, dataset, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.dataset = dataset
        self.analytics = None
        self.equipment = []
        
        # Store value labels for stats
        self.total_value = None
        self.flowrate_value = None
        self.pressure_value = None
        self.temp_value = None
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize UI with proper sizing."""
        self.setWindowTitle(f"Dataset Analysis - {self.dataset.get('filename')}")
        
        # Get screen size and set window to 75% of screen
        screen = QDesktopWidget().screenGeometry()
        width = int(screen.width() * 0.75)
        height = int(screen.height() * 0.75)
        
        # Apply constraints
        width = max(1000, min(width, 1400))
        height = max(700, min(height, 950))
        
        self.resize(width, height)
        self.setMinimumSize(1000, 700)
        
        # Center on screen
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.move(x, y)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Stats cards
        stats = self.create_stats()
        main_layout.addWidget(stats)
        
        # Tabs
        tabs = self.create_tabs()
        main_layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("✖ Close")
        close_btn.setMinimumHeight(45)
        close_btn.setMinimumWidth(130)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        main_layout.addLayout(button_layout)
        
        main_widget.setLayout(main_layout)
        
        # Stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f9fafb;
            }
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                background-color: white;
                padding: 15px;
            }
            QTabBar::tab {
                background-color: #F3F4F6;
                color: #374151;
                padding: 14px 28px;
                border: 1px solid #E5E7EB;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 6px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #1E3A8A;
            }
            QTabBar::tab:hover {
                background-color: #E5E7EB;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #F3F4F6;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 10px;
                border-bottom: 1px solid #F3F4F6;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E3A8A;
            }
            QHeaderView::section {
                background-color: #1E3A8A;
                color: white;
                padding: 14px 10px;
                border: none;
                font-weight: 700;
                font-size: 14px;
            }
        """)
    
    def create_header(self):
        """Create header section."""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        title = QLabel("📊 Dataset Analysis")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E3A8A;")
        layout.addWidget(title)
        
        filename = QLabel(self.dataset.get("filename", ""))
        filename.setStyleSheet("font-size: 15px; color: #6B7280;")
        layout.addWidget(filename)
        
        frame.setLayout(layout)
        return frame
    
    def create_stats(self):
        """Create statistics cards."""
        frame = QFrame()
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Card style
        card_style = """
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                padding: 18px;
            }
        """
        
        # Total Equipment
        total_card = QFrame()
        total_card.setStyleSheet(card_style)
        total_layout = QVBoxLayout()
        total_icon = QLabel("📊")
        total_icon.setStyleSheet("font-size: 28px;")
        total_label = QLabel("Total Equipment")
        total_label.setStyleSheet("font-size: 13px; color: #6B7280; font-weight: 600;")
        self.total_value = QLabel("-")
        self.total_value.setStyleSheet("font-size: 26px; font-weight: bold; color: #1E3A8A; margin-top: 8px;")
        total_layout.addWidget(total_icon)
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_value)
        total_layout.addStretch()
        total_card.setLayout(total_layout)
        grid.addWidget(total_card, 0, 0)
        
        # Avg Flowrate
        flow_card = QFrame()
        flow_card.setStyleSheet(card_style)
        flow_layout = QVBoxLayout()
        flow_icon = QLabel("💧")
        flow_icon.setStyleSheet("font-size: 28px;")
        flow_label = QLabel("Avg Flowrate")
        flow_label.setStyleSheet("font-size: 13px; color: #6B7280; font-weight: 600;")
        self.flowrate_value = QLabel("-")
        self.flowrate_value.setStyleSheet("font-size: 26px; font-weight: bold; color: #1E3A8A; margin-top: 8px;")
        flow_layout.addWidget(flow_icon)
        flow_layout.addWidget(flow_label)
        flow_layout.addWidget(self.flowrate_value)
        flow_layout.addStretch()
        flow_card.setLayout(flow_layout)
        grid.addWidget(flow_card, 0, 1)
        
        # Avg Pressure
        pressure_card = QFrame()
        pressure_card.setStyleSheet(card_style)
        pressure_layout = QVBoxLayout()
        pressure_icon = QLabel("⚡")
        pressure_icon.setStyleSheet("font-size: 28px;")
        pressure_label = QLabel("Avg Pressure")
        pressure_label.setStyleSheet("font-size: 13px; color: #6B7280; font-weight: 600;")
        self.pressure_value = QLabel("-")
        self.pressure_value.setStyleSheet("font-size: 26px; font-weight: bold; color: #1E3A8A; margin-top: 8px;")
        pressure_layout.addWidget(pressure_icon)
        pressure_layout.addWidget(pressure_label)
        pressure_layout.addWidget(self.pressure_value)
        pressure_layout.addStretch()
        pressure_card.setLayout(pressure_layout)
        grid.addWidget(pressure_card, 1, 0)
        
        # Avg Temperature
        temp_card = QFrame()
        temp_card.setStyleSheet(card_style)
        temp_layout = QVBoxLayout()
        temp_icon = QLabel("🌡️")
        temp_icon.setStyleSheet("font-size: 28px;")
        temp_label = QLabel("Avg Temperature")
        temp_label.setStyleSheet("font-size: 13px; color: #6B7280; font-weight: 600;")
        self.temp_value = QLabel("-")
        self.temp_value.setStyleSheet("font-size: 26px; font-weight: bold; color: #1E3A8A; margin-top: 8px;")
        temp_layout.addWidget(temp_icon)
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_value)
        temp_layout.addStretch()
        temp_card.setLayout(temp_layout)
        grid.addWidget(temp_card, 1, 1)
        
        frame.setLayout(grid)
        return frame
    
    def create_tabs(self):
        """Create tabbed interface."""
        tabs = QTabWidget()
        
        # Charts tab
        charts_widget = QWidget()
        charts_layout = QVBoxLayout()
        charts_layout.setSpacing(20)
        
        # Title
        charts_title = QLabel("Visual Analytics")
        charts_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #374151; margin-bottom: 10px;")
        charts_layout.addWidget(charts_title)
        
        # Charts side by side
        charts_h_layout = QHBoxLayout()
        charts_h_layout.setSpacing(20)
        
        # Pie chart
        pie_widget = QWidget()
        pie_layout = QVBoxLayout()
        pie_title = QLabel("Equipment Type Distribution")
        pie_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #374151; text-align: center;")
        pie_title.setAlignment(Qt.AlignCenter)
        pie_layout.addWidget(pie_title)
        
        self.pie_figure = Figure(figsize=(7, 6), dpi=90, facecolor='white')
        self.pie_canvas = FigureCanvas(self.pie_figure)
        self.pie_canvas.setMinimumSize(400, 400)
        pie_layout.addWidget(self.pie_canvas)
        pie_widget.setLayout(pie_layout)
        charts_h_layout.addWidget(pie_widget)
        
        # Bar chart
        bar_widget = QWidget()
        bar_layout = QVBoxLayout()
        bar_title = QLabel("Average Parameters")
        bar_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #374151; text-align: center;")
        bar_title.setAlignment(Qt.AlignCenter)
        bar_layout.addWidget(bar_title)
        
        self.bar_figure = Figure(figsize=(7, 6), dpi=90, facecolor='white')
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_canvas.setMinimumSize(400, 400)
        bar_layout.addWidget(self.bar_canvas)
        bar_widget.setLayout(bar_layout)
        charts_h_layout.addWidget(bar_widget)
        
        charts_layout.addLayout(charts_h_layout)
        charts_widget.setLayout(charts_layout)
        tabs.addTab(charts_widget, "📈 Charts")
        
        # Equipment tab
        equipment_widget = QWidget()
        equipment_layout = QVBoxLayout()
        equipment_layout.setSpacing(15)
        
        equipment_title = QLabel("Equipment Details")
        equipment_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #374151; margin-bottom: 10px;")
        equipment_layout.addWidget(equipment_title)
        
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(6)
        self.equipment_table.setHorizontalHeaderLabels([
            "Name", "Type", "Flowrate", "Pressure", "Temperature", "Status"
        ])
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.equipment_table.verticalHeader().setDefaultSectionSize(50)
        self.equipment_table.setAlternatingRowColors(True)
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.equipment_table.setEditTriggers(QTableWidget.NoEditTriggers)
        equipment_layout.addWidget(self.equipment_table)
        
        equipment_widget.setLayout(equipment_layout)
        tabs.addTab(equipment_widget, "📋 Equipment Details")
        
        return tabs
    
    def load_data(self):
        """Load analytics and equipment data."""
        try:
            # Analytics
            analytics_result = self.api_client.get_analytics(self.dataset["id"])
            if analytics_result["success"]:
                self.analytics = analytics_result["data"]
                self.update_stats()
                self.update_charts()
            
            # Equipment
            equipment_result = self.api_client.get_equipment(self.dataset["id"])
            if equipment_result["success"]:
                self.equipment = equipment_result["data"]
                self.populate_table()
            
            logger.info(f"Loaded data for: {self.dataset.get('filename')}")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
    
    def update_stats(self):
        """Update stat cards."""
        if self.analytics:
            self.total_value.setText(str(self.analytics.get('total_equipment', 0)))
            self.flowrate_value.setText(f"{self.analytics.get('avg_flowrate', 0):.2f}")
            self.pressure_value.setText(f"{self.analytics.get('avg_pressure', 0):.2f}")
            self.temp_value.setText(f"{self.analytics.get('avg_temperature', 0):.2f}°C")
    
    def update_charts(self):
        """Update charts with clean styling."""
        if not self.analytics:
            return
        
        # Colors
        colors = ['#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE', '#F97316', '#FB923C']
        
        # Pie chart
        distribution = self.analytics.get("equipment_type_distribution", {})
        if distribution:
            self.pie_figure.clear()
            ax = self.pie_figure.add_subplot(111)
            wedges, texts, autotexts = ax.pie(
                distribution.values(),
                labels=distribution.keys(),
                autopct='%1.1f%%',
                colors=colors[:len(distribution)],
                startangle=90,
                textprops={'fontsize': 12, 'weight': 'bold', 'color': '#1F2937'}
            )
            # Make percentage text white
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
                autotext.set_fontsize(11)
            ax.axis('equal')
            self.pie_figure.tight_layout(pad=2)
            self.pie_canvas.draw()
        
        # Bar chart
        self.bar_figure.clear()
        ax = self.bar_figure.add_subplot(111)
        parameters = ['Flowrate', 'Pressure', 'Temperature']
        values = [
            self.analytics.get('avg_flowrate', 0),
            self.analytics.get('avg_pressure', 0),
            self.analytics.get('avg_temperature', 0)
        ]
        bars = ax.bar(parameters, values, color=['#1E3A8A', '#3B82F6', '#60A5FA'], width=0.5)
        ax.set_ylabel("Value", fontsize=12, weight='bold', color='#374151')
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=11, colors='#374151')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=11, weight='bold', color='#1F2937')
        
        self.bar_figure.tight_layout(pad=2)
        self.bar_canvas.draw()
    
    def populate_table(self):
        """Populate equipment table."""
        self.equipment_table.setRowCount(len(self.equipment))
        
        for row, eq in enumerate(self.equipment):
            # Name
            self.equipment_table.setItem(row, 0, QTableWidgetItem(eq.get("equipment_name", "")))
            
            # Type
            self.equipment_table.setItem(row, 1, QTableWidgetItem(eq.get("equipment_type", "")))
            
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
                font = status_item.font()
                font.setBold(True)
                status_item.setFont(font)
            self.equipment_table.setItem(row, 5, status_item)


# Backward compatibility
DatasetDetailDialog = DatasetDetailWindow