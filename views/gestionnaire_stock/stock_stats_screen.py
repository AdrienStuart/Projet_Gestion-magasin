"""
Écran Statistiques Stock
Graphiques légitimes: Évolution, Entrées/Sorties
Limite: 2-3 graphiques max
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QComboBox, QFrame, QGroupBox)
from PySide6.QtCore import Qt
from datetime import datetime, timedelta

from db.database import Database


class StockStatsScreen(QWidget):
    """
    Écran des statistiques de stock
    Graphiques pertinents uniquement
    """
    
    def __init__(self, id_utilisateur: int):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        self.setup_ui()
        self.charger_statistiques()
    
    def setup_ui(self):
        """Construction de l'interface"""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)
        
        # Filtres période
        self._creer_filtres(layout_principal)
        
        # Zone graphiques (placeholder pour matplotlib)
        self._creer_zone_graphiques(layout_principal)
        
        # Note
        lbl_note = QLabel("💡 Les graphiques avancés seront ajoutés avec matplotlib dans une version future")
        lbl_note.setStyleSheet("color: #757575; font-size: 10pt; font-style: italic;")
        lbl_note.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(lbl_note)
    
    def _creer_filtres(self, parent_layout):
        """Filtres de période"""
        frame_filtres = QFrame()
        frame_filtres.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout_filtres = QHBoxLayout(frame_filtres)
        
        lbl_periode = QLabel("📅 Période:")
        lbl_periode.setStyleSheet("font-size: 11pt; font-weight: bold;")
        layout_filtres.addWidget(lbl_periode)
        
        self.combo_periode = QComboBox()
        self.combo_periode.addItem("7 derniers jours", 7)
        self.combo_periode.addItem("30 derniers jours", 30)
        self.combo_periode.addItem("3 derniers mois", 90)
        self.combo_periode.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 6px;
                font-size: 11pt;
                min-width: 180px;
            }
        """)
        self.combo_periode.currentIndexChanged.connect(self.charger_statistiques)
        layout_filtres.addWidget(self.combo_periode)
        
        layout_filtres.addStretch()
        
        parent_layout.addWidget(frame_filtres)
    
    def _creer_zone_graphiques(self, parent_layout):
        """Zone pour les graphiques (placeholder)"""
        # Graphique 1: Évolution du stock total
        group_evolution = QGroupBox("📈 Évolution du Stock Total")
        group_evolution.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
        """)
        
        layout_evolution = QVBoxLayout(group_evolution)
        
        self.lbl_graph_evolution = QLabel("📊 Graphique temporaire - Implémentation matplotlib à venir")
        self.lbl_graph_evolution.setMinimumHeight(200)
        self.lbl_graph_evolution.setAlignment(Qt.AlignCenter)
        self.lbl_graph_evolution.setStyleSheet("""
            QLabel {
                background-color: #F5F5F5;
                border: 2px dashed #BDBDBD;
                border-radius: 8px;
                color: #757575;
                font-size: 11pt;
            }
        """)
        layout_evolution.addWidget(self.lbl_graph_evolution)
        
        parent_layout.addWidget(group_evolution)
        
        # Graphique 2: Entrées vs Sorties
        group_mouvements = QGroupBox("📊 Entrées vs Sorties")
        group_mouvements.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
        """)
        
        layout_mouvements = QVBoxLayout(group_mouvements)
        
        self.lbl_graph_mouvements = QLabel("📊 Graphique temporaire - Implémentation matplotlib à venir")
        self.lbl_graph_mouvements.setMinimumHeight(200)
        self.lbl_graph_mouvements.setAlignment(Qt.AlignCenter)
        self.lbl_graph_mouvements.setStyleSheet("""
            QLabel {
                background-color: #F5F5F5;
                border: 2px dashed #BDBDBD;
                border-radius: 8px;
                color: #757575;
                font-size: 11pt;
            }
        """)
        layout_mouvements.addWidget(self.lbl_graph_mouvements)
        
        parent_layout.addWidget(group_mouvements)
        
        # Statistiques textuelles simples
        self._creer_stats_textuelles(parent_layout)
    
    def _creer_stats_textuelles(self, parent_layout):
        """Stats sous forme de texte (en attendant graphiques)"""
        group_stats = QGroupBox("📋 Résumé de la Période")
        group_stats.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
        """)
        
        layout_stats = QHBoxLayout(group_stats)
        layout_stats.setSpacing(30)
        
        # Total entrées
        self.lbl_total_entrees = self._creer_stat_card("📥", "Total Entrées", "0", "#00C853")
        layout_stats.addWidget(self.lbl_total_entrees)
        
        # Total sorties
        self.lbl_total_sorties = self._creer_stat_card("📤", "Total Sorties", "0", "#F44336")
        layout_stats.addWidget(self.lbl_total_sorties)
        
        # Mouvements totaux
        self.lbl_total_mvts = self._creer_stat_card("🔄", "Mouvements", "0", "#2196F3")
        layout_stats.addWidget(self.lbl_total_mvts)
        
        # Produits actifs
        self.lbl_produits_actifs = self._creer_stat_card("📦", "Produits Actifs", "0", "#FF9800")
        layout_stats.addWidget(self.lbl_produits_actifs)
        
        parent_layout.addWidget(group_stats)
    
    def _creer_stat_card(self, icone: str, titre: str, valeur: str, couleur: str) -> QFrame:
        """Crée une carte de statistique"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 5px solid {couleur};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        lbl_icone = QLabel(icone)
        lbl_icone.setStyleSheet(f"font-size: 24pt; color: {couleur};")
        lbl_icone.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_icone)
        
        lbl_titre = QLabel(titre)
        lbl_titre.setStyleSheet("font-size: 10pt; color: #757575; font-weight: bold;")
        lbl_titre.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_titre)
        
        lbl_valeur = QLabel(valeur)
        lbl_valeur.setStyleSheet(f"font-size: 18pt; color: {couleur}; font-weight: bold;")
        lbl_valeur.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_valeur)
        
        # Stocker le label pour mise à jour
        card.lbl_valeur = lbl_valeur
        
        return card
    
    # ========== LOGIQUE ==========
    
    def charger_statistiques(self):
        """Charge les statistiques"""
        periode_jours = self.combo_periode.currentData()
        
        # Récupérer les stats
        stats = Database.get_stock_stats(periode_jours)
        
        if stats:
            # Mettre à jour les cartes
            self.lbl_total_entrees.lbl_valeur.setText(str(stats.get('total_entrees', 0)))
            self.lbl_total_sorties.lbl_valeur.setText(str(stats.get('total_sorties', 0)))
            self.lbl_total_mvts.lbl_valeur.setText(str(stats.get('total_mouvements', 0)))
            self.lbl_produits_actifs.lbl_valeur.setText(str(stats.get('produits_actifs', 0)))
            
            # TODO: Mettre à jour les graphiques avec matplotlib
            # Exemple:
            # - Récupérer données journalières
            # - Créer FigureCanvas
            # - Afficher courbes/barres
    
    def rafraichir(self):
        """Rafraîchit les statistiques"""
        self.charger_statistiques()
