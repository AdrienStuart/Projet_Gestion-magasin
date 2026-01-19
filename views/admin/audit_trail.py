"""
Audit & Traçabilité
Log des actions: qui/quoi/quand
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget,
                               QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from db.database import Database


class AuditTrail(QWidget):
    """
    Audit
    Traçabilité complète des opérations
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.rafraichir()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Titre
        lbl = QLabel("📋 JOURNAL D'AUDIT (7 DERNIERS JOURS)")
        lbl.setStyleSheet("""
            color: #58A6FF; font-size: 13pt; letter-spacing: 2px; font-weight: bold;
            background-color: #161B22; padding: 15px; border-radius: 8px;
            border: 1px solid #30363D; border-left: 4px solid #58A6FF;
        """)
        layout.addWidget(lbl)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Type", "Utilisateur", "Date", "Détails"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #161B22; gridline-color: #30363D;
                border: 1px solid #30363D; color: #C9D1D9; font-size: 10pt;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #21262D; color: #8B949E;
                padding: 10px; border: none; font-weight: bold;
            }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #30363D; }
            QTableWidget::item:selected { background-color: #1F6FEB; color: white; }
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
    
    def rafraichir(self):
        logs = Database.get_audit_log(limit=100)
        self.table.setRowCount(len(logs))
        
        for row, log in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(log['action']))
            self.table.setItem(row, 1, QTableWidgetItem(log['user']))
            
            # Format date
            timestamp = log['timestamp']
            date_str = timestamp.strftime("%d/%m/%Y %H:%M")
            self.table.setItem(row, 2, QTableWidgetItem(date_str))
            
            self.table.setItem(row, 3, QTableWidgetItem(log['details']))
