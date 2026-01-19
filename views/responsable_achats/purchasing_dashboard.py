import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from db.database import Database

class PurchasingDashboard(QWidget):
    """
    DASHBOARD D'ARBITRAGE - RESPONSABLE ACHATS
    Objectif: Répondre à 'Y a-t-il le feu ?' en 10 secondes.
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.rafraichir() # Charger les données
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Titre section
        lbl_titre = QLabel("ÉTAT DES BESOINS")
        lbl_titre.setStyleSheet("color: #90A4AE; font-size: 14pt; letter-spacing: 2px;")
        layout.addWidget(lbl_titre)
        
        # Grille de KPIs
        grid = QGridLayout()
        grid.setSpacing(25)
        
        # KPI 1: Alertes Critiques (Le plus important)
        self.card_critical = self._create_kpi_card("ALERTES CRITIQUES", "0", "#FF1744", "🔥")
        grid.addWidget(self.card_critical, 0, 0)
        
        # KPI 2: Total Actives (Charge de travail)
        self.card_active = self._create_kpi_card("ALERTES ACTIVES", "0", "#2979FF", "⚡")
        grid.addWidget(self.card_active, 0, 1)
        
        # KPI 3: Valeur Estimée (Budget)
        self.card_value = self._create_kpi_card("VALEUR ESTIMÉE", "0 €", "#00E676", "💰")
        grid.addWidget(self.card_value, 1, 0)
        
        # KPI 4: Commandes en retard (Problèmes)
        self.card_late = self._create_kpi_card("COMMANDES RETARD", "0", "#FF9100", "⚠️")
        grid.addWidget(self.card_late, 1, 1)
        
        layout.addLayout(grid)
        layout.addStretch() # Pousse tout vers le haut
        
    def _create_kpi_card(self, title, value, color, icon):
        card = QFrame()
        card.setFixedHeight(180)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1E1E1E;
                border: 1px solid #333;
                border-left: 5px solid {color};
                border-radius: 8px;
            }}
            QFrame:hover {{ background-color: #262626; border: 1px solid {color}; }}
        """)
        
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 20, 20, 20)
        
        # Header
        h_lay = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 24pt; background: transparent; border: none;")
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11pt; letter-spacing: 1px; background: transparent; border: none;")
        
        h_lay.addWidget(lbl_icon)
        h_lay.addWidget(lbl_title)
        h_lay.addStretch()
        l.addLayout(h_lay)
        
        l.addStretch()
        
        # Value
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet("font-size: 42pt; font-weight: bold; color: white; background: transparent; border: none;")
        lbl_val.setAlignment(Qt.AlignRight)
        l.addWidget(lbl_val)
        
        card.lbl_val = lbl_val
        return card

    def rafraichir(self):
        """Récupère les stats DB et met à jour l'UI"""
        stats = Database.get_purchasing_dashboard_stats()
        if not stats: return
        
        self.card_critical.lbl_val.setText(str(stats.get('critical', 0)))
        self.card_active.lbl_val.setText(str(stats.get('total_active', 0)))
        
        val_needed = stats.get('value_needed', 0)
        self.card_value.lbl_val.setText(f"{val_needed:,.0f} €".replace(',', ' '))
        
        self.card_late.lbl_val.setText(str(stats.get('late_orders', 0)))
