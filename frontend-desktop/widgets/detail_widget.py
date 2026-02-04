
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QTabWidget, QHeaderView, QGridLayout, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

class DatasetDetailWindow(QMainWindow):
    """Symmetrical industrial analytics dashboard with high-visibility visualizations."""
    
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
        """Initialize a balanced, high-density command center interface."""
        self.resize(1150, 850)
        central = QWidget()
        central.setStyleSheet("background-color: #F8FAFC;") # Slate-50 background
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # === COMMAND HEADER ===
        head = QHBoxLayout()
        title_v = QVBoxLayout()
        
        # Balanced typography for title
        self.title_lbl = QLabel(f"Analysis: {self.dataset.get('filename', 'Dataset')}")
        self.title_lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: #0F172A;")
        
        # Symmetrical subtitle with equipment count
        self.count_lbl = QLabel("Monitoring system units...")
        self.count_lbl.setStyleSheet("font-size: 13px; color: #64748B; font-weight: 500;")
        
        title_v.addWidget(self.title_lbl)
        title_v.addWidget(self.count_lbl)
        head.addLayout(title_v)
        head.addStretch()
        
        # High-contrast action button
        exit_btn = QPushButton("✖  Close View")
        exit_btn.setFixedSize(130, 38)
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("""
            QPushButton { 
                background: white; border: 1.5px solid #E2E8F0; border-radius: 8px; 
                font-weight: 700; color: #475569; font-size: 12px;
            }
            QPushButton:hover { background: #F1F5F9; border-color: #CBD5E1; color: #1E293B; }
        """)
        head.addWidget(exit_btn)
        layout.addLayout(head)

        # === SYMMETRICAL STATS GRID ===
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: white; border: 1px solid #E2E8F0; border-radius: 12px;")
        grid_layout = QHBoxLayout(stats_frame)
        grid_layout.setContentsMargins(25, 20, 25, 20)
        
        metrics = [
            ("UNITS", "total", "#6366F1"),       # Indigo
            ("AVG FLOWRATE", "flowrate", "#0EA5E9"), # Sky
            ("AVG PRESSURE", "pressure", "#10B981"), # Emerald
            ("AVG TEMP", "temp", "#F59E0B")      # Amber
        ]
        
        for name, key, color in metrics:
            m_v = QVBoxLayout()
            n_lbl = QLabel(name)
            n_lbl.setStyleSheet("font-size: 10px; font-weight: 800; color: #94A3B8; letter-spacing: 1px;")
            
            # Scaled down metric value for better symmetry
            v_lbl = QLabel("-")
            v_lbl.setStyleSheet(f"font-size: 28px; font-weight: 800; color: {color};")
            
            self.stat_values[key] = v_lbl
            m_v.addWidget(n_lbl)
            m_v.addWidget(v_lbl)
            grid_layout.addLayout(m_v)
            if key != "temp": grid_layout.addStretch()
            
        layout.addWidget(stats_frame)

        # === TABBED CONTENT (HIGH DISTINCTION) ===
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #E2E8F0; border-radius: 12px; background: white; top: -1px; }
            QTabBar::tab { 
                padding: 12px 40px; font-weight: 700; color: #64748B; background: #E2E8F0; 
                border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 4px;
            }
            QTabBar::tab:selected { 
                background: white; color: #4F46E5; 
                border-bottom: 4px solid #4F46E5; /* Bold active indicator */
            }
            QTabBar::tab:hover:!selected { background: #CBD5E1; }
        """)
        
        self.tabs.addTab(self.create_visual_tab(), "📊  Visual Analytics")
        self.tabs.addTab(self.create_equipment_tab(), "📋  Equipment Details")
        layout.addWidget(self.tabs, 1)

    def create_visual_tab(self):
        """Visual analytics with expanded chart area."""
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(15, 15, 15, 15)
        l.setSpacing(20)
        
        # Charts take advantage of higher figsize
        self.pie_canvas = self.make_chart_box("Equipment Type Breakdown", l)
        self.bar_canvas = self.make_chart_box("Mean System Averages", l)
        return w

    def make_chart_box(self, title, layout):
        container = QFrame()
        container.setStyleSheet("background: white; border: 1px solid #F1F5F9; border-radius: 10px;")
        v = QVBoxLayout(container)
        
        lbl = QLabel(title)
        lbl.setStyleSheet("font-weight: 800; color: #1E293B; font-size: 14px; margin-bottom: 5px;")
        lbl.setAlignment(Qt.AlignCenter)
        v.addWidget(lbl)
        
        # Scaling charts up for industry visibility
        fig = Figure(figsize=(7, 6), dpi=95, facecolor='white')
        canvas = FigureCanvas(fig)
        v.addWidget(canvas)
        layout.addWidget(container)
        return canvas

    def create_equipment_tab(self):
        """Detailed equipment table with industrial status indicators."""
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(10, 10, 10, 10)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Unit Name", "Category", "Flow (m³/h)", "Press (bar)", "Temp (°C)", "System Status"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { border: none; font-size: 13px; background-color: white; }
            QHeaderView::section { 
                background: #F8FAFC; padding: 12px; font-weight: 700; color: #475569; 
                border-bottom: 2px solid #E2E8F0;
            }
        """)
        l.addWidget(self.table)
        return w

    def load_data(self):
        """Fetch and synchronize data metrics."""
        try:
            res_a = self.api_client.get_analytics(self.dataset["id"])
            if res_a["success"]:
                data = res_a["data"]
                count = data.get('total_equipment', 0)
                self.count_lbl.setText(f"Command center identifying {count} chemical units in dataset.")
                self.stat_values['total'].setText(str(count))
                self.stat_values['flowrate'].setText(f"{data.get('avg_flowrate', 0):.2f}")
                self.stat_values['pressure'].setText(f"{data.get('avg_pressure', 0):.2f}")
                self.stat_values['temp'].setText(f"{data.get('avg_temperature', 0):.2f}°C")
                self.update_charts(data)

            res_e = self.api_client.get_equipment(self.dataset["id"])
            if res_e["success"]:
                self.populate_table(res_e["data"])
        except Exception as e:
            logger.error(f"UI Integration Error: {e}")

    def update_charts(self, data):
        """Render high-legibility Full Pie and Bar charts."""
        # --- FULL PIE CHART (No Donut) ---
        ax_p = self.pie_canvas.figure.add_subplot(111)
        ax_p.clear()
        dist = data.get("equipment_type_distribution", {})
        if dist:
            # Industry-Standard Palette
            colors = ['#6366F1', '#10B981', '#F59E0B', '#0EA5E9', '#8B5CF6']
            ax_p.pie(dist.values(), labels=dist.keys(), autopct='%1.1f%%', 
                     startangle=140, colors=colors,
                     textprops={'fontsize': 10, 'fontweight': 'bold', 'color': '#1E293B'})
            ax_p.axis('equal')
        self.pie_canvas.figure.tight_layout()
        self.pie_canvas.draw()
        
        # --- SYSTEM AVERAGE BAR CHART ---
        ax_b = self.bar_canvas.figure.add_subplot(111)
        ax_b.clear()
        labels = ['Flow', 'Pressure', 'Temp']
        vals = [data.get('avg_flowrate', 0), data.get('avg_pressure', 0), data.get('avg_temperature', 0)]
        
        ax_b.bar(labels, vals, color=['#6366F1', '#10B981', '#F59E0B'], width=0.55)
        ax_b.spines['top'].set_visible(False)
        ax_b.spines['right'].set_visible(False)
        ax_b.tick_params(axis='both', which='major', labelsize=9)
        self.bar_canvas.figure.tight_layout()
        self.bar_canvas.draw()

    def populate_table(self, equipment):
        """Fill equipment explorer with formatted status items."""
        self.table.setRowCount(len(equipment))
        for r, eq in enumerate(equipment):
            self.table.setItem(r, 0, QTableWidgetItem(eq.get("equipment_name", "")))
            self.table.setItem(r, 1, QTableWidgetItem(eq.get("equipment_type", "")))
            self.table.setItem(r, 2, QTableWidgetItem(f"{eq.get('flowrate', 0):.2f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"{eq.get('pressure', 0):.2f}"))
            self.table.setItem(r, 4, QTableWidgetItem(f"{eq.get('temperature', 0):.2f}"))
            
            # Formatted Outlier Alerts
            is_warn = eq.get("is_pressure_outlier") or eq.get("is_temperature_outlier")
            status_txt = "⚠️  ALERT" if is_warn else "✅  NOMINAL"
            item = QTableWidgetItem(status_txt)
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QColor("#EF4444" if is_warn else "#059669"))
            self.table.setItem(r, 5, item)

# Compatibility Alias
DatasetDetailDialog = DatasetDetailWindow