"""
Module Administrateur
Rôle: Gouvernance, Pilotage, Contrôle
L'admin observe, compare, tranche - il n'opère pas
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                               QStackedWidget, QLabel, QFrame)
from PySide6.QtCore import Qt, QTimer
from datetime import datetime

# Import des écrans
from views.admin.strategic_dashboard import StrategicDashboard
from views.admin.commercial_performance import CommercialPerformance
from views.admin.stock_governance import StockGovernance
from views.admin.system_settings import SystemSettings
from views.admin.audit_trail import AuditTrail


class AdminView(QWidget):
    """
    Vue principale Administrateur
    Style: Executive, professionnel, clean
    """
    
    INDEX_DASHBOARD = 0
    INDEX_PERFORMANCE = 1
    INDEX_STOCK = 2
    INDEX_SETTINGS = 3
    INDEX_AUDIT = 4
    
    def __init__(self, user_id: int = 1, user_name: str = "Admin"):
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name
        
        self.setWindowTitle("Administration - Pilotage Stratégique")
        self.resize(1400, 850)
        
        # Style exécutif sombre
        self.setStyleSheet("background-color: #0D1117; color: #E6EDF3;")
        
        self.setup_ui()
        self.afficher_dashboard()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        self._creer_sidebar(layout)
        
        # Zone principale
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
        
        # Init screens
        self._init_screens()
    
    def _creer_sidebar(self, parent_layout):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setStyleSheet("background-color: #161B22; border-right: 1px solid #30363D;")
        
        lay = QVBoxLayout(self.sidebar)
        lay.setContentsMargins(15, 30, 15, 30)
        lay.setSpacing(12)
        
        # Logo
        lbl = QLabel("⚙️ ADMINISTRATION")
        lbl.setStyleSheet("color: #58A6FF; font-size: 16pt; font-weight: bold; margin-bottom: 25px;")
        lay.addWidget(lbl)
        
        # Navigation
        self.btn_dash = self._make_btn("📊 Dashboard", True)
        self.btn_dash.clicked.connect(self.afficher_dashboard)
        lay.addWidget(self.btn_dash)
        
        self.btn_perf = self._make_btn("📈 Performance", False)
        self.btn_perf.clicked.connect(self.afficher_performance)
        lay.addWidget(self.btn_perf)
        
        self.btn_stock = self._make_btn("📦 Pilotage Stocks", False)
        self.btn_stock.clicked.connect(self.afficher_stock)
        lay.addWidget(self.btn_stock)
        
        self.btn_settings = self._make_btn("⚙️ Gouvernance", False)
        self.btn_settings.clicked.connect(self.afficher_settings)
        lay.addWidget(self.btn_settings)
        
        self.btn_audit = self._make_btn("🔍 Audit", False)
        self.btn_audit.clicked.connect(self.afficher_audit)
        lay.addWidget(self.btn_audit)
        
        lay.addStretch()
        
        # User info
        lbl_user = QLabel(f"👤 {self.user_name}")
        lbl_user.setStyleSheet("color: #8B949E; font-size: 10pt;")
        lay.addWidget(lbl_user)
        
        # Logout
        btn_logout = QPushButton("🚪 Déconnexion")
        btn_logout.setStyleSheet("""
            QPushButton {
                color: #F85149; background: transparent; border: 1px solid #F85149;
                padding: 8px; border-radius: 6px; font-size: 10pt;
            }
            QPushButton:hover { background-color: rgba(248, 81, 73, 0.1); }
        """)
        btn_logout.clicked.connect(self._logout)
        lay.addWidget(btn_logout)
        
        parent_layout.addWidget(self.sidebar)
    
    def _make_btn(self, text, active):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setFixedHeight(48)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #C9D1D9; font-size: 11pt;
                text-align: left; padding-left: 18px; border-radius: 8px; border: none;
            }
            QPushButton:checked {
                background-color: #1F6FEB; color: white; font-weight: bold;
            }
            QPushButton:hover:!checked {
                background-color: #21262D;
            }
        """)
        return btn
    
    def _creer_top_bar(self, layout):
        bar = QFrame()
        bar.setFixedHeight(70)
        bar.setStyleSheet("background-color: #161B22; border-bottom: 1px solid #30363D;")
        
        l = QHBoxLayout(bar)
        l.setContentsMargins(30, 0, 30, 0)
        
        self.lbl_page_title = QLabel("TABLEAU DE BORD STRATÉGIQUE")
        self.lbl_page_title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #E6EDF3;")
        l.addWidget(self.lbl_page_title)
        
        l.addStretch()
        
        self.lbl_time = QLabel()
        self.lbl_time.setStyleSheet("color: #8B949E; font-size: 12pt;")
        l.addWidget(self.lbl_time)
        
        layout.addWidget(bar)
        
        # Timer
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.lbl_time.setText(datetime.now().strftime("%d/%m/%Y %H:%M")))
        timer.start(1000)
        self.lbl_time.setText(datetime.now().strftime("%d/%m/%Y %H:%M"))
    
    def _init_screens(self):
        self.screen_dashboard = StrategicDashboard()
        self.screen_performance = CommercialPerformance()
        self.screen_stock = StockGovernance()
        self.screen_settings = SystemSettings()
        self.screen_audit = AuditTrail()
        
        self.stacked_widget.addWidget(self.screen_dashboard)
        self.stacked_widget.addWidget(self.screen_performance)
        self.stacked_widget.addWidget(self.screen_stock)
        self.stacked_widget.addWidget(self.screen_settings)
        self.stacked_widget.addWidget(self.screen_audit)
    
    def _update_nav(self, btn, idx, title):
        for b in [self.btn_dash, self.btn_perf, self.btn_stock, self.btn_settings, self.btn_audit]:
            b.setChecked(b == btn)
        self.stacked_widget.setCurrentIndex(idx)
        self.lbl_page_title.setText(title)
        
        # Refresh
        widget = self.stacked_widget.widget(idx)
        if hasattr(widget, 'rafraichir'):
            widget.rafraichir()
    
    def afficher_dashboard(self):
        self._update_nav(self.btn_dash, self.INDEX_DASHBOARD, "TABLEAU DE BORD STRATÉGIQUE")
    
    def afficher_performance(self):
        self._update_nav(self.btn_perf, self.INDEX_PERFORMANCE, "PERFORMANCE COMMERCIALE")
    
    def afficher_stock(self):
        self._update_nav(self.btn_stock, self.INDEX_STOCK, "PILOTAGE DES STOCKS")
    
    def afficher_settings(self):
        self._update_nav(self.btn_settings, self.INDEX_SETTINGS, "GOUVERNANCE SYSTÈME")
    
    def afficher_audit(self):
        self._update_nav(self.btn_audit, self.INDEX_AUDIT, "AUDIT & TRAÇABILITÉ")
    
    def _logout(self):
        if hasattr(self, 'controller'):
            self.controller.logout()
        else:
            self.close()
