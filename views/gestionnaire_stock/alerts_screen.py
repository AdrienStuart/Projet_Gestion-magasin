"""
Écran Alertes Stock
Affiche les ruptures et stock critique
Intelligent, pas gadget
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QPushButton, QHeaderView,
                               QAbstractItemView, QFrame, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from datetime import datetime

from db.database import Database


class AlertsScreen(QWidget):
    """
    Écran des alertes de stock
    2 tables séparées: Ruptures + Stock Critique
    """
    
    def __init__(self, id_utilisateur: int):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        self.setup_ui()
        self.charger_alertes()
    
    def setup_ui(self):
        """Construction de l'interface"""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)
        
        # Section Ruptures
        self._creer_section_ruptures(layout_principal)
        
        # Section Stock Critique
        self._creer_section_critique(layout_principal)
        
        # Bouton Produitsà réapprovisionner
        self._creer_actions(layout_principal)
    
    def _creer_section_ruptures(self, parent_layout):
        """Section des ruptures de stock"""
        group_ruptures = QGroupBox("❌ PRODUITS EN RUPTURE (Stock = 0)")
        group_ruptures.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                color: #F44336;
                border: 3px solid #F44336;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #FFEBEE;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                background-color: white;
            }
        """)
        
        layout_ruptures = QVBoxLayout(group_ruptures)
        
        # Table ruptures
        self.table_ruptures = QTableWidget()
        self.table_ruptures.setColumnCount(4)
        self.table_ruptures.setHorizontalHeaderLabels([
            "Produit", "Catégorie", "Seuil", "Jours en rupture"
        ])
        
        # Configuration
        # Configuration
        header = self.table_ruptures.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)           # Produit (Stretch naturel)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Catégorie
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Seuil
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Jours
        
        self.table_ruptures.verticalHeader().setVisible(False)
        self.table_ruptures.verticalHeader().setDefaultSectionSize(50) # Hauteur augmentée
        self.table_ruptures.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_ruptures.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_ruptures.setMaximumHeight(300) # Un peu plus haut
        
        self.table_ruptures.setStyleSheet("""
            QTableWidget {
                font-size: 13pt; /* Police plus grande */
                background-color: white;
                gridline-color: #E0E0E0;
                border: 1px solid #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px 10px;
            }
            QTableWidget::item:selected {
                background-color: #FFEBEE;
                color: #C62828;
            }
            QHeaderView::section {
                background-color: #FFEBEE;
                color: #C62828;
                padding: 10px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #EF9A9A;
            }
        """)
        
        layout_ruptures.addWidget(self.table_ruptures)
        
        parent_layout.addWidget(group_ruptures)
    
    def _creer_section_critique(self, parent_layout):
        """Section du stock critique"""
        group_critique = QGroupBox("⚠️ STOCK CRITIQUE (Stock ≤ Seuil)")
        group_critique.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                color: #FF9800;
                border: 3px solid #FF9800;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #FFF3E0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                background-color: white;
            }
        """)
        
        layout_critique = QVBoxLayout(group_critique)
        
        # Table critique
        self.table_critique = QTableWidget()
        self.table_critique.setColumnCount(5)
        self.table_critique.setHorizontalHeaderLabels([
            "Produit", "Catégorie", "Stock Actuel", "Seuil", "Manquant"
        ])
        
        # Configuration
        header = self.table_critique.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)           # Produit (Natural stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Catégorie
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Stock
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Seuil
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Manquant
        
        self.table_critique.verticalHeader().setVisible(False)
        self.table_critique.verticalHeader().setDefaultSectionSize(50) # Hauteur augmentée
        self.table_critique.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_critique.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.table_critique.setStyleSheet("""
            QTableWidget {
                font-size: 13pt; /* Police plus grande */
                background-color: white;
                gridline-color: #E0E0E0;
                border: 1px solid #E0E0E0;
            }
            QTableWidget::item {
                padding: 5px 10px;
            }
            QTableWidget::item:selected {
                background-color: #FFF3E0;
                color: #EF6C00;
            }
            QHeaderView::section {
                background-color: #FFF3E0;
                color: #EF6C00;
                padding: 10px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #FFB74D;
            }
        """)
        
        layout_critique.addWidget(self.table_critique)
        
        parent_layout.addWidget(group_critique, stretch=1)
    
    def _creer_actions(self, parent_layout):
        """Boutons d'actions"""
        layout_actions = QHBoxLayout()
        
        # Info
        lbl_info = QLabel("💡 Astuce: Cliquez sur un produit puis allez dans Mouvements pour créer une entrée")
        lbl_info.setStyleSheet("color: #757575; font-size: 10pt; font-style: italic;")
        layout_actions.addWidget(lbl_info)
        
        layout_actions.addStretch()
        
        # Bouton liste réapprovisionnement
        btn_reappro = QPushButton("📋 Liste de Réapprovisionnement")
        btn_reappro.setFixedHeight(45)
        btn_reappro.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 25px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
        """)
        btn_reappro.clicked.connect(self.generer_liste_reappro)
        layout_actions.addWidget(btn_reappro)
        
        parent_layout.addLayout(layout_actions)
    
    # ========== LOGIQUE ==========
    
    def charger_alertes(self):
        """Charge les alertes depuis la base"""
        alertes = Database.get_stock_alerts()
        
        # Séparer ruptures et critiques
        ruptures = [a for a in alertes if a.get('stockactuel', 0) == 0]
        critiques = [a for a in alertes if a.get('stockactuel', 0) > 0]
        
        self.afficher_ruptures(ruptures)
        self.afficher_critiques(critiques)
    
    def afficher_ruptures(self, ruptures):
        """Affiche les produits en rupture"""
        self.table_ruptures.setRowCount(0)
        
        if not ruptures:
            # Message si aucune rupture
            row = self.table_ruptures.rowCount()
            self.table_ruptures.insertRow(row)
            item = QTableWidgetItem("✅ Aucun produit en rupture")
            item.setForeground(QColor("#00C853"))
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            self.table_ruptures.setItem(row, 0, item)
            self.table_ruptures.setSpan(row, 0, 1, 4)
            return
        
        for produit in ruptures:
            row = self.table_ruptures.rowCount()
            self.table_ruptures.insertRow(row)
            
            # Produit
            self.table_ruptures.setItem(row, 0, QTableWidgetItem(produit['nom']))
            
            # Catégorie
            self.table_ruptures.setItem(row, 1, QTableWidgetItem(produit.get('categorie', 'N/A')))
            
            # Seuil
            seuil = produit.get('stockalerte', 0)
            item_seuil = QTableWidgetItem(str(seuil))
            item_seuil.setTextAlignment(Qt.AlignCenter)
            self.table_ruptures.setItem(row, 2, item_seuil)
            
            # Jours en rupture (estimation)
            jours = produit.get('jours_rupture', 0) or 0
            item_jours = QTableWidgetItem(f"{jours} jours" if jours else "Récent")
            item_jours.setTextAlignment(Qt.AlignCenter)
            font = QFont()
            font.setBold(True)
            item_jours.setFont(font)
            self.table_ruptures.setItem(row, 3, item_jours)
    
    def afficher_critiques(self, critiques):
        """Affiche les produits en stock critique"""
        self.table_critique.setRowCount(0)
        
        if not critiques:
            # Message si tout va bien
            row = self.table_critique.rowCount()
            self.table_critique.insertRow(row)
            item = QTableWidgetItem("✅ Tous les stocks sont au-dessus du seuil")
            item.setForeground(QColor("#00C853"))
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            self.table_critique.setItem(row, 0, item)
            self.table_critique.setSpan(row, 0, 1, 5)
            return
        
        for produit in critiques:
            row = self.table_critique.rowCount()
            self.table_critique.insertRow(row)
            
            # Produit
            self.table_critique.setItem(row, 0, QTableWidgetItem(produit['nom']))
            
            # Catégorie
            self.table_critique.setItem(row, 1, QTableWidgetItem(produit.get('categorie', 'N/A')))
            
            # Stock actuel
            stock = produit.get('stockactuel', 0)
            item_stock = QTableWidgetItem(str(stock))
            item_stock.setTextAlignment(Qt.AlignCenter)
            font = QFont()
            font.setBold(True)
            item_stock.setFont(font)
            self.table_critique.setItem(row, 2, item_stock)
            
            # Seuil
            seuil = produit.get('stockalerte', 0)
            item_seuil = QTableWidgetItem(str(seuil))
            item_seuil.setTextAlignment(Qt.AlignCenter)
            self.table_critique.setItem(row, 3, item_seuil)
            
            # Manquant
            manquant = max(0, seuil - stock)
            item_manquant = QTableWidgetItem(f"≈ {manquant}")
            item_manquant.setTextAlignment(Qt.AlignCenter)
            item_manquant.setForeground(QColor("#F44336"))
            item_manquant.setFont(font)
            self.table_critique.setItem(row, 4, item_manquant)
    
    def generer_liste_reappro(self):
        """Génère une liste de réapprovisionnement (futur module Achats)"""
        from PySide6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox
        
        # Récupérer produits à réapprovisionner
        produits = Database.get_products_to_restock()
        
        # Créer dialogue
        dialog = QDialog(self)
        dialog.setWindowTitle("Liste de Réapprovisionnement")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        lbl_titre = QLabel("📋 Produits à commander:")
        lbl_titre.setStyleSheet("font-size: 13pt; font-weight: bold;")
        layout.addWidget(lbl_titre)
        
        text_liste = QTextEdit()
        text_liste.setReadOnly(True)
        
        if not produits:
            text_liste.setPlainText("✅ Aucun produit nécessite un réapprovisionnement.")
        else:
            contenu = "LISTE DE RÉAPPROVISIONNEMENT\n"
            contenu += "=" * 50 + "\n\n"
            for p in produits:
                nom = p.get('nom', '')
                stock = p.get('stockactuel', 0)
                seuil = p.get('stockalerte', 0)
                suggere = max(seuil * 2 - stock, seuil)  # Quantité suggérée
                contenu += f"• {nom}\n"
                contenu += f"  Stock: {stock} | Seuil: {seuil} | Suggéré: {suggere}\n\n"
            
            text_liste.setPlainText(contenu)
        
        text_liste.setStyleSheet("font-size: 11pt; font-family: monospace;")
        layout.addWidget(text_liste)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dialog.accept)
        layout.addWidget(btns)
        
        dialog.exec()
    
    def rafraichir(self):
        """Rafraîchit les alertes"""
        self.charger_alertes()
