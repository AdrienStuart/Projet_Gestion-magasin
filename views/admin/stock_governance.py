"""
Pilotage des Stocks
Corrélations, produits dormants, ruptures récurrentes
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                               QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from db.database import Database


class StockGovernance(QWidget):
    """
    Pilotage Stocks
    Corrélation alertes/commandes, dormants, surstocks
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.rafraichir()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)
        
        # KPI Global
        self.kpi_value = QLabel("VALEUR STOCK: 0 FCFA")
        self.kpi_value.setStyleSheet("""
            color: #A371F7; font-size: 16pt; font-weight: bold;
            background-color: #161B22; padding: 15px; border-radius: 8px;
            border: 1px solid #30363D; border-left: 4px solid #A371F7;
        """)
        layout.addWidget(self.kpi_value)
        
        # Problèmes
        problems_layout = QHBoxLayout()
        problems_layout.setSpacing(20)
        
        # Dormants
        frame_dorm = self._create_section("💤 PRODUITS DORMANTS", "#9E6A03")
        self.table_dormant = self._create_table(["Produit", "Stock", "Valeur Immobilisée"])
        frame_dorm.layout().addWidget(self.table_dormant)
        problems_layout.addWidget(frame_dorm)
        
        # Ruptures récurrentes
        frame_rupt = self._create_section("🔁 RUPTURES RÉCURRENTES", "#F85149")
        self.table_ruptures = self._create_table(["Produit", "Nb Ruptures (90j)"])
        frame_rupt.layout().addWidget(self.table_ruptures)
        problems_layout.addWidget(frame_rupt)
        
        layout.addLayout(problems_layout)
        
        # Surstocks
        frame_over = self._create_section("📦 SURSTOCKS (>3x Seuil)", "#FF7B72")
        self.table_overstock = self._create_table(["Produit", "Stock", "Seuil", "Valeur"])
        frame_over.layout().addWidget(self.table_overstock)
        layout.addWidget(frame_over)
    
    def _create_section(self, title, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #161B22; border: 1px solid #30363D;
                border-left: 4px solid {color}; border-radius: 8px;
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
        """)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setMaximumHeight(200)
        return table
    
    def rafraichir(self):
        analysis = Database.get_stock_analysis()
        if not analysis: return
        
        # KPI
        self.kpi_value.setText(f"VALEUR STOCK: {analysis['total_value']:,.0f} FCFA".replace(',', ' '))
        
        # Dormants
        dorm = analysis['dormant_products'][:10]
        self.table_dormant.setRowCount(len(dorm))
        for row, d in enumerate(dorm):
            self.table_dormant.setItem(row, 0, QTableWidgetItem(d['nom']))
            self.table_dormant.setItem(row, 1, QTableWidgetItem(str(d['stockactuel'])))
            val_item = QTableWidgetItem(f"{d['valeur_immobilisee']:,.0f} FCFA".replace(',', ' '))
            val_item.setForeground(QBrush(QColor("#F85149")))
            self.table_dormant.setItem(row, 2, val_item)
        
        # Ruptures récurrentes
        rupt = analysis['recurring_stockouts']
        self.table_ruptures.setRowCount(len(rupt))
        for row, r in enumerate(rupt):
            self.table_ruptures.setItem(row, 0, QTableWidgetItem(r['nom']))
            self.table_ruptures.setItem(row, 1, QTableWidgetItem(str(r['nb_ruptures'])))
        
        # Surstocks
        over = analysis['overstocked'][:10]
        self.table_overstock.setRowCount(len(over))
        for row, o in enumerate(over):
            self.table_overstock.setItem(row, 0, QTableWidgetItem(o['nom']))
            self.table_overstock.setItem(row, 1, QTableWidgetItem(str(o['stockactuel'])))
            self.table_overstock.setItem(row, 2, QTableWidgetItem(str(o['stockalerte'])))
            self.table_overstock.setItem(row, 3, QTableWidgetItem(f"{o['valeur']:,.0f} FCFA".replace(',', ' ')))
