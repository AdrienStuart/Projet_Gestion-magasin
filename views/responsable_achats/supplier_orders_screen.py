import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
                               QScrollArea, QComboBox, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QFont
from db.database import Database
from views.responsable_achats.alerts_processing_screen import NewSupplierDialog
from PySide6.QtWidgets import (QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, 
                               QDateEdit, QGroupBox, QMessageBox, QLineEdit, QListWidget)
from PySide6.QtCore import QDate


class ManualOrderDialog(QDialog):
    """Dialogue pour passer une commande libre (sans alerte)"""
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.selected_product = None
        
        self.setWindowTitle("➕ Nouvelle Commande Libre")
        self.resize(500, 600)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")
        
        self.setup_ui()
        
    def setup_ui(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(15)
        lay.setContentsMargins(25, 25, 25, 25)
        
        # 1. Sélection Produit
        lay.addWidget(QLabel("🔍 RECHERCHER UN PRODUIT"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Tapez le nom d'un produit...")
        self.txt_search.setStyleSheet("background-color: #2D2D2D; padding: 10px; border-radius: 5px;")
        self.txt_search.textChanged.connect(self._search_products)
        lay.addWidget(self.txt_search)
        
        self.list_results = QListWidget()
        self.list_results.setFixedHeight(120)
        self.list_results.setStyleSheet("""
            QListWidget { background-color: #2D2D2D; border: 1px solid #444; border-radius: 5px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #333; }
            QListWidget::item:selected { background-color: #263238; color: #00E676; }
        """)
        self.list_results.itemClicked.connect(self._select_product)
        lay.addWidget(self.list_results)
        
        # 2. Formulaire de commande
        self.form_frame = QFrame()
        self.form_frame.setStyleSheet("background-color: #263238; border-radius: 8px; padding: 10px;")
        self.form_frame.setEnabled(False) # Désactivé tant qu'aucun produit n'est choisi
        form = QFormLayout(self.form_frame)
        
        # Fournisseur
        h_sup = QHBoxLayout()
        self.cb_supplier = QComboBox()
        self._load_suppliers()
        self.cb_supplier.setStyleSheet("background-color: #3E3E3E; padding: 8px;")
        h_sup.addWidget(self.cb_supplier, 1)
        
        btn_add_sup = QPushButton("+")
        btn_add_sup.setFixedSize(35, 35)
        btn_add_sup.setStyleSheet("background-color: #333; color: #00E676; font-weight: bold; font-size: 14pt; border: 1px solid #555;")
        btn_add_sup.clicked.connect(self._add_new_supplier)
        h_sup.addWidget(btn_add_sup)
        form.addRow("Fournisseur :", h_sup)
        
        # Quantité
        self.sb_qty = QSpinBox()
        self.sb_qty.setRange(1, 100000)
        self.sb_qty.setValue(10)
        self.sb_qty.setStyleSheet("background-color: #3E3E3E; padding: 8px;")
        form.addRow("Quantité :", self.sb_qty)
        
        # Prix Unitaire
        self.sb_price = QDoubleSpinBox()
        self.sb_price.setRange(0, 1000000)
        self.sb_price.setSuffix(" FCFA")
        self.sb_price.setStyleSheet("background-color: #3E3E3E; padding: 8px;")
        form.addRow("Prix Unitaire :", self.sb_price)
        
        lay.addWidget(self.form_frame)
        lay.addStretch()
        
        # Actions
        btn_confirm = QPushButton("🛒 CRÉER LA COMMANDE")
        btn_confirm.setStyleSheet("background-color: #00E676; color: black; font-weight: bold; border-radius: 6px; padding: 12px;")
        btn_confirm.clicked.connect(self.valider)
        lay.addWidget(btn_confirm)

    def _search_products(self, query):
        if len(query) < 2: 
            self.list_results.clear()
            return
        products = Database.search_products(query)
        self.list_results.clear()
        for p in products:
            item = QListWidgetItem(f"{p['nom']} (Stock: {p['stockactuel']})")
            item.setData(Qt.UserRole, p)
            self.list_results.addItem(item)

    def _select_product(self, item):
        self.selected_product = item.data(Qt.UserRole)
        self.txt_search.setText(self.selected_product['nom'])
        self.list_results.clear()
        self.form_frame.setEnabled(True)
        self.sb_price.setValue(float(self.selected_product.get('dernierprixachat', 0)))

    def _load_suppliers(self):
        self.cb_supplier.clear()
        sups = Database.get_suppliers()
        for s in sups:
            self.cb_supplier.addItem(s['nom'], s['id_fournisseur'])

    def _add_new_supplier(self):
        dlg = NewSupplierDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            if not data['nom']: return
            if Database.create_supplier(data['nom'], data['contact'], data['adresse']):
                self._load_suppliers()
                # Sélectionner le dernier ajouté (approximatif ici par nom)
                idx = self.cb_supplier.findText(data['nom'])
                if idx >= 0: self.cb_supplier.setCurrentIndex(idx)

    def valider(self):
        if not self.selected_product:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit.")
            return
            
        success = Database.create_purchase_order_advanced(
            self.user_id,
            self.cb_supplier.currentData(),
            [{
                'product_id': self.selected_product['id_produit'],
                'qty': self.sb_qty.value(),
                'price': self.sb_price.value()
            }]
        )
        if success: self.accept()
        else: QMessageBox.critical(self, "Erreur", "Échec de la création.")

class SupplierOrdersScreen(QWidget):
    """
    ÉCRAN SUIVI DES COMMANDES FOURNISSEURS (Version 2)
    Vue tabulaire filtrable avec filtres avancés et style premium
    """
    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.current_status = None
        self.current_period = None
        self.current_category = None
        self.setup_ui()
        self.charger_categories()
        self.rafraichir()
        
    def setup_ui(self):
        # Layout principal de la page (Scrollable)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #121212; }")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #121212;")
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(30, 25, 30, 30)
        self.content_layout.setSpacing(25)
        
        # --- HEADER ---
        header_layout = QHBoxLayout()
        lbl_title = QLabel("HISTORIQUE DES COMMANDES")
        lbl_title.setStyleSheet("color: #FFFFFF; font-size: 20pt; font-weight: bold; letter-spacing: 1px;")
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        # Bouton Actualiser
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.setFixedSize(120, 40)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D; color: #E0E0E0; border-radius: 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: #3D3D3D; color: #00E676; }
        """)
        btn_refresh.clicked.connect(self.rafraichir)
        header_layout.addWidget(btn_refresh)
        
        # Bouton Nouvelle Commande (NEW)
        btn_new = QPushButton("➕ Nouvelle Commande")
        btn_new.setFixedSize(180, 40)
        btn_new.setStyleSheet("""
            QPushButton {
                background-color: #00E676; color: black; border-radius: 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: #00C853; }
        """)
        btn_new.clicked.connect(self._nouvelle_commande)
        header_layout.addWidget(btn_new)
        
        self.content_layout.addLayout(header_layout)
        
        # --- FILTRES ---
        filters_frame = QFrame()
        filters_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E; border-radius: 12px; border: 1px solid #333;
            }
        """)
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setContentsMargins(20, 15, 20, 15)
        filters_layout.setSpacing(25)
        
        # Filtre Statut (Boutons segmentés)
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        self.btn_all = self._create_filter_btn("TOUT", None, True)
        self.btn_pending = self._create_filter_btn("EN ATTENTE", "EN_ATTENTE")
        self.btn_received = self._create_filter_btn("REÇUES", "RECU")
        status_layout.addWidget(self.btn_all)
        status_layout.addWidget(self.btn_pending)
        status_layout.addWidget(self.btn_received)
        filters_layout.addLayout(status_layout)
        
        # Séparateur vertical
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("background-color: #333;")
        filters_layout.addWidget(line)
        
        # Filtre Période
        period_layout = QVBoxLayout()
        lbl_period = QLabel("PÉRIODE")
        lbl_period.setStyleSheet("color: #757575; font-size: 8pt; font-weight: bold;")
        self.combo_period = QComboBox()
        self.combo_period.setFixedWidth(160)
        self.combo_period.addItems(["Tout", "Aujourd'hui", "7 derniers jours", "30 derniers jours"])
        self.combo_period.setStyleSheet(self._combo_style())
        self.combo_period.currentIndexChanged.connect(self._on_period_changed)
        period_layout.addWidget(lbl_period)
        period_layout.addWidget(self.combo_period)
        filters_layout.addLayout(period_layout)
        
        # Filtre Catégorie
        cat_layout = QVBoxLayout()
        lbl_cat = QLabel("CATÉGORIE")
        lbl_cat.setStyleSheet("color: #757575; font-size: 8pt; font-weight: bold;")
        self.combo_cat = QComboBox()
        self.combo_cat.setFixedWidth(180)
        self.combo_cat.setStyleSheet(self._combo_style()) # Style combo
        self.combo_cat.currentIndexChanged.connect(self._on_category_changed)
        cat_layout.addWidget(lbl_cat)
        cat_layout.addWidget(self.combo_cat)
        filters_layout.addLayout(cat_layout)
        
        filters_layout.addStretch()
        self.content_layout.addWidget(filters_frame)
        
        # --- TABLE ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["PRODUITS", "FOURNISSEUR", "DATE", "MONTANT", "STATUT"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(60) # Élargis pour une meilleure vue
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: transparent; gridline-color: #333; border: none; font-size: 11pt;
                alternate-background-color: #1A1A1A;
            }
            QHeaderView::section {
                background-color: transparent; color: #757575; padding: 15px; border: none; 
                font-weight: bold; font-size: 9pt; text-transform: uppercase;
            }
            QTableWidget::item { padding: 15px; border-bottom: 1px solid #222; color: #E0E0E0; }
            QTableWidget::item:selected { background-color: #263238; color: white; }
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self._voir_details)
        self.content_layout.addWidget(self.table)
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
    def _combo_style(self):
        return """
            QComboBox {
                background-color: #2D2D2D; color: white; border: 1px solid #424242; 
                border-radius: 6px; padding: 8px; font-weight: bold;
            }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #757575; margin-right: 10px; }
            QComboBox QAbstractItemView { background-color: #2D2D2D; color: white; selection-background-color: #00E676; }
        """

    def _create_filter_btn(self, text, filter_val, active=False):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setFixedSize(130, 40)
        btn.setProperty("filter", filter_val)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #757575; border: 1px solid #444; border-radius: 20px; font-weight: bold;
            }
            QPushButton:checked {
                background-color: #00E676; color: black; border: none;
            }
            QPushButton:hover:!checked { border-color: #00E676; color: #00E676; }
        """)
        btn.clicked.connect(lambda: self._apply_status_filter(btn))
        return btn
        
    def _apply_status_filter(self, sender):
        for b in [self.btn_all, self.btn_pending, self.btn_received]:
            b.setChecked(b == sender)
        self.current_status = sender.property("filter")
        self.rafraichir()

    def _on_period_changed(self, index):
        periods = [None, 0, 7, 30] # Mapping indices to days (0 for today)
        self.current_period = periods[index]
        self.rafraichir()

    def _on_category_changed(self, index):
        self.current_category = self.combo_cat.itemData(index)
        self.rafraichir()

    def charger_categories(self):
        self.combo_cat.clear()
        self.combo_cat.addItem("Toutes les catégories", None)
        try:
            categories = Database.get_all_categories()
            for cat in categories:
                self.combo_cat.addItem(cat['libelle'], cat['id_categorie'])
        except: pass

    def rafraichir(self):
        self.table.setRowCount(0)
        orders = Database.get_supplier_orders(self.current_status, self.current_period, self.current_category)
        
        self.table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            status = order['statut']
            
            # Définir les couleurs selon le statut
            if status == "EN_ATTENTE":
                color_hex = "#FFAB40" # Orange
                bg_color = QColor(255, 171, 64, 40)
            elif status == "RECU":
                color_hex = "#00E676" # Vert
                bg_color = QColor(0, 230, 118, 40)
            else:
                color_hex = "#9E9E9E" # Gris
                bg_color = QColor(158, 158, 158, 40)
                
            text_color = QColor(color_hex)
            
            # 1. PRODUITS
            prod_text = order.get('produits', 'N/A')
            if len(prod_text) > 40: prod_text = prod_text[:37] + "..."
            item_prod = QTableWidgetItem(prod_text)
            item_prod.setFont(QFont("", 10, QFont.Bold))
            item_prod.setToolTip(order.get('produits', ''))
            
            # 2. FOURNISSEUR
            item_fourn = QTableWidgetItem(order['fournisseur'])
            
            # 3. DATE
            date_str = order['date_achat'].strftime("%d %b %Y")
            item_date = QTableWidgetItem(date_str)
            item_date.setTextAlignment(Qt.AlignCenter)
            
            # 4. MONTANT
            total = order.get('total_amount', 0)
            item_price = QTableWidgetItem(f"{total:,.0f} FCFA".replace(',', ' '))
            item_price.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_price.setFont(QFont("Monospace", 11, QFont.Bold))
            
            # 5. STATUT (Badge Style)
            status_item = QTableWidgetItem(status.replace('_', ' '))
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setFont(QFont("", 9, QFont.Bold))

            # Appliquer les styles à toute la ligne
            for col, item in enumerate([item_prod, item_fourn, item_date, item_price, status_item]):
                item.setBackground(bg_color)
                item.setForeground(text_color)
                # Bordure colorée à gauche pour la première colonne
                if col == 0:
                    item.setData(Qt.UserRole + 1, color_hex) # Stocker pour ref
                self.table.setItem(row, col, item)
            
            # Stocker l'ID de l'achat dans la ligne
            item_prod.setData(Qt.UserRole, order['id_achat'])

    def _voir_details(self, item):
        """Affiche les lignes de produits de la commande"""
        row = item.row()
        id_achat = self.table.item(row, 0).data(Qt.UserRole)
        
        # Récupérer les détails depuis la DB
        details = Database.get_order_details(id_achat)
        if not details: return
        
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Détails Commande #{id_achat}")
        dlg.resize(600, 400)
        dlg.setStyleSheet("background-color: #1E1E1E; color: white;")
        
        layout = QVBoxLayout(dlg)
        
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["PRODUIT", "QUANTITÉ", "PRIX UNIT.", "TOTAL"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setRowCount(len(details))
        table.setStyleSheet("QTableWidget { background: transparent; border: none; } QHeaderView::section { background: #2D2D2D; }")
        
        for r, d in enumerate(details):
            table.setItem(r, 0, QTableWidgetItem(d['nom']))
            table.setItem(r, 1, QTableWidgetItem(str(d['quantite'])))
            table.setItem(r, 2, QTableWidgetItem(f"{d['prixachatnegocie']:,.0f}"))
            table.setItem(r, 3, QTableWidgetItem(f"{d['quantite'] * d['prixachatnegocie']:,.0f}"))
            
        layout.addWidget(table)
        
        btn_close = QPushButton("Fermer")
        btn_close.clicked.connect(dlg.accept)
        btn_close.setStyleSheet("background: #333; padding: 10px;")
        layout.addWidget(btn_close)
        
        dlg.exec()

    def _nouvelle_commande(self):
        """Ouvre le dialogue de commande libre"""
        dlg = ManualOrderDialog(self.user_id, self)
        if dlg.exec():
            QMessageBox.information(self, "Succès", "Commande libre créée avec succès !")
            self.rafraichir()
