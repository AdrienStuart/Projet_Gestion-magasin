import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QScrollArea, QGridLayout, 
                               QDialog, QTextEdit, QComboBox, QMessageBox, QGroupBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QPixmap, QIcon
from datetime import datetime
from db.database import Database

class SignalementsScreen(QWidget):
    """
    CENTRE DE COMMANDE - SIGNALEMENTS & ALERTES
    Interface sombre, immersive et orientée action.
    """
    def __init__(self, id_utilisateur: int):
        super().__init__()
        self.id_utilisateur = id_utilisateur
        
        # Charte graphique sombre (#121212)
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI', sans-serif; }
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { background: #1E1E1E; width: 10px; }
            QScrollBar::handle:vertical { background: #424242; border-radius: 5px; }
        """)
        
        self.setup_ui()
        self.charger_donnees()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 1. HEADER KPI
        self._creer_header_kpi(layout)
        
        # 2. ZONE CENTRALE (Action Cards)
        self._creer_zone_cartes(layout)
    
    def _creer_header_kpi(self, parent_layout):
        kpi_container = QHBoxLayout()
        kpi_container.setSpacing(15)
        
        # KPI 1: Ruptures Critiques
        self.kpi_critical = self._creer_kpi_card("RUPTURES CRITIQUES", "0", "#FF1744", "🚨")
        kpi_container.addWidget(self.kpi_critical)
        
        # KPI 2: Réappros Urgents
        self.kpi_high = self._creer_kpi_card("RÉAPPROS URGENTS", "0", "#FF9100", "⚠️")
        kpi_container.addWidget(self.kpi_high)
        
        # KPI 3: Alertes Préventives
        self.kpi_preventive = self._creer_kpi_card("PRÉVENTIF / MANUEL", "0", "#D500F9", "🔮")
        kpi_container.addWidget(self.kpi_preventive)
        
        # Bouton Action Manuelle
        btn_manual = QPushButton(" [+] SIGNALEMENT\nPRÉVENTIF")
        btn_manual.setFixedSize(160, 80)
        btn_manual.setCursor(Qt.PointingHandCursor)
        btn_manual.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A; color: #00E5FF;
                border: 2px dashed #00E5FF; border-radius: 10px;
                font-weight: bold; font-size: 10pt;
            }
            QPushButton:hover { background-color: #333; }
        """)
        btn_manual.clicked.connect(self.creer_alerte_manuelle)
        kpi_container.addWidget(btn_manual)
        
        parent_layout.addLayout(kpi_container)

    def _creer_kpi_card(self, titre, valeur, couleur, icone):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #1E1E1E; border-left: 5px solid {couleur};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(card)
        
        top_layout = QHBoxLayout()
        lbl_icone = QLabel(icone); lbl_icone.setStyleSheet("font-size: 20pt; border: none;")
        lbl_titre = QLabel(titre); lbl_titre.setStyleSheet(f"color: {couleur}; font-weight: bold; font-size: 10pt; border: none;")
        top_layout.addWidget(lbl_icone); top_layout.addWidget(lbl_titre); top_layout.addStretch()
        layout.addLayout(top_layout)
        
        lbl_val = QLabel(valeur)
        lbl_val.setStyleSheet("font-size: 28pt; font-weight: bold; color: white; border: none;")
        lbl_val.setAlignment(Qt.AlignRight)
        layout.addWidget(lbl_val)
        
        card.lbl_val = lbl_val
        return card

    def _creer_zone_cartes(self, parent_layout):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.container_cartes = QWidget()
        self.container_cartes.setStyleSheet("background-color: transparent;")
        self.layout_cartes = QVBoxLayout(self.container_cartes)
        self.layout_cartes.setSpacing(15)
        self.layout_cartes.addStretch() # Pousse vers le haut
        
        scroll.setWidget(self.container_cartes)
        parent_layout.addWidget(scroll)

    def charger_donnees(self):
        # Nettoyage
        while self.layout_cartes.count() > 1: # On garde le stretch
            item = self.layout_cartes.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        alertes = Database.get_persistent_alerts()
        
        # Filtrer et Trier
        actives = [a for a in alertes if a['statut'] not in ['ARCHIVEE', 'COMMANDE_PASSEE']]
        
        # Update KPI
        n_crit = len([a for a in actives if a['priorite'] == 'CRITICAL'])
        n_high = len([a for a in actives if a['priorite'] == 'HIGH'])
        n_prev = len([a for a in actives if a['priorite'] in ['MEDIUM', 'LOW']])
        
        self.kpi_critical.lbl_val.setText(str(n_crit))
        self.kpi_high.lbl_val.setText(str(n_high))
        self.kpi_preventive.lbl_val.setText(str(n_prev))
        
        if not actives:
            lbl_empty = QLabel("✅ Tout est calme. Aucun signalement en cours.")
            lbl_empty.setAlignment(Qt.AlignCenter)
            lbl_empty.setStyleSheet("font-size: 14pt; color: #4CAF50; margin-top: 50px;")
            self.layout_cartes.insertWidget(0, lbl_empty)
            return

        for alerte in actives:
            card = self._creer_carte_alerte(alerte)
            self.layout_cartes.insertWidget(self.layout_cartes.count()-1, card)

    def _creer_carte_alerte(self, alerte):
        color_map = {
            'CRITICAL': '#FF1744', # Rouge Néon
            'HIGH': '#FF9100',     # Orange Vif
            'MEDIUM': '#00E5FF'    # Cyan
        }
        color = color_map.get(alerte['priorite'], '#E0E0E0')
        
        frame = QFrame()
        frame.setFixedHeight(100)
        frame.setCursor(Qt.PointingHandCursor)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: #252525;
                border: 1px solid #333;
                border-left: 6px solid {color};
                border-radius: 8px;
            }}
            QFrame:hover {{ background-color: #2F2F2F; border-color: {color}; }}
        """)
        
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(10, 10, 10, 10)
        
        # 1. Image & Badge
        img_container = QWidget()
        img_container.setFixedSize(80, 80)
        img_container.setStyleSheet("background: transparent; border: none;")
        
        # (Placeholder image logic)
        lbl_icon = QLabel("📦", img_container)
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.resize(80, 80)
        lbl_icon.setStyleSheet("font-size: 30pt;")
        
        # Badge Stock
        lbl_badge = QLabel(str(alerte['stock_alerte']), img_container)
        lbl_badge.setStyleSheet(f"background-color: {color}; color: black; font-weight: bold; border-radius: 10px; padding: 2px 6px;")
        lbl_badge.move(0, 0)
        lbl_badge.adjustSize()
        
        lay.addWidget(img_container)
        
        # 2. Contenu (Motif)
        info_lay = QVBoxLayout()
        lbl_prod = QLabel(alerte['nom_produit'])
        lbl_prod.setStyleSheet("font-size: 14pt; font-weight: bold; color: white; border: none;")
        
        motif = alerte['commentaire'].split('|')[0] if alerte['commentaire'] else "Alerte Automatique"
        lbl_motif = QLabel(motif)
        lbl_motif.setStyleSheet("color: #B0B0B0; font-style: italic; border: none;")
        
        info_lay.addWidget(lbl_prod)
        info_lay.addWidget(lbl_motif)
        lay.addLayout(info_lay)
        lay.addStretch()
        
        # 3. Actions Rapides
        btn_action = QPushButton("VOIR / AGIR")
        btn_action.setFixedSize(120, 40)
        btn_action.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; color: black; font-weight: bold; border-radius: 20px;
            }}
            QPushButton:hover {{ background-color: white; }}
        """)
        btn_action.clicked.connect(lambda: self.ouvrir_detail_alerte(alerte))
        lay.addWidget(btn_action)
        
        return frame

    def creer_alerte_manuelle(self):
        # Dialog pour création préventive (non DB-bound pour l'instant dans ce snippet, simulation UX)
        QMessageBox.information(self, "Fonctionnalité", "Le module de prédiction/création manuelle sera connecté prochainement.")

    def ouvrir_detail_alerte(self, alerte):
        """Ouvre le panneau latéral (simulé par un dialogue ici pour l'instant)"""
        dlg = DetailAlerteDialog(alerte, self)
        if dlg.exec():
            self.charger_donnees()
            
    def rafraichir(self):
        self.charger_donnees()


class DetailAlerteDialog(QDialog):
    """Panneau de détail et d'action"""
    def __init__(self, alerte, parent=None):
        super().__init__(parent)
        self.alerte = alerte
        self.setWindowTitle(f"Traitement : {alerte['nom_produit']}")
        self.resize(500, 400)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        
        self.setup_ui()
        
    def setup_ui(self):
        lay = QVBoxLayout(self)
        
        # Header
        lbl_titre = QLabel(f"Alert #{self.alerte['id_alerte']} - {self.alerte['nom_produit']}")
        lbl_titre.setStyleSheet("font-size: 16pt; font-weight: bold; color: #00E5FF;")
        lay.addWidget(lbl_titre)
        
        # Info
        info = f"Stock Actuel: {self.alerte['stock_alerte']}  |  Seuil Visé: {self.alerte['seuil_vise']}\n"
        info += f"Priorité: {self.alerte['priorite']}  |  Détecté le: {self.alerte['date_creation'].strftime('%d/%m %H:%M')}"
        lay.addWidget(QLabel(info))
        
        lay.addWidget(QLabel("\n📝 Enrichir (Commentaire Métier):"))
        self.txt_comment = QTextEdit()
        self.txt_comment.setPlaceholderText("Ex: Fournisseur contacté, livraison prévue demain...")
        self.txt_comment.setStyleSheet("background-color: #2D2D2D; border: 1px solid #444; color: white;")
        lay.addWidget(self.txt_comment)
        
        # Actions
        btn_box = QHBoxLayout()
        
        btn_valider = QPushButton("✅ VALIDER & ENVOYER (EN COURS)")
        btn_valider.setStyleSheet("background-color: #00C853; color: white; padding: 10px; font-weight: bold;")
        btn_valider.clicked.connect(lambda: self.traiter('EN_COURS'))
        
        btn_archive = QPushButton("📁 ARCHIVER (RÉSOLU)")
        btn_archive.setStyleSheet("background-color: #757575; color: white; padding: 10px; font-weight: bold;")
        btn_archive.clicked.connect(lambda: self.traiter('ARCHIVEE'))
        
        btn_box.addWidget(btn_archive)
        btn_box.addWidget(btn_valider)
        
        lay.addLayout(btn_box)
        
    def traiter(self, statut):
        comment = self.txt_comment.toPlainText()
        Database.update_alert_status(self.alerte['id_alerte'], statut, comment)
        self.accept()
