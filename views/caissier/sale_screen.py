"""
Écran de Vente (Nouvelle Vente)
C'est l'écran par défaut et le "point de sécurité mentale" du caissier
Mode rapide prioritaire avec mode catalogue optionnel
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QTableWidget, QTableWidgetItem, QLabel, QPushButton,
                               QHeaderView, QAbstractItemView, QFrame, QMessageBox,
                               QDialog, QInputDialog, QGridLayout, QScrollArea, QDialogButtonBox)
from PySide6.QtCore import Qt, Signal, QTimer, QEvent
from PySide6.QtGui import QFont, QShortcut, QKeySequence
import qtawesome as qta

from db.database import Database
from views.caissier.cashier_service import (
    PanierService, CalculateurVente, ValidationVente, FormateurDevise
)


class EcranVente(QWidget):
    """
    Écran principal de vente
    Focus permanent sur la saisie rapide (scanner/clavier)
    """
    
    # Signal émis quand une vente est validée avec succès
    vente_validee = Signal()
    
    def __init__(self, id_utilisateur: int, nom_utilisateur: str = "Caissier"):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        self.nom_utilisateur = nom_utilisateur
        self.panier_service = PanierService()
        self.calculateur = CalculateurVente()
        
        self.setup_ui()
        self.setup_raccourcis()
        
        # Focus immédiat sur la barre de recherche
        QTimer.singleShot(100, lambda: self.barre_recherche.setFocus())
    
    def setup_ui(self):
        """Construction de l'interface utilisateur"""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)
        
        # ========== ZONE SAISIE PRODUIT ==========
        self._creer_zone_saisie(layout_principal)
        
        # ========== ZONE PANIER + TOTAUX ==========
        zone_panier_layout = QHBoxLayout()
        
        # Panier (gauche - 60%)
        self._creer_zone_panier(zone_panier_layout)
        
        # Totaux et paiement (droite - 40%)
        self._creer_zone_totaux(zone_panier_layout)
        
        layout_principal.addLayout(zone_panier_layout, stretch=1)
        
        # ========== ZONE ACTIONS ==========
        self._creer_zone_actions(layout_principal)
    
    def _creer_zone_saisie(self, parent_layout):
        """Zone de saisie rapide (mode principal)"""
        # En-tête avec mode rapide + bouton catalogue
        layout_entete = QHBoxLayout()
        
        # Barre de recherche/scan (MODE RAPIDE)
        self.barre_recherche = QLineEdit()
        self.barre_recherche.setPlaceholderText("🔍 Scanner ou taper code/nom produit (Entrée pour ajouter)...")
        self.barre_recherche.setFixedHeight(60)
        self.barre_recherche.setStyleSheet("""
            QLineEdit {
                font-size: 18pt;
                padding-left: 15px;
                border-radius: 8px;
                border: 2px solid #3E3E5E;
                background-color: white;
                color: #1E1E2E;
            }
            QLineEdit:focus {
                border: 2px solid #00C853;
            }
        """)
        self.barre_recherche.returnPressed.connect(self.traiter_saisie_produit)
        layout_entete.addWidget(self.barre_recherche, stretch=1)
        
        # Bouton Catalogue (MODE VISUEL - optionnel)
        self.btn_catalogue = QPushButton("📦 Catalogue")
        self.btn_catalogue.setFixedSize(150, 60)
        self.btn_catalogue.setStyleSheet("""
            QPushButton {
                background-color: #3E3E5E;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #4E4E6E;
            }
        """)
        self.btn_catalogue.clicked.connect(self.ouvrir_catalogue)
        layout_entete.addWidget(self.btn_catalogue)
        
        parent_layout.addLayout(layout_entete)
    
    def _creer_zone_panier(self, parent_layout):
        """Table du panier"""
        frame_panier = QFrame()
        frame_panier.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        layout_panier = QVBoxLayout(frame_panier)
        layout_panier.setContentsMargins(10, 10, 10, 10)
        
        # Label en-tête
        lbl_panier = QLabel("🛒 PANIER")
        lbl_panier.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2A2A40; border: none;")
        layout_panier.addWidget(lbl_panier)
        
        # Table panier
        self.table_panier = QTableWidget()
        self.table_panier.setColumnCount(5)
        self.table_panier.setHorizontalHeaderLabels(["Code", "Produit", "Qté", "P.U.", "Total"])
        
        # Configuration colonnes
        header = self.table_panier.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Code
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Produit
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Qté
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # P.U.
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Total
        
        self.table_panier.verticalHeader().setVisible(False)
        self.table_panier.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_panier.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_panier.setAlternatingRowColors(True)
        self.table_panier.setStyleSheet("""
            QTableWidget {
                font-size: 13pt;
                alternate-background-color: #F0F0F0;
                background-color: white;
                border: none;
                color: #1E1E2E;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #00C853;
                color: white;
            }
            QHeaderView::section {
                background-color: #2A2A40;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        
        layout_panier.addWidget(self.table_panier)
        
        # Boutons d'actions panier
        layout_actions_panier = QHBoxLayout()
        layout_actions_panier.setSpacing(8)
        
        # Bouton Remise
        btn_remise = QPushButton("% Remise")
        btn_remise.setFixedHeight(40)
        btn_remise.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #FFB74D;
            }
        """)
        btn_remise.setIcon(qta.icon('fa5s.percentage', color='white'))
        btn_remise.clicked.connect(self.ouvrir_dialog_remise)
        layout_actions_panier.addWidget(btn_remise, stretch=1)
        
        # Bouton Retirer
        btn_retirer = QPushButton("Retirer")
        btn_retirer.setFixedHeight(40)
        btn_retirer.setStyleSheet("""
            QPushButton {
                background-color: #FF3D00;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #FF6E40;
            }
        """)
        btn_retirer.setIcon(qta.icon('fa5s.trash', color='white'))
        btn_retirer.clicked.connect(self.retirer_article_selectionne)
        layout_actions_panier.addWidget(btn_retirer, stretch=1)
        
        layout_panier.addLayout(layout_actions_panier)
        
        # Aide raccourcis
        lbl_aide = QLabel("💡 [+/-] Quantité | [F5] Remise | [Suppr] Retirer")
        lbl_aide.setStyleSheet("color: #757575; font-size: 9pt; font-style: italic; border: none;")
        layout_panier.addWidget(lbl_aide)
        
        parent_layout.addWidget(frame_panier, stretch=3)
    
    def _creer_zone_totaux(self, parent_layout):
        """Panneau totaux et moyens de paiement"""
        frame_totaux = QFrame()
        frame_totaux.setStyleSheet("""
            QFrame {
                background-color: #2A2A40;
                border-radius: 10px;
            }
        """)
        
        layout_totaux = QVBoxLayout(frame_totaux)
        layout_totaux.setContentsMargins(20, 20, 20, 20)
        layout_totaux.setSpacing(15)
        
        layout_totaux.addStretch()
        
        # Sous-total
        self.lbl_subtotal = self._creer_ligne_total("Sous-total:", "0 FCFA", 11)
        layout_totaux.addWidget(self.lbl_subtotal)
        
        # Remises
        self.lbl_remises = self._creer_ligne_total("Remises:", "0 FCFA", 11, "#FF9800")
        layout_totaux.addWidget(self.lbl_remises)
        
        # TVA (18%)
        self.lbl_tva = self._creer_ligne_total("TVA (18%):", "0 FCFA", 11)
        layout_totaux.addWidget(self.lbl_tva)
        
        # Séparateur
        separateur = QFrame()
        separateur.setFrameShape(QFrame.HLine)
        separateur.setStyleSheet("background-color: #4E4E6E;")
        layout_totaux.addWidget(separateur)
        
        # TOTAL (gros et vert)
        lbl_total_titre = QLabel("TOTAL À PAYER")
        lbl_total_titre.setAlignment(Qt.AlignRight)
        lbl_total_titre.setStyleSheet("font-size: 14pt; color: white;")
        layout_totaux.addWidget(lbl_total_titre)
        
        self.lbl_total = QLabel("0 FCFA")
        self.lbl_total.setAlignment(Qt.AlignRight)
        self.lbl_total.setStyleSheet("font-size: 36pt; font-weight: bold; color: #00C853;")
        layout_totaux.addWidget(self.lbl_total)
        
        layout_totaux.addStretch()
        
        parent_layout.addWidget(frame_totaux, stretch=2)
    
    def _creer_ligne_total(self, label_text: str, valeur_text: str, taille: int, couleur: str = "white") -> QLabel:
        """Crée une ligne de total formatée"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel(label_text)
        lbl.setStyleSheet(f"font-size: {taille}pt; color: #A0A0B0;")
        layout.addWidget(lbl)
        
        layout.addStretch()
        
        val = QLabel(valeur_text)
        val.setStyleSheet(f"font-size: {taille}pt; font-weight: bold; color: {couleur};")
        layout.addWidget(val)
        
        # Stocker le widget de valeur pour mise à jour
        container.valeur_widget = val
        
        return container
    
    def _creer_zone_actions(self, parent_layout):
        """Boutons d'action principaux"""
        layout_actions = QHBoxLayout()
        layout_actions.setSpacing(10)
        
        # Bouton Annuler
        btn_annuler = QPushButton("❌ Annuler")
        btn_annuler.setFixedHeight(70)
        btn_annuler.setStyleSheet("""
            QPushButton {
                background-color: #FF3D00;
                color: white;
                font-size: 16pt;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #FF6E40;
            }
        """)
        btn_annuler.clicked.connect(self.annuler_vente)
        layout_actions.addWidget(btn_annuler)
        
        # Bouton Mettre en attente (optionnel pour future implémentation)
        btn_attente = QPushButton("⏸️ En attente")
        btn_attente.setFixedHeight(70)
        btn_attente.setEnabled(False)  # Désactivé pour l'instant
        btn_attente.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                font-size: 16pt;
                font-weight: bold;
                border-radius: 10px;
            }
        """)
        layout_actions.addWidget(btn_attente)
        
        # Bouton Valider (principal)
        self.btn_valider = QPushButton("✅ VALIDER (F12)")
        self.btn_valider.setFixedHeight(70)
        self.btn_valider.setStyleSheet("""
            QPushButton {
                background-color: #00C853;
                color: white;
                font-size: 18pt;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #00E676;
            }
            QPushButton:pressed {
                background-color: #00A344;
            }
        """)
        self.btn_valider.clicked.connect(self.valider_vente)
        layout_actions.addWidget(self.btn_valider, stretch=2)
        
        parent_layout.addLayout(layout_actions)
    
    def setup_raccourcis(self):
        """Configuration des raccourcis clavier"""
        QShortcut(QKeySequence(Qt.Key_Plus), self, self.incrementer_quantite)
        QShortcut(QKeySequence(Qt.Key_Minus), self, self.decrementer_quantite)
        QShortcut(QKeySequence(Qt.Key_Delete), self, self.retirer_article_selectionne)
        QShortcut(QKeySequence("F5"), self, self.ouvrir_dialog_remise)
        QShortcut(QKeySequence("F12"), self, self.valider_vente)
        QShortcut(QKeySequence("Escape"), self, lambda: self.barre_recherche.setFocus())
    
    # ========== GESTION PRODUITS ==========
    
    def traiter_saisie_produit(self):
        """Traite la saisie d'un produit (scan ou clavier)"""
        texte = self.barre_recherche.text().strip()
        if not texte:
            return
        
        # Rechercher le produit
        produits = Database.search_products(texte)
        
        if not produits:
            QMessageBox.warning(self, "Produit introuvable", 
                              f"Aucun produit trouvé pour '{texte}'")
            self.barre_recherche.selectAll()
            return
        
        # Match exact ou premier résultat
        produit_cible = produits[0]
        for p in produits:
            if p['id_produit'].upper() == texte.upper() or p['nom_produit'].upper() == texte.upper():
                produit_cible = p
                break
        
        # Ajouter au panier
        self.panier_service.ajouter_produit(produit_cible)
        self.rafraichir_affichage()
        
        # Clear et refocus
        self.barre_recherche.clear()
        self.barre_recherche.setFocus()
    
    def ouvrir_catalogue(self):
        """Ouvre le mode catalogue (grille de produits)"""
        dlg = DialogueCatalogue(self)
        if dlg.exec():
            produit_selectionne = dlg.produit_selectionne
            if produit_selectionne:
                self.panier_service.ajouter_produit(produit_selectionne)
                self.rafraichir_affichage()
        
        # Refocus sur la recherche
        self.barre_recherche.setFocus()
    
    # ========== GESTION PANIER ==========
    
    def rafraichir_affichage(self):
        """Met à jour l'affichage du panier et des totaux"""
        self.table_panier.setRowCount(0)
        
        articles = self.panier_service.obtenir_articles()
        
        for id_produit, article in articles.items():
            produit = article['produit']
            quantite = article['quantite']
            remise = article['remise']
            prix_u = float(produit['prix_unitaire'])
            
            total_ligne = self.calculateur.calculer_total_ligne(prix_u, quantite, remise)
            
            row = self.table_panier.rowCount()
            self.table_panier.insertRow(row)
            
            # Code
            self.table_panier.setItem(row, 0, QTableWidgetItem(id_produit))
            
            # Nom produit
            item_nom = QTableWidgetItem(produit['nom_produit'])
            # Avertissement stock faible
            stock = produit.get('quantite_stock', 0)
            if stock <= 5:
                item_nom.setIcon(qta.icon('fa5s.exclamation-triangle', color='#FFD600'))
                item_nom.setToolTip(f"⚠️ Stock faible ({stock})")
            self.table_panier.setItem(row, 1, item_nom)
            
            # Quantité
            self.table_panier.setItem(row, 2, QTableWidgetItem(str(quantite)))
            
            # Prix unitaire (avec remise si applicable)
            prix_str = f"{prix_u:,.0f}"
            if remise > 0:
                prix_str += f" (-{remise:g}%)"
            self.table_panier.setItem(row, 3, QTableWidgetItem(prix_str))
            
            # Total ligne
            self.table_panier.setItem(row, 4, QTableWidgetItem(f"{total_ligne:,.0f}"))
        
        # Mettre à jour les totaux
        self._rafraichir_totaux(articles)
    
    def _rafraichir_totaux(self, articles: dict):
        """Met à jour l'affichage des totaux"""
        if not articles:
            self.lbl_subtotal.valeur_widget.setText("0 FCFA")
            self.lbl_remises.valeur_widget.setText("0 FCFA")
            self.lbl_tva.valeur_widget.setText("0 FCFA")
            self.lbl_total.setText("0 FCFA")
            return
        
        totaux = self.calculateur.calculer_totaux_panier(articles)
        
        self.lbl_subtotal.valeur_widget.setText(FormateurDevise.formater_fcfa(totaux['subtotal_ttc']))
        self.lbl_remises.valeur_widget.setText(FormateurDevise.formater_fcfa(totaux['total_remises']))
        self.lbl_tva.valeur_widget.setText(FormateurDevise.formater_fcfa(totaux['montant_tva']))
        self.lbl_total.setText(FormateurDevise.formater_fcfa(totaux['total_ttc']))
    
    def incrementer_quantite(self):
        """Incrémente la quantité de l'article sélectionné"""
        row = self.table_panier.currentRow()
        if row < 0:
            return
        
        id_produit = self.table_panier.item(row, 0).text()
        article = self.panier_service.articles.get(id_produit)
        if article:
            self.panier_service.modifier_quantite(id_produit, article['quantite'] + 1)
            self.rafraichir_affichage()
            self.table_panier.selectRow(row)
    
    def decrementer_quantite(self):
        """Décrémente la quantité de l'article sélectionné"""
        row = self.table_panier.currentRow()
        if row < 0:
            return
        
        id_produit = self.table_panier.item(row, 0).text()
        article = self.panier_service.articles.get(id_produit)
        if article and article['quantite'] > 1:
            self.panier_service.modifier_quantite(id_produit, article['quantite'] - 1)
            self.rafraichir_affichage()
            self.table_panier.selectRow(row)
    
    def retirer_article_selectionne(self):
        """Retire l'article sélectionné du panier"""
        row = self.table_panier.currentRow()
        if row < 0:
            return
        
        id_produit = self.table_panier.item(row, 0).text()
        self.panier_service.retirer_produit(id_produit)
        self.rafraichir_affichage()
    
    def ouvrir_dialog_remise(self):
        """Ouvre le dialogue de saisie de remise"""
        row = self.table_panier.currentRow()
        if row < 0:
            return
        
        id_produit = self.table_panier.item(row, 0).text()
        article = self.panier_service.articles.get(id_produit)
        if not article:
            return
        
        remise_actuelle = article['remise']
        remise, ok = QInputDialog.getDouble(
            self, "Remise", 
            "Pourcentage de remise (0-100):",
            remise_actuelle, 0, 100, 2
        )
        
        if ok:
            self.panier_service.appliquer_remise(id_produit, remise)
            self.rafraichir_affichage()
            self.table_panier.selectRow(row)
    
    # ========== VALIDATION VENTE ==========
    
    def annuler_vente(self):
        """Annule la vente en cours et vide le panier"""
        if self.panier_service.est_vide():
            return
        
        reponse = QMessageBox.question(
            self, "Annuler la vente",
            "Voulez-vous vraiment annuler cette vente ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reponse == QMessageBox.Yes:
            self.panier_service.vider_panier()
            self.rafraichir_affichage()
            self.barre_recherche.setFocus()
    
    def valider_vente(self):
        """Valide et enregistre la vente (sans dialogue montant)"""
        articles = self.panier_service.obtenir_articles()
        
        # Validation
        valide, message_erreur = ValidationVente.valider_panier(articles)
        if not valide:
            QMessageBox.warning(self, "Validation échouée", message_erreur)
            return
        
        # Calcul du total
        totaux = self.calculateur.calculer_totaux_panier(articles)
        total_a_payer = totaux['total_ttc']
        
        # Choix du mode de paiement
        modes = ["ESPECES", "MOBILE_MONEY", "CARTE", "CHEQUE"]
        mode_paiement, ok = QInputDialog.getItem(
            self, "Mode de Paiement",
            f"Total à payer: {FormateurDevise.formater_fcfa(total_a_payer)}\n\nChoisissez le mode de paiement:",
            modes, 0, False
        )
        
        if not ok:
            return
            
        # Préparer données pour DB
        cart_items = []
        for id_produit, article in articles.items():
            cart_items.append({
                'id': id_produit,
                'quantité': article['quantite'],
                'prix_unitaire': float(article['produit']['prix_unitaire']),
                'remise': article['remise'],
                'taux_tva': float(article['produit'].get('tauxtva', 18.00))
            })
        
        # Enregistrer la vente avec le mode de paiement choisi
        succes, resultat = Database.process_sale(cart_items, self.id_utilisateur, mode_paiement)
        
        if succes:
            # === GÉNÉRATION REÇU ===
            try:
                from utils.receipt_generator import ReceiptGenerator
                from datetime import datetime
                
                vente_data = {
                    'id_vente': resultat,
                    'date_vente': datetime.now(),
                    'caissier': self.nom_utilisateur,
                    'articles': [
                        {
                            'nom_produit': art['produit']['nom_produit'],
                            'quantite': art['quantite'],
                            'prix_unitaire': float(art['produit']['prix_unitaire']),
                            'remise': art['remise'],
                            'total_ligne': self.calculateur.calculer_total_ligne(
                                float(art['produit']['prix_unitaire']), 
                                art['quantite'], 
                                art['remise']
                            )
                        }
                        for art in articles.values()
                    ]
                }
                
                # Générer PDF avec le mode choisi
                pdf_path = ReceiptGenerator.generate_receipt(vente_data, totaux, mode_paiement)
                
                # Ouvrir le PDF automatiquement (viewer système par défaut)
                import subprocess
                import sys
                if sys.platform.startswith('linux'):
                    subprocess.Popen(['xdg-open', pdf_path])
                elif sys.platform == 'win32':
                    os.startfile(pdf_path)
                
            except Exception as e:
                print(f"Erreur génération reçu: {e}")
                # Ne pas bloquer la suite si l'impression échoue
            
            # Vider le panier et reset
            self.panier_service.vider_panier()
            self.rafraichir_affichage()
            self.barre_recherche.setFocus()
            self.vente_validee.emit()
            
        else:
            QMessageBox.critical(self, "Erreur", 
                               f"Échec de l'enregistrement de la vente:\n{resultat}")


class DialogueCatalogue(QDialog):
    """Dialogue du mode catalogue (grille de produits)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Catalogue Produits")
        self.resize(800, 600)
        self.produit_selectionne = None
        
        self.setup_ui()
        self.charger_produits()
    
    def setup_ui(self):
        """Construction de l'interface"""
        layout = QVBoxLayout(self)
        
        # Zone scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Container pour la grille
        container = QWidget()
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(10)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def charger_produits(self):
        """Charge les produits dans la grille avec images et stock"""
        import os
        from PySide6.QtCore import Qt
        produits = Database.get_all_products()
        
        col = 0
        row = 0
        max_cols = 3  # 3 colonnes au lieu de 4 pour plus d'espace
        
        # Chemin vers image par défaut
        default_img_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "assets", "default.png"
        )
        
        for produit in produits[:30]:  # Augmenter à 30 produits
            # Container pour chaque produit (carte)
            product_card = QFrame()
            product_card.setFrameShape(QFrame.Box)
            product_card.setFixedSize(230, 200)
            product_card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #E0E0E0;
                    border-radius: 10px;
                }
                QFrame:hover {
                    border-color: #00C853;
                    background-color: #F0F0F0;
                }
            """)
            
            card_layout = QVBoxLayout(product_card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(5)
            
            # Image produit
            from PySide6.QtGui import QPixmap
            lbl_image = QLabel()
            pixmap = QPixmap(default_img_path)
            if pixmap.isNull():
                # Si l'image ne charge pas, créer un placeholder
                lbl_image.setText("📦")
                lbl_image.setAlignment(Qt.AlignCenter)
                lbl_image.setStyleSheet("font-size: 48pt;")
            else:
                lbl_image.setPixmap(pixmap.scaled(150, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                lbl_image.setAlignment(Qt.AlignCenter)
            lbl_image.setFixedHeight(100)
            card_layout.addWidget(lbl_image)
            
            # Nom produit
            lbl_nom = QLabel(produit['nom_produit'][:25])  # Limiter longueur
            lbl_nom.setStyleSheet("font-size: 10pt; font-weight: bold; color: #2A2A40;")
            lbl_nom.setAlignment(Qt.AlignCenter)
            lbl_nom.setWordWrap(True)
            card_layout.addWidget(lbl_nom)
            
            # Prix
            lbl_prix = QLabel(f"{produit['prix_unitaire']:,.0f} FCFA")
            lbl_prix.setStyleSheet("font-size: 12pt; font-weight: bold; color: #00C853;")
            lbl_prix.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(lbl_prix)
            
            # Stock restant
            stock = produit.get('quantite_stock', 0)
            is_hs = stock <= 0
            
            stock_color = "#FF3D00" if stock <= 5 else "#757575"
            lbl_stock = QLabel(f"Stock: {'RUPTURE' if is_hs else stock}")
            lbl_stock.setStyleSheet(f"font-size: 9pt; font-weight: bold; color: {stock_color};")
            lbl_stock.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(lbl_stock)
            
            # Rendre la carte cliquable uniquement si stock > 0
            if not is_hs:
                product_card.mousePressEvent = lambda event, p=produit: self.selectionner_produit(p)
                product_card.setCursor(Qt.PointingHandCursor)
            else:
                # Style "désactivé"
                product_card.setStyleSheet("""
                    QFrame {
                        background-color: #F5F5F5;
                        border: 2px solid #E0E0E0;
                        border-radius: 10px;
                        opacity: 0.6;
                    }
                """)
                lbl_image.setStyleSheet("opacity: 0.5;")
                lbl_nom.setStyleSheet("color: #9E9E9E;")
                lbl_prix.setStyleSheet("color: #9E9E9E;")
            
            self.grid_layout.addWidget(product_card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def selectionner_produit(self, produit):
        """Sélectionne un produit et ferme le dialogue"""
        self.produit_selectionne = produit
        self.accept()
