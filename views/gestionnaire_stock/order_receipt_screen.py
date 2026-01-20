import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, 
                               QLabel, QMessageBox, QFrame, QAbstractItemView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor, QFont
from db.database import Database

class OrderReceiptScreen(QWidget):
    """
    Écran de Réception des Commandes Fournisseurs
    Permet au Gestionnaire de Stock de valider l'entrée des marchandises.
    """
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # En-tête
        header = QHBoxLayout()
        lbl_titre = QLabel("RÉCEPTION DES COMMANDES")
        lbl_titre.setStyleSheet("color: white; font-size: 18pt; font-weight: bold;")
        header.addWidget(lbl_titre)
        header.addStretch()
        
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.setFixedWidth(120)
        btn_refresh.setStyleSheet("""
            QPushButton { background-color: #333; color: white; border: 1px solid #555; padding: 8px; border-radius: 5px; }
            QPushButton:hover { background-color: #444; }
        """)
        btn_refresh.clicked.connect(self.rafraichir)
        header.addWidget(btn_refresh)
        
        layout.addLayout(header)
        
        # Explication
        lbl_info = QLabel("Validez la réception des commandes pour mettre à jour les stocks automatiquement.")
        lbl_info.setStyleSheet("color: #90A4AE; font-size: 10pt; font-style: italic;")
        layout.addWidget(lbl_info)
        
        # Tableau
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID Achat", "Date", "Fournisseur", "Articles", "Montant", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                color: #E0E0E0;
                gridline-color: #333;
                border: 1px solid #333;
                font-size: 10pt;
            }
            QTableWidget::item { padding: 10px; }
            QHeaderView::section {
                background-color: #263238;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)
        
    def rafraichir(self):
        """Charge les commandes en attente"""
        self.table.setRowCount(0)
        orders = Database.get_pending_purchases()
        
        if not orders:
            self.table.setRowCount(1)
            item = QTableWidgetItem("Aucune commande en attente de réception.")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 6)
            return
            
        self.table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            # order is a dict (RealDictCursor) or tuple? Check Query.
            # Query uses fetchall. Assuming dict if using RealDictCursor globally or manually configured.
            # Based on previous file reads, Database methods often assume dict access if configured, but let's be safe.
            # The method added uses `cur = connection.get_cursor(conn)` which returns RealDictCursor usually in this project context.
            
            # Access keys: Id_Achat, DateAchat, NomFournisseur, NbProduits, MontantTotal
            # Note: Postgres returns keys in lowercase usually with psycopg2 extras? Let's check keys used in 'get_purchasing_dashboard_summary'.
            # Yes, fetchone()['count']. Keys are likely lowercase.
            
            oid = order.get('id_achat')
            date = order.get('dateachat').strftime("%d/%m/%Y") if order.get('dateachat') else ""
            fourn = order.get('nomfournisseur', "")
            nb = order.get('nbproduits', 0)
            montant = order.get('montanttotal', 0)
            
            self.table.setItem(row, 0, QTableWidgetItem(f"Cmd #{oid}"))
            self.table.setItem(row, 1, QTableWidgetItem(date))
            self.table.setItem(row, 2, QTableWidgetItem(fourn))
            
            itm_nb = QTableWidgetItem(str(nb))
            itm_nb.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, itm_nb)
            
            itm_total = QTableWidgetItem(f"{montant:,.0f} FCFA")
            itm_total.setForeground(QColor("#00E676"))
            itm_total.setTextAlignment(Qt.AlignRight)
            self.table.setItem(row, 4, itm_total)
            
            # Button Action
            btn_container = QWidget()
            l_btn = QHBoxLayout(btn_container)
            l_btn.setContentsMargins(5, 5, 5, 5)
            
            btn_recevoir = QPushButton("✅ Valider Réception")
            btn_recevoir.setCursor(Qt.PointingHandCursor)
            btn_recevoir.setStyleSheet("""
                QPushButton { background-color: #2962FF; color: white; border-radius: 4px; padding: 5px; font-weight: bold; }
                QPushButton:hover { background-color: #448AFF; }
            """)
            btn_recevoir.clicked.connect(lambda _, x=oid: self.recevoir_commande(x))
            
            l_btn.addWidget(btn_recevoir)
            self.table.setCellWidget(row, 5, btn_container)
            
    def recevoir_commande(self, order_id):
        """Valide la réception"""
        reply = QMessageBox.question(self, "Confirmer Réception", 
                                     f"Confirmez-vous la réception complète de la commande #{order_id} ?\n\nCela mettra à jour les stocks immédiatement.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            success = Database.confirm_purchase_receipt(order_id, self.user_id)
            if success:
                QMessageBox.information(self, "Succès", f"Commande #{order_id} réceptionnée avec succès.\nStocks mis à jour.")
                self.rafraichir()
            else:
                QMessageBox.critical(self, "Erreur", "Une erreur est survenue lors de la validation.")

