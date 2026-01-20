import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplcursors

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QGridLayout, QScrollArea, QComboBox, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont

from db.database import Database

# Configurer Matplotlib pour le style sombre
plt.style.use('dark_background')

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#1E1E1E')
        self.axes = self.fig.add_subplot(111, facecolor='#1E1E1E')
        super().__init__(self.fig)
        self.setStyleSheet("background-color: #1E1E1E;")
        # Ajuster les marges
        self.fig.tight_layout()

class PurchasingStatsScreen(QWidget):
    """
    ÉCRAN STATISTIQUES ACHATS (V2 - Matplotlib & Interactivité)
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.rafraichir()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        container.setObjectName("StatsContainer")
        container.setStyleSheet("#StatsContainer { background-color: #121212; }")
        
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(30, 25, 30, 30)
        self.content_layout.setSpacing(25)
        
        # --- HEADER & FILTRES ---
        header_frame = QFrame()
        header_frame.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_vbox = QVBoxLayout()
        lbl_title = QLabel("ANALYSE DÉCISIONNELLE")
        lbl_title.setStyleSheet("color: white; font-size: 20pt; font-weight: bold; letter-spacing: 1px;")
        lbl_sub = QLabel("Suivi des performances, risques et impact financier")
        lbl_sub.setStyleSheet("color: #757575; font-size: 10pt;")
        title_vbox.addWidget(lbl_title)
        title_vbox.addWidget(lbl_sub)
        header_layout.addLayout(title_vbox)
        
        header_layout.addStretch()
        
        self.cb_period = QComboBox()
        self.cb_period.setFixedWidth(220)
        self.cb_period.addItems(["30 Derniers Jours", "90 Derniers Jours", "7 Derniers Jours"])
        self.cb_period.setStyleSheet("""
            QComboBox {
                background-color: #1E1E1E; color: white; border: 1px solid #333; 
                border-radius: 20px; padding: 10px 15px; font-weight: bold;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.cb_period.currentIndexChanged.connect(self.rafraichir)
        header_layout.addWidget(self.cb_period)
        
        self.content_layout.addWidget(header_frame)
        
        # --- BLOC KPI ---
        kpi_container = QWidget()
        self.kpi_grid = QGridLayout(kpi_container)
        self.kpi_grid.setSpacing(20)
        self.kpi_grid.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(kpi_container)
        
        # --- ZONE GRAPHIQUES ---
        # Utilisation d'une grille pour éviter les chevauchements
        charts_container = QWidget()
        self.charts_grid = QGridLayout(charts_container)
        self.charts_grid.setSpacing(25)
        self.charts_grid.setContentsMargins(0, 0, 0, 0)
        
        # Graphique 1 : Tendances Multilines (Alertes par Priorité)
        self.panel_trend = self._create_chart_panel("📈 TENDANCE DES ALERTES PAR PRIORITÉ")
        self.canvas_trend = MplCanvas(self.panel_trend)
        self.panel_trend.layout().addWidget(self.canvas_trend)
        self.charts_grid.addWidget(self.panel_trend, 0, 0)
        
        # Graphique 2 : Combo Ruptures vs Commandes
        self.panel_risk = self._create_chart_panel("🚨 CORRÉLATION RUPTURES / COMMANDES")
        self.canvas_risk = MplCanvas(self.panel_risk)
        self.panel_risk.layout().addWidget(self.canvas_risk)
        self.charts_grid.addWidget(self.panel_risk, 0, 1)
        
        # Graphique 3 : Répartition Fournisseurs (Large)
        self.panel_supp = self._create_chart_panel("🤝 VOLUME D'ACHATS PAR FOURNISSEUR")
        self.canvas_supp = MplCanvas(self.panel_supp)
        self.panel_supp.layout().addWidget(self.canvas_supp)
        self.charts_grid.addWidget(self.panel_supp, 1, 0, 1, 2)
        
        self.content_layout.addWidget(charts_container)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_chart_panel(self, title):
        frame = QFrame()
        frame.setMinimumHeight(350)
        frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E; border-radius: 12px; border: 1px solid #333;
            }
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(15, 15, 15, 15)
        
        lbl = QLabel(title)
        lbl.setStyleSheet("color: #B0BEC5; font-weight: bold; font-size: 10pt; margin-bottom: 10px;")
        lay.addWidget(lbl)
        return frame

    def _create_kpi_card(self, title, items, color_accent):
        card = QFrame()
        card.setFixedHeight(160)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1E1E1E; border-radius: 12px; border: 1px solid #333;
                border-top: 4px solid {color_accent};
            }}
        """)
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 15, 20, 15)
        
        t = QLabel(title.upper())
        t.setStyleSheet(f"color: {color_accent}; font-weight: bold; font-size: 9pt; letter-spacing: 1px;")
        l.addWidget(t)
        
        for label, value in items:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #90A4AE; font-size: 10pt;")
            val = QLabel(str(value))
            val.setStyleSheet("color: white; font-weight: bold; font-size: 13pt; font-family: 'Monospace';")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            l.addLayout(row)
            
        l.addStretch()
        return card

    def rafraichir(self):
        txt = self.cb_period.currentText()
        days = 30
        if "90" in txt: days = 90
        elif "7" in txt: days = 7
        
        # Récupérer les données
        stats = Database.get_purchasing_stats(days)
        if not stats: return

        # --- REFRESH KPIs ---
        while self.kpi_grid.count():
            item = self.kpi_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Performance
        p = stats['performance']
        self.kpi_grid.addWidget(self._create_kpi_card("⚡ PERFORMANCE", [
            ("Alertes Traitées", p.get('processed_alerts', 0)),
            ("Délai Réaction Moy.", f"{p.get('avg_process_time', 0)}h"),
            ("SLA Critique <24h", f"{p.get('critical_reactivity', 0)}%")
        ], "#00E676"), 0, 0)
        
        # Risques
        r = stats['ruptures']
        self.kpi_grid.addWidget(self._create_kpi_card("🚨 STOCKS & RISQUES", [
            ("Ruptures Évitées", r.get('avoided_shortages', 0)),
            ("Ruptures Actuelles", r.get('real_shortages', 0)),
            ("Produits en Tension", f"{len(r.get('top_risks', []))} réf.")
        ], "#FF5252"), 0, 1)
        
        # Finance
        f = stats['finance']
        self.kpi_grid.addWidget(self._create_kpi_card("💰 IMPACT FINANCIER", [
            ("Volume d'achats", f"{f.get('total_ordered', 0):,.0f} FCFA"),
            ("Surcoût Urgences", f"{f.get('emergency_cost', 0):,.0f} FCFA"),
            ("Optimisation Pot.", f"{(float(f.get('emergency_cost', 0)) * 0.15):,.0f} FCFA")
        ], "#FFD700"), 0, 2)

        # --- REFRESH CHARTS ---
        self._plot_trend_chart(stats['charts']['alerts_trend'])
        self._plot_risk_chart(stats['charts']['orders_vs_risk'])
        self._plot_supplier_chart(stats['charts']['supplier_repartition'])

    def _plot_trend_chart(self, raw_data):
        ax = self.canvas_trend.axes
        ax.clear()
        
        # Organiser par priorité
        # raw_data: [{'jour': date, 'priorite': '...', 'count': X}, ...]
        data_by_prio = {'CRITICAL': {}, 'HIGH': {}, 'MEDIUM': {}}
        dates = sorted(list(set(r['jour'] for r in raw_data)))
        
        for r in raw_data:
            data_by_prio[r['priorite']][r['jour']] = r['count']
            
        x_labels = [d.strftime("%d/%m") for d in dates]
        
        colors = {'CRITICAL': '#FF5252', 'HIGH': '#FFAB40', 'MEDIUM': '#448AFF'}
        labels = {'CRITICAL': 'Critique', 'HIGH': 'Élevée', 'MEDIUM': 'Moyenne'}
        
        for prio, values in data_by_prio.items():
            y_vals = [values.get(d, 0) for d in dates]
            ax.plot(x_labels, y_vals, label=labels[prio], color=colors[prio], marker='o', linewidth=2, markersize=4)
        
        ax.legend(loc='upper right', frameon=False, fontsize=8)
        ax.grid(True, linestyle='--', alpha=0.1)
        ax.set_ylabel("Nombre d'alertes", color="#757575", fontsize=8)
        
        # Tooltips
        cursor = mplcursors.cursor(ax, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(f"{sel.target[1]:.0f} alertes"))
        
        self.canvas_trend.draw()

    def _plot_risk_chart(self, raw_data):
        ax = self.canvas_risk.axes
        ax.clear()
        
        dates = [r['jour'].strftime("%d/%m") for r in raw_data]
        nb_cdes = [r['nb_cdes'] for r in raw_data]
        nb_rupt = [r['nb_ruptures'] for r in raw_data]
        
        ax.bar(dates, nb_cdes, label='Commandes', color='#2979FF', alpha=0.4)
        ax.plot(dates, nb_rupt, label='Ruptures', color='#FF5252', marker='x', linewidth=2)
        
        ax.legend(loc='upper right', frameon=False, fontsize=8)
        ax.grid(True, axis='y', linestyle='--', alpha=0.1)
        
        self.canvas_risk.draw()

    def _plot_supplier_chart(self, raw_data):
        ax = self.canvas_supp.axes
        ax.clear()
        
        if not raw_data:
            ax.text(0.5, 0.5, "Pas de données fournisseurs", ha='center', va='center')
            self.canvas_supp.draw()
            return

        names = [r['nom'] for r in raw_data]
        counts = [r['nb'] for r in raw_data]
        
        # Pie chart pour la répartition
        wedges, texts, autotexts = ax.pie(counts, labels=names, autopct='%1.1f%%', 
                                          startangle=140, colors=plt.cm.viridis(range(len(names))))
        
        plt.setp(autotexts, size=8, weight="bold", color="white")
        plt.setp(texts, size=8)
        
        self.canvas_supp.draw()
