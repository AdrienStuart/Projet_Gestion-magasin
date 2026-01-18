"""
Écran Historique
Liste simple et claire des ventes du caissier
Filtres: Aujourd'hui / Hier / Ce mois
Pas de graphiques - table claire > graphes inutiles
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QLabel, QHeaderView,
                               QAbstractItemView, QMessageBox, QButtonGroup, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import qtawesome as qta

from db.database import Database


class EcranHistorique(QWidget):
    """
    Écran d'historique des ventes du caissier
    Consultation uniquement, pas d'actions dangereuses
    """
    
    def __init__(self, id_utilisateur: int):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        self.filtre_actuel = 'today'  # 'today', 'yesterday', 'month'
        
        self.setup_ui()
        self.charger_historique()
    
    def setup_ui(self):
        """Construction de l'interface"""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)
        
        # En-tête avec filtres
        self._creer_entete_filtres(layout_principal)
        
        # Table historique
        self._creer_table_historique(layout_principal)
        
        # Zone actions
        self._creer_zone_actions(layout_principal)
    
    def _creer_entete_filtres(self, parent_layout):
        """En-tête avec titre et boutons filtres"""
        layout_entete = QHBoxLayout()
        
        # Titre
        lbl_titre = QLabel("📋 HISTORIQUE DES VENTES")
        lbl_titre.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2A2A40;")
        layout_entete.addWidget(lbl_titre)
        
        layout_entete.addStretch()
        
        # Groupe de boutons filtres
        self.groupe_filtres = QButtonGroup(self)
        
        # Aujourd'hui
        self.btn_today = self._creer_btn_filtre("Aujourd'hui", "today", True)
        self.groupe_filtres.addButton(self.btn_today)
        layout_entete.addWidget(self.btn_today)
        
        # Hier
        self.btn_yesterday = self._creer_btn_filtre("Hier", "yesterday", False)
        self.groupe_filtres.addButton(self.btn_yesterday)
        layout_entete.addWidget(self.btn_yesterday)
        
        # Ce mois
        self.btn_month = self._creer_btn_filtre("Ce mois", "month", False)
        self.groupe_filtres.addButton(self.btn_month)
        layout_entete.addWidget(self.btn_month)
        
        parent_layout.addLayout(layout_entete)
    
    def _creer_btn_filtre(self, texte: str, filtre: str, checked: bool) -> QPushButton:
        """Crée un bouton filtre"""
        btn = QPushButton(texte)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #2A2A40;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 20px;
            }
            QPushButton:checked {
                background-color: #00C853;
                color: white;
            }
            QPushButton:hover {
                background-color: #4E4E6E;
                color: white;
            }
        """)
        btn.clicked.connect(lambda: self.changer_filtre(filtre))
        return btn
    
    def _creer_table_historique(self, parent_layout):
        """Table des ventes"""
        # Frame conteneur
        frame_table = QFrame()
        frame_table.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        layout_table = QVBoxLayout(frame_table)
        layout_table.setContentsMargins(10, 10, 10, 10)
        
        # Table
        self.table_historique = QTableWidget()
        self.table_historique.setColumnCount(6)
        self.table_historique.setHorizontalHeaderLabels([
            "N° Ticket", "Date/Heure", "Articles", "Total HT", "Total TTC", "Paiement"
        ])
        
        # Configuration
        header = self.table_historique.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # N° Ticket
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Date
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Articles
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # HT
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # TTC
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Paiement
        
        self.table_historique.verticalHeader().setVisible(False)
        self.table_historique.verticalHeader().setDefaultSectionSize(50)  # Plus de hauteur par ligne
        self.table_historique.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_historique.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_historique.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_historique.setAlternatingRowColors(True)
        self.table_historique.setStyleSheet("""
            QTableWidget {
                font-size: 13pt;
                alternate-background-color: #F0F4F8;
                background-color: white;
                gridline-color: #E0E0E0;
                border: none;
                color: #2A2A40;
            }
            QTableWidget::item {
                padding-left: 10px;
                border-bottom: 1px solid #E0E0E0;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #37474F;
                color: white;
                padding: 12px;
                font-size: 12pt;
                font-weight: bold;
                border: none;
            }
        """)
        
        # Double-clic pour voir détails
        self.table_historique.doubleClicked.connect(self.voir_details_vente)
        
        layout_table.addWidget(self.table_historique)
        
        parent_layout.addWidget(frame_table, stretch=1)
    
    def _creer_zone_actions(self, parent_layout):
        """Boutons d'action"""
        layout_actions = QHBoxLayout()
        layout_actions.setSpacing(10)
        
        layout_actions.addStretch()
        
        # Voir détails
        btn_details = QPushButton("🔍 Voir détails")
        btn_details.setFixedHeight(50)
        btn_details.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 30px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
        """)
        btn_details.clicked.connect(self.voir_details_vente)
        layout_actions.addWidget(btn_details)
        
        # Réimprimer reçu
        btn_reimprimer = QPushButton("🖨️ Réimprimer")
        btn_reimprimer.setFixedHeight(50)
        btn_reimprimer.setEnabled(False)  # Désactivé pour l'instant
        btn_reimprimer.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 30px;
            }
        """)
        layout_actions.addWidget(btn_reimprimer)
        
        parent_layout.addLayout(layout_actions)
    
    # ========== LOGIQUE ==========
    
    def changer_filtre(self, filtre: str):
        """Change le filtre et recharge les données"""
        self.filtre_actuel = filtre
        self.charger_historique()
    
    def charger_historique(self):
        """Charge l'historique des ventes selon le filtre"""
        self.table_historique.setRowCount(0)
        
        # Récupérer les ventes du caissier
        ventes = Database.get_cashier_sales_history(self.id_utilisateur, self.filtre_actuel)
        
        for vente in ventes:
            row = self.table_historique.rowCount()
            self.table_historique.insertRow(row)
            
            # N° Ticket
            self.table_historique.setItem(row, 0, QTableWidgetItem(str(vente.get('id_vente', ''))))
            
            # Date/Heure
            date_str = vente.get('date_vente', '')
            if date_str:
                # Format: JJ/MM/AAAA HH:MM
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(str(date_str))
                    date_str = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    pass
            self.table_historique.setItem(row, 1, QTableWidgetItem(date_str))
            
            # Nombre d'articles
            nb_articles = vente.get('nb_articles', 0)
            self.table_historique.setItem(row, 2, QTableWidgetItem(str(nb_articles)))
            
            # Total HT
            total_ht = vente.get('total_ht', 0)
            self.table_historique.setItem(row, 3, QTableWidgetItem(f"{total_ht:,.0f}"))
            
            # Total TTC
            total_ttc = vente.get('total_ttc', 0)
            item_ttc = QTableWidgetItem(f"{total_ttc:,.0f} FCFA")
            font_bold = QFont()
            font_bold.setBold(True)
            item_ttc.setFont(font_bold)
            self.table_historique.setItem(row, 4, item_ttc)
            
            # Mode paiement
            paiement = vente.get('mode_paiement', 'ESPECES')
            self.table_historique.setItem(row, 5, QTableWidgetItem(paiement))
    
    def voir_details_vente(self):
        """Affiche les détails d'une vente sélectionnée"""
        row = self.table_historique.currentRow()
        if row < 0:
            QMessageBox.information(self, "Sélection requise",
                                  "Veuillez sélectionner une vente dans le tableau.")
            return
        
        id_vente = int(self.table_historique.item(row, 0).text())
        
        # Récupérer les détails
        details = Database.get_sale_details(id_vente)
        
        if not details:
            QMessageBox.warning(self, "Erreur", "Impossible de charger les détails de la vente.")
            return
        
        # Construire le message de détails
        lignes = details.get('lignes', [])
        
        details_text = "<h2>Détails de la Vente</h2>"
        details_text += f"<p><b>N° Ticket:</b> {id_vente}</p>"
        details_text += f"<p><b>Date:</b> {details.get('date_vente', '')}</p>"
        details_text += "<hr>"
        details_text += "<h3>Articles:</h3><ul>"
        
        for ligne in lignes:
            nom = ligne.get('nom_produit', '')
            qte = ligne.get('qte_vendue', 0)
            prix = ligne.get('prix_unitaire', 0)
            total = ligne.get('total_ligne', 0)
            details_text += f"<li>{nom} x{qte} = {total:,.0f} FCFA</li>"
        
        details_text += "</ul><hr>"
        details_text += f"<p><b>Total TTC:</b> {details.get('total_ttc', 0):,.0f} FCFA</p>"
        
        # Afficher dans un message box
        msg = QMessageBox(self)
        msg.setWindowTitle("Détails de la Vente")
        msg.setText(details_text)
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("QLabel{min-width: 500px;}")
        msg.exec()
