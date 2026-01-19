import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QTableWidget, QTableWidgetItem, QPushButton, QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from db.database import Database

class SupplierOrdersScreen(QWidget):
    """
    ÉCRAN SUIVI DES COMMANDES FOURNISSEURS
    Vue tabulaire filtrable
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_filter = None
        self.rafraichir()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(20)
        
        # Header + Filtres
        top_layout = QHBoxLayout()
        
        lbl_title = QLabel("HISTORIQUE COMMANDES")
        lbl_title.setStyleSheet("color: #90A4AE; font-size: 14pt; font-weight: bold; letter-spacing: 1px;")
        top_layout.addWidget(lbl_title)
        
        top_layout.addStretch()
        
        self.btn_all = self._create_filter_btn("TOUT", None, True)
        self.btn_pending = self._create_filter_btn("EN ATTENTE", "EN_ATTENTE")
        self.btn_received = self._create_filter_btn("REÇUES", "RECU")
        # Note: 'RETARD' isn't a DB status, it's a computed state. 
        # For simplicity, we filter 'EN_ATTENTE' then sort or highlight in table.
        
        top_layout.addWidget(self.btn_all)
        top_layout.addWidget(self.btn_pending)
        top_layout.addWidget(self.btn_received)
        
        layout.addLayout(top_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "DATE", "FOURNISSEUR", "LIGNES", "STATUT"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E; gridline-color: #333; border: none; font-size: 11pt;
            }
            QHeaderView::section {
                background-color: #2D2D2D; color: #B0BEC5; padding: 10px; border: none; font-weight: bold;
            }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #2A2A2A; color: #E0E0E0; }
            QTableWidget::item:selected { background-color: #263238; color: white; }
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
    def _create_filter_btn(self, text, filter_val, active=False):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setFixedSize(120, 35)
        btn.setProperty("filter", filter_val)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #757575; border: 1px solid #424242; border-radius: 17px; font-weight: bold;
            }
            QPushButton:checked {
                background-color: #00E676; color: black; border: none;
            }
            QPushButton:hover:!checked { border-color: #00E676; color: #00E676; }
        """)
        btn.clicked.connect(lambda: self._apply_filter(btn))
        return btn
        
    def _apply_filter(self, sender):
        # Update UI state
        for b in [self.btn_all, self.btn_pending, self.btn_received]:
            b.setChecked(b == sender)
        
        self.current_filter = sender.property("filter")
        self.rafraichir()

    def rafraichir(self):
        self.table.setRowCount(0)
        orders = Database.get_supplier_orders(self.current_filter)
        
        self.table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            # ID
            self.table.setItem(row, 0, QTableWidgetItem(f"#{order['id_achat']}"))
            
            # Date
            date_str = order['date_achat'].strftime("%d/%m/%Y")
            self.table.setItem(row, 1, QTableWidgetItem(date_str))
            
            # Fournisseur
            self.table.setItem(row, 2, QTableWidgetItem(order['fournisseur']))
            
            # Lignes
            self.table.setItem(row, 3, QTableWidgetItem(f"{order['nb_lignes']} art."))
            
            # Statut
            status = order['statut']
            status_item = QTableWidgetItem(status)
            color = "#FF9100" if status == "EN_ATTENTE" else "#00E676" if status == "RECU" else "#9E9E9E"
            status_item.setForeground(QBrush(QColor(color)))
            status_item.setFont(Qt.font()) # Reset font but keeping color
            self.table.setItem(row, 4, status_item)

