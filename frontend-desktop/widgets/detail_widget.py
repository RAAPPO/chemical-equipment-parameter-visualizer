"""
Dataset Detail Window - SIMPLE, CLEAN, EVERYTHING VISIBLE
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QHeaderView, QApplication, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import logging

logger = logging.getLogger(__name__)


class DatasetDetailWindow(QMainWindow):
    """Simple, clean dataset detail window - everything visible."""
    
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
        
        # Window size
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * 0.85)
        height = int(screen.height() * 0.85)
        
        self.resize(width, height)
        self.setMinimumSize(1000, 700)
        
        # Center
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.move(x, y)
        
        # Main container
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # Header
        header = QLabel(self.dataset.get('filename', 'Dataset Analysis'))
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E3A8A; padding: 8px;")
        main_layout.addWidget(header)
        
        # === STATS ROW (4 cards horizontal) ===
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        
        stats_data = [
            ("Total Equipment", "total", "#1E3A8A"),
            ("Avg Flowrate", "flowrate", "#3B82F6"),
            ("Avg Pressure", "pressure", "#60A5FA"),
            ("Avg Temperature", "temp", "#F97316")
        ]
        
        for title, key, color in stats_data:
            card = self.create_simple_stat_card(title, key, color)
            stats_layout.addWidget(card)
        
        main_layout.addLayout(stats_layout)
        
        # === CHARTS ROW (side by side) ===
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(10)
        
        # Pie Chart
        pie_widget = QWidget()
        pie_layout = QVBoxLayout()
        pie_layout.setContentsMargins(5, 5, 5, 5)
        pie_layout.setSpacing(5)
        
        pie_title = QLabel("Equipment Type Distribution")
        pie_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #374151;")
        pie_title.setAlignment(Qt.AlignCenter)
        pie_layout.addWidget(pie_title)
        
        self.pie_figure = Figure(figsize=(6, 4), dpi=80, facecolor='white')
        self.pie_canvas = FigureCanvas(self.pie_figure)
        self.pie_canvas.setMaximumHeight(320)
        pie_layout.addWidget(self.pie_canvas)
        
        pie_widget.setLayout(pie_layout)
        pie_widget.setStyleSheet("background-color: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 8px;")
        charts_layout.addWidget(pie_widget)
        
        # Bar Chart
        bar_widget = QWidget()
        bar_layout = QVBoxLayout()
        bar_layout.setContentsMargins(5, 5, 5, 5)
        bar_layout.setSpacing(5)
        
        bar_title = QLabel("Average Parameters")
        bar_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #374151;")
        bar_title.setAlignment(Qt.AlignCenter)
        bar_layout.addWidget(bar_title)
        
        self.bar_figure = Figure(figsize=(6, 4), dpi=80, facecolor='white')
        self.bar_canvas = FigureCanvas(self.bar_figure)
        self.bar_canvas.setMaximumHeight(320)
        bar_layout.addWidget(self.bar_canvas)
        
        bar_widget.setLayout(bar_layout)
        bar_widget.setStyleSheet("background-color: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 8px;")
        charts_layout.addWidget(bar_widget)
        
        main_layout.addLayout(charts_layout)
        
        # === TABLE (bottom) ===
        table_label = QLabel("Equipment Details")
        table_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #374151; padding: 5px;")
        main_layout.addWidget(table_label)
        
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(6)
        self.equipment_table.setHorizontalHeaderLabels([
            "Name", "Type", "Flowrate", "Pressure", "Temperature", "Status"
        ])
        self.equipment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.equipment_table.verticalHeader().setDefaultSectionSize(40)
        self.equipment_table.setAlternatingRowColors(True)
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.equipment_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.equipment_table.setMaximumHeight(250)  # Limit table height
        
        main_layout.addWidget(self.equipment_table)
        
        # Close button
        close_btn = QPushButton("✖ Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        close_btn.setMaximumWidth(120)
        close_btn.clicked.connect(self.close)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)
        
        container.setLayout(main_layout)
        self.apply_stylesheet()
    
    def create_simple_stat_card(self, title, key, color):
        """Create simple stat card."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        card.setFixedHeight(80)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #6B7280; font-weight: 600;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel("-")
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        self.stat_values[key] = value_label
        return card
    
    def apply_stylesheet(self):
        """Apply stylesheet."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F3F4F6;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                gridline-color: #E5E7EB;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px 8px;
                color: #1F2937;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E3A8A;
            }
            QHeaderView::section {
                background-color: #1E3A8A;
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: 700;
                font-size: 13px;
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
            
            wedges, texts, autotexts = ax.pie(
                list(distribution.values()),
                labels=list(distribution.keys()),
                autopct='%1.1f%%',
                colors=colors[:len(distribution)],
                startangle=90,
                textprops={'fontsize': 10, 'weight': 'bold', 'color': '#1F2937'},
                wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(9)
            
            ax.axis('equal')
            self.pie_figure.tight_layout(pad=0.5)
            self.pie_canvas.draw()
        
        # BAR CHART
        self.bar_figure.clear()
        ax = self.bar_figure.add_subplot(111)
        
        params = ['Flowrate', 'Pressure', 'Temperature']
        values = [
            self.analytics.get('avg_flowrate', 0),
            self.analytics.get('avg_pressure', 0),
            self.analytics.get('avg_temperature', 0)
        ]
        
        bars = ax.bar(params, values, color=['#1E3A8A', '#3B82F6', '#60A5FA'], 
                     width=0.5, edgecolor='white', linewidth=1.5)
        
        ax.set_ylabel("Value", fontsize=11, weight='bold', color='#374151')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=10, colors='#374151')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=11, weight='bold', color='#1F2937')
        
        self.bar_figure.tight_layout(pad=0.5)
        self.bar_canvas.draw()
    
    def populate_table(self):
        """Fill table."""
        self.equipment_table.setRowCount(len(self.equipment))
        
        for row, eq in enumerate(self.equipment):
            # All items with proper text color
            name = QTableWidgetItem(eq.get("equipment_name", ""))
            name.setForeground(QColor("#1F2937"))
            self.equipment_table.setItem(row, 0, name)
            
            type_item = QTableWidgetItem(eq.get("equipment_type", ""))
            type_item.setForeground(QColor("#1F2937"))
            self.equipment_table.setItem(row, 1, type_item)
            
            flow = QTableWidgetItem(f"{eq.get('flowrate', 0):.2f}")
            flow.setTextAlignment(Qt.AlignCenter)
            flow.setForeground(QColor("#1F2937"))
            self.equipment_table.setItem(row, 2, flow)
            
            pres = QTableWidgetItem(f"{eq.get('pressure', 0):.2f}")
            pres.setTextAlignment(Qt.AlignCenter)
            pres.setForeground(QColor("#1F2937"))
            self.equipment_table.setItem(row, 3, pres)
            
            temp = QTableWidgetItem(f"{eq.get('temperature', 0):.2f}")
            temp.setTextAlignment(Qt.AlignCenter)
            temp.setForeground(QColor("#1F2937"))
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