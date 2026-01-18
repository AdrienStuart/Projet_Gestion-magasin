
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QGridLayout, QSizePolicy)
from PySide6.QtCore import Qt
import qtawesome as qta
from db.database import Database

# Try importing plotting libs
try:
    import pyqtgraph as pg
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False

class KPICard(QFrame):
    def __init__(self, title, value, icon_name, color):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2A2A40;
                border-radius: 12px;
                border-left: 5px solid {color};
            }}
        """)
        self.setFixedHeight(120)
        
        layout = QHBoxLayout(self)
        
        # Icon
        icon = QLabel()
        icon.setPixmap(qta.icon(icon_name, color=color).pixmap(48, 48))
        layout.addWidget(icon)
        
        # Text
        text_layout = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #A0A0B0; font-size: 12pt;")
        
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(f"color: white; font-size: 24pt; font-weight: bold;")
        
        text_layout.addWidget(title_lbl)
        text_layout.addWidget(self.value_lbl)
        layout.addLayout(text_layout)

class AdminView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # 1. KPIs Row
        kpi_layout = QHBoxLayout()
        self.card_daily = KPICard("CA du Jour", "0 FCFA", "fa5s.coins", "#00C853")
        self.card_monthly = KPICard("CA Mensuel", "0 FCFA", "fa5s.chart-line", "#2979FF")
        self.card_alerts = KPICard("Alertes Stock", "0", "fa5s.exclamation-triangle", "#FF3D00")
        
        kpi_layout.addWidget(self.card_daily)
        kpi_layout.addWidget(self.card_monthly)
        kpi_layout.addWidget(self.card_alerts)
        layout.addLayout(kpi_layout)
        
        # 2. Charts Area
        charts_layout = QHBoxLayout()
        
        # Chart 1: Bar Chart (Weekly Sales)
        self.chart1_container = QFrame()
        self.chart1_layout = QVBoxLayout(self.chart1_container)
        self.chart1_layout.addWidget(QLabel("Ventes des 7 derniers jours"))
        if HAS_PLOT:
            self.bar_plot = pg.PlotWidget()
            self.bar_plot.setBackground('#2A2A40')
            self.chart1_layout.addWidget(self.bar_plot)
            # Mock Data
            x = [1, 2, 3, 4, 5, 6, 7]
            y = [10, 15, 8, 20, 25, 18, 30]
            bg = pg.BarGraphItem(x=x, height=y, width=0.6, brush='#00C853')
            self.bar_plot.addItem(bg)
        else:
            self.chart1_layout.addWidget(QLabel("Installer 'pyqtgraph' pour voir le graphique"))
            
        # Chart 2: Placeholder for Pie (PyQtGraph doesn't do Pies easily, just show text or rects)
        self.chart2_container = QFrame()
        self.chart2_layout = QVBoxLayout(self.chart2_container)
        self.chart2_layout.addWidget(QLabel("Top Catégories (Volume)"))
        if HAS_PLOT:
             self.line_plot = pg.PlotWidget()
             self.line_plot.setBackground('#2A2A40')
             self.chart2_layout.addWidget(self.line_plot)
             self.line_plot.plot([1, 4, 2, 3, 5], pen=pg.mkPen(color='#2979FF', width=3))
        else:
             self.chart2_layout.addWidget(QLabel("Graphique non disponible"))

        charts_layout.addWidget(self.chart1_container)
        charts_layout.addWidget(self.chart2_container)
        layout.addLayout(charts_layout)
        
        # 3. Footer / Actions
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        self.btn_refresh = QPushButton("Actualiser les Statistiques")
        self.btn_refresh.setIcon(qta.icon('fa5s.sync', color='white'))
        self.btn_refresh.clicked.connect(self.refresh_stats)
        footer_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(footer_layout)
        
        self.load_data()

    def load_data(self):
        # Update KPIs with real data
        daily = Database.get_kpi_daily_revenue()
        self.card_daily.value_lbl.setText(f"{daily:,.0f} FCFA")
        
        # TODO: Get other metrics from DB
        # monthly = ...
        # alerts = ...

    def refresh_stats(self):
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setText("Actualisation...")
        
        success = Database.refresh_materialized_views()
        
        self.btn_refresh.setEnabled(True)
        self.btn_refresh.setText("Actualiser les Statistiques")
        
        if success:
            self.load_data()
            # Update charts if real data available
        else:
            # Maybe show error
            pass

