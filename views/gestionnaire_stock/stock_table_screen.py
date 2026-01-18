"""
Écran Tableau de Stock
Liste dense et claire des produits avec statuts
Filtres: Catégorie, Stock critique, Recherche texte
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QLineEdit, QComboBox, QCheckBox,
                               QLabel, QHeaderView, QAbstractItemView, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import qtawesome as qta

from db.database import Database


class StockTableScreen(QWidget):
    """
    Écran principal du gestionnaire stock
    Table claire avec statuts coloriés et filtres
    """
    
    def __init__(self, id_utilisateur: int):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        """Construction de l'interface"""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)
        
        # Zone de filtres
        self._creer_zone_filtres(layout_principal)
        
        # Table de stock
        self._creer_table_stock(layout_principal)
        
        # Légende des statuts
        self._creer_legende(layout_principal)
    
    def _creer_zone_filtres(self, parent_layout):
        """Barre de filtres"""
        frame_filtres = QFrame()
        frame_filtres.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout_filtres = QHBoxLayout(frame_filtres)
        
        # Recherche texte
        lbl_recherche = QLabel("🔍 Recherche:")
        lbl_recherche.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout_filtres.addWidget(lbl_recherche)
        
        self.input_recherche = QLineEdit()
        self.input_recherche.setPlaceholderText("Nom du produit...")
        self.input_recherche.setFixedWidth(250)
        self.input_recherche.textChanged.connect(self.appliquer_filtres)
        self.input_recherche.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border-color: #00C853;
            }
        """)
        layout_filtres.addWidget(self.input_recherche)
        
        layout_filtres.addSpacing(20)
        
        # Filtre catégorie
        lbl_categorie = QLabel("📂 Catégorie:")
        lbl_categorie.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout_filtres.addWidget(lbl_categorie)
        
        self.combo_categorie = QComboBox()
        self.combo_categorie.setFixedWidth(180)
        self.combo_categorie.currentIndexChanged.connect(self.appliquer_filtres)
        self.combo_categorie.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 11pt;
            }
        """)
        layout_filtres.addWidget(self.combo_categorie)
        
        layout_filtres.addSpacing(20)
        
        # Checkbox stock critique
        self.check_critique = QCheckBox("⚠️ Stock critique seulement")
        self.check_critique.stateChanged.connect(self.appliquer_filtres)
        self.check_critique.setStyleSheet("""
            QCheckBox {
                font-size: 11pt;
                font-weight: bold;
            }
        """)
        layout_filtres.addWidget(self.check_critique)
        
        layout_filtres.addStretch()
        
        parent_layout.addWidget(frame_filtres)
    
    def _creer_table_stock(self, parent_layout):
        """Table principale des produits"""
        self.table_stock = QTableWidget()
        self.table_stock.setColumnCount(6)
        self.table_stock.setHorizontalHeaderLabels([
            "Code", "Produit", "Catégorie", "Stock", "Seuil", "Statut"
        ])
        
        # Configuration
        header = self.table_stock.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Code
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Produit
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Catégorie
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Stock
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Seuil
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Statut
        
        self.table_stock.verticalHeader().setVisible(False)
        self.table_stock.verticalHeader().setDefaultSectionSize(45)
        self.table_stock.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_stock.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_stock.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_stock.setAlternatingRowColors(True)
        
        self.table_stock.setStyleSheet("""
            QTableWidget {
                font-size: 12pt;
                alternate-background-color: #F9F9F9;
                background-color: white;
                gridline-color: #E0E0E0;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #37474F;
                color: white;
                padding: 10px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
        """)
        
        # Double-clic pour historique (futur)
        self.table_stock.doubleClicked.connect(self.voir_historique_produit)
        
        parent_layout.addWidget(self.table_stock, stretch=1)
    
    def _creer_legende(self, parent_layout):
        """Légende des couleurs de statut"""
        frame_legende = QFrame()
        frame_legende.setStyleSheet("background-color: #F5F5F5; padding: 10px; border-radius: 6px;")
        
        layout_legende = QHBoxLayout(frame_legende)
        
        lbl_titre = QLabel("Légende:")
        lbl_titre.setStyleSheet("font-weight: bold; font-size: 10pt;")
        layout_legende.addWidget(lbl_titre)
        
        # OK (Vert)
        lbl_ok = QLabel("● OK (Stock suffisant)")
        lbl_ok.setStyleSheet("color: #00C853; font-size: 10pt; font-weight: bold;")
        layout_legende.addWidget(lbl_ok)
        
        # Critique (Orange)
        lbl_critique = QLabel("● Critique (Stock ≤ Seuil)")
        lbl_critique.setStyleSheet("color: #FF9800; font-size: 10pt; font-weight: bold;")
        layout_legende.addWidget(lbl_critique)
        
        # Rupture (Rouge)
        lbl_rupture = QLabel("● Rupture (Stock = 0)")
        lbl_rupture.setStyleSheet("color: #F44336; font-size: 10pt; font-weight: bold;")
        layout_legende.addWidget(lbl_rupture)
        
        layout_legende.addStretch()
        
        parent_layout.addWidget(frame_legende)
    
    # ========== LOGIQUE ==========
    
    def charger_donnees(self):
        """Charge les données depuis la base"""
        # Charger catégories pour le filtre
        categories = Database.get_all_categories()
        self.combo_categorie.clear()
        self.combo_categorie.addItem("Toutes", None)
        for cat in categories:
            self.combo_categorie.addItem(cat['libelle'], cat['id_categorie'])
        
        # Charger stock
        self.stock_complet = Database.get_stock_overview()
        self.appliquer_filtres()
    
    def appliquer_filtres(self):
        """Applique les filtres à la table"""
        texte_recherche = self.input_recherche.text().lower()
        categorie_selectionnee = self.combo_categorie.currentData()
        critique_seulement = self.check_critique.isChecked()
        
        # Filtrer les données
        donnees_filtrees = []
        for produit in self.stock_complet:
            # Filtre recherche
            if texte_recherche and texte_recherche not in produit['nom'].lower():
                continue
            
            # Filtre catégorie
            if categorie_selectionnee and produit['id_categorie'] != categorie_selectionnee:
                continue
            
            # Filtre critique
            stock = produit['stockactuel']
            seuil = produit['stockalerte']
            if critique_seulement and stock > seuil:
                continue
            
            donnees_filtrees.append(produit)
        
        # Remplir la table
        self.afficher_donnees(donnees_filtrees)
    
    def afficher_donnees(self, donnees):
        """Affiche les données dans la table"""
        self.table_stock.setRowCount(0)
        
        for produit in donnees:
            row = self.table_stock.rowCount()
            self.table_stock.insertRow(row)
            
            # Code
            self.table_stock.setItem(row, 0, QTableWidgetItem(str(produit['id_produit'])))
            
            # Nom
            self.table_stock.setItem(row, 1, QTableWidgetItem(produit['nom']))
            
            # Catégorie
            self.table_stock.setItem(row, 2, QTableWidgetItem(produit.get('categorie', 'N/A')))
            
            # Stock
            stock = produit['stockactuel']
            item_stock = QTableWidgetItem(str(stock))
            item_stock.setTextAlignment(Qt.AlignCenter)
            font_bold = QFont()
            font_bold.setBold(True)
            item_stock.setFont(font_bold)
            self.table_stock.setItem(row, 3, item_stock)
            
            # Seuil
            seuil = produit['stockalerte']
            item_seuil = QTableWidgetItem(str(seuil))
            item_seuil.setTextAlignment(Qt.AlignCenter)
            self.table_stock.setItem(row, 4, item_seuil)
            
            # Statut (avec couleur)
            if stock == 0:
                statut_text = "❌ RUPTURE"
                couleur = QColor("#F44336")
                text_color = QColor("white")
            elif stock <= seuil:
                statut_text = "⚠️ CRITIQUE"
                couleur = QColor("#FF9800")
                text_color = QColor("white")
            else:
                statut_text = "✅ OK"
                couleur = QColor("#00C853")
                text_color = QColor("white")
            
            item_statut = QTableWidgetItem(statut_text)
            item_statut.setBackground(couleur)
            item_statut.setForeground(text_color)
            item_statut.setTextAlignment(Qt.AlignCenter)
            item_statut.setFont(font_bold)
            self.table_stock.setItem(row, 5, item_statut)
    
    def voir_historique_produit(self):
        """Affiche l'historique d'un produit (double-clic)"""
        # TODO: Implémenter dialogue historique
        pass
    
    def rafraichir(self):
        """Rafraîchit les données"""
        self.charger_donnees()
