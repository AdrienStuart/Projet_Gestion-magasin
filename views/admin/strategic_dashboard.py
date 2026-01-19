"""
Dashboard Stratégique
L'admin comprend l'état global en <10s
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout)
from PySide6.QtCore import Qt
from db.database import Database


class StrategicDashboard(QWidget):
    """
    Dashboard exécutif
    Vue immédiate: CA, Marge, Top produits, Alertes, Stock
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.rafraichir()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)
        
        # Titre
        lbl =QLabel("VUE EXÉCUTIVE")
        lbl.setStyleSheet("color: #8B949E; font-size: 13pt; letter-spacing: 2px; font-weight: bold;")
        layout.addWidget(lbl)
        
        # Grille KPIs (3x3)
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Ligne 1: CA
        self.kpi_today = self._create_kpi("CA AUJOURD'HUI", "0 FCFA", "#2EA043")
        self.kpi_month = self._create_kpi("CA MOIS", "0 FCFA", "#58A6FF")
        self.kpi_year = self._create_kpi("CA ANNÉE", "0 FCFA", "#9E6A03")
        
        grid.addWidget(self.kpi_today, 0, 0)
        grid.addWidget(self.kpi_month, 0, 1)
        grid.addWidget(self.kpi_year, 0, 2)
        
        # Ligne 2: Indicateurs
        self.kpi_marge = self._create_kpi("MARGE BRUTE", "0 FCFA", "#BC4C00")
        self.kpi_alerts = self._create_kpi("ALERTES CRITIQUES", "0", "#F85149")
        self.kpi_stock = self._create_kpi("VALEUR STOCK", "0 FCFA", "#A371F7")
        
        grid.addWidget(self.kpi_marge, 1, 0)
        grid.addWidget(self.kpi_alerts, 1, 1)
        grid.addWidget(self.kpi_stock, 1, 2)
        
        layout.addLayout(grid)
        
        # Section produits
        prod_layout = QHBoxLayout()
        prod_layout.setSpacing(20)
        
        # Top produits
        top_frame = QFrame()
        top_frame.setStyleSheet("background-color: #161B22; border: 1px solid #30363D; border-radius: 8px;")
        top_lay = QVBoxLayout(top_frame)
        top_lay.setContentsMargins(20, 15, 20, 15)
        
        lbl_top = QLabel("🔥 TOP 5 PRODUITS (Mois)")
        lbl_top.setStyleSheet("color: #58A6FF; font-weight: bold; font-size: 11pt;")
        top_lay.addWidget(lbl_top)
        
        self.lbl_top_products = QLabel("Chargement...")
        self.lbl_top_products.setStyleSheet("color: #C9D1D9; font-size: 10pt; margin-top: 10px;")
        self.lbl_top_products.setWordWrap(True)
        top_lay.addWidget(self.lbl_top_products)
        
        prod_layout.addWidget(top_frame)
        
        # Faible rotation
        low_frame = QFrame()
        low_frame.setStyleSheet("background-color: #161B22; border: 1px solid #30363D; border-radius: 8px;")
        low_lay = QVBoxLayout(low_frame)
        low_lay.setContentsMargins(20, 15, 20, 15)
        
        lbl_low = QLabel("⚠️ FAIBLE ROTATION (30j)")
        lbl_low.setStyleSheet("color: #F85149; font-weight: bold; font-size: 11pt;")
        low_lay.addWidget(lbl_low)
        
        self.lbl_low_rotation = QLabel("Chargement...")
        self.lbl_low_rotation.setStyleSheet("color: #C9D1D9; font-size: 10pt; margin-top: 10px;")
        self.lbl_low_rotation.setWordWrap(True)
        low_lay.addWidget(self.lbl_low_rotation)
        
        prod_layout.addWidget(low_frame)
        
        layout.addLayout(prod_layout)
        layout.addStretch()
    
    def _create_kpi(self, title, value, color):
        card = QFrame()
        card.setFixedHeight(140)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #161B22;
                border: 1px solid #30363D;
                border-left: 4px solid {color};
                border-radius: 8px;
            }}
            QFrame:hover {{ background-color: #1C2128; }}
        """)
        
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 15, 20, 15)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 10pt; letter-spacing: 1px;")
        l.addWidget(lbl_title)
        
        l.addStretch()
        
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet("font-size: 32pt; font-weight: bold; color: #E6EDF3;")
        lbl_val.setAlignment(Qt.AlignRight)
        l.addWidget(lbl_val)
        
        card.lbl_val = lbl_val
        return card
    
    def rafraichir(self):
        """Récupère les KPIs depuis la DB"""
        kpis = Database.get_admin_dashboard_kpis()
        
        if not kpis:
            return
        
        # Update CA
        self.kpi_today.lbl_val.setText(f"{kpis['ca_today']:,.0f}".replace(',', ' '))
        self.kpi_month.lbl_val.setText(f"{kpis['ca_month']:,.0f}".replace(',', ' '))
        self.kpi_year.lbl_val.setText(f"{kpis['ca_year']:,.0f}".replace(',', ' '))
        
        # Update autres
        self.kpi_marge.lbl_val.setText(f"{kpis['marge_brute']:,.0f}".replace(',', ' '))
        self.kpi_alerts.lbl_val.setText(str(kpis['critical_alerts']))
        self.kpi_stock.lbl_val.setText(f"{kpis['stock_value']:,.0f}".replace(',', ' '))
        
        # Top products
        top_text = "\n".join([f"{i+1}. {p['nom']} ({p['qty']} unités)" 
                              for i, p in enumerate(kpis['top_products'])])
        self.lbl_top_products.setText(top_text or "Aucune vente ce mois")
        
        # Low rotation
        low_text = "\n".join([f"• {p['nom']} (Stock: {p['stockactuel']})" 
                              for p in kpis['low_rotation'][:5]])
        self.lbl_low_rotation.setText(low_text or "Aucun produit immobilisé")
