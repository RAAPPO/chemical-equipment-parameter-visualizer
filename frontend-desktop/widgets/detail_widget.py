from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class DatasetDetailDialog(QDialog):
    """Dialog showing dataset details with charts."""
    
    def __init__(self, api_client, dataset, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.dataset = dataset
        self.analytics = None
        self.equipment = []
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize UI."""
        self.setWindowTitle(f"Dataset Analysis - {self.dataset.get('filename')}")
        self.setGeometry(150, 150, 1000, 700)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(self.dataset.get("filename", "Dataset"))
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1E3A8A;")
        layout.addWidget(title)
        
        # Statistics
        stats_frame = self.create_stats_frame()
        layout.addWidget(stats_frame)
        
        # Charts
        charts_frame = self.create_charts_frame()
        layout.addWidget(charts_frame)
        
        # Equipment table
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(6)
        self.equipment_table.setHorizontalHeaderLabels([
            "Name", "Type", "Flowrate", "Pressure", "Temperature", "Status"
        ])
        layout.addWidget(self.equipment_table)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def create_stats_frame(self):
        """Create statistics cards."""
        frame = QFrame()
        layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: -")
        self.flowrate_label = QLabel("Avg Flowrate: -")
        self.pressure_label = QLabel("Avg Pressure: -")
        self.temp_label = QLabel("Avg Temp: -")
        
        for label in [self.total_label, self.flowrate_label, self.pressure_label, self.temp_label]:
            label.setStyleSheet("background-color: white; padding: 15px; border-radius: 5px; font-size: 14px;")
            layout.addWidget(label)
        
        frame.setLayout(layout)
        return frame
    
    def create_charts_frame(self):
        """Create matplotlib charts."""
        frame = QFrame()
        layout = QHBoxLayout()
        
        # Pie chart
        self.pie_figure = Figure(figsize=(5, 4))
        self.pie_canvas = FigureCanvas(self.pie_figure)
        layout.addWidget(self.pie_canvas)
        
        # Bar chart
        self.bar_figure = Figure(figsize=(5, 4))
        self.bar_canvas = FigureCanvas(self.bar_figure)
        layout.addWidget(self.bar_canvas)
        
        frame.setLayout(layout)
        return frame
    
    def load_data(self):
        """Load analytics and equipment data."""
        # Get analytics
        analytics_result = self.api_client.get_analytics(self.dataset["id"])
        if analytics_result["success"]:
            self.analytics = analytics_result["data"]
            self.update_stats()
            self.update_charts()
        
        # Get equipment
        equipment_result = self.api_client.get_equipment(self.dataset["id"])
        if equipment_result["success"]:
            self.equipment = equipment_result["data"]
            self.populate_equipment_table()
    
    def update_stats(self):
        """Update statistics labels."""
        if self.analytics:
            self.total_label.setText(f"Total Equipment: {self.analytics.get('total_equipment', 0)}")
            self.flowrate_label.setText(f"Avg Flowrate: {self.analytics.get('avg_flowrate', 0):.2f}")
            self.pressure_label.setText(f"Avg Pressure: {self.analytics.get('avg_pressure', 0):.2f}")
            self.temp_label.setText(f"Avg Temperature: {self.analytics.get('avg_temperature', 0):.2f}")
    
    def update_charts(self):
        """Update matplotlib charts."""
        if not self.analytics:
            return
        
        # Pie chart - Equipment type distribution
        distribution = self.analytics.get("equipment_type_distribution", {})
        if distribution:
            self.pie_figure.clear()
            ax = self.pie_figure.add_subplot(111)
            ax.pie(
                distribution.values(),
                labels=distribution.keys(),
                autopct='%1.1f%%',
                colors=['#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE', '#F97316']
            )
            ax.set_title("Equipment Type Distribution")
            self.pie_canvas.draw()
        
        # Bar chart - Average parameters
        self.bar_figure.clear()
        ax = self.bar_figure.add_subplot(111)
        parameters = ['Flowrate', 'Pressure', 'Temperature']
        values = [
            self.analytics.get('avg_flowrate', 0),
            self.analytics.get('avg_pressure', 0),
            self.analytics.get('avg_temperature', 0)
        ]
        ax.bar(parameters, values, color=['#1E3A8A', '#3B82F6', '#60A5FA'])
        ax.set_title("Average Parameters")
        ax.set_ylabel("Value")
        self.bar_canvas.draw()
    
    def populate_equipment_table(self):
        """Populate equipment table."""
        self.equipment_table.setRowCount(len(self.equipment))
        
        for row, eq in enumerate(self.equipment):
            self.equipment_table.setItem(row, 0, QTableWidgetItem(eq.get("equipment_name", "")))
            self.equipment_table.setItem(row, 1, QTableWidgetItem(eq.get("equipment_type", "")))
            self.equipment_table.setItem(row, 2, QTableWidgetItem(f"{eq.get('flowrate', 0):.1f}"))
            self.equipment_table.setItem(row, 3, QTableWidgetItem(f"{eq.get('pressure', 0):.1f}"))
            self.equipment_table.setItem(row, 4, QTableWidgetItem(f"{eq.get('temperature', 0):.1f}"))
            
            # Status
            is_outlier = eq.get("is_pressure_outlier") or eq.get("is_temperature_outlier")
            status = "⚠️ Outlier" if is_outlier else "✅ Normal"
            status_item = QTableWidgetItem(status)
            if is_outlier:
                status_item.setForeground(Qt.red)
            self.equipment_table.setItem(row, 5, status_item)
