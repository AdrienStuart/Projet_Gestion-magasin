"""
Vue principale du module Gestionnaire Stock
Architecture avec sidebar et écrans modulaires
Principe: Efficacité opérationnelle, pas de fioritures
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                               QStackedWidget, QLabel, QFrame)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon
import qtawesome as qta
from datetime import datetime

# Importer les écrans
from views.gestionnaire_stock.stock_table_screen import StockTableScreen
from views.gestionnaire_stock.movements_screen import MovementsScreen
from views.gestionnaire_stock.alerts_screen import AlertsScreen
from views.gestionnaire_stock.stock_stats_screen import StockStatsScreen
from views.gestionnaire_stock.signalements_screen import SignalementsScreen


class StockManagerView(QWidget):
    """
    Vue principale du gestionnaire de stock
    Architecture identique au Caissier (QWidget avec Layout)
    """
    
    # Index des écrans du StackedWidget
    INDEX_STOCK = 0
    INDEX_MOUVEMENTS = 1
    INDEX_ALERTES = 2
    INDEX_STATS = 3
    
    def __init__(self, id_utilisateur: int = 1, nom_utilisateur: str = "Gestionnaire"):
        super().__init__()
        
        self.setWindowTitle("Gestionnaire de Stock")
        self.resize(1280, 800) # Taille par défaut
        
        self.id_utilisateur = id_utilisateur
        self.nom_utilisateur = nom_utilisateur
        self.is_sidebar_collapsed = False
        
        self.setup_ui()
        self.afficher_tableau_stock()
        
        # Mode plein écran (Demandé explicitement)
        self.showMaximized()
    
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
        
        # Top bar (Style Caisse)
        self._creer_top_bar(layout_droit)
        
        # StackedWidget pour les écrans
        self.stacked_widget = QStackedWidget()
        self._initialiser_ecrans()
        layout_droit.addWidget(self.stacked_widget)
        
        layout_principal.addWidget(self.container_droit, stretch=1)
    
    def _creer_sidebar(self, parent_layout):
        """Crée la sidebar de navigation"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220) # Taille Caisse
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #2A2A40;
                border-right: 2px solid #3A3A50;
            }
        """)
        
        layout_sidebar = QVBoxLayout(self.sidebar)
        layout_sidebar.setContentsMargins(10, 20, 10, 20) # Marges Caisse
        layout_sidebar.setSpacing(10) # Espacement Caisse
        
        # Titre module
        lbl_module = QLabel("📦 STOCK")
        lbl_module.setStyleSheet("color: #00C853; font-size: 16pt; font-weight: bold; margin-bottom: 20px;")
        lbl_module.setAlignment(Qt.AlignCenter)
        layout_sidebar.addWidget(lbl_module)
        
        layout_sidebar.addSpacing(30)
        
        # Boutons navigation
        self.btn_stock = self._creer_btn_sidebar("📋", "Stock", True)
        self.btn_stock.clicked.connect(self.afficher_tableau_stock)
        layout_sidebar.addWidget(self.btn_stock)
        
        self.btn_mouvements = self._creer_btn_sidebar("🔄", "Mouvements", False)
        self.btn_mouvements.clicked.connect(self.afficher_mouvements)
        layout_sidebar.addWidget(self.btn_mouvements)
        
        self.btn_alertes = self._creer_btn_sidebar("⚠️", "Alertes (Vue Simple)", False)
        self.btn_alertes.clicked.connect(self.afficher_alertes)
        layout_sidebar.addWidget(self.btn_alertes)
        
        self.btn_signalements = self._creer_btn_sidebar("🚥", "Centre Signalements", False)
        self.btn_signalements.clicked.connect(self.afficher_signalements)
        layout_sidebar.addWidget(self.btn_signalements)
        
        self.btn_stats = self._creer_btn_sidebar("📊", "Statistiques", False)
        self.btn_stats.clicked.connect(self.afficher_statistiques)
        layout_sidebar.addWidget(self.btn_stats)
        
        layout_sidebar.addStretch()
        
        # Info utilisateur
        lbl_user = QLabel(f"👤 {self.nom_utilisateur}")
        lbl_user.setStyleSheet("color: #757575; font-size: 10pt; font-weight: bold;")
        lbl_user.setAlignment(Qt.AlignCenter)
        layout_sidebar.addWidget(lbl_user)

        # Bouton déconnexion (Style Caisse - Bas Sidebar)
        btn_logout = QPushButton("🚪 Déconnexion")
        btn_logout.setFixedHeight(45)
        btn_logout.setStyleSheet("""
            QPushButton {
                color: #FF3D00;
                background-color: transparent;
                border: 1px solid #FF3D00;
                border-radius: 8px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 61, 0, 0.1);
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
        btn.setFixedHeight(50) # Hauteur Caisse
        
        style_base = """
            QPushButton {
                background-color: transparent;
                color: #B0B0C0;
                font-size: 12pt; /* Police Caisse */
                font-weight: bold;
                border-radius: 10px;
                padding-left: 15px; /* Padding Caisse */
                text-align: left;
            }
            QPushButton:checked {
                background-color: #3A3A50;
                color: #00C853;
                border-left: 5px solid #00C853;
            }
            QPushButton:hover {
                background-color: #32324A;
                color: white;
            }
        """
        btn.setStyleSheet(style_base)
        return btn
    
    def _creer_top_bar(self, parent_layout):
        """Barre supérieure style Caisse (Sombre)"""
        top_bar = QFrame()
        top_bar.setFixedHeight(60) # Hauteur standard Caisse
        top_bar.setStyleSheet("""
            QFrame {
                background-color: #1E1E2E;
                border-bottom: 1px solid #3E3E5E;
            }
        """)
        
        layout_top = QHBoxLayout(top_bar)
        layout_top.setContentsMargins(20, 0, 20, 0)
        
        # Titre écran (Vert)
        self.lbl_titre_ecran = QLabel("TABLEAU DE STOCK")
        self.lbl_titre_ecran.setStyleSheet("font-size: 14pt; font-weight: bold; color: #00C853;")
        layout_top.addWidget(self.lbl_titre_ecran)
        
        layout_top.addStretch()
        
        # Shift Info (Style Caisse)
        lbl_shift = QLabel("📅 Session Gestionnaire")
        lbl_shift.setStyleSheet("color: #A0A0B0; font-size: 10pt; margin-right: 20px; font-weight: bold;")
        layout_top.addWidget(lbl_shift)
        
        # Date/Heure (Blanc)
        from datetime import datetime
        from PySide6.QtCore import QTimer
        
        self.lbl_heure = QLabel()
        self.lbl_heure.setStyleSheet("color: white; font-size: 12pt; font-weight: bold;")
        layout_top.addWidget(self.lbl_heure)
        
        # Timer Heure
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        self._update_time()
        
        parent_layout.addWidget(top_bar)

    def _update_time(self):
        self.lbl_heure.setText(datetime.now().strftime("%H:%M:%S"))
    
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
        
        # Écran 3: Signalements (Centre de Commande)
        self.ecran_signalements = SignalementsScreen(self.id_utilisateur)
        self.stacked_widget.addWidget(self.ecran_signalements)

        # Écran 4: Statistiques
        self.ecran_stats = StockStatsScreen(self.id_utilisateur)
        self.stacked_widget.addWidget(self.ecran_stats)
    
    # ========== NAVIGATION ==========
    
    def afficher_tableau_stock(self):
        """Affiche le tableau de stock"""
        self._update_active_btn(self.btn_stock)
        self.stacked_widget.setCurrentIndex(self.INDEX_STOCK)
        self.lbl_titre_ecran.setText("📋 Tableau de Stock")
        self.ecran_stock.rafraichir()
    
    def afficher_mouvements(self):
        """Affiche l'écran des mouvements"""
        self._update_active_btn(self.btn_mouvements)
        self.stacked_widget.setCurrentIndex(self.INDEX_MOUVEMENTS)
        self.lbl_titre_ecran.setText("🔄 Mouvements & Historique")
        self.ecran_mouvements.rafraichir()
    
    def afficher_alertes(self):
        """Affiche les alertes"""
        self._update_active_btn(self.btn_alertes)
        self.stacked_widget.setCurrentIndex(self.INDEX_ALERTES)
        self.lbl_titre_ecran.setText("⚠️ Alertes Stock")
        self.ecran_alertes.rafraichir()
    
    def afficher_signalements(self):
        """Affiche le Centre de Signalements"""
        self._update_active_btn(self.btn_signalements)
        self.stacked_widget.setCurrentIndex(self.INDEX_SIGNALEMENTS)
        self.lbl_titre_ecran.setText("🚥 Centre de Signalements")
        self.ecran_signalements.rafraichir()
    
    def afficher_statistiques(self):
        """Affiche les statistiques"""
        self._update_active_btn(self.btn_stats)
        self.stacked_widget.setCurrentIndex(self.INDEX_STATS)
        self.lbl_titre_ecran.setText("📊 Statistiques")
        self.ecran_stats.rafraichir()
    
    def _update_active_btn(self, btn_actif):
        """Active un bouton et désactive les autres"""
        for btn in [self.btn_stock, self.btn_mouvements, self.btn_alertes, self.btn_signalements, self.btn_stats]:
            btn.setChecked(btn == btn_actif)
    
    def _deconnecter(self):
        """Déconnexion"""
        # Signal vers le contrôleur principal
        if hasattr(self, 'controller') and self.controller:
            self.controller.logout()
        else:
            self.close()
