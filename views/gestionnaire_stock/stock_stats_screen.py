import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QFrame, QGroupBox, QGridLayout,
                               QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from datetime import datetime, timedelta

from db.database import Database


class StockStatsScreen(QWidget):
    """
    Écran des statistiques de stock
    Graphiques réels avec Matplotlib et données DB
    """
    
    def __init__(self, id_utilisateur: int):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        
        # Style général de l'écran (fond plus aéré)
        self.setStyleSheet("background-color: #F5F7F9;")
        
        self.setup_ui()
        self.charger_statistiques()
    
    def setup_ui(self):
        """Construction de l'interface"""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 25, 25, 25)
        layout_principal.setSpacing(25)
        
        # 1. Filtres (Thème sombre cohérent avec le reste du module)
        self._creer_filtres(layout_principal)
        
        # 2. Cartes de résumé (Stats textuelles)
        self._creer_stats_textuelles(layout_principal)
        
        # 3. Zone Graphiques (Réels)
        self._creer_zone_graphiques(layout_principal)
        
    def _creer_filtres(self, parent_layout):
        """Zone de filtres avec thème sombre contrasté"""
        frame_filtres = QFrame()
        frame_filtres.setStyleSheet("""
            QFrame {
                background-color: #2A2A40;
                border-radius: 10px;
                padding: 12px;
            }
            QLabel {
                color: white;
                font-size: 11pt;
                font-weight: bold;
            }
        """)
        
        layout_filtres = QHBoxLayout(frame_filtres)
        
        lbl_periode = QLabel("📅 Période d'analyse :")
        layout_filtres.addWidget(lbl_periode)
        
        self.combo_periode = QComboBox()
        self.combo_periode.addItem("Aujourd'hui", 1)
        self.combo_periode.addItem("7 derniers jours", 7)
        self.combo_periode.addItem("30 derniers jours", 30)
        self.combo_periode.addItem("90 derniers jours", 90)
        self.combo_periode.setFixedWidth(220)
        self.combo_periode.setStyleSheet("""
            QComboBox {
                background-color: #3E3E5E;
                color: white;
                padding: 8px;
                border: 1px solid #4E4E6E;
                border-radius: 6px;
                font-size: 11pt;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.combo_periode.currentIndexChanged.connect(self.charger_statistiques)
        layout_filtres.addWidget(self.combo_periode)
        
        layout_filtres.addStretch()
        
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #00C853;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #00E676; }
        """)
        btn_refresh.clicked.connect(self.charger_statistiques)
        layout_filtres.addWidget(btn_refresh)
        
        parent_layout.addWidget(frame_filtres)

    def _creer_stats_textuelles(self, parent_layout):
        """Cartes de résumé KPI"""
        layout_stats = QHBoxLayout()
        layout_stats.setSpacing(20)
        
        self.card_entrees = self._creer_stat_card("📥", "ENTRÉES", "0", "#00C853")
        self.card_sorties = self._creer_stat_card("📤", "SORTIES", "0", "#F44336")
        self.card_mvts = self._creer_stat_card("🔄", "MOUVEMENTS", "0", "#2196F3")
        self.card_actifs = self._creer_stat_card("📦", "STOCK ACTIF", "0", "#FF9800")
        
        layout_stats.addWidget(self.card_entrees)
        layout_stats.addWidget(self.card_sorties)
        layout_stats.addWidget(self.card_mvts)
        layout_stats.addWidget(self.card_actifs)
        
        parent_layout.addLayout(layout_stats)

    def _creer_stat_card(self, icone: str, titre: str, valeur: str, couleur: str) -> QFrame:
        card = QFrame()
        card.setFixedHeight(110)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E0E0E0;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icone
        lbl_icone = QLabel(icone)
        lbl_icone.setFixedWidth(50)
        lbl_icone.setStyleSheet(f"font-size: 24pt; border: none; background: transparent;")
        lbl_icone.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_icone)
        
        # Texte (Titre + Valeur)
        layout_txt = QVBoxLayout()
        layout_txt.setSpacing(2)
        layout_txt.setAlignment(Qt.AlignCenter)
        
        lbl_titre = QLabel(titre)
        lbl_titre.setStyleSheet(f"color: #757575; font-size: 9pt; font-weight: bold; border: none; background: transparent;")
        layout_txt.addWidget(lbl_titre)
        
        lbl_valeur = QLabel(valeur)
        lbl_valeur.setStyleSheet(f"color: {couleur}; font-size: 18pt; font-weight: bold; border: none; background: transparent;")
        layout_txt.addWidget(lbl_valeur)
        
        layout.addLayout(layout_txt)
        
        card.lbl_valeur = lbl_valeur
        return card

    def _creer_zone_graphiques(self, parent_layout):
        """Zone contenant les graphiques Matplotlib réels"""
        layout_graphs = QHBoxLayout()
        layout_graphs.setSpacing(20)
        
        # 1. Graphique Entrées vs Sorties (Barres)
        self.group_barres = QGroupBox("📊 Volumes Entrées vs Sorties")
        self._styler_group(self.group_barres)
        lay_barres = QVBoxLayout(self.group_barres)
        
        self.figure_barres = Figure(figsize=(5, 4), dpi=100)
        self.canvas_barres = FigureCanvas(self.figure_barres)
        lay_barres.addWidget(self.canvas_barres)
        
        # 2. Graphique Évolution (Ligne)
        self.group_ligne = QGroupBox("📈 Activité Journalière Globale")
        self._styler_group(self.group_ligne)
        lay_ligne = QVBoxLayout(self.group_ligne)
        
        self.figure_ligne = Figure(figsize=(5, 4), dpi=100)
        self.canvas_ligne = FigureCanvas(self.figure_ligne)
        lay_ligne.addWidget(self.canvas_ligne)
        
        layout_graphs.addWidget(self.group_barres, stretch=1)
        layout_graphs.addWidget(self.group_ligne, stretch=1)
        
        parent_layout.addLayout(layout_graphs)

    def _styler_group(self, group):
        group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 12px;
                margin-top: 20px;
                padding: 15px;
                font-size: 12pt;
                font-weight: bold;
                color: #2A2A40;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                background-color: #F5F7F9;
                border-radius: 4px;
            }
        """)

    def charger_statistiques(self):
        """Charge les données et met à jour l'affichage"""
        periode = self.combo_periode.currentData()
        
        # 1. Stats globales
        stats = Database.get_stock_stats(periode)
        if stats:
            self.card_entrees.lbl_valeur.setText(f"{stats.get('total_entrees', 0 or 0):,}")
            self.card_sorties.lbl_valeur.setText(f"{stats.get('total_sorties', 0 or 0):,}")
            self.card_mvts.lbl_valeur.setText(f"{stats.get('total_mouvements', 0 or 0):,}")
            self.card_actifs.lbl_valeur.setText(f"{stats.get('produits_actifs', 0 or 0):,}")
        
        # 2. Données pour graphiques (Journalier ou Horaire)
        is_today = (periode == 1)
        
        if is_today:
            historique = Database.get_stock_history_hourly()
            if not historique: return
            
            dates = [f"{int(h['heure'])}h" for h in historique]
            entrees = [h['entrees'] for h in historique]
            sorties = [h['sorties'] for h in historique]
            totaux = [h['entrees'] + h['sorties'] for h in historique]
            xlabel_rot = 0
            label_fs = 9
        else:
            historique = Database.get_stock_history_daily(periode)
            if not historique: return
            
            dates = [h['jour'].strftime("%d/%m") for h in historique]
            entrees = [h['entrees'] for h in historique]
            sorties = [h['sorties'] for h in historique]
            totaux = [h['entrees'] + h['sorties'] for h in historique]
            xlabel_rot = 45
            label_fs = 8
        
        # --- Dessin Graphique 1 (Barres Groupées) ---
        self.figure_barres.clear()
        ax1 = self.figure_barres.add_subplot(111)
        import numpy as np
        x = np.arange(len(dates))
        width = 0.35
        
        ax1.bar(x - width/2, entrees, width, label='Entrées', color='#00C853', alpha=0.8)
        ax1.bar(x + width/2, sorties, width, label='Sorties', color='#F44336', alpha=0.8)
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(dates, rotation=xlabel_rot, fontsize=label_fs)
        ax1.legend(loc='upper left', fontsize=9)
        ax1.grid(True, linestyle='--', alpha=0.3)
        self.figure_barres.tight_layout()
        self.canvas_barres.draw()
        
        # --- Dessin Graphique 2 (Courbe Activité) ---
        self.figure_ligne.clear()
        ax2 = self.figure_ligne.add_subplot(111)
        ax2.plot(dates, totaux, marker='o', linestyle='-', color='#2196F3', linewidth=2, label='Flux Total')
        ax2.fill_between(dates, totaux, color='#2196F3', alpha=0.1)
        
        ax2.set_xticks(range(len(dates)))
        ax2.set_xticklabels(dates, rotation=xlabel_rot, fontsize=label_fs)
        ax2.legend(loc='upper left', fontsize=9)
        ax2.grid(True, linestyle='--', alpha=0.3)
        self.figure_ligne.tight_layout()
        self.canvas_ligne.draw()

    def rafraichir(self):
        self.charger_statistiques()

