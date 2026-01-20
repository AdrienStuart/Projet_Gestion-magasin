import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QGridLayout, QScrollArea, QProgressBar, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, QSize, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from db.database import Database

class Sparkline(QWidget):
    """Mini graphique de tendance"""
    def __init__(self, data, color="#00E676"):
        super().__init__()
        self.data = data # list of values
        self.color = QColor(color)
        self.setFixedHeight(40)
        self.setFixedWidth(100)
        self.setStyleSheet("background: transparent;")
        
    def paintEvent(self, event):
        if not self.data or len(self.data) < 2: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        max_val = max(self.data) if max(self.data) > 0 else 1
        step = w / (len(self.data) - 1)
        
        path_points = []
        for i, val in enumerate(self.data):
            x = i * step
            y = h - (val / max_val * h)
            path_points.append(QPointF(x, y))
            
        pen = QPen(self.color, 2)
        painter.setPen(pen)
        for i in range(len(path_points) - 1):
            painter.drawLine(path_points[i], path_points[i+1])

class PurchasingDashboard(QWidget):
    """
    COMMAND CENTER V2 - RESPONSABLE ACHATS
    Structure:
    A. Urgence (Bandeau)
    B. KPIs Décisionnels (Grille)
    C. Finance (Impact)
    D. Risques (Anticipation)
    E. Mini-Tendances
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
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #121212; }")
        
        content = QWidget()
        content.setStyleSheet("background-color: #121212;")
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(30, 20, 30, 30)
        self.layout.setSpacing(25)
        
        # ZONE A: URGENCES
        self.emergency_banner = QFrame()
        self.emergency_banner.setVisible(False)
        self.emergency_layout = QHBoxLayout(self.emergency_banner)
        self.emergency_layout.setContentsMargins(20, 15, 20, 15)
        self.layout.addWidget(self.emergency_banner)
        
        # ZONE B: KPIs DÉCISIONNELS
        lbl_kpi = QLabel("INDICATEURS CLÉS")
        lbl_kpi.setStyleSheet("color: #90A4AE; font-size: 10pt; font-weight: bold; letter-spacing: 1px;")
        self.layout.addWidget(lbl_kpi)
        
        self.kpi_grid = QGridLayout()
        self.kpi_grid.setSpacing(20)
        self.layout.addLayout(self.kpi_grid)
        
        # ZONE C & D: FINANCE & RISQUES
        lower_layout = QHBoxLayout()
        lower_layout.setSpacing(25)
        
        # Colonne Gauche: FINANCE (C) - Agrandissement
        finance_container = QWidget()
        fin_layout = QVBoxLayout(finance_container)
        fin_layout.setContentsMargins(0, 0, 0, 0)
        fin_layout.setSpacing(15)
        
        lbl_fin = QLabel("💰 IMPACT FINANCIER & BUDGET")
        lbl_fin.setStyleSheet("color: #90A4AE; font-size: 10pt; font-weight: bold; letter-spacing: 1px;")
        fin_layout.addWidget(lbl_fin)
        
        self.finance_card = QFrame()
        self.finance_card.setStyleSheet("""
            QFrame { background-color: #1E1E1E; border-radius: 12px; border: 1px solid #333; }
        """)
        self.fin_card_layout = QVBoxLayout(self.finance_card)
        self.fin_card_layout.setContentsMargins(25, 25, 25, 25)
        self.fin_card_layout.setSpacing(20)
        fin_layout.addWidget(self.finance_card)
        
        lower_layout.addWidget(finance_container, 5) # 50% width
        
        # Colonne Droite: RISQUES & ANTICIPATION (D)
        risk_container = QWidget()
        risk_layout = QVBoxLayout(risk_container)
        risk_layout.setContentsMargins(0, 0, 0, 0)
        risk_layout.setSpacing(15)
        
        lbl_risk = QLabel("🔮 ANTICIPATION (Produits proches de l'alerte)")
        lbl_risk.setStyleSheet("color: #90A4AE; font-size: 10pt; font-weight: bold; letter-spacing: 1px;")
        risk_layout.addWidget(lbl_risk)
        
        self.risk_list = QListWidget()
        self.risk_list.setStyleSheet("""
            QListWidget { background-color: #1E1E1E; border-radius: 12px; border: 1px solid #333; padding: 10px; }
            QListWidget::item { padding: 12px; border-bottom: 1px solid #333; }
            QListWidget::item:last { border-bottom: none; }
        """)
        risk_layout.addWidget(self.risk_list)
        
        lower_layout.addWidget(risk_container, 5) # 50% width
        
        self.layout.addLayout(lower_layout)
        self.layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def rafraichir(self):
        summary = Database.get_purchasing_dashboard_summary()
        if not summary: return
        
        # 1. UPDATE URGENCES
        urg = summary['urgences']
        total_urgences = urg['critical'] + urg['ruptures'] + urg['retards']
        
        if total_urgences > 0:
            self.emergency_banner.setVisible(True)
            self.emergency_banner.setStyleSheet("""
                QFrame { background-color: rgba(255, 23, 68, 0.15); border: 1px solid #FF1744; border-radius: 8px; }
            """)
            # Clear previous
            while self.emergency_layout.count():
                child = self.emergency_layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
                
            # Add Icon
            lbl_icon = QLabel("🚨")
            lbl_icon.setStyleSheet("font-size: 20pt; background: transparent; border: none;")
            self.emergency_layout.addWidget(lbl_icon)
            
            # Add Texts
            msg = ""
            if urg['critical']: msg += f"<b>{urg['critical']}</b> Alertes Critiques  •  "
            if urg['ruptures']: msg += f"<b>{urg['ruptures']}</b> Produits en Rupture  •  "
            if urg['retards']: msg += f"<b>{urg['retards']}</b> Commandes en Retard"
            
            lbl_msg = QLabel(msg)
            lbl_msg.setStyleSheet("color: #FF5252; font-size: 11pt; background: transparent; border: none;")
            self.emergency_layout.addWidget(lbl_msg)
            self.emergency_layout.addStretch()
        else:
            self.emergency_banner.setVisible(False)
            
        # 2. UPDATE KPIs
        kpis = summary['kpis']
        
        # Clear Grid
        while self.kpi_grid.count():
            item = self.kpi_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        items = [
            ("ALERTES ACTIVES", kpis['actives'], "⚡", "#2979FF"),
            ("TEMPS MOYEN TRAITEMENT", f"{kpis['avg_time']}h", "⏱️", "#00E676"),
            ("RÉACTIVITÉ <24H", f"{kpis['reactivity']}%", "🚀", "#FFD700"),
            ("COMMANDES EN COURS", f"{kpis['valeur_commandes_cours']:,.0f} FCFA", "📦", "#AB47BC")
        ]
        
        for i, (title, val, icon, color) in enumerate(items):
            self.kpi_grid.addWidget(self._create_kpi_card(title, str(val), icon, color), 0, i)
            
        # 3. UPDATE FINANCE (ENRICHIE)
        fin = summary['finance']
        # Clear
        while self.fin_card_layout.count():
            child = self.fin_card_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        # Budget Restant (Gros chiffre)
        reste = fin['budget'] - fin['depenses']
        lbl_reste_titre = QLabel("BUDGET RESTANT (Mois)")
        lbl_reste_titre.setStyleSheet("color: #90A4AE; font-size: 9pt; font-weight: bold;")
        self.fin_card_layout.addWidget(lbl_reste_titre)
        
        lbl_reste_val = QLabel(f"{reste:,.0f} FCFA")
        lbl_reste_val.setStyleSheet("color: #00E676; font-size: 28pt; font-weight: bold;")
        self.fin_card_layout.addWidget(lbl_reste_val)
        
        # Barre progression
        pct = min(100, (fin['depenses'] / fin['budget'] * 100)) if fin['budget'] else 0
        self.fin_card_layout.addWidget(self._create_progress_block("Consommation Budget", pct, fin['depenses'], fin['budget'], "#2979FF"))
        
        # Coût Urgences
        urg_cost = fin['cout_urgences']
        lbl_urg = QLabel(f"Dont Coût des Urgences : <span style='color:#FF5252; font-weight:bold'>{urg_cost:,.0f} FCFA</span>")
        lbl_urg.setStyleSheet("color: #E0E0E0; font-size: 11pt; margin-top: 10px;")
        self.fin_card_layout.addWidget(lbl_urg)
        
        self.fin_card_layout.addStretch()
        
        # 4. UPDATE RISQUES
        self.risk_list.clear()
        risks = summary['risques']
        if not risks:
            item = QListWidgetItem("Toutes les rotations sont saines. ✅")
            item.setForeground(QBrush(QColor("#00E676"))) # Vert
            self.risk_list.addItem(item)
        else:
            for r in risks:
                 nom = r.get('nom', 'Produit')
                 stock = r.get('stockactuel', 0)
                 seuil = r.get('stockalerte', 0)
                 
                 w = QWidget()
                 l = QHBoxLayout(w)
                 l.setContentsMargins(0, 0, 0, 0)
                 
                 # Icone Warning
                 lbl_warn = QLabel("⚠️")
                 l.addWidget(lbl_warn)
                 
                 # Info Produit
                 info_layout = QVBoxLayout()
                 lbl_nom = QLabel(f"{nom}")
                 lbl_nom.setStyleSheet("color: white; font-weight: bold; font-size: 10pt;")
                 lbl_detail = QLabel(f"Stock: {stock} (Seuil: {seuil})")
                 lbl_detail.setStyleSheet("color: #FF9800; font-size: 9pt;")
                 info_layout.addWidget(lbl_nom)
                 info_layout.addWidget(lbl_detail)
                 l.addLayout(info_layout)
                 
                 l.addStretch()
                 
                 # Action ? (Juste visuel pour le moment)
                 lbl_action = QLabel("À surveiller")
                 lbl_action.setStyleSheet("color: #757575; font-size: 8pt; font-style: italic;")
                 l.addWidget(lbl_action)
                 
                 item = QListWidgetItem(self.risk_list)
                 item.setSizeHint(w.sizeHint())
                 self.risk_list.setItemWidget(item, w)

    def _create_kpi_card(self, title, value, icon, color):
        card = QFrame()
        card.setFixedHeight(140)
        card.setStyleSheet(f"""
            QFrame {{ background-color: #1E1E1E; border-radius: 12px; border: 1px solid #333; }}
            QFrame:hover {{ border-color: {color}; }}
        """)
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 20, 20, 20)
        
        h = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 22pt; background: transparent; border: none;")
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #90A4AE; font-size: 8pt; font-weight: bold; background: transparent; border: none;")
        h.addWidget(lbl_icon)
        h.addStretch()
        l.addLayout(h)
        l.addWidget(lbl_title)
        
        val_lbl = QLabel(str(value)) # Convert to string to avoid TypeError
        val_lbl.setStyleSheet("color: white; font-size: 18pt; font-weight: bold; background: transparent; border: none;")
        l.addWidget(val_lbl)
        
        # Decorative bar
        bar = QFrame()
        bar.setFixedHeight(4)
        bar.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
        l.addWidget(bar)
        
        return card

    def _create_progress_block(self, title, pct, val, total, color):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0,0,0,0)
        
        h = QHBoxLayout()
        lbl = QLabel(title)
        lbl.setStyleSheet("color: #E0E0E0; font-weight: bold;")
        lbl_val = QLabel(f"{val:,.0f} / {total:,.0f} FCFA")
        lbl_val.setStyleSheet("color: #90A4AE;")
        h.addWidget(lbl)
        h.addStretch()
        h.addWidget(lbl_val)
        l.addLayout(h)
        
        prog = QProgressBar()
        prog.setRange(0, 100)
        prog.setValue(int(pct))
        prog.setFixedHeight(10)
        prog.setStyleSheet(f"""
            QProgressBar {{ border: none; background-color: #333; border-radius: 5px; }}
            QProgressBar::chunk {{ background-color: {color}; border-radius: 5px; }}
        """)
        l.addWidget(prog)
        return w
