"""
Écran Statistiques
KPIs légers pour le caissier
Total encaissé / Nombre de tickets / Panier moyen
1 graphique max (optionnel): barres 7 derniers jours
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QFrame, QGridLayout, QPushButton, QButtonGroup)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import qtawesome as qta

from db.database import Database


class EcranStatistiques(QWidget):
    """
    Écran statistiques (consultation légère)
    Affichage sobre et lecture rapide
    """
    
    def __init__(self, id_utilisateur: int):
        super().__init__()
        
        self.id_utilisateur = id_utilisateur
        self.filtre_actuel = 'today'  # 'today', 'week', 'month'
        
        self.setup_ui()
        self.charger_statistiques()
    
    def setup_ui(self):
        """Construction de l'interface"""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)
        
        # En-tête avec filtres
        self._creer_entete_filtres(layout_principal)
        
        # Grille de KPIs
        self._creer_grille_kpis(layout_principal)
        
        # Zone graphique horaire (Nouveau)
        self._creer_zone_graphique(layout_principal)
        
        layout_principal.addStretch()
        
        # Note informative
        lbl_info = QLabel("💡 Survoler les barres pour voir les détails d'une tranche horaire.")
        lbl_info.setStyleSheet("color: #757575; font-size: 10pt; font-style: italic;")
        lbl_info.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(lbl_info)

    def _creer_zone_graphique(self, parent_layout):
        """Crée la zone pour le graphique d'activité horaire"""
        self.container_graphique = QFrame()
        self.container_graphique.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        self.container_graphique.setMinimumHeight(300)
        
        layout_graph = QVBoxLayout(self.container_graphique)
        
        lbl_graph_titre = QLabel("📈 ACTIVITÉ PAR TRANCHE HORAIRE (AUJOURD'HUI)")
        lbl_graph_titre.setStyleSheet("font-size: 11pt; font-weight: bold; color: #757575; margin-bottom: 10px;")
        layout_graph.addWidget(lbl_graph_titre)
        
        # Le layout qui contiendra les barres
        self.layout_barres = QHBoxLayout()
        self.layout_barres.setSpacing(10)
        self.layout_barres.setAlignment(Qt.AlignBottom)
        
        layout_graph.addLayout(self.layout_barres)
        
        # Labels des heures en bas
        self.layout_heures = QHBoxLayout()
        self.layout_heures.setSpacing(10)
        layout_graph.addLayout(self.layout_heures)
        
        parent_layout.addWidget(self.container_graphique)
    
    def _creer_entete_filtres(self, parent_layout):
        """En-tête avec titre et boutons filtres"""
        layout_entete = QHBoxLayout()
        
        # Titre
        lbl_titre = QLabel("📊 MES STATISTIQUES")
        lbl_titre.setStyleSheet("font-size: 16pt; font-weight: bold; color: #2A2A40;")
        layout_entete.addWidget(lbl_titre)
        
        layout_entete.addStretch()
        
        # Groupe de boutons filtres
        self.groupe_filtres = QButtonGroup(self)
        
        # Aujourd'hui
        self.btn_today = self._creer_btn_filtre("Aujourd'hui", "today", True)
        self.groupe_filtres.addButton(self.btn_today)
        layout_entete.addWidget(self.btn_today)
        
        # Cette semaine
        self.btn_week = self._creer_btn_filtre("Cette Semaine", "week", False)
        self.groupe_filtres.addButton(self.btn_week)
        layout_entete.addWidget(self.btn_week)
        
        # Ce mois
        self.btn_month = self._creer_btn_filtre("Ce Mois", "month", False)
        self.groupe_filtres.addButton(self.btn_month)
        layout_entete.addWidget(self.btn_month)
        
        parent_layout.addLayout(layout_entete)
    
    def _creer_btn_filtre(self, texte: str, filtre: str, checked: bool) -> QPushButton:
        """Crée un bouton filtre"""
        btn = QPushButton(texte)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #E0E0E0;
                color: #2A2A40;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 15px;
            }
            QPushButton:checked {
                background-color: #2196F3;
                color: white;
            }
            QPushButton:hover {
                background-color: #BBDEFB;
            }
        """)
        btn.clicked.connect(lambda: self.changer_filtre(filtre))
        return btn

    def _creer_grille_kpis(self, parent_layout):
        """Grille des 3 KPIs principaux"""
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # KPI 1: Total encaissé
        self.carte_total = self._creer_carte_kpi(
            "💰", "Total Encaissé", "0 FCFA", "#00C853"
        )
        grid.addWidget(self.carte_total, 0, 0)
        
        # KPI 2: Nombre de tickets
        self.carte_tickets = self._creer_carte_kpi(
            "🎫", "Nombre de Tickets", "0", "#2196F3"
        )
        grid.addWidget(self.carte_tickets, 0, 1)
        
        # KPI 3: Panier moyen
        self.carte_panier_moyen = self._creer_carte_kpi(
            "🛒", "Panier Moyen", "0 FCFA", "#FF9800"
        )
        grid.addWidget(self.carte_panier_moyen, 0, 2)
        
        parent_layout.addLayout(grid)
    
    def _creer_carte_kpi(self, icone: str, titre: str, valeur: str, couleur: str) -> QFrame:
        """Crée une carte KPI"""
        carte = QFrame()
        carte.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border-left: 5px solid {couleur};
                padding: 20px;
            }}
        """)
        carte.setMinimumHeight(120)
        
        layout = QVBoxLayout(carte)
        layout.setSpacing(5)
        
        # Icône + Titre
        layout_entete = QHBoxLayout()
        
        lbl_icone = QLabel(icone)
        lbl_icone.setStyleSheet(f"font-size: 24pt; color: {couleur};")
        layout_entete.addWidget(lbl_icone)
        
        lbl_titre = QLabel(titre)
        lbl_titre.setStyleSheet("font-size: 11pt; color: #757575; font-weight: bold;")
        layout_entete.addWidget(lbl_titre, alignment=Qt.AlignBottom)
        layout_entete.addStretch()
        
        layout.addLayout(layout_entete)
        
        # Valeur (gros chiffre)
        lbl_valeur = QLabel(valeur)
        lbl_valeur.setStyleSheet(f"font-size: 22pt; font-weight: bold; color: {couleur};")
        lbl_valeur.setAlignment(Qt.AlignRight)
        layout.addWidget(lbl_valeur)
        
        # Stocker le label de valeur pour mise à jour
        carte.lbl_valeur = lbl_valeur
        
        return carte
    
    # ========== LOGIQUE ==========
    
    def changer_filtre(self, filtre: str):
        """Change le filtre et recharge les données"""
        self.filtre_actuel = filtre
        self.charger_statistiques()

    def charger_statistiques(self):
        """Charge et affiche les statistiques du caissier"""
        stats = Database.get_cashier_stats(self.id_utilisateur, self.filtre_actuel)
        
        if not stats:
            # En cas d'erreur ou vide, on met à 0
            self.carte_total.lbl_valeur.setText(f"0 FCFA")
            self.carte_tickets.lbl_valeur.setText("0")
            self.carte_panier_moyen.lbl_valeur.setText(f"0 FCFA")
            # Cacher le graph si ce n'est pas "Aujourd'hui"
            if self.filtre_actuel != 'today':
                self.container_graphique.hide()
            else:
                self.container_graphique.show()
                self.charger_graphique_horaire()
            return
        
        # Mettre à jour les KPIs
        total_encaisse = stats.get('total_encaisse', 0)
        nb_tickets = stats.get('nb_tickets', 0)
        panier_moyen = stats.get('panier_moyen', 0)
        
        self.carte_total.lbl_valeur.setText(f"{total_encaisse:,.0f} FCFA")
        self.carte_tickets.lbl_valeur.setText(str(nb_tickets))
        self.carte_panier_moyen.lbl_valeur.setText(f"{panier_moyen:,.0f} FCFA")

        # Affichage conditionnel du graphique horaire
        if self.filtre_actuel == 'today':
            self.container_graphique.show()
            self.charger_graphique_horaire()
        else:
            self.container_graphique.hide()
    
    def charger_graphique_horaire(self):
        """Récupère et affiche les données horaires"""
        # Nettoyer les barres existantes
        while self.layout_barres.count():
            item = self.layout_barres.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        while self.layout_heures.count():
            item = self.layout_heures.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        data = Database.get_cashier_hourly_stats(self.id_utilisateur)
        
        if not data:
            lbl_empty = QLabel("Aucune activité enregistrée pour le moment.")
            lbl_empty.setStyleSheet("color: #757575; font-style: italic;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            self.layout_barres.addWidget(lbl_empty)
            return
            
        # Trouver le maximum pour l'échelle
        max_ca = max([d['total'] for d in data]) if data else 1
        
        # On définit une plage d'heures (ex: 8h à 20h ou simplement les heures avec données)
        heures_potentielles = range(min([d['heure'] for d in data]), max([d['heure'] for d in data]) + 1)
        
        dict_data = {int(d['heure']): d for d in data}
        
        for h in heures_potentielles:
            info = dict_data.get(h, {'total': 0, 'nb_tickets': 0})
            ca = info['total']
            tickets = info['nb_tickets']
            
            # Créer la barre
            barre = QFrame()
            hauteur_max = 200
            hauteur = int((ca / max_ca) * hauteur_max) if max_ca > 0 else 2
            if hauteur < 5: hauteur = 5 # Hauteur mini visible
            
            barre.setFixedHeight(hauteur)
            barre.setFixedWidth(30)
            
            couleur = "#B0BEC5" if ca == 0 else "#2196F3"
            barre.setStyleSheet(f"""
                QFrame {{
                    background-color: {couleur};
                    border-radius: 4px;
                }}
                QFrame:hover {{
                    background-color: #64B5F6;
                }}
            """)
            
            # Tooltip interactif
            if ca > 0:
                tooltip = f"<b>Heure : {h}h</b><br/>CA : {ca:,.0f} FCFA<br/>Clients : {tickets}".replace(",", " ")
                barre.setToolTip(tooltip)
            else:
                barre.setToolTip(f"{h}h : Aucune vente")
                
            self.layout_barres.addWidget(barre)
            
            # Label heure
            lbl_h = QLabel(f"{h}h")
            lbl_h.setFixedWidth(30)
            lbl_h.setAlignment(Qt.AlignCenter)
            lbl_h.setStyleSheet("color: #9E9E9E; font-size: 8pt;")
            self.layout_heures.addWidget(lbl_h)

    def rafraichir(self):
        """Rafraîchit les statistiques (appelé lors du changement d'écran)"""
        self.charger_statistiques()
