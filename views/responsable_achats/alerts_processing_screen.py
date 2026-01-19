import os
from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, 
                               QListWidget, QListWidgetItem, QPushButton, QDialog, 
                               QFormLayout, QSpinBox, QComboBox, QTextEdit, QMessageBox,
                               QScrollArea)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon
from db.database import Database

class AlertsProcessingScreen(QWidget):
    """
    ÉCRAN DE TRAITEMENT DES ALERTES
    Architecture Master-Detail
    Gauche: Liste priorisée
    Droite: Fiche décisionnelle
    """
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.current_alert = None
        
        self.setup_ui()
        self.rafraichir()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ZONE GAUCHE : LISTE (30%)
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(350)
        self.left_panel.setStyleSheet("background-color: #1E1E1E; border-right: 1px solid #333;")
        l_layout = QVBoxLayout(self.left_panel)
        l_layout.setContentsMargins(10, 10, 10, 10)
        
        lbl_list = QLabel("FILE D'ATTENTE")
        lbl_list.setStyleSheet("color: #90A4AE; font-weight: bold; font-size: 10pt;")
        l_layout.addWidget(lbl_list)
        
        self.alert_list = QListWidget()
        self.alert_list.setStyleSheet("""
            QListWidget { background-color: transparent; border: none; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #2C2C2C; }
            QListWidget::item:selected { background-color: #263238; border-left: 3px solid #00E676; }
        """)
        self.alert_list.currentItemChanged.connect(self._on_alert_selected)
        l_layout.addWidget(self.alert_list)
        
        main_layout.addWidget(self.left_panel)
        
        # ZONE DROITE : DÉTAIL (70%)
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("background-color: #121212;")
        self.detail_layout = QVBoxLayout(self.right_panel)
        self.detail_layout.setAlignment(Qt.AlignCenter)
        
        # Placeholder text
        self.lbl_placeholder = QLabel("Sélectionnez une alerte à traiter")
        self.lbl_placeholder.setStyleSheet("color: #546E7A; font-size: 14pt;")
        self.detail_layout.addWidget(self.lbl_placeholder)
        
        main_layout.addWidget(self.right_panel)

    def rafraichir(self):
        self.alert_list.clear()
        self._clear_detail()
        
        # Récupérer alertes persistantes
        alerts = Database.get_persistent_alerts()
        # Filtrer pour ne garder que 'NON_LUE', 'VU', 'EN_COURS'
        # (L'exclusion est déjà faite en partie dans le SQL mais vérifions)
        active_alerts = [a for a in alerts if a['statut'] in ['NON_LUE', 'VU', 'EN_COURS']]
        
        for alert in active_alerts:
            item = QListWidgetItem()
            # Custom widget item could be better but sticking to simple text with icon for speed
            # Or use item data to store full object
            
            prio_icon = "🔴" if alert['priorite'] == 'CRITICAL' else "🟠" if alert['priorite'] == 'HIGH' else "🔵"
            item.setText(f"{prio_icon} {alert['nom_produit']}\nStock: {alert['stock_alerte']}")
            item.setData(Qt.UserRole, alert)
            self.alert_list.addItem(item)

    def _on_alert_selected(self, current, previous):
        if not current: return
        alert = current.data(Qt.UserRole)
        self._show_alert_detail(alert)

    def _clear_detail(self):
        # Clean right panel layout
        if self.detail_layout.count():
            item = self.detail_layout.takeAt(0)
            while item:
                w = item.widget()
                if w: w.deleteLater()
                item = self.detail_layout.takeAt(0)

    def _show_alert_detail(self, alert):
        self._clear_detail()
        self.current_alert = alert
        
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setSpacing(20)
        lay.setContentsMargins(40, 20, 40, 40)
        
        # Header
        lbl_prod = QLabel(f"{alert['nom_produit']}")
        lbl_prod.setStyleSheet("font-size: 24pt; font-weight: bold; color: white;")
        lay.addWidget(lbl_prod)
        
        # Badges
        badges = QHBoxLayout()
        badges.addWidget(self._create_badge(alert['priorite'], "#FF1744" if alert['priorite']=='CRITICAL' else "#FF9100"))
        badges.addWidget(self._create_badge(f"STOCK: {alert['stock_alerte']}", "#00E676"))
        badges.addStretch()
        lay.addLayout(badges)
        
        # Context Data (Factuel)
        context = Database.get_alert_purchasing_context(alert['id_produit'])
        if context:
            grid = QHBoxLayout()
            grid.setSpacing(30)
            grid.addWidget(self._create_fact("Ventes 30j", str(context.get('sales_30d', 0))))
            grid.addWidget(self._create_fact("Dernière Cde", str(context.get('last_supplier_order') or 'Jamais')))
            grid.addWidget(self._create_fact("Freq. Ruptures", f"{context.get('shortage_freq_90d', 0)}x / 90j"))
            lay.addLayout(grid)
            
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #333;")
        lay.addWidget(line)
        
        # Actions Title
        lbl_action = QLabel("DÉCISION")
        lbl_action.setStyleSheet("color: #90A4AE; letter-spacing: 2px; font-weight: bold;")
        lay.addWidget(lbl_action)
        
        # Action Buttons
        actions = QHBoxLayout()
        actions.setSpacing(15)
        
        btn_buy = self._create_action_btn("🛒 COMMANDER", "#00E676")
        btn_buy.clicked.connect(self._action_commander)
        actions.addWidget(btn_buy)
        
        btn_defer = self._create_action_btn("⏳ REPORTER", "#FF9100", outline=True)
        btn_defer.clicked.connect(lambda: self._action_update_status('ARCHIVEE', "Reporté")) # Simplification pour 'Reporter' -> Archive avec commentaire
        actions.addWidget(btn_defer)
        
        btn_refuse = self._create_action_btn("❌ REFUSER", "#FF5252", outline=True)
        btn_refuse.clicked.connect(lambda: self._action_update_status('ARCHIVEE', "Refusé")) 
        actions.addWidget(btn_refuse)
        
        lay.addLayout(actions)
        lay.addStretch()
        
        self.detail_layout.addWidget(container)

    def _create_badge(self, text, color):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"background-color: {color}; color: black; font-weight: bold; padding: 5px 10px; border-radius: 4px;")
        return lbl
        
    def _create_fact(self, title, value):
        w = QWidget()
        l = QVBoxLayout(w)
        l.setSpacing(2)
        l.setContentsMargins(0,0,0,0)
        t = QLabel(title.upper())
        t.setStyleSheet("color: #757575; font-size: 9pt;")
        v = QLabel(str(value))
        v.setStyleSheet("color: white; font-size: 14pt; font-weight: bold;")
        l.addWidget(t)
        l.addWidget(v)
        return w

    def _create_action_btn(self, text, color, outline=False):
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.setCursor(Qt.PointingHandCursor)
        if outline:
            style = f"background-color: transparent; border: 2px solid {color}; color: {color};"
        else:
            style = f"background-color: {color}; border: none; color: black;"
        
        btn.setStyleSheet(f"""
            QPushButton {{ {style} font-weight: bold; font-size: 11pt; border-radius: 6px; }}
            QPushButton:hover {{ background-color: {color}; color: black; }}
        """)
        return btn

    def _action_commander(self):
        if not self.current_alert: return
        dlg = CreateOrderDialog(self.current_alert, self.user_id, self)
        if dlg.exec():
            QMessageBox.information(self, "Succès", "Commande créée avec succès !")
            self.rafraichir() # Recharger liste

    def _action_update_status(self, status, reason_prefix):
        # Dialog for reason
        # For simplicity, using input dialog or simplified logic
        # Here just update
        if not self.current_alert: return
        Database.update_alert_status(self.current_alert['id_alerte'], status, reason_prefix)
        self.rafraichir()


class CreateOrderDialog(QDialog):
    def __init__(self, alert, user_id, parent=None):
        super().__init__(parent)
        self.alert = alert
        self.user_id = user_id
        self.setWindowTitle("Créer Commande Fournisseur")
        self.resize(500, 400)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        
        self.setup_ui()
        
    def setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(15)
        
        lay.addWidget(QLabel(f"Commande pour: {self.alert['nom_produit']}"))
        
        form = QFormLayout()
        
        # Fournisseur
        self.cb_k = QComboBox()
        self.suppliers = Database.get_suppliers()
        for s in self.suppliers:
            self.cb_k.addItem(s['nom'], s['id_fournisseur'])
        self.cb_k.setStyleSheet("background-color: #2D2D2D; padding: 5px; color: white;")
        form.addRow("Fournisseur:", self.cb_k)
        
        # Quantité
        self.sb_qty = QSpinBox()
        self.sb_qty.setRange(1, 9999)
        # Default suggestion: Seuil * 3 (arbitrary rule or max limit)
        suggestion = self.alert['seuil_vise'] * 2
        self.sb_qty.setValue(suggestion)
        self.sb_qty.setStyleSheet("background-color: #2D2D2D; padding: 5px; color: white;")
        form.addRow("Quantité:", self.sb_qty)
        
        # Prix Achat (Est.)
        self.sb_price = QSpinBox() # Should be DoubleSpinBox but for now...
        self.sb_price.setRange(0, 999999)
        self.sb_price.setValue(0) # TODO: Retrieve last price
        form.addRow("Prix Unitaire (Est.):", self.sb_price)
        
        lay.addLayout(form)
        lay.addStretch()
        
        btn_save = QPushButton("✅ VALIDER LA COMMANDE")
        btn_save.setStyleSheet("background-color: #00E676; color: black; padding: 10px; font-weight: bold;")
        btn_save.clicked.connect(self.save)
        lay.addWidget(btn_save)
        
    def save(self):
        supplier_id = self.cb_k.currentData()
        qty = self.sb_qty.value()
        price = self.sb_price.value()
        
        lines = [{'product_id': self.alert['id_produit'], 'qty': qty, 'price': price}]
        
        success = Database.create_purchase_order(
            self.user_id, 
            supplier_id, 
            lines, 
            linked_alert_ids=[self.alert['id_alerte']]
        )
        
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Échec création commande")

