import os
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
                               QStackedWidget, QLabel, QFrame)
from PySide6.QtCore import Qt, QTimer
from datetime import datetime

from views.responsable_achats.purchasing_dashboard import PurchasingDashboard
from views.responsable_achats.alerts_processing_screen import AlertsProcessingScreen
from views.responsable_achats.supplier_orders_screen import SupplierOrdersScreen
from views.responsable_achats.purchasing_stats_screen import PurchasingStatsScreen

class PurchasingManagerView(QWidget):
    """
    Vue principale du Responsable Achats
    Style: Command Center (Sombre, Épuré, Décisionnel)
    """
    
    INDEX_DASHBOARD = 0
    INDEX_TRAITEMENT = 1
    INDEX_COMMANDES = 2
    INDEX_STATS = 3
    
    def __init__(self, id_utilisateur: int, nom_utilisateur: str):
        super().__init__()
        self.id_utilisateur = id_utilisateur
        self.nom_utilisateur = nom_utilisateur
        
        self.setWindowTitle("Responsable Achats - Command Center")
        self.resize(1280, 800)
        
        # Style global sombre
        self.setStyleSheet("background-color: #121212; color: #E0E0E0;")
        
        self.setup_ui()
        # Default screen
        self.afficher_dashboard()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        self._creer_sidebar(layout)
        
        # Main Area
        self.container_droit = QWidget()
        layout_droit = QVBoxLayout(self.container_droit)
        layout_droit.setContentsMargins(0, 0, 0, 0)
        layout_droit.setSpacing(0)
        
        # Top Bar
        self._creer_top_bar(layout_droit)
        
        # Stacked Widget
        self.stacked_widget = QStackedWidget()
        layout_droit.addWidget(self.stacked_widget)
        
        layout.addWidget(self.container_droit)
        
        # Initialisation des écrans
        self._init_screens()

    def _creer_sidebar(self, parent_layout):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet("background-color: #1E1E1E; border-right: 1px solid #333;")
        
        lay = QVBoxLayout(self.sidebar)
        lay.setContentsMargins(15, 30, 15, 30)
        lay.setSpacing(15)
        
        # Titre
        lbl = QLabel("ACHATS 🛒")
        lbl.setStyleSheet("color: #00E676; font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        lay.addWidget(lbl)
        
        # Boutons
        self.btn_dash = self._make_btn("📊 Dashboard", True)
        self.btn_dash.clicked.connect(self.afficher_dashboard)
        lay.addWidget(self.btn_dash)
        
        self.btn_process = self._make_btn("⚡ Traitement", False)
        self.btn_process.clicked.connect(self.afficher_traitement)
        lay.addWidget(self.btn_process)
        
        self.btn_orders = self._make_btn("📦 Commandes", False)
        self.btn_orders.clicked.connect(self.afficher_commandes)
        lay.addWidget(self.btn_orders)
        
        self.btn_stats = self._make_btn("📈 Statistiques", False)
        self.btn_stats.clicked.connect(self.afficher_stats)
        lay.addWidget(self.btn_stats)
        
        lay.addStretch()
        
        # User & Logout
        lbl_user = QLabel(f"👤 {self.nom_utilisateur}")
        lbl_user.setStyleSheet("color: #757575;")
        lay.addWidget(lbl_user)
        
        btn_logout = QPushButton("🚪 Déconnexion")
        btn_logout.setStyleSheet("color: #FF5252; background: transparent; border: 1px solid #FF5252; padding: 8px; border-radius: 5px;")
        btn_logout.clicked.connect(self._logout)
        lay.addWidget(btn_logout)
        
        parent_layout.addWidget(self.sidebar)

    def _make_btn(self, text, active):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setFixedHeight(50)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #B0BEC5; font-size: 11pt; text-align: left; padding-left: 15px; border-radius: 8px;
            }
            QPushButton:checked {
                background-color: #263238; color: #00E676; border-left: 4px solid #00E676;
            }
            QPushButton:hover { background-color: #263238; }
        """)
        return btn

    def _creer_top_bar(self, layout):
        bar = QFrame()
        bar.setFixedHeight(60)
        bar.setStyleSheet("background-color: #1E1E1E; border-bottom: 1px solid #333;")
        l = QHBoxLayout(bar)
        
        self.lbl_page_title = QLabel("TABLEAU DE BORD")
        self.lbl_page_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: white;")
        l.addWidget(self.lbl_page_title)
        
        l.addStretch()
        
        self.lbl_time = QLabel()
        self.lbl_time.setStyleSheet("color: #90A4AE; font-size: 12pt;")
        l.addWidget(self.lbl_time)
        
        layout.addWidget(bar)
        
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.lbl_time.setText(datetime.now().strftime("%H:%M:%S")))
        timer.start(1000)

    def _init_screens(self):
        self.screen_dashboard = PurchasingDashboard()
        self.screen_process = AlertsProcessingScreen(self.id_utilisateur)
        self.screen_orders = SupplierOrdersScreen(self.id_utilisateur)
        self.screen_stats = PurchasingStatsScreen()
        
        self.stacked_widget.addWidget(self.screen_dashboard)
        self.stacked_widget.addWidget(self.screen_process)
        self.stacked_widget.addWidget(self.screen_orders)
        self.stacked_widget.addWidget(self.screen_stats)
        
    def _update_nav(self, btn, idx, title):
        for b in [self.btn_dash, self.btn_process, self.btn_orders, self.btn_stats]:
            b.setChecked(b == btn)
        self.stacked_widget.setCurrentIndex(idx)
        self.lbl_page_title.setText(title)
        
        # Rafraîchir l'écran actif si nécessaire
        widget = self.stacked_widget.widget(idx)
        if hasattr(widget, 'rafraichir'):
            widget.rafraichir()

    def afficher_dashboard(self):
        self._update_nav(self.btn_dash, self.INDEX_DASHBOARD, "TABLEAU DE BORD - ARBITRAGE")
        
    def afficher_traitement(self):
        self._update_nav(self.btn_process, self.INDEX_TRAITEMENT, "TRAITEMENT DES ALERTES")
        
    def afficher_commandes(self):
        self._update_nav(self.btn_orders, self.INDEX_COMMANDES, "SUIVI COMMANDES FOURNISSEURS")

    def afficher_stats(self):
        self._update_nav(self.btn_stats, self.INDEX_STATS, "STATISTIQUES & PERFORMANCES")

    def _logout(self):
        if hasattr(self, 'controller'): self.controller.logout()
        else: self.close()
