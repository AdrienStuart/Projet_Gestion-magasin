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
from PySide6.QtGui import QFont, QColor
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
                margin-top: 15px; /* Marge augmentée */
                padding-top: 25px; /* Padding augmenté pour éviter chevauchement titre */
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                background-color: white; /* Important pour lisibilité */
            }
        """)
        
        layout_form = QVBoxLayout(group_form)
        layout_form.setSpacing(20) # Espacement aéré
        layout_form.setContentsMargins(15, 25, 15, 15)
        
        # Ligne 1: Produit (Combo + Bouton Catalogue) + Type
        layout_ligne1 = QHBoxLayout()
        
        # Produit
        lbl_produit = QLabel("Produit:")
        lbl_produit.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout_ligne1.addWidget(lbl_produit)
        
        self.combo_produit = QComboBox()
        self.combo_produit.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 11pt;
                min-width: 250px;
            }
        """)
        layout_ligne1.addWidget(self.combo_produit, stretch=2)
        
        # Bouton Catalogue
        self.btn_catalogue = QPushButton("📦 Catalogue")
        self.btn_catalogue.setCursor(Qt.PointingHandCursor)
        self.btn_catalogue.setStyleSheet("""
            QPushButton {
                background-color: #3E3E5E;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #4E4E6E;
            }
        """)
        self.btn_catalogue.clicked.connect(self.ouvrir_catalogue)
        layout_ligne1.addWidget(self.btn_catalogue)
        
        layout_ligne1.addSpacing(20)
        
        # Type de mouvement
        lbl_type = QLabel("Type:")
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
                min-width: 150px;
            }
        """)
        layout_ligne1.addWidget(self.combo_type, stretch=1)
        
        layout_form.addLayout(layout_ligne1)
        
        # Ligne 2: Quantité (Gros boutons) + Bouton Valider
        layout_ligne2 = QHBoxLayout()
        
        # Quantité
        lbl_qte = QLabel("Quantité:")
        lbl_qte.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout_ligne2.addWidget(lbl_qte)
        
        self.spin_quantite = QSpinBox()
        self.spin_quantite.setRange(1, 10000)
        self.spin_quantite.setValue(1)
        self.spin_quantite.setFixedWidth(150)
        self.spin_quantite.setMinimumHeight(45)
        # Style pour gros boutons +/-
        self.spin_quantite.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 14pt;
                font-weight: bold;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 30px;
                border-width: 1px;
            }
        """)
        layout_ligne2.addWidget(self.spin_quantite)
        
        layout_ligne2.addStretch()
        
        # Bouton valider
        self.btn_valider = QPushButton("Valider le mouvement")
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
        
        # Ligne 3: Motif
        layout_ligne3 = QVBoxLayout()
        
        lbl_motif = QLabel("Motif (recommandé):")
        lbl_motif.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout_ligne3.addWidget(lbl_motif)
        
        self.text_motif = QTextEdit()
        self.text_motif.setPlaceholderText("Ex: Livraison Fournisseur X, Casse durant transport, Ajustement inventaire...")
        self.text_motif.setMaximumHeight(60) # Réduit un peu
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
        # Label titre (avec style forcé pour visibilité)
        lbl_titre = QLabel("📜 Historique des Mouvements")
        lbl_titre.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2A2A40; margin-top: 20px; margin-bottom: 10px;")
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
        self.table_historique.verticalHeader().setDefaultSectionSize(50) 
        self.table_historique.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_historique.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_historique.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_historique.setAlternatingRowColors(True)
        
        self.table_historique.setStyleSheet("""
            QTableWidget {
                font-size: 12pt;
                alternate-background-color: #F9F9F9;
                background-color: white;
                gridline-color: #E0E0E0;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 5px 10px;
                color: #2A2A40;
            }
            QTableWidget::item:selected {
                background-color: #2196F3; /* Bleu sélection */
                color: white;
            }
            QHeaderView::section {
                background-color: #2A2A40; /* En-tête sombre */
                color: white;
                padding: 10px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }
        """)
        
        parent_layout.addWidget(self.table_historique, stretch=1)
        
        # Bouton Voir Détails
        self.btn_details = QPushButton("🔍 Voir détails du mouvement sélectionné")
        self.btn_details.setCursor(Qt.PointingHandCursor)
        self.btn_details.setStyleSheet("""
            QPushButton {
                background-color: #5C6BC0;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #7986CB;
            }
        """)
        self.btn_details.clicked.connect(self.voir_details_mouvement)
        parent_layout.addWidget(self.btn_details, alignment=Qt.AlignRight)
    
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
            
            # Déterminer style selon type
            type_mvt = mvt.get('type', '')
            bg_color = QColor("white")
            text_color = QColor("#2A2A40")
            
            if type_mvt == 'ENTREE':
                type_text = "📥 ENTREE"
                bg_color = QColor("#E8F5E9") # Vert très clair
                type_color = QColor("#2E7D32") # Vert foncé
            elif type_mvt == 'SORTIE':
                type_text = "📤 SORTIE"
                bg_color = QColor("#FFEBEE") # Rouge très clair
                type_color = QColor("#C62828") # Rouge foncé
            else:
                type_text = f"🔧 {type_mvt}"
                bg_color = QColor("#FFF3E0") # Orange clair
                type_color = QColor("#EF6C00") # Orange foncé
            
            # Helper pour créer items colorés
            def create_item(text, color=text_color, bold=False):
                item = QTableWidgetItem(str(text))
                item.setBackground(bg_color)
                item.setForeground(color)
                if bold:
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                return item

            # Date
            date_str = mvt.get('datemouvement', '')
            if date_str:
                try:
                    dt = datetime.fromisoformat(str(date_str))
                    date_str = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    pass
            self.table_historique.setItem(row, 0, create_item(date_str))
            
            # Produit
            self.table_historique.setItem(row, 1, create_item(mvt.get('nom_produit', ''), bold=True))
            
            # Type
            self.table_historique.setItem(row, 2, create_item(type_text, type_color, bold=True))
            
            # Quantité
            qte = mvt.get('quantite', 0)
            item_qte = create_item(str(qte), bold=True)
            item_qte.setTextAlignment(Qt.AlignCenter)
            self.table_historique.setItem(row, 3, item_qte)
            
            # Utilisateur
            self.table_historique.setItem(row, 4, create_item(mvt.get('nom_utilisateur', 'N/A')))
            
            # Motif
            self.table_historique.setItem(row, 5, create_item(mvt.get('commentaire', '-')))
    
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
    
    def ouvrir_catalogue(self):
        """Ouvre le catalogue pour sélectionner un produit"""
        dlg = DialogueCatalogue(self)
        if dlg.exec():
            produit = dlg.produit_selectionne
            if produit:
                # Trouver l'index dans le combobox
                index = self.combo_produit.findData(produit['id_produit'])
                if index >= 0:
                    self.combo_produit.setCurrentIndex(index)
    
    def voir_details_mouvement(self):
        """Affiche les détails du mouvement sélectionné"""
        row = self.table_historique.currentRow()
        if row < 0:
            return
            
        # Récupérer les infos de la ligne
        date = self.table_historique.item(row, 0).text()
        produit = self.table_historique.item(row, 1).text()
        type_mvt = self.table_historique.item(row, 2).text()
        qte = self.table_historique.item(row, 3).text()
        motif = self.table_historique.item(row, 5).text()
        
        # Afficher dans un dialogue simple
        QMessageBox.information(
            self, f"Détails du Mouvement",
            f"📅 Date: {date}\n"
            f"📦 Produit: {produit}\n"
            f"🔄 Type: {type_mvt}\n"
            f"🔢 Quantité: {qte}\n\n"
            f"📝 Motif complet:\n{motif}"
        )
            
    def rafraichir(self):
        """Rafraîchit les données"""
        self.charger_donnees()


class DialogueCatalogue(QDialog):
    """Dialogue du mode catalogue (grille de produits) - Version Gestionnaire"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Catalogue Produits")
        self.resize(900, 700) # Un peu plus grand
        self.produit_selectionne = None
        
        self.setup_ui()
        self.charger_produits()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titre
        lbl_titre = QLabel("📦 Sélectionnez un produit")
        lbl_titre.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2A2A40; margin-bottom: 10px;")
        lbl_titre.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titre)
        
        # Zone scrollable
        from PySide6.QtWidgets import QScrollArea, QDialogButtonBox, QGridLayout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(15)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def charger_produits(self):
        import os
        from PySide6.QtGui import QPixmap
        produits = Database.get_all_products()
        
        col = 0
        row = 0
        max_cols = 3
        
        default_img_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "assets", "default.png"
        )
        
        for produit in produits:
            card = QFrame()
            card.setFixedSize(250, 220)
            card.setCursor(Qt.PointingHandCursor)
            card.mousePressEvent = lambda event, p=produit: self.selectionner_produit(p)
            
            # Style unifié
            stock = produit.get('quantite_stock', 0)
            border_color = "#E0E0E0"
            if stock <= 0: border_color = "#F44336" # Rouge si vide
            elif stock <= 5: border_color = "#FF9800" # Orange si critique
            
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 2px solid {border_color};
                    border-radius: 10px;
                }}
                QFrame:hover {{
                    background-color: #F5F5F5;
                    border-color: #00C853;
                }}
            """)
            
            layout = QVBoxLayout(card)
            
            # Image
            lbl_img = QLabel("📦")
            lbl_img.setAlignment(Qt.AlignCenter)
            lbl_img.setStyleSheet("font-size: 40pt; color: #BDBDBD; border: none;")
            
            # Tentative chargement image (simple)
            pixmap = QPixmap(default_img_path)
            if not pixmap.isNull():
                 lbl_img.setPixmap(pixmap.scaled(120, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                 
            layout.addWidget(lbl_img)
            
            # Nom
            lbl_nom = QLabel(produit['nom_produit'])
            lbl_nom.setAlignment(Qt.AlignCenter)
            lbl_nom.setWordWrap(True)
            lbl_nom.setStyleSheet("font-weight: bold; font-size: 11pt; color: #2A2A40; border: none;")
            layout.addWidget(lbl_nom)
            
            # Stock
            lbl_stock = QLabel(f"Stock: {stock}")
            lbl_stock.setAlignment(Qt.AlignCenter)
            color_stock = "red" if stock <= 0 else "orange" if stock <= 5 else "green"
            lbl_stock.setStyleSheet(f"color: {color_stock}; font-weight: bold; border: none;")
            layout.addWidget(lbl_stock)
            
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def selectionner_produit(self, produit):
        self.produit_selectionne = produit
        self.accept()
