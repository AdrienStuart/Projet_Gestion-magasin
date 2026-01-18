"""
Vue principale du module Gestionnaire Stock
Architecture avec sidebar et écrans modulaires
Principe: Efficacité opérationnelle, pas de fioritures
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                               QStackedWidget, QLabel, QFrame)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
import qtawesome as qta
from datetime import datetime

# Importer les écrans
from views.gestionnaire_stock.stock_table_screen import StockTableScreen
from views.gestionnaire_stock.movements_screen import MovementsScreen
from views.gestionnaire_stock.alerts_screen import AlertsScreen
from views.gestionnaire_stock.stock_stats_screen import StockStatsScreen


class StockManagerView(QWidget):
    """
    Vue principale du gestionnaire de stock
    Interface sobre, dense, axée sur l'efficacité
    """
    
    # Index des écrans
    INDEX_STOCK = 0
    INDEX_MOUVEMENTS = 1
    INDEX_ALERTES = 2
    INDEX_STATS = 3
    
    def __init__(self, id_utilisateur: int = 1, nom_utilisateur: str = "Gestionnaire"):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        self.nom_utilisateur = nom_utilisateur
        self.is_sidebar_collapsed = False
        
        self.setup_ui()
        self.afficher_tableau_stock()
    
    def setup_ui(self):
        """Construction de l'interface principale"""
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        
        # ========== SIDEBAR GAUCHE ==========
        self._creer_sidebar(layout_principal)
        
        # ========== ZONE PRINCIPALE DROITE ==========
        self.container_droit = QWidget()
        layout_droit = QVBoxLayout(self.container_droit)
        layout_droit.setContentsMargins(0, 0, 0, 0)
        layout_droit.setSpacing(0)
        
        # Top bar
        self._creer_top_bar(layout_droit)
        
        # StackedWidget pour les écrans
        self.stacked_widget = QStackedWidget()
        self._initialiser_ecrans()
        layout_droit.addWidget(self.stacked_widget)
        
        layout_principal.addWidget(self.container_droit, stretch=1)
    
    def _creer_sidebar(self, parent_layout):
        """Crée la sidebar de navigation"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #2A2A40;
                border-right: 2px solid #3A3A50;
            }
        """)
        
        layout_sidebar = QVBoxLayout(self.sidebar)
        layout_sidebar.setContentsMargins(10, 20, 10, 20)
        layout_sidebar.setSpacing(5)
        
        # Titre module
        lbl_module = QLabel("📦 GESTION STOCK")
        lbl_module.setStyleSheet("color: white; font-size: 16pt; font-weight: bold; padding: 10px;")
        lbl_module.setAlignment(Qt.AlignCenter)
        layout_sidebar.addWidget(lbl_module)
        
        layout_sidebar.addSpacing(20)
        
        # Boutons navigation
        self.btn_stock = self._creer_btn_sidebar("📋", "Tableau de Stock", True)
        self.btn_stock.clicked.connect(self.afficher_tableau_stock)
        layout_sidebar.addWidget(self.btn_stock)
        
        self.btn_mouvements = self._creer_btn_sidebar("🔄", "Mouvements", False)
        self.btn_mouvements.clicked.connect(self.afficher_mouvements)
        layout_sidebar.addWidget(self.btn_mouvements)
        
        self.btn_alertes = self._creer_btn_sidebar("⚠️", "Alertes", False)
        self.btn_alertes.clicked.connect(self.afficher_alertes)
        layout_sidebar.addWidget(self.btn_alertes)
        
        self.btn_stats = self._creer_btn_sidebar("📊", "Statistiques", False)
        self.btn_stats.clicked.connect(self.afficher_statistiques)
        layout_sidebar.addWidget(self.btn_stats)
        
        layout_sidebar.addStretch()
        
        # Bouton déconnexion
        btn_logout = QPushButton("🔓 Déconnexion")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 6px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
        """)
        btn_logout.clicked.connect(self._deconnecter)
        layout_sidebar.addWidget(btn_logout)
        
        parent_layout.addWidget(self.sidebar)
    
    def _creer_btn_sidebar(self, icone: str, texte: str, actif: bool) -> QPushButton:
        """Crée un bouton de navigation"""
        btn = QPushButton(f"{icone}  {texte}")
        btn.setCheckable(True)
        btn.setChecked(actif)
        btn.setFixedHeight(50)
        
        style_base = """
            QPushButton {
                background-color: #3A3A50;
                color: #B0B0C0;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
                text-align: left;
            }
            QPushButton:checked {
                background-color: #00C853;
                color: white;
            }
            QPushButton:hover {
                background-color: #4E4E6E;
                color: white;
            }
        """
        btn.setStyleSheet(style_base)
        return btn
    
    def _creer_top_bar(self, parent_layout):
        """Barre de titre avec date"""
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-bottom: 2px solid #E0E0E0;
            }
        """)
        
        layout_top = QHBoxLayout(top_bar)
        layout_top.setContentsMargins(20, 10, 20, 10)
        
        # Titre écran (dynamique)
        self.lbl_titre_ecran = QLabel("Tableau de Stock")
        self.lbl_titre_ecran.setStyleSheet("font-size: 18pt; font-weight: bold; color: #2A2A40;")
        layout_top.addWidget(self.lbl_titre_ecran)
        
        layout_top.addStretch()
        
        # Date/Heure
        now = datetime.now()
        lbl_date = QLabel(now.strftime("%d/%m/%Y %H:%M"))
        lbl_date.setStyleSheet("font-size: 11pt; color: #757575;")
        layout_top.addWidget(lbl_date)
        
        parent_layout.addWidget(top_bar)
    
    def _initialiser_ecrans(self):
        """Initialise et ajoute tous les écrans"""
        # Écran 0: Tableau Stock
        self.ecran_stock = StockTableScreen(self.id_utilisateur)
        self.stacked_widget.addWidget(self.ecran_stock)
        
        # Écran 1: Mouvements
        self.ecran_mouvements = MovementsScreen(self.id_utilisateur, self.nom_utilisateur)
        self.stacked_widget.addWidget(self.ecran_mouvements)
        
        # Écran 2: Alertes
        self.ecran_alertes = AlertsScreen(self.id_utilisateur)
        self.stacked_widget.addWidget(self.ecran_alertes)
        
        # Écran 3: Statistiques
        self.ecran_stats = StockStatsScreen(self.id_utilisateur)
        self.stacked_widget.addWidget(self.ecran_stats)
    
    # ========== NAVIGATION ==========
    
    def afficher_tableau_stock(self):
        """Affiche le tableau de stock"""
        self._activer_bouton(self.btn_stock)
        self.stacked_widget.setCurrentIndex(self.INDEX_STOCK)
        self.lbl_titre_ecran.setText("📋 Tableau de Stock")
        self.ecran_stock.rafraichir()
    
    def afficher_mouvements(self):
        """Affiche l'écran des mouvements"""
        self._activer_bouton(self.btn_mouvements)
        self.stacked_widget.setCurrentIndex(self.INDEX_MOUVEMENTS)
        self.lbl_titre_ecran.setText("🔄 Mouvements de Stock")
        self.ecran_mouvements.rafraichir()
    
    def afficher_alertes(self):
        """Affiche les alertes"""
        self._activer_bouton(self.btn_alertes)
        self.stacked_widget.setCurrentIndex(self.INDEX_ALERTES)
        self.lbl_titre_ecran.setText("⚠️ Alertes Stock")
        self.ecran_alertes.rafraichir()
    
    def afficher_statistiques(self):
        """Affiche les statistiques"""
        self._activer_bouton(self.btn_stats)
        self.stacked_widget.setCurrentIndex(self.INDEX_STATS)
        self.lbl_titre_ecran.setText("📊 Statistiques Stock")
        self.ecran_stats.rafraichir()
    
    def _activer_bouton(self, btn_actif):
        """Active un bouton et désactive les autres"""
        for btn in [self.btn_stock, self.btn_mouvements, self.btn_alertes, self.btn_stats]:
            btn.setChecked(btn == btn_actif)
    
    def _deconnecter(self):
        """Déconnexion"""
        # Signal vers le contrôleur principal
        self.parent().parent().controller.logout()
