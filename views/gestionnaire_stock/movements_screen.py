"""
Écran Mouvements de Stock
Formulaire de saisie + Historique
Règle: JAMAIS de modification directe du stock
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QLabel, QComboBox, QSpinBox,
                               QTextEdit, QPushButton, QHeaderView, QAbstractItemView,
                               QFrame, QMessageBox, QGroupBox, QDialog,
                               QScrollArea, QDialogButtonBox, QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPixmap
from datetime import datetime
import os

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
        """Construction de l'interface avec défilement global"""
        layout_main = QVBoxLayout(self)
        layout_main.setContentsMargins(0, 0, 0, 0)
        
        # Area de défilement
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: #0D1117; border: none;")
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #0D1117;")
        layout_principal = QVBoxLayout(self.container)
        layout_principal.setContentsMargins(30, 30, 30, 30)
        layout_principal.setSpacing(30)
        
        # Formulaire de saisie
        self._creer_formulaire(layout_principal)
        
        # Table historique
        self._creer_table_historique(layout_principal)
        
        scroll.setWidget(self.container)
        layout_main.addWidget(scroll)
    
    def _creer_formulaire(self, parent_layout):
        """Formulaire de saisie de mouvement avec design harmonisé"""
        group_form = QGroupBox("📝 Enregistrer un nouveau mouvement")
        group_form.setStyleSheet("""
            QGroupBox {
                font-size: 14pt;
                font-weight: bold;
                border: 1px solid #30363D;
                border-radius: 12px;
                margin-top: 20px;
                padding-top: 35px;
                background-color: #161B22;
                color: #58A6FF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
            }
        """)
        
        layout_form = QVBoxLayout(group_form)
        layout_form.setSpacing(25)
        layout_form.setContentsMargins(25, 30, 25, 25)
        
        # Ligne 1: Produit + Type
        layout_ligne1 = QHBoxLayout()
        layout_ligne1.setSpacing(30)
        
        # Produit
        vbox_prod = QVBoxLayout()
        lbl_produit = QLabel("PRODUIT")
        lbl_produit.setStyleSheet("font-size: 10pt; font-weight: bold; color: #8B949E; letter-spacing: 1px;")
        vbox_prod.addWidget(lbl_produit)
        
        self.combo_produit = QComboBox()
        self.combo_produit.setStyleSheet("""
            QComboBox {
                padding: 10px;
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-radius: 8px;
                font-size: 11pt;
                color: #E6EDF3;
                min-width: 300px;
            }
            QComboBox:hover { border-color: #58A6FF; }
        """)
        vbox_prod.addWidget(self.combo_produit)
        layout_ligne1.addLayout(vbox_prod, stretch=3)
        
        # Type de mouvement
        vbox_type = QVBoxLayout()
        lbl_type = QLabel("TYPE DE MOUVEMENT")
        lbl_type.setStyleSheet("font-size: 10pt; font-weight: bold; color: #8B949E; letter-spacing: 1px;")
        vbox_type.addWidget(lbl_type)
        
        self.combo_type = QComboBox()
        self.combo_type.addItem("📥 ENTREE", "ENTREE")
        self.combo_type.addItem("📤 SORTIE", "SORTIE")
        self.combo_type.setStyleSheet("""
            QComboBox {
                padding: 10px;
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-radius: 8px;
                font-size: 11pt;
                color: #E6EDF3;
                min-width: 200px; /* Largeur augmentée */
            }
            QComboBox:hover { border-color: #58A6FF; }
        """)
        vbox_type.addWidget(self.combo_type)
        layout_ligne1.addLayout(vbox_type, stretch=1)
        
        layout_form.addLayout(layout_ligne1)
        
        # Ligne 2: Quantité + Boutons
        layout_ligne2 = QHBoxLayout()
        layout_ligne2.setSpacing(30)
        
        # Quantité
        vbox_qte = QVBoxLayout()
        lbl_qte = QLabel("QUANTITÉ")
        lbl_qte.setStyleSheet("font-size: 10pt; font-weight: bold; color: #8B949E; letter-spacing: 1px;")
        vbox_qte.addWidget(lbl_qte)
        
        self.spin_quantite = QSpinBox()
        self.spin_quantite.setRange(1, 10000)
        self.spin_quantite.setValue(1)
        self.spin_quantite.setFixedWidth(200)
        self.spin_quantite.setMinimumHeight(45)
        self.spin_quantite.setStyleSheet("""
            QSpinBox {
                padding: 5px 15px;
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-radius: 8px;
                font-size: 14pt;
                font-weight: bold;
                color: #58A6FF;
            }
        """)
        vbox_qte.addWidget(self.spin_quantite)
        layout_ligne2.addLayout(vbox_qte)
        
        layout_ligne2.addStretch()
        
        # Bouton Catalogue
        self.btn_catalogue = QPushButton("📦 Ouvrir le Catalogue")
        self.btn_catalogue.setCursor(Qt.PointingHandCursor)
        self.btn_catalogue.setFixedHeight(45)
        self.btn_catalogue.setStyleSheet("""
            QPushButton {
                background-color: #21262D;
                color: #C9D1D9;
                font-weight: bold;
                border: 1px solid #30363D;
                border-radius: 8px;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #30363D; }
        """)
        self.btn_catalogue.clicked.connect(self.ouvrir_catalogue)
        layout_ligne2.addWidget(self.btn_catalogue)
        
        # Bouton valider
        self.btn_valider = QPushButton("Valider le mouvement")
        self.btn_valider.setFixedHeight(45)
        self.btn_valider.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: white;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 30px;
            }
            QPushButton:hover { background-color: #2EA043; }
        """)
        self.btn_valider.clicked.connect(self.valider_mouvement)
        layout_ligne2.addWidget(self.btn_valider)
        
        layout_form.addLayout(layout_ligne2)
        
        # Ligne 3: Motif
        layout_ligne3 = QVBoxLayout()
        layout_ligne3.setSpacing(10)
        
        lbl_motif = QLabel("MOTIF (RECOMMANDÉ)")
        lbl_motif.setStyleSheet("font-size: 10pt; font-weight: bold; color: #8B949E; letter-spacing: 1px;")
        layout_ligne3.addWidget(lbl_motif)
        
        self.text_motif = QTextEdit()
        self.text_motif.setPlaceholderText("Ex: Livraison Fournisseur X, Casse durant transport, Ajustement inventaire...")
        self.text_motif.setMinimumHeight(100) # Hauteur augmentée
        self.text_motif.setMaximumHeight(150)
        self.text_motif.setStyleSheet("""
            QTextEdit {
                padding: 12px;
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-radius: 8px;
                font-size: 11pt;
                color: #E6EDF3;
            }
            QTextEdit:focus { border-color: #58A6FF; }
        """)
        layout_ligne3.addWidget(self.text_motif)
        
        layout_form.addLayout(layout_ligne3)
        
        parent_layout.addWidget(group_form)
    
    def _creer_table_historique(self, parent_layout):
        """Table de l'historique des mouvements avec design sombre"""
        # Header Section
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #161B22; border: 1px solid #30363D; border-radius: 8px; margin-top: 10px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        lbl_titre = QLabel("📜 HISTORIQUE DES MOUVEMENTS")
        lbl_titre.setStyleSheet("font-size: 13pt; font-weight: bold; color: #E6EDF3;")
        header_layout.addWidget(lbl_titre)
        
        header_layout.addStretch()
        
        # Bouton Voir Détails
        self.btn_details = QPushButton("🔍 Détails")
        self.btn_details.setCursor(Qt.PointingHandCursor)
        self.btn_details.setStyleSheet("""
            QPushButton {
                background-color: #21262D;
                color: #C9D1D9;
                font-weight: bold;
                border: 1px solid #30363D;
                border-radius: 6px;
                padding: 6px 15px;
            }
            QPushButton:hover { background-color: #30363D; }
        """)
        self.btn_details.clicked.connect(self.voir_details_mouvement)
        header_layout.addWidget(self.btn_details)
        
        parent_layout.addWidget(header_frame)
        
        # Table
        self.table_historique = QTableWidget()
        self.table_historique.setColumnCount(6)
        self.table_historique.setHorizontalHeaderLabels([
            "DATE", "PRODUIT", "TYPE", "QUANTITÉ", "PAR", "MOTIF"
        ])
        
        # Configuration
        header = self.table_historique.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        self.table_historique.verticalHeader().setVisible(False)
        self.table_historique.verticalHeader().setDefaultSectionSize(50) 
        self.table_historique.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_historique.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_historique.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.table_historique.setMinimumHeight(400) # Assurer une hauteur min
        
        self.table_historique.setStyleSheet("""
            QTableWidget {
                background-color: #161B22;
                gridline-color: #30363D;
                border: 1px solid #30363D;
                border-radius: 8px;
                color: #C9D1D9;
                font-size: 11pt;
            }
            QHeaderView::section {
                background-color: #21262D;
                color: #8B949E;
                padding: 12px;
                font-size: 9pt;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #30363D;
                text-transform: uppercase;
            }
            QTableWidget::item { padding: 10px; }
            QTableWidget::item:selected {
                background-color: rgba(31, 111, 235, 0.2);
                color: #58A6FF;
            }
        """)
        
        parent_layout.addWidget(self.table_historique)
    
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
            bg_color = QColor("transparent")
            text_color = QColor("#E6EDF3") # Gris clair GitHub
            
            if type_mvt == 'ENTREE':
                type_text = "📥 ENTREE"
                bg_color = QColor(35, 134, 54, 40) # Vert GitHub transparent
                type_color = QColor("#3FB950") # Vert clair
            elif type_mvt == 'SORTIE':
                type_text = "📤 SORTIE"
                bg_color = QColor(248, 81, 73, 40) # Rouge GitHub transparent
                type_color = QColor("#F85149") # Rouge clair
            else:
                type_text = f"🔧 {type_mvt}"
                bg_color = QColor(187, 128, 9, 40) # Jaune/Orange transparent
                type_color = QColor("#D29922") # Jaune clair
            
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
