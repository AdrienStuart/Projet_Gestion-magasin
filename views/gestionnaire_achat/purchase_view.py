
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView, 
                               QPushButton, QHeaderView, QAbstractItemView, QDialog, 
                               QLabel, QComboBox, QSpinBox, QProgressBar, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QTimer
from PySide6.QtGui import QFont
from db.database import Database
import qtawesome as qta

# === MODEL ===
class RestockingTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["Produit", "Stock Actuel", "Seuil", "Qté Suggérée", "Fournisseur"]
        self.keys = ["nom_produit", "quantite_stock", "seuil_min_personnalise", "qte_suggeree", "nom_fournisseur_pref"]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        row = self._data[index.row()]
        key = self.keys[index.column()]
        
        if role == Qt.DisplayRole:
            val = row.get(key, "")
            return str(val)
        
        if role == Qt.FontRole and index.column() == 3: # Suggested Qty
             font = QFont()
             font.setBold(True)
             return font
             
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

# === WIZARD DIALOG ===
class OrderWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvelle Commande Fournisseur")
        self.resize(600, 400)
        self.setStyleSheet("background-color: #2A2A40; color: white;")
        
        layout = QVBoxLayout(self)
        
        # Step 1: Supplier
        layout.addWidget(QLabel("1. Sélectionner le Fournisseur :"))
        self.supplier_cb = QComboBox()
        # Mock Suppliers or fetch
        # self.supplier_cb.addItems(["Fournisseur A", "Fournisseur B"]) 
        # Ideally fetch from DB
        layout.addWidget(self.supplier_cb)
        
        layout.addSpacing(20)
        
        # Step 2: Products
        layout.addWidget(QLabel("2. Ajouter des Produits :"))
        self.products_list = QTableView()
        layout.addWidget(self.products_list)
        
        # Step 3: Validate
        self.btn_validate = QPushButton("Valider la Commande")
        self.btn_validate.setProperty("class", "primary")
        self.btn_validate.clicked.connect(self.process_order)
        layout.addWidget(self.btn_validate)

    def process_order(self):
        # UX: Loading Bar
        self.progress = QDialog(self)
        self.progress.setWindowTitle("Traitement en cours...")
        self.progress.setFixedSize(300, 100)
        self.progress.setStyleSheet("background-color: #1E1E2E; color: white;")
        p_layout = QVBoxLayout(self.progress)
        p_layout.addWidget(QLabel("Calcul des nouveaux PMP et mise à jour des stocks..."))
        bar = QProgressBar()
        bar.setRange(0, 100)
        p_layout.addWidget(bar)
        self.progress.show()
        
        # Simulate delay
        self.timer = QTimer()
        self.step = 0
        def update_progress():
            self.step += 10
            bar.setValue(self.step)
            if self.step >= 100:
                self.timer.stop()
                self.progress.close()
                QMessageBox.information(self, "Succès", "Commande envoyée et stocks mis à jour !")
                self.accept()
                
        self.timer.timeout.connect(update_progress)
        self.timer.start(100) # 1s total

# === VIEW ===
class PurchaseView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Liste de Courses (Besoin Réappro)")
        header.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Table
        self.table = QTableView()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table)
        
        # Action Bar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_order = QPushButton("Passer Commande")
        self.btn_order.setIcon(qta.icon('fa5s.shipping-fast', color='white'))
        self.btn_order.setProperty("class", "primary")
        self.btn_order.clicked.connect(self.open_order_wizard)
        btn_layout.addWidget(self.btn_order)
        
        layout.addLayout(btn_layout)
        
        self.refresh_data()

    def refresh_data(self):
        data = Database.get_replenishment_needs()
        self.model = RestockingTableModel(data)
        self.table.setModel(self.model)

    def open_order_wizard(self):
        # In a real app, pre-fill based on selected rows
        dlg = OrderWizard(self)
        if dlg.exec():
            # Refresh after order
            self.refresh_data()

