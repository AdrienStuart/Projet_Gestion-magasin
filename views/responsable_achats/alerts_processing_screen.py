from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, 
                               QListWidget, QListWidgetItem, QPushButton, QDialog, 
                               QFormLayout, QSpinBox, QComboBox, QTextEdit, QMessageBox,
                               QScrollArea, QDoubleSpinBox, QDateEdit, QCheckBox, QGroupBox)
from PySide6.QtCore import Qt, QSize, QDate, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QIcon
from db.database import Database

# ... (AlertsProcessingScreen content remains, we will update it in next step) ...


class NewSupplierDialog(QDialog):
    """Dialogue pour enregistrer un nouveau fournisseur"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau Fournisseur")
        self.resize(400, 300)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        
        lay = QVBoxLayout(self)
        form = QFormLayout()
        
        self.txt_nom = QTextEdit()
        self.txt_nom.setFixedHeight(35)
        self.txt_nom.setStyleSheet("background-color: #3E3E3E; border-radius: 4px;")
        
        self.txt_contact = QTextEdit()
        self.txt_contact.setFixedHeight(35)
        self.txt_contact.setStyleSheet("background-color: #3E3E3E; border-radius: 4px;")
        
        self.txt_adresse = QTextEdit()
        self.txt_adresse.setFixedHeight(60)
        self.txt_adresse.setStyleSheet("background-color: #3E3E3E; border-radius: 4px;")
        
        form.addRow("Nom :", self.txt_nom)
        form.addRow("Contact :", self.txt_contact)
        form.addRow("Adresse :", self.txt_adresse)
        
        lay.addLayout(form)
        
        btn_box = QHBoxLayout()
        btn_save = QPushButton("Enregistrer")
        btn_save.setStyleSheet("background-color: #00E676; color: black; font-weight: bold; padding: 10px;")
        btn_save.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        lay.addLayout(btn_box)

    def get_data(self):
        return {
            'nom': self.txt_nom.toPlainText().strip(),
            'contact': self.txt_contact.toPlainText().strip(),
            'adresse': self.txt_adresse.toPlainText().strip()
        }

class AdvancedOrderDialog(QDialog):
    """Dialogue de commmande avancé"""
    def __init__(self, alert, user_id, parent=None):
        super().__init__(parent)
        self.alert = alert
        self.user_id = user_id
        
        # 1. Obtenir recommandation
        self.reco = Database.get_order_recommendation(alert['id_produit'])
        
        self.setWindowTitle(f"Commander : {alert['nom_produit']}")
        self.resize(600, 700)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        
        self.setup_ui()
        
    def setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(20)
        lay.setContentsMargins(30, 30, 30, 30)
        
        # Header Entête
        lbl_titre = QLabel(f"🛒 Nouvelle Commande : {self.alert['nom_produit']}")
        lbl_titre.setStyleSheet("font-size: 16pt; font-weight: bold; color: #00E676;")
        lay.addWidget(lbl_titre)
        
        # Panneau Recommandation
        if self.reco:
            grp_reco = QGroupBox("💡 Analyse & Recommandation")
            grp_reco.setStyleSheet("QGroupBox { border: 1px solid #4caf50; margin-top: 10px; color: #4caf50; font-weight: bold; }")
            l_reco = QVBoxLayout(grp_reco)
            txt = (f"• Quantité suggérée : {self.reco['suggested_qty']} unités\n"
                   f"• Fournisseur habituel : {self.reco['supplier_name']}\n"
                   f"• Coût estimé : {self.reco['total_cost']:,.0f} FCFA")
            l_reco.addWidget(QLabel(txt))
            lay.addWidget(grp_reco)
        
        # Formulaire
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #2D2D2D; border-radius: 8px; padding: 10px;")
        form = QFormLayout(form_frame)
        
        # Fournisseur
        h_sup = QHBoxLayout()
        self.cb_supplier = QComboBox()
        self._load_suppliers()
        self.cb_supplier.setStyleSheet("background-color: #3E3E3E; padding: 8px;")
        h_sup.addWidget(self.cb_supplier, 1)
        
        btn_add_sup = QPushButton("+")
        btn_add_sup.setFixedSize(35, 35)
        btn_add_sup.setStyleSheet("background-color: #333; color: #00E676; font-weight: bold; font-size: 14pt; border: 1px solid #555;")
        btn_add_sup.setToolTip("Enregistrer un nouveau fournisseur")
        btn_add_sup.clicked.connect(self._add_new_supplier)
        h_sup.addWidget(btn_add_sup)
        
        form.addRow("Fournisseur :", h_sup)
        
        # Quantité
        self.sb_qty = QSpinBox()
        self.sb_qty.setRange(1, 100000)
        self.sb_qty.setValue(self.reco['suggested_qty'] if self.reco else 10)
        self.sb_qty.setStyleSheet("background-color: #3E3E3E; padding: 8px; border: 2px solid #00E676;") # Highlight Editable
        self.sb_qty.valueChanged.connect(self._update_simulation)
        
        lbl_qty_info = QLabel("(Modifiable manuellement)")
        lbl_qty_info.setStyleSheet("color: #757575; font-size: 8pt; font-style: italic;")
        
        h_qty = QVBoxLayout()
        h_qty.addWidget(self.sb_qty)
        h_qty.addWidget(lbl_qty_info)
        
        form.addRow("Quantité à commander :", h_qty)
        
        # Prix Unitaire
        self.sb_price = QDoubleSpinBox()
        self.sb_price.setRange(0, 1000000)
        self.sb_price.setValue(self.reco['unit_price'] if self.reco else 0)
        self.sb_price.setSuffix(" FCFA")
        self.sb_price.setStyleSheet("background-color: #3E3E3E; padding: 8px;")
        self.sb_price.valueChanged.connect(self._update_simulation)
        form.addRow("Prix Unitaire (Négocié) :", self.sb_price)
        
        # Date Livraison
        self.de_delivery = QDateEdit()
        self.de_delivery.setDate(QDate.currentDate().addDays(self.reco['lead_time_days'] if self.reco else 3))
        self.de_delivery.setCalendarPopup(True)
        self.de_delivery.setStyleSheet("background-color: #3E3E3E; padding: 8px;")
        form.addRow("Livraison souhaitée :", self.de_delivery)
        
        lay.addWidget(form_frame)
        
        # Option Groupement
        self.chk_group = QCheckBox("Grouper avec d'autres alertes de ce fournisseur ?")
        self.chk_group.setStyleSheet("color: #90A4AE; font-style: italic;")
        # (Pour l'instant grisé ou simple placeholder, l'implémentation complète nécessite plus de logique)
        # self.chk_group.setEnabled(False) 
        lay.addWidget(self.chk_group)
        
        # Simulation Impact
        self.lbl_impact = QLabel()
        self.lbl_impact.setStyleSheet("color: #FFD700; font-weight: bold; font-size: 11pt; margin-top: 10px;")
        lay.addWidget(self.lbl_impact)
        self._update_simulation()
        
        lay.addStretch()
        
        # Actions
        btn_box = QHBoxLayout()
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("background-color: transparent; border: 1px solid #555; padding: 10px;")
        
        btn_confirm = QPushButton("✅ CONFIRMER LA COMMANDE")
        btn_confirm.setStyleSheet("background-color: #00E676; color: black; font-weight: bold; border-radius: 6px; padding: 12px;")
        btn_confirm.setCursor(Qt.PointingHandCursor)
        btn_confirm.clicked.connect(self.valider)
        
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_confirm)
        lay.addLayout(btn_box)
        
    def _update_simulation(self):
        qty = self.sb_qty.value()
        price = self.sb_price.value()
        total = qty * price
        
        current_stock = self.alert['stock_alerte'] # Approximatif (stock au moment alerte)
        target = self.alert['seuil_vise']
        
        txt = (f"📊 IMPACT IMMÉDIAT :\n"
               f"• Total Commande : {total:,.0f} FCFA\n"
               f"• Stock Prévisionnel : {current_stock} + {qty} = {current_stock + qty} (Cible: >{target})")
        self.lbl_impact.setText(txt)
        
    def valider(self):
        # Validation simple
        
        lines = [{
            'product_id': self.alert['id_produit'],
            'qty': self.sb_qty.value(),
            'price': self.sb_price.value()
        }]
        
        # Liste des alertes à fermer
        linked_alerts = [self.alert['id_alerte']]
        
        # TODO: Si groupement coché, chercher autres alertes du même fournisseur
        
        if QMessageBox.question(self, "Confirmation", f"Valider commande de {lines[0]['qty']} unités ?", 
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return

        success = Database.create_purchase_order_advanced(
            self.user_id,
            self.cb_supplier.currentData(),
            lines,
            linked_alert_ids=linked_alerts
        )
        
        if success:
            QMessageBox.information(self, "Succès", "Commande créée et alertes mises à jour !")
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Impossible de créer la commande.")

    def _load_suppliers(self, select_id=None):
        self.cb_supplier.clear()
        self.suppliers = Database.get_suppliers()
        for s in self.suppliers:
            self.cb_supplier.addItem(s['nom'], s['id_fournisseur'])
        
        if select_id:
            idx = self.cb_supplier.findData(select_id)
            if idx >= 0: self.cb_supplier.setCurrentIndex(idx)
        elif self.reco and self.reco['supplier_id']:
            idx = self.cb_supplier.findData(self.reco['supplier_id'])
            if idx >= 0: self.cb_supplier.setCurrentIndex(idx)

    def _add_new_supplier(self):
        dlg = NewSupplierDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            if not data['nom']: return
            
            success = Database.create_supplier(data['nom'], data['contact'], data['adresse'])
            if success:
                QMessageBox.information(self, "Succès", f"Fournisseur {data['nom']} enregistré !")
                # Recharger la liste et sélectionner le nouveau
                self._load_suppliers() # On pourrait chercher l'ID généré mais simple rechargement suffit ici
            else:
                QMessageBox.critical(self, "Erreur", "Impossible d'enregistrer le fournisseur.")

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
        
        # État initial de l'animation
        self.is_expanded = True
        self._set_panel_width(800) # Large au début
        
    def _set_panel_width(self, width):
        self.left_panel.setFixedWidth(width)
        
    def _animate_panel(self, expand=True):
        if self.is_expanded == expand:
            return
            
        self.is_expanded = expand
        target_width = 800 if expand else 350
        
        # Animation de la largeur
        self.anim = QPropertyAnimation(self.left_panel, b"minimumWidth")
        self.anim.setDuration(400)
        self.anim.setStartValue(self.left_panel.width())
        self.anim.setEndValue(target_width)
        self.anim.setEasingCurve(QEasingCurve.InOutQuart)
        
        # On doit aussi animer maximumWidth pour que setFixedWidth soit simulé
        self.anim_max = QPropertyAnimation(self.left_panel, b"maximumWidth")
        self.anim_max.setDuration(400)
        self.anim_max.setStartValue(self.left_panel.width())
        self.anim_max.setEndValue(target_width)
        self.anim_max.setEasingCurve(QEasingCurve.InOutQuart)
        
        # Masquer/Afficher le détail pour un look plus propre
        if expand:
            self.anim.finished.connect(lambda: self.right_panel.hide())
        else:
            self.right_panel.show()
            try: self.anim.finished.disconnect() 
            except: pass
        
        self.anim.start()
        self.anim_max.start()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ZONE GAUCHE : LISTE
        self.left_panel = QFrame()
        # On ne met pas de setFixedWidth fixe ici, on laisse l'animation/état initial gérer
        self.left_panel.setStyleSheet("background-color: #1E1E1E; border-right: 1px solid #333;")
        l_layout = QVBoxLayout(self.left_panel)
        l_layout.setContentsMargins(10, 10, 10, 10)
        
        lbl_list = QLabel("TRAITEMENT")
        lbl_list.setStyleSheet("color: #90A4AE; font-weight: bold; font-size: 10pt; margin-bottom: 5px;")
        l_layout.addWidget(lbl_list)
        
        from PySide6.QtWidgets import QTabWidget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background-color: transparent; }
            QTabBar::tab { 
                background: #2C2C2C; color: #90A4AE; padding: 10px; border: none; min-width: 100px;
                font-weight: bold;
            }
            QTabBar::tab:selected { background: #1E1E1E; color: #00E676; border-bottom: 2px solid #00E676; }
        """)
        
        # TAB 1: File d'attente
        self.alert_list = QListWidget()
        self.alert_list.setStyleSheet("""
            QListWidget { background-color: transparent; border: none; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #2C2C2C; }
            QListWidget::item:selected { background-color: #263238; border-left: 3px solid #00E676; }
        """)
        self.alert_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.alert_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.tabs.addTab(self.alert_list, "FILE D'ATTENTE")
        
        # TAB 2: Historique
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget { background-color: transparent; border: none; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #2C2C2C; }
            QListWidget::item:selected { background-color: #263238; border-left: 3px solid #2196F3; }
        """)
        self.history_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.tabs.addTab(self.history_list, "HISTORIQUE")
        
        self.tabs.currentChanged.connect(self._on_tab_changed)
        l_layout.addWidget(self.tabs)
        
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
        self.history_list.clear()
        self._clear_detail()
        
        # Récupérer alertes persistantes
        all_alerts = Database.get_persistent_alerts()
        
        # 1. File d'attente (Active)
        active_alerts = [a for a in all_alerts if a['statut'] in ['NON_LUE', 'VU', 'EN_COURS']]
        for alert in active_alerts:
            item = QListWidgetItem()
            prio_icon = "🔴" if alert['priorite'] == 'CRITICAL' else "🟠" if alert['priorite'] == 'HIGH' else "🔵"
            item.setText(f"{prio_icon} {alert['nom_produit']}\nStock: {alert['stock_alerte']}")
            item.setData(Qt.UserRole, alert)
            self.alert_list.addItem(item)
            
        # 2. Historique (Traitées)
        processed_alerts = [a for a in all_alerts if a['statut'] in ['ARCHIVEE', 'COMMANDE_PASSEE']]
        # Trier par date de traitement (plus récent d'abord)
        processed_alerts.sort(key=lambda x: x['date_traitement'] or x['date_creation'], reverse=True)
        
        for alert in processed_alerts:
            item = QListWidgetItem()
            status_icon = "✅" if alert['statut'] == 'COMMANDE_PASSEE' else "⏳" if "Report" in (alert['commentaire'] or "") else "❌"
            item.setText(f"{status_icon} {alert['nom_produit']}\nTraitée le: {alert['date_traitement'].strftime('%d/%m %H:%M') if alert['date_traitement'] else '?'}")
            item.setData(Qt.UserRole, alert)
            self.history_list.addItem(item)

    def _on_tab_changed(self, index):
        self._clear_detail()
        self.alert_list.clearSelection()
        self.history_list.clearSelection()
        self._animate_panel(expand=True)

    def _on_selection_changed(self):
        # Détecter quelle liste a la sélection
        if self.tabs.currentIndex() == 0:
            items = self.alert_list.selectedItems()
        else:
            items = self.history_list.selectedItems()
            
        if not items:
            self._clear_detail()
            self._animate_panel(expand=True)
            return

        # Rétracter pour laisser place au détail
        self._animate_panel(expand=False)

        if len(items) == 1:
            alert = items[0].data(Qt.UserRole)
            self._show_alert_detail(alert)
        else:
            self._show_bulk_actions(items)

    def _clear_detail(self):
        # Clean right panel layout
        if self.detail_layout.count():
            item = self.detail_layout.takeAt(0)
            while item:
                w = item.widget()
                if w: w.deleteLater()
                item = self.detail_layout.takeAt(0)

    def _show_bulk_actions(self, items):
        self._clear_detail()
        
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setSpacing(20)
        lay.setContentsMargins(40, 40, 40, 40)
        
        lbl_count = QLabel(f"{len(items)} ALERTES SÉLECTIONNÉES")
        lbl_count.setStyleSheet("font-size: 24pt; font-weight: bold; color: white;")
        lay.addWidget(lbl_count)
        
        # Analyse rapide
        products = [i.data(Qt.UserRole)['nom_produit'] for i in items]
        lbl_prods = QLabel("\n".join(products[:10]) + ("\n..." if len(products) > 10 else ""))
        lbl_prods.setStyleSheet("color: #90A4AE; font-size: 11pt;")
        lay.addWidget(lbl_prods)
        
        lay.addStretch()
        
        # Action Groupée
        btn_group = QPushButton("📦 GROUPER ET COMMANDER TOUT")
        btn_group.setStyleSheet("""
            QPushButton { background-color: #2979FF; color: white; border-radius: 6px; padding: 15px; font-weight: bold; font-size: 12pt; }
            QPushButton:hover { background-color: #448AFF; }
        """)
        # Pour l'instant, on n'implémente pas la vraie commande groupée complexe, 
        # mais on pourrait ouvrir un dialogue spécial ou traiter séquentiellement.
        # Ici on met un placeholder.
        btn_group.clicked.connect(lambda: QMessageBox.information(self, "Info", "Fonctionnalité 'Commande Groupée Complète' à venir.\nVeuillez traiter individuellement pour le moment."))
        lay.addWidget(btn_group)
        
        self.detail_layout.addWidget(container)

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
            
        # RECOMMANDATION (NEW)
        reco = Database.get_order_recommendation(alert['id_produit'])
        if reco:
            reco_frame = QFrame()
            reco_frame.setStyleSheet("background-color: #1b262c; border: 1px solid #37474f; border-radius: 6px;")
            rl = QHBoxLayout(reco_frame)
            
            rl.addWidget(QLabel("💡 RECOMMANDATION :"))
            rl.addWidget(self._create_fact("Qté Suggérée", f"{reco['suggested_qty']}"))
            rl.addWidget(self._create_fact("Fournisseur", reco['supplier_name']))
            rl.addWidget(self._create_fact("Coût Est.", f"{reco['total_cost']:,.0f} FCFA"))
            
            lay.addWidget(reco_frame)

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
        btn_defer.clicked.connect(lambda: self._action_update_status('ARCHIVEE', "Reporté"))
        actions.addWidget(btn_defer)
        
        btn_refuse = self._create_action_btn("❌ REFUSER", "#FF5252", outline=True)
        btn_refuse.clicked.connect(lambda: self._action_update_status('ARCHIVEE', "Refusé")) 
        actions.addWidget(btn_refuse)
        
        lay.addLayout(actions)
        
        # Si c'est l'historique, on affiche le commentaire de traitement
        if alert['statut'] in ['ARCHIVEE', 'COMMANDE_PASSEE']:
            # Désactiver les boutons d'action
            btn_buy.setEnabled(False)
            btn_defer.setEnabled(False)
            btn_refuse.setEnabled(False)
            btn_buy.setStyleSheet("background-color: #333; color: #555; border: none;")
            
            # Ajouter encadré historique
            h_frame = QFrame()
            h_frame.setStyleSheet("background-color: #263238; border-radius: 6px; padding: 15px; margin-top: 20px;")
            hl = QVBoxLayout(h_frame)
            hl.addWidget(QLabel("📜 RÉCAPITULATIF DU TRAITEMENT"))
            
            status_text = "✨ COMMANDE PASSÉE" if alert['statut'] == 'COMMANDE_PASSEE' else "📁 ARCHIVÉE / REPORTÉE"
            lbl_st = QLabel(status_text)
            lbl_st.setStyleSheet("color: #00E676; font-weight: bold; font-size: 11pt;")
            hl.addWidget(lbl_st)
            
            if alert['commentaire']:
                comm = QLabel(f"Note: {alert['commentaire']}")
                comm.setWordWrap(True)
                comm.setStyleSheet("color: #90A4AE; font-style: italic;")
                hl.addWidget(comm)
                
            lay.addWidget(h_frame)
        
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
        dlg = AdvancedOrderDialog(self.current_alert, self.user_id, self)
        if dlg.exec():
            # QMessageBox.information(self, "Succès", "Commande créée avec succès !") # Déjà fait dans le dialog
            self.rafraichir() # Recharger liste

    def _action_update_status(self, status, reason_prefix):
        # Dialog for reason
        # For simplicity, using input dialog or simplified logic
        # Here just update
        if not self.current_alert: return
        Database.update_alert_status(self.current_alert['id_alerte'], status, reason_prefix)
        self.rafraichir()



