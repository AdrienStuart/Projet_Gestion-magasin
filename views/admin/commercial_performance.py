"""
Performance Commerciale
Analyse CA par période/produit/caissier
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                               QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from db.database import Database


class CommercialPerformance(QWidget):
    """
    Écran Performance
    CA, Panier moyen, Top products, Top cashiers
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
        lbl = QLabel("ANALYSE COMMERCIALE (30 JOURS)")
        lbl.setStyleSheet("color: #8B949E; font-size: 13pt; letter-spacing: 2px; font-weight: bold;")
        layout.addWidget(lbl)
        
        # Top Products
        frame_prod = self._create_section("📦 TOP 10 PRODUITS PAR CA", "#58A6FF")
        self.table_products = self._create_table(["Produit", "Qté Vendue", "CA (FCFA)"])
        frame_prod.layout().addWidget(self.table_products)
        layout.addWidget(frame_prod)
        
        # Performance Caissiers
        frame_cash = self._create_section("👤 PERFORMANCE PAR CAISSIER", "#2EA043")
        self.table_cashiers = self._create_table(["Caissier", "Nb Ventes", "CA (FCFA)", "Panier Moyen"])
        frame_cash.layout().addWidget(self.table_cashiers)
        layout.addWidget(frame_cash)
    
    def _create_section(self, title, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #161B22;
                border: 1px solid #30363D;
                border-left: 4px solid {color};
                border-radius: 8px;
            }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(20, 15, 20, 15)
        
        lbl = QLabel(title)
        lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11pt;")
        lay.addWidget(lbl)
        
        return frame
    
    def _create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet("""
            QTableWidget {
                background-color: transparent; gridline-color: #30363D;
                border: none; color: #C9D1D9; font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #21262D; color: #8B949E;
                padding: 8px; border: none; font-weight: bold;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #30363D; }
            QTableWidget::item:selected { background-color: #1F6FEB; color: white; }
        """)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        return table
    
    def rafraichir(self):
        # Products
        products = Database.get_sales_by_product(limit=10)
        self.table_products.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table_products.setItem(row, 0, QTableWidgetItem(p['produit']))
            self.table_products.setItem(row, 1, QTableWidgetItem(str(p['qty_vendue'])))
            self.table_products.setItem(row, 2, QTableWidgetItem(f"{p['ca']:,.0f}".replace(',', ' ')))
        
        # Cashiers
        cashiers = Database.get_sales_by_cashier()
        self.table_cashiers.setRowCount(len(cashiers))
        for row, c in enumerate(cashiers):
            self.table_cashiers.setItem(row, 0, QTableWidgetItem(c['caissier']))
            self.table_cashiers.setItem(row, 1, QTableWidgetItem(str(c['nb_ventes'])))
            self.table_cashiers.setItem(row, 2, QTableWidgetItem(f"{c['ca']:,.0f}".replace(',', ' ')))
            self.table_cashiers.setItem(row, 3, QTableWidgetItem(f"{c['panier_moyen']:,.0f}".replace(',', ' ')))
