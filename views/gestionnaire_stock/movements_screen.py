"""
Écran Mouvements de Stock
Formulaire de saisie + Historique
Règle: JAMAIS de modification directe du stock
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QComboBox, QSpinBox,
                               QTextEdit, QPushButton, QHeaderView, QAbstractItemView,
                               QFrame, QMessageBox, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from datetime import datetime

from db.database import Database


class MovementsScreen(QWidget):
    """
    Écran de gestion des mouvements de stock
    Entrées (livraisons) et Sorties (casse, perte, ajustement)
    """
    
    def __init__(self, id_utilisateur: int, nom_utilisateur: str):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        self.nom_utilisateur = nom_utilisateur
        
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        """Construction de l'interface"""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)
        
        # Formulaire de saisie
        self._creer_formulaire(layout_principal)
        
        # Table historique
        self._creer_table_historique(layout_principal)
    
    def _creer_formulaire(self, parent_layout):
        """Formulaire de saisie de mouvement"""
        group_form = QGroupBox("📝 Nouveau Mouvement")
        group_form.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout_form = QVBoxLayout(group_form)
        layout_form.setSpacing(15)
        
        # Ligne 1: Produit + Type
        layout_ligne1 = QHBoxLayout()
        
        # Produit
        lbl_produit = QLabel("Produit:")
        lbl_produit.setFixedWidth(100)
        lbl_produit.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout_ligne1.addWidget(lbl_produit)
        
        self.combo_produit = QComboBox()
        self.combo_produit.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 11pt;
                min-width: 300px;
            }
        """)
        layout_ligne1.addWidget(self.combo_produit, stretch=1)
        
        layout_ligne1.addSpacing(20)
        
        # Type de mouvement
        lbl_type = QLabel("Type:")
        lbl_type.setFixedWidth(80)
        lbl_type.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout_ligne1.addWidget(lbl_type)
        
        self.combo_type = QComboBox()
        self.combo_type.addItem("📥 ENTREE", "ENTREE")
        self.combo_type.addItem("📤 SORTIE", "SORTIE")
        self.combo_type.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 11pt;
                min-width: 180px;
            }
        """)
        layout_ligne1.addWidget(self.combo_type)
        
        layout_form.addLayout(layout_ligne1)
        
        # Ligne 2: Quantité + Bouton Valider
        layout_ligne2 = QHBoxLayout()
        
        # Quantité
        lbl_qte = QLabel("Quantité:")
        lbl_qte.setFixedWidth(100)
        lbl_qte.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout_ligne2.addWidget(lbl_qte)
        
        self.spin_quantite = QSpinBox()
        self.spin_quantite.setRange(1, 10000)
        self.spin_quantite.setValue(1)
        self.spin_quantite.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 11pt;
                min-width: 120px;
            }
        """)
        layout_ligne2.addWidget(self.spin_quantite)
        
        layout_ligne2.addStretch()
        
        # Bouton valider
        self.btn_valider = QPushButton("✅ Valider le Mouvement")
        self.btn_valider.setFixedHeight(45)
        self.btn_valider.setStyleSheet("""
            QPushButton {
                background-color: #00C853;
                color: white;
                font-size: 13pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 30px;
            }
            QPushButton:hover {
                background-color: #00E676;
            }
        """)
        self.btn_valider.clicked.connect(self.valider_mouvement)
        layout_ligne2.addWidget(self.btn_valider)
        
        layout_form.addLayout(layout_ligne2)
        
        # Ligne 3: Motif/Commentaire
        layout_ligne3 = QVBoxLayout()
        
        lbl_motif = QLabel("Motif (recommandé):")
        lbl_motif.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout_ligne3.addWidget(lbl_motif)
        
        self.text_motif = QTextEdit()
        self.text_motif.setPlaceholderText("Ex: Livraison Fournisseur X, Casse durant transport, Ajustement inventaire...")
        self.text_motif.setMaximumHeight(80)
        self.text_motif.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 11pt;
            }
        """)
        layout_ligne3.addWidget(self.text_motif)
        
        layout_form.addLayout(layout_ligne3)
        
        parent_layout.addWidget(group_form)
    
    def _creer_table_historique(self, parent_layout):
        """Table de l'historique des mouvements"""
        # Label titre
        lbl_titre = QLabel("📜 Historique des Mouvements")
        lbl_titre.setStyleSheet("font-size: 13pt; font-weight: bold; color: #2A2A40;")
        parent_layout.addWidget(lbl_titre)
        
        # Table
        self.table_historique = QTableWidget()
        self.table_historique.setColumnCount(6)
        self.table_historique.setHorizontalHeaderLabels([
            "Date", "Produit", "Type", "Quantité", "Utilisateur", "Motif"
        ])
        
        # Configuration
        header = self.table_historique.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.Stretch)            # Produit
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Quantité
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Utilisateur
        header.setSectionResizeMode(5, QHeaderView.Stretch)            # Motif
        
        self.table_historique.verticalHeader().setVisible(False)
        self.table_historique.verticalHeader().setDefaultSectionSize(40)
        self.table_historique.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_historique.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_historique.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_historique.setAlternatingRowColors(True)
        
        self.table_historique.setStyleSheet("""
            QTableWidget {
                font-size: 11pt;
                alternate-background-color: #F9F9F9;
                background-color: white;
                gridline-color: #E0E0E0;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #455A64;
                color: white;
                padding: 10px;
                font-size: 10pt;
                font-weight: bold;
                border: none;
            }
        """)
        
        parent_layout.addWidget(self.table_historique, stretch=1)
    
    # ========== LOGIQUE ==========
    
    def charger_donnees(self):
        """Charge les produits et l'historique"""
        # Charger produits
        produits = Database.get_all_products()
        self.combo_produit.clear()
        for produit in produits:
            self.combo_produit.addItem(
                f"{produit['nom_produit']} (Stock: {produit['quantite_stock']})",
                produit['id_produit']
            )
        
        # Charger historique
        self.charger_historique()
    
    def charger_historique(self):
        """Charge l'historique des mouvements"""
        mouvements = Database.get_stock_movements()
        
        self.table_historique.setRowCount(0)
        
        for mvt in mouvements:
            row = self.table_historique.rowCount()
            self.table_historique.insertRow(row)
            
            # Date
            date_str = mvt.get('datemouvement', '')
            if date_str:
                try:
                    dt = datetime.fromisoformat(str(date_str))
                    date_str = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    pass
            self.table_historique.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Produit
            self.table_historique.setItem(row, 1, QTableWidgetItem(mvt.get('nom_produit', '')))
            
            # Type (avec icône)
            type_mvt = mvt.get('type', '')
            if type_mvt == 'ENTREE':
                type_text = "📥 ENTREE"
                couleur = "#00C853"
            elif type_mvt == 'SORTIE':
                type_text = "📤 SORTIE"
                couleur = "#F44336"
            else:
                type_text = f"🔧 {type_mvt}"
                couleur = "#FF9800"
            
            item_type = QTableWidgetItem(type_text)
            item_type.setForeground(QFont().setWeight(QFont.Bold))
            self.table_historique.setItem(row, 2, item_type)
            
            # Quantité
            qte = mvt.get('quantite', 0)
            item_qte = QTableWidgetItem(str(qte))
            item_qte.setTextAlignment(Qt.AlignCenter)
            font_bold = QFont()
            font_bold.setBold(True)
            item_qte.setFont(font_bold)
            self.table_historique.setItem(row, 3, item_qte)
            
            # Utilisateur
            self.table_historique.setItem(row, 4, QTableWidgetItem(mvt.get('nom_utilisateur', 'N/A')))
            
            # Motif
            self.table_historique.setItem(row, 5, QTableWidgetItem(mvt.get('commentaire', '-')))
    
    def valider_mouvement(self):
        """Valide et enregistre le mouvement"""
        # Récupérer les données
        id_produit = self.combo_produit.currentData()
        nom_produit = self.combo_produit.currentText().split(" (Stock:")[0]
        type_mvt = self.combo_type.currentData()
        quantite = self.spin_quantite.value()
        motif = self.text_motif.toPlainText().strip()
        
        if not id_produit:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit.")
            return
        
        if not motif:
            reponse = QMessageBox.question(
                self, "Confirmation",
                "Aucun motif saisi. Continuer quand même ?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reponse != QMessageBox.Yes:
                return
        
        # Créer le mouvement
        succes, message = Database.create_stock_movement(
            id_produit, type_mvt, quantite, self.id_utilisateur, motif
        )
        
        if succes:
            QMessageBox.information(
                self, "Succès",
                f"Mouvement enregistré:\n{type_mvt} de {quantite} unité(s) pour {nom_produit}"
            )
            
            # Réinitialiser le formulaire
            self.spin_quantite.setValue(1)
            self.text_motif.clear()
            
            # Recharger les données
            self.charger_donnees()
        else:
            QMessageBox.critical(self, "Erreur", f"Échec de l'enregistrement:\n{message}")
    
    def rafraichir(self):
        """Rafraîchit les données"""
        self.charger_donnees()
