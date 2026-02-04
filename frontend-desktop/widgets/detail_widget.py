import logging
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QTabWidget, QHeaderView, QComboBox, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches

logger = logging.getLogger(__name__)

class DatasetDetailWindow(QMainWindow):
    """
    World-Class Industrial Dashboard for Desktop.
    Features: Dynamic View Switching, Advanced Matplotlib Rendering, Contextual Insights.
    """
    
    def __init__(self, api_client, dataset, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.dataset = dataset
        self.analytics = {}
        self.equipment = []
        self.current_view = "safety" # Options: safety, distribution, correlation
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Initialize the layout with a fixed Control Bar and Dynamic Stage."""
        self.resize(1280, 850)
        central = QWidget()
        central.setStyleSheet("background-color: #F8FAFC; color: #1E293B;")
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # --- 1. HEADER & CONTROL BAR ---
        header_layout = QHBoxLayout()
        
        # Title Section
        title_box = QVBoxLayout()
        self.title_lbl = QLabel(f"{self.dataset.get('filename', 'Dataset')}")
        self.title_lbl.setStyleSheet("font-size: 24px; font-weight: 800; color: #0F172A;")
        subtitle = QLabel("Industrial Parameter Monitoring System")
        subtitle.setStyleSheet("font-size: 13px; color: #64748B; font-weight: 500;")
        title_box.addWidget(self.title_lbl)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)
        
        header_layout.addStretch()
        
        # VIEW SELECTOR (The Core Interaction)
        view_label = QLabel("Analysis Mode:")
        view_label.setStyleSheet("font-weight: 700; color: #475569; margin-right: 8px;")
        header_layout.addWidget(view_label)
        
        self.view_selector = QComboBox()
        self.view_selector.addItems(["🛡️  Process Safety", "📊  Distributions", "🔗  Correlations"])
        self.view_selector.setFixedSize(220, 40)
        self.view_selector.setCursor(Qt.PointingHandCursor)
        self.view_selector.setStyleSheet("""
            QComboBox { 
                background: white; border: 1px solid #CBD5E1; border-radius: 8px; 
                padding: 5px 15px; font-weight: 700; color: #334155; font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: white; selection-background-color: #E2E8F0; color: #1E293B;
            }
        """)
        self.view_selector.currentIndexChanged.connect(self.change_view)
        header_layout.addWidget(self.view_selector)
        
        # Exit Button
        exit_btn = QPushButton("✖")
        exit_btn.setFixedSize(40, 40)
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("background: white; border: 1px solid #E2E8F0; border-radius: 8px; color: #64748B;")
        header_layout.addWidget(exit_btn)
        
        main_layout.addLayout(header_layout)

        # --- 2. KPI METRICS ROW ---
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: white; border: 1px solid #E2E8F0; border-radius: 12px;")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(30, 20, 30, 20)
        
        self.stat_widgets = {}
        metrics = [
            ("TOTAL UNITS", "total_equipment", "", "#6366F1"),
            ("AVG FLOW", "avg_flowrate", " m³/h", "#0EA5E9"),
            ("AVG PRESSURE", "avg_pressure", " bar", "#10B981"),
            ("AVG TEMP", "avg_temperature", " °C", "#F59E0B")
        ]
        
        for name, key, unit, color in metrics:
            container = QVBoxLayout()
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("font-size: 11px; font-weight: 800; color: #94A3B8; letter-spacing: 0.5px;")
            lbl_val = QLabel("-")
            lbl_val.setStyleSheet(f"font-size: 26px; font-weight: 900; color: {color};")
            
            self.stat_widgets[key] = (lbl_val, unit)
            container.addWidget(lbl_name)
            container.addWidget(lbl_val)
            stats_layout.addLayout(container)
            if key != "avg_temperature": stats_layout.addStretch()
            
        main_layout.addWidget(stats_frame)

        # --- 3. DYNAMIC CONTENT STAGE ---
        # Split: 70% Chart Area | 30% Context Panel
        content_split = QHBoxLayout()
        
        # A. Chart Container
        chart_frame = QFrame()
        chart_frame.setStyleSheet("background: white; border: 1px solid #E2E8F0; border-radius: 12px;")
        chart_layout = QVBoxLayout(chart_frame)
        
        self.chart_title = QLabel("Process Envelope Analysis")
        self.chart_title.setAlignment(Qt.AlignCenter)
        self.chart_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #334155; margin-bottom: 10px;")
        chart_layout.addWidget(self.chart_title)
        
        # Matplotlib Canvas
        self.figure = Figure(figsize=(8, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        content_split.addWidget(chart_frame, 70)
        
        # B. Context Panel (Dynamic Insights)
        self.context_frame = QFrame()
        self.context_frame.setStyleSheet("background: white; border: 1px solid #E2E8F0; border-radius: 12px;")
        self.context_layout = QVBoxLayout(self.context_frame)
        self.context_layout.setAlignment(Qt.AlignTop)
        
        # Placeholder for dynamic content
        self.context_label = QLabel("Loading Insights...")
        self.context_layout.addWidget(self.context_label)
        
        # Scroll area for long lists (like outliers)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.context_frame)
        self.scroll.setStyleSheet("border: none; background: white;")
        
        content_split.addWidget(self.scroll, 30)
        main_layout.addLayout(content_split, 1)

    def load_data(self):
        """Fetch full analytics payload."""
        try:
            # Get Analytics (Now includes distribution_stats and correlation_matrix)
            res_a = self.api_client.get_analytics(self.dataset["id"])
            if res_a["success"]:
                self.analytics = res_a["data"]
                self.update_kpis()
                self.update_view() # Initial Render

            # Get Equipment List for raw data if needed
            res_e = self.api_client.get_equipment(self.dataset["id"])
            if res_e["success"]:
                self.equipment = res_e["data"]

        except Exception as e:
            logger.error(f"Data Load Error: {e}")

    def update_kpis(self):
        """Fill the top metric bar."""
        for key, (lbl, unit) in self.stat_widgets.items():
            val = self.analytics.get(key, 0)
            if isinstance(val, float):
                lbl.setText(f"{val:.2f}{unit}")
            else:
                lbl.setText(f"{val}{unit}")

    def change_view(self, index):
        """Handle Dropdown Selection."""
        views = ["safety", "distribution", "correlation"]
        self.current_view = views[index]
        self.update_view()

    def update_view(self):
        """Router to render the specific dashboard mode."""
        if not self.analytics: return

        self.figure.clear()
        
        # Clear Side Panel
        for i in reversed(range(self.context_layout.count())): 
            self.context_layout.itemAt(i).widget().setParent(None)

        if self.current_view == "safety":
            self.render_safety_view()
        elif self.current_view == "distribution":
            self.render_distribution_view()
        elif self.current_view == "correlation":
            self.render_correlation_view()
            
        self.canvas.draw()

    # --- MODE 1: SAFETY VIEW ---
    def render_safety_view(self):
        self.chart_title.setText("🛡️  Process Safety Envelope (Pressure vs Temperature)")
        ax = self.figure.add_subplot(111)
        
        data = self.analytics.get('scatter_data', [])
        
        # Split Data
        safe_x, safe_y = [], []
        danger_x, danger_y = [], []
        
        outlier_names = {o['name'] for o in self.analytics.get('outlier_equipment', [])}
        
        for item in data:
            if item['name'] in outlier_names:
                danger_x.append(item['x'])
                danger_y.append(item['y'])
            else:
                safe_x.append(item['x'])
                safe_y.append(item['y'])
        
        # Plot Safe Points
        ax.scatter(safe_x, safe_y, c='#10B981', label='Safe Operation', alpha=0.7, s=80, edgecolors='white')
        # Plot Danger Points
        ax.scatter(danger_x, danger_y, c='#EF4444', marker='^', label='Critical Alerts', s=120, edgecolors='black')
        
        # Draw "Safe Zone" Box (Visual Approximation based on avg +/- stddev logic implies)
        # Using fixed arbitrary visual box for demo: P: 2-8 bar, T: 90-140 C
        rect = patches.Rectangle((3, 90), 6, 50, linewidth=1, edgecolor='#10B981', facecolor='#ECFDF5', alpha=0.5, linestyle='--')
        ax.add_patch(rect)
        ax.text(3.2, 135, "Nominal Operating Zone", fontsize=9, color='#059669', weight='bold')

        ax.set_xlabel("Pressure (bar)", fontweight='bold')
        ax.set_ylabel("Temperature (°C)", fontweight='bold')
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)

        # -- Populate Side Panel --
        self.add_sidebar_header("Critical Alerts")
        outliers = self.analytics.get('outlier_equipment', [])
        if not outliers:
            self.add_sidebar_item("✅ All Systems Nominal", "No outliers detected.", "#10B981")
        else:
            for out in outliers:
                desc = []
                if out.get('pressure_outlier'): desc.append("High Pressure")
                if out.get('temperature_outlier'): desc.append("Temp Excursion")
                self.add_sidebar_item(f"⚠️ {out['name']}", ", ".join(desc), "#EF4444")

    # --- MODE 2: DISTRIBUTION VIEW ---
    def render_distribution_view(self):
        self.chart_title.setText("📊  Flowrate Variability by Equipment Type")
        ax = self.figure.add_subplot(111)
        
        # Prepare Data for Horizontal Floating Bar
        # Backend sends 'peer_benchmarks' (averages) but we calculated min/max in frontend for web.
        # Since desktop shares backend, let's use the raw scatter data to aggregate min/max here quickly.
        data = self.analytics.get('scatter_data', [])
        types = {}
        
        # Aggregate logic
        for d in data:
            t = d['type']
            # Reconstruct flow from r? No, backend sends flowrate in equipment list.
            # Ideally backend sends stats. Let's use the 'peer_benchmarks' (avg) and mock range for visual demo
            # OR better: Use the equipment list we fetched in load_data
            pass

        # Using self.equipment for accurate ranges
        if self.equipment:
            cats = list(set(e['equipment_type'] for e in self.equipment))
            y_pos = np.arange(len(cats))
            
            mins = []
            maxs = []
            means = []
            
            for c in cats:
                flows = [e['flowrate'] for e in self.equipment if e['equipment_type'] == c]
                mins.append(min(flows))
                maxs.append(max(flows) - min(flows)) # Height for barh
                means.append(sum(flows)/len(flows))
            
            # Draw Range Bars (Floating)
            ax.barh(y_pos, maxs, left=mins, height=0.5, color='#BFDBFE', edgecolor='#3B82F6', label='Operating Range')
            # Draw Mean Line
            ax.plot(means, y_pos, 'D', color='#2563EB', markersize=8, label='Average Flow')
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(cats, fontweight='bold')
            ax.set_xlabel("Flowrate (m³/h)")
            ax.legend()
        
        # -- Populate Side Panel --
        self.add_sidebar_header("Distribution Stats")
        dist = self.analytics.get('distribution_stats', {})
        if dist:
            self.add_sidebar_text(f"Global Median Flow: {dist.get('median')} m³/h")
            self.add_sidebar_text(f"Max Recorded: {dist.get('max')} m³/h")
            self.add_sidebar_text(f"Min Recorded: {dist.get('min')} m³/h")
            self.add_sidebar_text(f"IQR Spread: {dist.get('q3') - dist.get('q1'):.2f}")

    # --- MODE 3: CORRELATION VIEW ---
    def render_correlation_view(self):
        self.chart_title.setText("🔗  Multi-Variable Correlation Analysis")
        
        # Use GridSpec for Layout (Bubble Chart Left, Heatmap Right) - Simplified to just Bubble for space
        ax = self.figure.add_subplot(111)
        
        data = self.analytics.get('scatter_data', [])
        x = [d['x'] for d in data]
        y = [d['y'] for d in data]
        s = [d['r'] * 15 for d in data] # Scale radius up for visibility
        colors = [hash(d['type']) % 10 for d in data] # Random consistent color
        
        scatter = ax.scatter(x, y, s=s, c=colors, cmap='viridis', alpha=0.6, edgecolors='grey')
        
        ax.set_xlabel("Pressure (bar)")
        ax.set_ylabel("Temperature (°C)")
        ax.grid(True, linestyle='--', alpha=0.4)
        
        # Add dummy legend for size
        # ax.legend(*scatter.legend_elements("sizes", num=3), loc="lower right", title="Flowrate")

        # -- Populate Side Panel (Heatmap Text) --
        self.add_sidebar_header("Correlation Matrix")
        matrix = self.analytics.get('correlation_matrix', [])
        
        for row in matrix:
            var = row.get('variable', 'Unknown')
            self.add_sidebar_item(f"{var.upper()}", "", "#475569")
            txt = f"vs Flow: {row.get('flowrate', 0)}\nvs Press: {row.get('pressure', 0)}\nvs Temp: {row.get('temperature', 0)}"
            lbl = QLabel(txt)
            lbl.setStyleSheet("font-family: monospace; color: #334155; margin-bottom: 8px; background: #F1F5F9; padding: 5px; border-radius: 4px;")
            self.context_layout.addWidget(lbl)

    # --- HELPER FUNCTIONS ---
    def add_sidebar_header(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 12px; font-weight: 800; color: #94A3B8; text-transform: uppercase; margin-bottom: 10px; margin-top: 10px;")
        self.context_layout.addWidget(lbl)

    def add_sidebar_item(self, title, subtitle, color):
        frame = QFrame()
        frame.setStyleSheet(f"background: white; border-left: 4px solid {color}; border-radius: 4px; background-color: #FAFAFA;")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(10, 8, 10, 8)
        
        t = QLabel(title)
        t.setStyleSheet(f"font-weight: 700; color: #1E293B;")
        lay.addWidget(t)
        
        if subtitle:
            s = QLabel(subtitle)
            s.setStyleSheet("font-size: 11px; color: #64748B;")
            lay.addWidget(s)
            
        self.context_layout.addWidget(frame)

    def add_sidebar_text(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 13px; font-weight: 500; color: #334155; padding: 4px 0;")
        self.context_layout.addWidget(lbl)

# Alias for compatibility
DatasetDetailDialog = DatasetDetailWindow