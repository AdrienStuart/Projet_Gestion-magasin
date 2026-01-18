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
    Écran des alertes et signalements persistants
    Affiche les données de la table AlerteStock
    """
    
    def __init__(self, id_utilisateur: int):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        self.setup_ui()
        self.charger_alertes()
    
    def setup_ui(self):
        """Construction de l'interface"""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 25, 25, 25)
        layout_principal.setSpacing(25)
        
        # Filtres simples (Actives / Toutes)
        self._creer_barre_recherche(layout_principal)
        
        # Section Alertes Actives
        self._creer_section_actives(layout_principal)
        
        # Section Historique (Optionnelle/Repliable)
        self._creer_actions(layout_principal)
    
    def _creer_barre_recherche(self, parent_layout):
        frame = QFrame()
        frame.setStyleSheet("background-color: #2A2A40; border-radius: 8px; padding: 10px;")
        layout = QHBoxLayout(frame)
        
        lbl = QLabel("🔔 JOURNAL DES SIGNALEMENTS")
        lbl.setStyleSheet("color: white; font-size: 14pt; font-weight: bold;")
        layout.addWidget(lbl)
        
        layout.addStretch()
        
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.setFixedWidth(120)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_refresh.clicked.connect(self.charger_alertes)
        layout.addWidget(btn_refresh)
        
        parent_layout.addWidget(frame)

    def _creer_section_actives(self, parent_layout):
        """Tableau principal des alertes"""
        self.group_alertes = QGroupBox("🚧 Alertes en cours de traitement")
        self.group_alertes.setStyleSheet("""
            QGroupBox {
                font-size: 13pt;
                font-weight: bold;
                color: #2A2A40;
                border: 2px solid #E0E0E0;
                border-radius: 10px;
                margin-top: 20px;
                padding-top: 30px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                background-color: #F8F9FA;
            }
        """)
        
        layout = QVBoxLayout(self.group_alertes)
        
        self.table_alertes = QTableWidget()
        self.table_alertes.setColumnCount(7)
        self.table_alertes.setHorizontalHeaderLabels([
            "ID", "Priorité", "Statut", "Produit", "Stock/Seuil", "Date Création", "Actions"
        ])
        
        header = self.table_alertes.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        self.table_alertes.setColumnWidth(6, 180)
        
        self.table_alertes.verticalHeader().setVisible(False)
        self.table_alertes.verticalHeader().setDefaultSectionSize(60)
        self.table_alertes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_alertes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.table_alertes.setStyleSheet("""
            QTableWidget {
                font-size: 12pt;
                border: none;
                gridline-color: #F0F0F0;
            }
            QHeaderView::section {
                background-color: #2A2A40;
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
            }
        """)
        
        layout.addWidget(self.table_alertes)
        parent_layout.addWidget(self.group_alertes, stretch=1)

    def _creer_actions(self, parent_layout):
        layout = QHBoxLayout()
        
        lbl_info = QLabel("💡 Astuce: Les alertes sont archivées automatiquement quand le stock remonte.")
        lbl_info.setStyleSheet("color: #757575; font-style: italic;")
        layout.addWidget(lbl_info)
        
        layout.addStretch()
        
        self.btn_liste_reappro = QPushButton("📋 Liste de Réapprovisionnement")
        self.btn_liste_reappro.setFixedHeight(45)
        self.btn_liste_reappro.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 20px;
            }
        """)
        self.btn_liste_reappro.clicked.connect(self.generer_liste_reappro)
        layout.addWidget(self.btn_liste_reappro)
        
        parent_layout.addLayout(layout)

    def charger_alertes(self):
        """Charge les données de AlerteStock"""
        alertes = Database.get_persistent_alerts()
        self.afficher_alertes(alertes)

    def afficher_alertes(self, alertes):
        self.table_alertes.setRowCount(0)
        
        if not alertes:
            self.table_alertes.insertRow(0)
            item = QTableWidgetItem("✨ Aucune alerte de stock active. Beau travail !")
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QColor("#4CAF50"))
            self.table_alertes.setItem(0, 0, item)
            self.table_alertes.setSpan(0, 0, 1, 7)
            return

        for a in alertes:
            # On n'affiche que les alertes non archivées dans la vue principale
            if a['statut'] in ['ARCHIVEE', 'COMMANDE_PASSEE']: continue
            
            row = self.table_alertes.rowCount()
            self.table_alertes.insertRow(row)
            
            # ID
            self.table_alertes.setItem(row, 0, QTableWidgetItem(f"#{a['id_alerte']}"))
            
            # Priorité
            item_prio = QTableWidgetItem(a['priorite'])
            item_prio.setTextAlignment(Qt.AlignCenter)
            color = "#000000"
            bg_color = "#FFFFFF"
            if a['priorite'] == 'CRITICAL': 
                bg_color = "#FFEBEE"; color = "#D32F2F"
            elif a['priorite'] == 'HIGH':
                bg_color = "#FFF3E0"; color = "#EF6C00"
            elif a['priorite'] == 'MEDIUM':
                bg_color = "#E3F2FD"; color = "#1976D2"
            
            item_prio.setBackground(QColor(bg_color))
            item_prio.setForeground(QColor(color))
            font = QFont(); font.setBold(True)
            item_prio.setFont(font)
            self.table_alertes.setItem(row, 1, item_prio)
            
            # Statut
            item_statut = QTableWidgetItem(a['statut'].replace('_', ' '))
            item_statut.setTextAlignment(Qt.AlignCenter)
            self.table_alertes.setItem(row, 2, item_statut)
            
            # Produit
            item_prod = QTableWidgetItem(a['nom_produit'])
            item_prod.setFont(font)
            self.table_alertes.setItem(row, 3, item_prod)
            
            # Stock/Seuil
            item_valeurs = QTableWidgetItem(f"{a['stock_alerte']} / {a['seuil_vise']}")
            item_valeurs.setTextAlignment(Qt.AlignCenter)
            self.table_alertes.setItem(row, 4, item_valeurs)
            
            # Date
            date_str = a['date_creation'].strftime("%d/%m %H:%M")
            self.table_alertes.setItem(row, 5, QTableWidgetItem(date_str))
            
            # ACTIONS
            container = QWidget()
            lay = QHBoxLayout(container)
            lay.setContentsMargins(5, 5, 5, 5)
            lay.setSpacing(5)
            
            btn_vu = QPushButton("👁️")
            btn_vu.setToolTip("Marquer comme VU")
            btn_vu.setFixedSize(35, 35)
            btn_vu.clicked.connect(lambda _, aid=a['id_alerte']: self.update_statut(aid, 'VU'))
            
            btn_process = QPushButton("🔧")
            btn_process.setToolTip("En cours de traitement")
            btn_process.setFixedSize(35, 35)
            btn_process.clicked.connect(lambda _, aid=a['id_alerte']: self.update_statut(aid, 'EN_COURS'))

            btn_archive = QPushButton("📁")
            btn_archive.setToolTip("Archiver")
            btn_archive.setFixedSize(35, 35)
            btn_archive.clicked.connect(lambda _, aid=a['id_alerte']: self.update_statut(aid, 'ARCHIVEE'))
            
            lay.addWidget(btn_vu); lay.addWidget(btn_process); lay.addWidget(btn_archive)
            self.table_alertes.setCellWidget(row, 6, container)

    def update_statut(self, alert_id, new_status):
        if Database.update_alert_status(alert_id, new_status):
            self.charger_alertes()
        else:
            QMessageBox.critical(self, "Erreur", "Impossible de mettre à jour le statut.")

    def generer_liste_reappro(self):
        """Dialogue de liste de réapprovisionnement"""
        from PySide6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox
        
        produits = Database.get_products_to_restock()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("📋 Liste de Réapprovisionnement")
        dialog.resize(600, 450)
        lay = QVBoxLayout(dialog)
        
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setFont(QFont("Monospace", 10))
        
        content = "=== LISTE DE RÉAPPROVISIONNEMENT ===\n"
        content += f"Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        content += "-" * 40 + "\n\n"
        
        for p in produits:
            content += f"• {p['nom']} :\n"
            content += f"  Stock actuel : {p['stockactuel']} | Seuil : {p['stockalerte']}\n"
            content += f"  QUANTITÉ SUGGÉRÉE : {p['qte_suggere']} unités\n\n"
        
        txt.setPlainText(content)
        lay.addWidget(txt)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok)
        btns.accepted.connect(dialog.accept)
        lay.addWidget(btns)
        
        dialog.exec()

    def rafraichir(self):
        self.charger_alertes()
