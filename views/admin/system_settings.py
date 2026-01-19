"""
Gouvernance Système
Configuration seuils, TVA, règles, gestion utilisateurs
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                               QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
                               QMessageBox, QInputDialog)
from PySide6.QtCore import Qt
from db.database import Database


class SystemSettings(QWidget):
    """
    Gouvernance
    Seul l'admin a accès: paramétrage système
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.rafraichir()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)
        
        # Section Utilisateurs
        frame_users = QFrame()
        frame_users.setStyleSheet("""
            QFrame {
                background-color: #161B22; border: 1px solid #30363D;
                border-left: 4px solid #58A6FF; border-radius: 8px;
            }
        """)
        users_lay = QVBoxLayout(frame_users)
        users_lay.setContentsMargins(20, 15, 20, 15)
        
        lbl_users = QLabel("👥 GESTION UTILISATEURS")
        lbl_users.setStyleSheet("color: #58A6FF; font-weight: bold; font-size: 11pt;")
        users_lay.addWidget(lbl_users)
        
        self.table_users = self._create_table(["ID", "Nom", "Rôle", "Email"])
        users_lay.addWidget(self.table_users)
        
        layout.addWidget(frame_users)
        
        # Section Configuration Produits
        frame_config = QFrame()
        frame_config.setStyleSheet("""
            QFrame {
                background-color: #161B22; border: 1px solid #30363D;
                border-left: 4px solid #2EA043; border-radius: 8px;
            }
        """)
        config_lay = QVBoxLayout(frame_config)
        config_lay.setContentsMargins(20, 15, 20, 15)
        
        lbl_config = QLabel("⚙️ CONFIGURATION SEUILS")
        lbl_config.setStyleSheet("color: #2EA043; font-weight: bold; font-size: 11pt;")
        config_lay.addWidget(lbl_config)
        
        info = QLabel("Les seuils de stock peuvent être modifiés individuellement via:\n"
                     "Gestionnaire Stock → Tableau produits → Double-clic")
        info.setStyleSheet("color: #8B949E; font-size: 10pt; padding: 10px;")
        info.setWordWrap(True)
        config_lay.addWidget(info)
        
        layout.addWidget(frame_config)
        layout.addStretch()
    
    def _create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet("""
            QTableWidget {
                background-color: transparent; gridline-color: #30363D;
                border: none; color: #C9D1D9; font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #21262D; color: #8B949E;
                padding: 8px; border: none; font-weight: bold;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #30363D; }
        """)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        return table
    
    def rafraichir(self):
        users = Database.get_system_users()
        self.table_users.setRowCount(len(users))
        
        for row, u in enumerate(users):
            self.table_users.setItem(row, 0, QTableWidgetItem(str(u['id_utilisateur'])))
            self.table_users.setItem(row, 1, QTableWidgetItem(u['nom']))
            self.table_users.setItem(row, 2, QTableWidgetItem(u['role']))
            self.table_users.setItem(row, 3, QTableWidgetItem(u['email']))
