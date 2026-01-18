"""
Écran Alertes Stock
Affiche les ruptures et stock critique
Intelligent, pas gadget
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QPushButton, QHeaderView,
                               QAbstractItemView, QFrame, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from datetime import datetime

from db.database import Database


class AlertsScreen(QWidget):
    """
    Écran des alertes de stock (Vue Classique)
    Affiche les ruptures et stock critique calculés en temps réel.
    """
    
    def __init__(self, id_utilisateur: int):
        super().__init__()
        self.id_utilisateur = id_utilisateur
        self.setup_ui()
        self.charger_alertes()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        self._creer_section_ruptures(layout)
        self._creer_section_critique(layout)
        self._creer_actions(layout)
    
    def _creer_section_ruptures(self, parent_layout):
        group = QGroupBox("❌ PRODUITS EN RUPTURE (Stock = 0)")
        group.setStyleSheet("""
            QGroupBox { font-size: 13pt; font-weight: bold; color: #D32F2F; border: 2px solid #EF9A9A; border-radius: 8px; margin-top: 15px; padding-top: 25px; background-color: #FAFAFA; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 8px; background-color: #FFEBEE; border: 1px solid #EF9A9A; border-radius: 4px; }
        """)
        lay = QVBoxLayout(group)
        
        self.table_ruptures = QTableWidget()
        self.table_ruptures.setColumnCount(4)
        self.table_ruptures.setHorizontalHeaderLabels(["Produit", "Catégorie", "Seuil", "Jours en rupture"])
        self.table_ruptures.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_ruptures.verticalHeader().setVisible(False)
        self.table_ruptures.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_ruptures.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_ruptures.setMaximumHeight(250)
        self.table_ruptures.setStyleSheet("QHeaderView::section { background-color: #2A2A40; color: white; font-weight: bold; }")
        
        lay.addWidget(self.table_ruptures)
        parent_layout.addWidget(group)

    def _creer_section_critique(self, parent_layout):
        group = QGroupBox("⚠️ STOCK CRITIQUE (Stock ≤ Seuil)")
        group.setStyleSheet("""
            QGroupBox { font-size: 13pt; font-weight: bold; color: #E65100; border: 2px solid #FFCC80; border-radius: 8px; margin-top: 15px; padding-top: 25px; background-color: #FAFAFA; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 8px; background-color: #FFF3E0; border: 1px solid #FFCC80; border-radius: 4px; }
        """)
        lay = QVBoxLayout(group)
        
        self.table_critique = QTableWidget()
        self.table_critique.setColumnCount(5)
        self.table_critique.setHorizontalHeaderLabels(["Produit", "Catégorie", "Stock Actuel", "Seuil", "Manquant"])
        self.table_critique.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_critique.verticalHeader().setVisible(False)
        self.table_critique.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_critique.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_critique.setStyleSheet("QHeaderView::section { background-color: #2A2A40; color: white; font-weight: bold; }")
        
        lay.addWidget(self.table_critique)
        parent_layout.addWidget(group)

    def _creer_actions(self, parent_layout):
        lay = QHBoxLayout()
        lay.addWidget(QLabel("💡 Astuce: Ces tableaux reflètent l'état actuel du stock."))
        lay.addStretch()
        btn = QPushButton("📋 Liste Réappro (Calculée)")
        btn.clicked.connect(self.generer_liste_reappro)
        btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        lay.addWidget(btn)
        parent_layout.addLayout(lay)

    def charger_alertes(self):
        # Utilise l'ancienne méthode basée sur les seuils actuels
        alertes = Database.get_stock_alerts()
        ruptures = [a for a in alertes if a.get('stockactuel', 0) == 0]
        critiques = [a for a in alertes if a.get('stockactuel', 0) > 0]
        
        self._remplir_table(self.table_ruptures, ruptures, is_rupture=True)
        self._remplir_table(self.table_critique, critiques, is_rupture=False)

    def _remplir_table(self, table, data, is_rupture):
        table.setRowCount(0)
        for row, item in enumerate(data):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(item['nom']))
            table.setItem(row, 1, QTableWidgetItem(item['categorie']))
            if is_rupture:
                table.setItem(row, 2, QTableWidgetItem(str(item['stockalerte'])))
                table.setItem(row, 3, QTableWidgetItem(f"{item.get('jours_rupture',0)} jours"))
            else:
                table.setItem(row, 2, QTableWidgetItem(str(item['stockactuel'])))
                table.setItem(row, 3, QTableWidgetItem(str(item['stockalerte'])))
                manquant = max(0, item['stockalerte'] - item['stockactuel'])
                table.setItem(row, 4, QTableWidgetItem(str(manquant)))

    def generer_liste_reappro(self):
        # ... (Garder le code existant ou similaire)
        pass

    def rafraichir(self):
        self.charger_alertes()
