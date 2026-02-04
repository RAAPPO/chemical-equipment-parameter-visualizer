import logging
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, QFrame,
                             QScrollArea, QHeaderView, QButtonGroup, QComboBox, QSizePolicy,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches

logger = logging.getLogger(__name__)

class DatasetDetailWindow(QMainWindow):
 
    def __init__(self, api_client, dataset, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.dataset = dataset
        self.analytics = {}
        self.equipment = []
        self.filtered_equipment = []
        self.current_view = "safety" 
        self.is_dark_mode = False 
        
        self.init_ui()
        self.load_data()
        self.apply_theme() 
    
    def init_ui(self):
        self.resize(1280, 850)
        self.setWindowTitle(f"Analysis: {self.dataset.get('filename')}")
        
        # --- STATIC SHELL ---
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0,0,0,0)

        # 1. TOOLBAR HEADER
        self.header = QFrame()
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(24, 12, 24, 12)
        h_layout.setSpacing(20)
        
        # Title
        self.title_lbl = QLabel(f"{self.dataset.get('filename')}")
        self.title_lbl.setStyleSheet("font-size: 18px; font-weight: 900;")
        h_layout.addWidget(self.title_lbl)
        
        # Filter
        f_lbl = QLabel("FILTER:")
        f_lbl.setStyleSheet("font-weight: 700; color: #94A3B8; font-size: 11px;")
        h_layout.addWidget(f_lbl)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All Equipment")
        self.filter_combo.setFixedWidth(160)
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        h_layout.addWidget(self.filter_combo)
        
        h_layout.addStretch()

        # Switcher Pills
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        self.pill_layout = QHBoxLayout()
        self.pill_layout.setSpacing(0)
        
        views = [("safety", "🛡️ Process Safety"), ("dist", "📊 Distribution"), ("corr", "🔗 Correlation"), ("data", "📋 Equipment Data")]
        self.view_btns = {}
        
        for i, (id, txt) in enumerate(views):
            btn = QPushButton(txt)
            btn.setCheckable(True)
            if i == 0: btn.setChecked(True)
            self.btn_group.addButton(btn)
            btn.clicked.connect(lambda _, x=id: self.switch_view(x))
            self.pill_layout.addWidget(btn)
            self.view_btns[id] = btn
            
        h_layout.addLayout(self.pill_layout)
        h_layout.addSpacing(20)
        
        # Theme Toggle
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(100,36)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        h_layout.addWidget(self.theme_btn)

        # Close
        close_btn = QPushButton("Close ✖")
        close_btn.setFixedSize(80, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("color: #94A3B8; border: none; font-weight: bold; font-size: 16px;")
        h_layout.addWidget(close_btn)
        
        self.main_layout.addWidget(self.header)

        # 2. KPI BAR
        self.kpi_frame = QFrame()
        k_layout = QHBoxLayout(self.kpi_frame)
        k_layout.setContentsMargins(24, 20, 24, 20)
        k_layout.setSpacing(40)
        
        self.kpis = {}
        for k in ['units', 'flow', 'press', 'temp']:
            v_box = QVBoxLayout()
            l = QLabel(k.upper()); l.setStyleSheet("color:#94A3B8; font-size:11px; font-weight:800; letter-spacing: 0.5px;")
            v = QLabel("-"); v.setStyleSheet("font-size:24px; font-weight:900;")
            self.kpis[k] = v
            v_box.addWidget(l); v_box.addWidget(v)
            k_layout.addLayout(v_box)
            
        k_layout.addStretch()

        self.main_layout.addWidget(self.kpi_frame)

        # 3. DYNAMIC STAGE CONTAINER
        self.stage_container = QWidget()
        self.stage_layout = QVBoxLayout(self.stage_container)
        self.stage_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.addWidget(self.stage_container)

    def add_shadow(self, widget):
        """Adds a subtle web-like shadow to cards."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15)) # Very light shadow
        shadow.setOffset(0, 4)
        widget.setGraphicsEffect(shadow)

    def load_data(self):
        try:
            res_a = self.api_client.get_analytics(self.dataset["id"])
            res_e = self.api_client.get_equipment(self.dataset["id"])
            if res_a["success"] and res_e["success"]:
                self.analytics = res_a["data"]
                self.equipment = res_e["data"]
                self.filtered_equipment = self.equipment
                
                # Populate Filter
                types = sorted(list(set(e['equipment_type'] for e in self.equipment)))
                self.filter_combo.blockSignals(True)
                self.filter_combo.clear()
                self.filter_combo.addItem("All Equipment")
                for t in types: self.filter_combo.addItem(t)
                self.filter_combo.blockSignals(False)
                
                self.update_ui()
        except Exception as e:
            logger.error(str(e))

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        self.update_ui()

    def apply_theme(self):
        """Styles the Persistent Shell."""
        if self.is_dark_mode:
            bg_main = "#0F172A"; bg_card = "#1E293B"; text_main = "#F8FAFC"; text_sub = "#94A3B8"; border = "#334155"
            self.theme_btn.setText("Light mode ☀️")
        else:
            bg_main = "#F8FAFC"; bg_card = "#FFFFFF"; text_main = "#1E293B"; text_sub = "#64748B"; border = "#E2E8F0"
            self.theme_btn.setText("Dark mode 🌙")

        self.central.setStyleSheet(f"background-color: {bg_main};")
        self.header.setStyleSheet(f"background: {bg_card}; border-bottom: 1px solid {border};")
        self.title_lbl.setStyleSheet(f"font-size: 18px; font-weight: 900; color: {text_main}; border: none;")
        self.kpi_frame.setStyleSheet(f"background: {bg_card}; border-bottom: 1px solid {border};")
        
        colors = {'units': '#6366F1', 'flow': '#3B82F6', 'press': '#10B981', 'temp': '#F59E0B'}
        for k, v in self.kpis.items():
            v.setStyleSheet(f"font-size: 24px; font-weight: 900; color: {colors[k]}; border: none;")

        # Style Pills
        for i, (id, btn) in enumerate(self.view_btns.items()):
            radius = "border-top-left-radius: 6px; border-bottom-left-radius: 6px;" if i==0 else \
                     "border-top-right-radius: 6px; border-bottom-right-radius: 6px;" if i==3 else ""
            border_right = "border-right: none;" if i < 3 else ""
            
            is_active = btn.isChecked()
            btn_bg = ("#3B82F6" if not self.is_dark_mode else "#60A5FA") if is_active else bg_card
            btn_fg = ("white" if not self.is_dark_mode else "#0F172A") if is_active else text_sub
            
            btn.setStyleSheet(f"""
                QPushButton {{ 
                    background: {btn_bg}; border: 1px solid {border}; color: {btn_fg}; 
                    padding: 8px 20px; font-weight: 700; {radius} {border_right}
                }}
            """)

        self.filter_combo.setStyleSheet(f"color: {text_main}; background: {bg_card}; border: 1px solid {border}; padding: 4px;")
        self.theme_btn.setStyleSheet(f"background: {bg_card}; border: 1px solid {border}; border-radius: 18px;")

    def switch_view(self, view_id):
        self.current_view = view_id
        self.apply_theme()
        self.update_ui()

    def apply_filter(self, text):
        if text == "All Equipment":
            self.filtered_equipment = self.equipment
        else:
            self.filtered_equipment = [e for e in self.equipment if e['equipment_type'] == text]
        self.update_ui()

    def clear_stage(self):
        """Safely delete all widgets in stage."""
        while self.stage_layout.count():
            item = self.stage_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    def update_ui(self):
        # 1. Update KPIs
        self.kpis['units'].setText(str(len(self.filtered_equipment)))
        self.kpis['flow'].setText(f"{self.analytics.get('avg_flowrate',0)} m³/h")
        self.kpis['press'].setText(f"{self.analytics.get('avg_pressure',0)} bar")
        self.kpis['temp'].setText(f"{self.analytics.get('avg_temperature',0)} °C")

        # 2. Clear & Rebuild Stage
        self.clear_stage()

        if self.current_view == "data":
            self.build_data_view()
        else:
            self.build_chart_view()

    def build_data_view(self):
        bg_card = "#1E293B" if self.is_dark_mode else "white"
        text_main = "#F8FAFC" if self.is_dark_mode else "#1E293B"
        border = "#334155" if self.is_dark_mode else "#E2E8F0" # Lighter border for clean look
        header_bg = "#0F172A" if self.is_dark_mode else "#F8FAFC"
        
        container = QFrame() # Container for shadow
        container.setStyleSheet(f"background: {bg_card}; border-radius: 12px; border: 1px solid {border};")
        self.add_shadow(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        
        self.table = QTableWidget()
        self.table.setStyleSheet(f"""
            QTableWidget {{ background: transparent; border: none; color: {text_main}; gridline-color: {border}; }}
            QHeaderView::section {{ background: {header_bg}; color: #94A3B8; border: none; padding: 12px; font-weight: bold; text-transform: uppercase; }}
            QTableWidget::item {{ padding: 12px; border-bottom: 1px solid {border}; }}
        """)
        self.table.setShowGrid(False)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Flow", "Press", "Temp", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setRowCount(len(self.filtered_equipment))
        
        for r, eq in enumerate(self.filtered_equipment):
            self.table.setItem(r,0, QTableWidgetItem(eq['equipment_name']))
            self.table.setItem(r,1, QTableWidgetItem(eq['equipment_type']))
            self.table.setItem(r,2, QTableWidgetItem(f"{eq['flowrate']:.2f}"))
            self.table.setItem(r,3, QTableWidgetItem(f"{eq['pressure']:.2f}"))
            self.table.setItem(r,4, QTableWidgetItem(f"{eq['temperature']:.2f}"))
            
            alert = eq.get('is_pressure_outlier') or eq.get('is_temperature_outlier')
            item = QTableWidgetItem("⚠️ ALERT" if alert else "OK")
            item.setForeground(QColor("#EF4444") if alert else QColor("#10B981"))
            item.setFont(QFont("Arial", weight=QFont.Bold))
            self.table.setItem(r,5, item)
            
        layout.addWidget(self.table)
        self.stage_layout.addWidget(container)

    def build_chart_view(self):
        bg_card = "#1E293B" if self.is_dark_mode else "white"
        text_sub = "#94A3B8"
        border = "#334155" if self.is_dark_mode else "#E2E8F0"
        
        split_container = QWidget()
        split_layout = QHBoxLayout(split_container)
        split_layout.setContentsMargins(0,0,0,0)
        split_layout.setSpacing(24)
        
        # A. MAIN CHART CARD (Left)
        c_frame = QFrame()
        c_frame.setStyleSheet(f"background:{bg_card}; border:1px solid {border}; border-radius:12px;")
        self.add_shadow(c_frame)
        cv = QVBoxLayout(c_frame)
        cv.setContentsMargins(20,20,20,20)
        
        # Chart Title
        titles = {'safety': "Process Envelope", 'dist': "Flowrate Distribution", 'corr': "Correlation Analysis"}
        title_lbl = QLabel(titles.get(self.current_view, ""))
        title_lbl.setStyleSheet(f"color: {text_sub}; font-weight: 800; font-size: 12px; letter-spacing: 1px; border: none;")
        cv.addWidget(title_lbl)
        
        self.figure = Figure(figsize=(8, 5), dpi=100) # Created Fresh
        self.canvas = FigureCanvas(self.figure)
        cv.addWidget(self.canvas)
        split_layout.addWidget(c_frame, 65)
        
        # B. INSIGHT CARD (Right) - Now Holds Sidebar Chart or List
        i_frame = QFrame()
        i_frame.setStyleSheet(f"background:{bg_card}; border:1px solid {border}; border-radius:12px;")
        self.add_shadow(i_frame)
        iv = QVBoxLayout(i_frame)
        iv.setContentsMargins(20,20,20,20)
        
        lbl = QLabel("INSIGHTS")
        lbl.setStyleSheet(f"color: {text_sub}; font-weight: 800; font-size: 12px; letter-spacing: 1px; border: none;")
        iv.addWidget(lbl)
        
        # The content area for the sidebar (Can be ScrollArea OR Chart)
        self.side_content_area = QVBoxLayout() 
        iv.addLayout(self.side_content_area)
        
        split_layout.addWidget(i_frame, 35)
        self.stage_layout.addWidget(split_container)
        
        # Render Contents
        self.render_charts()
        self.populate_sidebar()

    def render_charts(self):
        bg_color = "#1E293B" if self.is_dark_mode else "white"
        text_color = "white" if self.is_dark_mode else "#334155"
        self.figure.patch.set_facecolor(bg_color)
        
        all_data = self.analytics.get('scatter_data', [])
        filter_type = self.filter_combo.currentText()
        data = [d for d in all_data if d['type'] == filter_type] if filter_type != "All Equipment" else all_data

        ax = self.figure.add_subplot(111)
        ax.set_facecolor(bg_color)
        ax.tick_params(colors=text_color, which='both')
        for spine in ax.spines.values(): spine.set_color(text_color)
        ax.xaxis.label.set_color(text_color); ax.yaxis.label.set_color(text_color)
        
        if self.current_view == 'safety':
            outliers = {o['name'] for o in self.analytics.get('outlier_equipment', [])}
            safe = [d for d in data if d['name'] not in outliers]
            risk = [d for d in data if d['name'] in outliers]
            ax.scatter([d['x'] for d in safe], [d['y'] for d in safe], c='#10B981', alpha=0.6, s=60, label='Safe', edgecolors='none')
            ax.scatter([d['x'] for d in risk], [d['y'] for d in risk], c='#EF4444', marker='^', s=90, label='Alert', edgecolors='white')
            ax.set_xlabel("Pressure (bar)"); ax.set_ylabel("Temp (°C)")
            ax.legend(facecolor=bg_color, edgecolor=text_color, labelcolor=text_color)
            ax.grid(True, linestyle='--', alpha=0.1)

        elif self.current_view == 'dist':
            bench = self.analytics.get('peer_benchmarks', {})
            keys = [filter_type] if filter_type != "All Equipment" and filter_type in bench else list(bench.keys())
            if keys:
                mins = [bench[k]['flowrate_min'] for k in keys]
                ranges = [bench[k]['flowrate_max'] - bench[k]['flowrate_min'] for k in keys]
                ax.barh(keys, ranges, left=mins, height=0.5, color='#3B82F6')
                ax.set_xlabel("Flowrate Range (m³/h)")
                ax.grid(axis='x', linestyle='--', alpha=0.1)

        elif self.current_view == 'corr':
            s = [d.get('r', 5) * 5 for d in data]
            ax.scatter([d['x'] for d in data], [d['y'] for d in data], s=s, alpha=0.5, c='#6366F1', edgecolors='white', linewidth=0.5)
            ax.set_xlabel("Pressure"); ax.set_ylabel("Temp")
            ax.grid(True, linestyle='--', alpha=0.1)

        self.canvas.draw()

    def populate_sidebar(self):
        """Populates the Right Sidebar with either Text Lists OR Secondary Charts."""
        text_color = "white" if self.is_dark_mode else "#1E293B"
        bg_color = "#1E293B" if self.is_dark_mode else "white"
        
        # 1. DISTRIBUTION VIEW -> SHOW PIE CHART (Like Web)
        if self.current_view == 'dist':
            self.side_figure = Figure(figsize=(4, 4), dpi=100)
            self.side_figure.patch.set_facecolor(bg_color)
            self.side_canvas = FigureCanvas(self.side_figure)
            self.side_content_area.addWidget(self.side_canvas)
            
            ax = self.side_figure.add_subplot(111)
            dist = self.analytics.get('equipment_type_distribution', {})
            
            # Web colors
            colors = ['#6366F1', '#3B82F6', '#10B981', '#F59E0B', '#EF4444']
            wedges, texts, autotexts = ax.pie(dist.values(), labels=dist.keys(), colors=colors, autopct='%1.1f%%', startangle=90)
            
            # Style text
            for t in texts: t.set_color(text_color); t.set_fontsize(8)
            for t in autotexts: t.set_color('white'); t.set_fontsize(8); t.set_weight('bold')
            self.side_canvas.draw()
            return

        # 2. SAFETY VIEW -> SHOW ALERT LIST
        if self.current_view == 'safety':
            scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border:none; background:transparent;")
            content = QWidget(); content.setStyleSheet("background:transparent;")
            layout = QVBoxLayout(content); layout.setContentsMargins(0,0,0,0)
            scroll.setWidget(content)
            self.side_content_area.addWidget(scroll)

            outliers = self.analytics.get('outlier_equipment', [])
            if not outliers:
                lbl = QLabel("✅ All Systems Nominal"); lbl.setStyleSheet("color: #10B981; font-weight: bold;")
                layout.addWidget(lbl)
            else:
                for out in outliers:
                    w = QFrame()
                    w.setStyleSheet(f"background: {'#450a0a' if self.is_dark_mode else '#FEF2F2'}; border-left: 3px solid #EF4444; border-radius: 4px;")
                    l = QVBoxLayout(w); l.setContentsMargins(10,8,10,8); l.setSpacing(2)
                    name = QLabel(out['name']); name.setStyleSheet(f"font-weight:bold; color: {'#F87171' if self.is_dark_mode else '#991B1B'}; border:none;")
                    desc = QLabel("Parameter Excursion"); desc.setStyleSheet(f"color: {'#FECACA' if self.is_dark_mode else '#B91C1C'}; font-size:11px; border:none;")
                    l.addWidget(name); l.addWidget(desc)
                    layout.addWidget(w)
            layout.addStretch()
            return

        # 3. CORRELATION VIEW -> SHOW HEATMAP TEXT GRID
        if self.current_view == 'corr':
            scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("border:none; background:transparent;")
            content = QWidget(); content.setStyleSheet("background:transparent;")
            layout = QVBoxLayout(content); layout.setContentsMargins(0,0,0,0)
            scroll.setWidget(content)
            self.side_content_area.addWidget(scroll)

            matrix = self.analytics.get('correlation_matrix', [])
            for row in matrix:
                lbl = QLabel(row['variable'].upper())
                lbl.setStyleSheet(f"color: {text_color}; font-weight: bold; margin-top: 10px; border:none;")
                layout.addWidget(lbl)
                
                # Mini Grid
                g = QFrame()
                g.setStyleSheet("background: transparent; border: none;")
                gl = QHBoxLayout(g); gl.setContentsMargins(0,0,0,0); gl.setSpacing(4)
                
                for k in ['flowrate', 'pressure', 'temperature']:
                    val = row.get(k, 0)
                    bg = "#3B82F6" if abs(val) > 0.7 else ("#1E293B" if self.is_dark_mode else "#F1F5F9")
                    fg = "white" if abs(val) > 0.7 else text_color
                    box = QLabel(f"{val:.2f}")
                    box.setAlignment(Qt.AlignCenter)
                    box.setFixedSize(60, 30)
                    box.setStyleSheet(f"background: {bg}; color: {fg}; border-radius: 4px; font-size: 11px;")
                    gl.addWidget(box)
                layout.addWidget(g)
            layout.addStretch()

# Compatibility Alias
DatasetDetailDialog = DatasetDetailWindow