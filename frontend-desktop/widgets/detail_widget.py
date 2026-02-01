"""
Dataset Detail Window - MINIMAL CLEAN DESIGN
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QTabWidget, QHeaderView, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import logging

logger = logging.getLogger(__name__)


class DatasetDetailWindow(QMainWindow):
    """Minimal, clean dataset detail window."""
    
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
        """Initialize UI."""
        self.setWindowTitle(f"Dataset Analysis - {self.dataset.get('filename')}")
        
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * 0.85)
        height = int(screen.height() * 0.85)
        
        self.resize(width, height)
        self.setMinimumSize(1000, 700)
        
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.move(x, y)
        
        # Main container
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header with filename
        header = QLabel(self.dataset.get('filename', 'Dataset Analysis'))
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E3A8A;")
        main_layout.addWidget(header)
        
        # === SIMPLE STATS (no boxes!) ===
        stats_container = QWidget()
        stats_container.setStyleSheet("background-color: white; border-radius: 10px; padding: 20px;")
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(40)
        
        stats_data = [
            ("Total Equipment", "total", "#1E3A8A"),
            ("Avg Flowrate", "flowrate", "#3B82F6"),
            ("Avg Pressure", "pressure", "#60A5FA"),
            ("Avg Temperature", "temp", "#F97316")
        ]
        
        for title, key, color in stats_data:
            stat_widget = self.create_minimal_stat(title, key, color)
            stats_layout.addWidget(stat_widget)
        
        stats_container.setLayout(stats_layout)
        main_layout.addWidget(stats_container)
        
        # TABS
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
                padding: 20px;
            }
            QTabBar::tab {
                background-color: #F9FAFB;
                color: #374151;
                padding: 12px 30px;
                border: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-size: 15px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #1E3A8A;
                border-bottom: 2px solid #1E3A8A;
            }
        """)
        
        tabs.addTab(self.create_charts_tab(), "📊 Visual Analytics")
        tabs.addTab(self.create_equipment_tab(), "📋 Equipment Data")
        
        main_layout.addWidget(tabs, 1)
        
        # Close button
        close_btn = QPushButton("✖ Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                padding: 10px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)
        
        container.setLayout(main_layout)
        self.apply_stylesheet()
    
    def create_minimal_stat(self, title, key, color):
        """Create MINIMAL stat display - no boxes!"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title (small, gray)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #9CA3AF; font-weight: 500;")
        layout.addWidget(title_label)
        
        # Value (big, colored)
        value_label = QLabel("-")
        value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        layout.addWidget(value_label)
        
        widget.setLayout(layout)
        self.stat_values[key] = value_label
        return widget
    
    def create_charts_tab(self):
        """Charts tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Charts side by side
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # PIE CHART
        pie_container = QWidget()
        pie_container.setStyleSheet("background-color: #F9FAFB; border-radius: 8px; padding: 15px;")
        pie_layout = QVBoxLayout()
        
        pie_title = QLabel("Equipment Type Distribution")
        pie_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #374151;")
        pie_title.setAlignment(Qt.AlignCenter)
        pie_layout.addWidget(pie_title)
        
        self.pie_figure = Figure(figsize=(7, 5.5), dpi=85, facecolor='#F9FAFB')
        self.pie_canvas = FigureCanvas(self.pie_figure)
        self.pie_canvas.setMinimumHeight(420)
        pie_layout.addWidget(self.pie_canvas)
        
        pie_container.setLayout(pie_layout)
        charts_layout.addWidget(pie_container)
        
        # BAR CHART
        bar_container = QWidget()
        bar_container.setStyleSheet("background-color: #F9FAFB; border-radius: 8px; padding: 15px;")
        bar_layout = QVBoxLayout()
        
        bar_title = QLabel("Average Parameters Comparison")
        bar_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #374151;")
        bar_title.setAlignment(Qt.AlignCenter)
        bar_layout.addWidget(bar_title)
        
        self.bar_figure = Figure(figsize=(7, 5.5), dpi=85, facecolor='#F9FAFB')
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_canvas.setMinimumHeight(420)
        bar_layout.addWidget(self.bar_canvas)
        
        bar_container.setLayout(bar_layout)
        charts_layout.addWidget(bar_container)
        
        layout.addLayout(charts_layout)
        widget.setLayout(layout)
        return widget
    
    def create_equipment_tab(self):
        """Equipment table tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title = QLabel("Equipment Details")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #374151;")
        layout.addWidget(title)
        
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(6)
        self.equipment_table.setHorizontalHeaderLabels([
            "Equipment Name", "Type", "Flowrate", "Pressure", "Temperature", "Status"
        ])
        
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.equipment_table.verticalHeader().setDefaultSectionSize(48)
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
                background-color: #F9FAFB;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                gridline-color: #E5E7EB;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 12px 10px;
                color: #1F2937;
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
            self.stat_values['total'].setText(str(self.analytics.get('total_equipment', 0)))
            self.stat_values['flowrate'].setText(f"{self.analytics.get('avg_flowrate', 0):.2f}")
            self.stat_values['pressure'].setText(f"{self.analytics.get('avg_pressure', 0):.2f}")
            self.stat_values['temp'].setText(f"{self.analytics.get('avg_temperature', 0):.2f}°C")
    
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
                textprops={'fontsize': 11, 'weight': 'bold'},
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
            
            ax.axis('equal')
            self.pie_figure.tight_layout(pad=0.8)
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
                     width=0.55, edgecolor='white', linewidth=2)
        
        ax.set_ylabel("Value", fontsize=12, weight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=11)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=12, weight='bold')
        
        self.bar_figure.tight_layout(pad=0.8)
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
            else:
                status_item.setForeground(QColor("#059669"))
            
            self.equipment_table.setItem(row, 5, status_item)


# Backward compatibility
DatasetDetailDialog = DatasetDetailWindow