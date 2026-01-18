"""
Vue principale du module Caissier
Architecture avec sidebar et écrans multiples
L'écran de vente (Nouvelle Vente) est le point central et par défaut
"""

from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                               QStackedWidget, QLabel, QFrame)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont
import qtawesome as qta
from datetime import datetime

# Importer les écrans
from views.caissier.sale_screen import EcranVente
from views.caissier.history_screen import EcranHistorique
from views.caissier.stats_screen import EcranStatistiques


class CashierView(QWidget):
    """
    Vue principale du caissier avec sidebar
    Principe: L'écran de vente est le point d'entrée, de sortie, et de sécurité mentale
    """
    
    # Index des écrans
    INDEX_VENTE = 0
    INDEX_HISTORIQUE = 1
    INDEX_STATS = 2
    INDEX_PARAMETRES = 3  # Réservé pour future implémentation
    
    def __init__(self, id_utilisateur: int = 1, nom_utilisateur: str = "Caissier"):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        self.nom_utilisateur = nom_utilisateur
        self.is_sidebar_collapsed = False
        
        self.setup_ui()
        
        # Toujours commencer par l'écran de vente
        self.afficher_ecran_vente()
    
    def setup_ui(self):
        """Construction de l'interface principale"""
        # Layout principal horizontal (sidebar + contenu)
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        
        # ========== SIDEBAR GAUCHE ==========
        self._creer_sidebar(layout_principal)
        
        # ========== ZONE PRINCIPALE DROITE ==========
        # Container pour top bar + écrans
        self.container_droit = QWidget()
        layout_droit = QVBoxLayout(self.container_droit)
        layout_droit.setContentsMargins(0, 0, 0, 0)
        layout_droit.setSpacing(0)
        
        # Top bar
        self._creer_topbar(layout_droit)
        
        # Stacked widget pour les écrans
        self.stacked_widget = QStackedWidget()
        layout_droit.addWidget(self.stacked_widget)
        
        # Initialiser les écrans
        self._initialiser_ecrans()
        
        layout_principal.addWidget(self.container_droit, stretch=1)
    
    def _creer_sidebar(self, parent_layout):
        """Sidebar de navigation (rétractile)"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #2A2A40;
                border-right: 1px solid #3E3E5E;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # Logo / Titre
        lbl_logo = QLabel("🏪 CAISSE")
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setStyleSheet("font-size: 16pt; font-weight: bold; color: #00C853; margin-bottom: 20px; border: none;")
        sidebar_layout.addWidget(lbl_logo)
        
        # Boutons de navigation
        self.btn_vente = self._creer_btn_sidebar("🛒 Nouvelle vente", self.INDEX_VENTE, True)
        sidebar_layout.addWidget(self.btn_vente)
        
        self.btn_historique = self._creer_btn_sidebar("📋 Historique", self.INDEX_HISTORIQUE, False)
        sidebar_layout.addWidget(self.btn_historique)
        
        self.btn_stats = self._creer_btn_sidebar("📊 Mes statistiques", self.INDEX_STATS, False)
        sidebar_layout.addWidget(self.btn_stats)
        
        # Paramètres (désactivé pour l'instant)
        self.btn_params = self._creer_btn_sidebar("⚙️ Paramètres", self.INDEX_PARAMETRES, False)
        self.btn_params.setEnabled(False)
        sidebar_layout.addWidget(self.btn_params)
        
        sidebar_layout.addStretch()
        
        # Info utilisateur en bas
        lbl_user = QLabel(f"👤 {self.nom_utilisateur}")
        lbl_user.setStyleSheet("color: #A0A0B0; font-size: 10pt; border: none;")
        lbl_user.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl_user)
        
        # Bouton déconnexion
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
        # Get controller from parent
        main_window = self.window()
        if hasattr(main_window, 'controller') and main_window.controller:
            btn_logout.clicked.connect(main_window.controller.logout)
        sidebar_layout.addWidget(btn_logout)
        
        parent_layout.addWidget(self.sidebar)
    
    def _creer_btn_sidebar(self, texte: str, index: int, checked: bool) -> QPushButton:
        """Crée un bouton de sidebar"""
        btn = QPushButton(texte)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setFixedHeight(50)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 15px;
                font-size: 12pt;
                color: white;
                border: none;
                border-radius: 8px;
                background-color: transparent;
            }
            QPushButton:checked {
                background-color: #00C853;
                font-weight: bold;
            }
            QPushButton:hover:!checked {
                background-color: #3E3E5E;
            }
            QPushButton:disabled {
                color: #757575;
            }
        """)
        btn.clicked.connect(lambda: self.changer_ecran(index))
        return btn
    
    def _creer_topbar(self, parent_layout):
        """Barre supérieure avec info shift et heure"""
        topbar = QFrame()
        topbar.setFixedHeight(50)
        topbar.setStyleSheet("""
            QFrame {
                background-color: #1E1E2E;
                border-bottom: 1px solid #3E3E5E;
            }
        """)
        
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)
        
        # Titre écran actuel
        self.lbl_titre_ecran = QLabel("NOUVELLE VENTE")
        self.lbl_titre_ecran.setStyleSheet("font-size: 13pt; font-weight: bold; color: #00C853; border: none;")
        topbar_layout.addWidget(self.lbl_titre_ecran)
        
        topbar_layout.addStretch()
        
        # Shift (optionnel - toujours affiché pour l'instant)
        lbl_shift = QLabel("📅 Shift du jour")
        lbl_shift.setStyleSheet("color: #A0A0B0; font-size: 10pt; margin-right: 20px; border: none;")
        topbar_layout.addWidget(lbl_shift)
        
        # Horloge
        self.lbl_heure = QLabel()
        self.lbl_heure.setStyleSheet("color: white; font-size: 11pt; font-weight: bold; border: none;")
        topbar_layout.addWidget(self.lbl_heure)
        
        # Timer pour l'horloge
        self.timer_heure = QTimer(self)
        self.timer_heure.timeout.connect(self._mettre_a_jour_heure)
        self.timer_heure.start(1000)
        self._mettre_a_jour_heure()
        
        parent_layout.addWidget(topbar)
    
    def _initialiser_ecrans(self):
        """Initialise et ajoute tous les écrans au stacked widget"""
        # Écran 0: Nouvelle vente (défaut)
        self.ecran_vente = EcranVente(self.id_utilisateur, self.nom_utilisateur)
        self.ecran_vente.vente_validee.connect(self._on_vente_validee)
        self.stacked_widget.addWidget(self.ecran_vente)
        
        # Écran 1: Historique
        self.ecran_historique = EcranHistorique(self.id_utilisateur)
        self.stacked_widget.addWidget(self.ecran_historique)
        
        # Écran 2: Statistiques
        self.ecran_stats = EcranStatistiques(self.id_utilisateur)
        self.stacked_widget.addWidget(self.ecran_stats)
        
        # Écran 3: Paramètres (placeholder)
        placeholder = QLabel("Paramètres\n(En développement)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 16pt; color: #757575;")
        self.stacked_widget.addWidget(placeholder)
    
    # ========== NAVIGATION ==========
    
    def changer_ecran(self, index: int):
        """Change l'écran affiché"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Mettre à jour le titre
        titres = ["NOUVELLE VENTE", "HISTORIQUE", "MES STATISTIQUES", "PARAMÈTRES"]
        if 0 <= index < len(titres):
            self.lbl_titre_ecran.setText(titres[index])
        
        # Mettre à jour les boutons
        self.btn_vente.setChecked(index == self.INDEX_VENTE)
        self.btn_historique.setChecked(index == self.INDEX_HISTORIQUE)
        self.btn_stats.setChecked(index == self.INDEX_STATS)
        self.btn_params.setChecked(index == self.INDEX_PARAMETRES)
        
        # Rafraîchir les données si nécessaire
        if index == self.INDEX_HISTORIQUE:
            self.ecran_historique.charger_historique()
        elif index == self.INDEX_STATS:
            self.ecran_stats.rafraichir()
    
    def afficher_ecran_vente(self):
        """Retourne à l'écran de vente (point de sécurité mentale)"""
        self.changer_ecran(self.INDEX_VENTE)
    
    def _on_vente_validee(self):
        """Callback quand une vente est validée avec succès"""
        # L'écran reste sur la vente (principe: point de sécurité)
        # Les stats et historique seront mis à jour automatiquement quand le caissier y navigue
        pass
    
    def _mettre_a_jour_heure(self):
        """Met à jour l'affichage de l'heure"""
        maintenant = datetime.now()
        self.lbl_heure.setText(maintenant.strftime("%H:%M:%S"))
