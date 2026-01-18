
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTableView, 
                               QHeaderView, QAbstractItemDelegate, QStyleOptionViewItem, QAbstractItemView)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor, QBrush
from db.database import Database

# === CUSTOM MODELS ===

class StockTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data # List of dicts or rows
        # Assumes keys match expected columns roughly, or we map them
        self.headers = ["ID", "Produit", "Stock", "Seuil", "Statut", "Catégorie"]
        self.keys = ["id_produit", "nom_produit", "quantite_stock", "seuil_min_personnalise", "statut", "nom_categorie"]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
            
        row_data = self._data[index.row()]
        key = self.keys[index.column()]
        
        if role == Qt.DisplayRole:
            val = row_data.get(key, "")
            return str(val)
        
        # Color coding for Status or Stock
        if role == Qt.BackgroundRole:
            statut = row_data.get('statut', '')
            stock = row_data.get('quantite_stock', 0)
            threshold = row_data.get('seuil_min_personnalise', 5)
            
            # Use columns or whole row logic? User asked for "Delegate on column Etat" 
            # but usually row highlighting is clearer or specific cells.
            # Let's highlight the Status cell specifically (col 4)
            if index.column() == 4: 
                if statut == "RUPTURE" or stock == 0:
                    return QColor("#FF3D00") # Red
                elif statut == "ALERTE" or stock <= threshold:
                    return QColor("#FFD600") # Yellow
                elif statut == "DISPONIBLE":
                    return QColor("#1E1E2E") # Normal (or Greenish text)
        
        if role == Qt.ForegroundRole:
             if index.column() == 4:
                statut = row_data.get('statut', '')
                stock = row_data.get('quantite_stock', 0)
                if statut == "RUPTURE" or stock == 0:
                    return QColor("white")
                if statut == "ALERTE":
                    return QColor("black") # Contrast on yellow

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

class MovementTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headers = ["Date", "Produit", "Type", "Qté", "Responsable"]
        # Allow flexible mapping depending on what view_journal_mouvements returns
        # Usually: date_mouvement, nom_produit, type_mouvement, quantite, nom_utilisateur
        self.keys = ["date_mouvement", "nom_produit", "type_mouvement", "quantite", "nom_utilisateur"]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = self._data[index.row()]
        key = self.keys[index.column()]
        
        if role == Qt.DisplayRole:
            val = row.get(key, "")
            
            # Decorate Type with Icon emoji
            if key == "type_mouvement":
                if "ENTREE" in str(val).upper(): return f"📥 {val}"
                if "SORTIE" in str(val).upper(): return f"📤 {val}"
                if "AJUSTEMENT" in str(val).upper(): return f"🔧 {val}"
            return str(val)
            
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

# === VIEW ===

class StockView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Tab 1: Etat Stock
        self.tab_stock = QWidget()
        self.setup_stock_tab()
        self.tabs.addTab(self.tab_stock, "État du Stock")
        
        # Tab 2: Journal
        self.tab_journal = QWidget()
        self.setup_journal_tab()
        self.tabs.addTab(self.tab_journal, "Journal des Mouvements")
        
        # Initial Load
        self.refresh_data()

    def setup_stock_tab(self):
        layout = QVBoxLayout(self.tab_stock)
        self.stock_table = QTableView()
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stock_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.stock_table)

    def setup_journal_tab(self):
        layout = QVBoxLayout(self.tab_journal)
        self.journal_table = QTableView()
        self.journal_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.journal_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.journal_table)

    def refresh_data(self):
        # 1. Stock Data
        stock_data = Database.get_stock_status()
        self.stock_model = StockTableModel(stock_data)
        self.stock_table.setModel(self.stock_model)
        
        # 2. Movement Data
        mv_data = Database.get_movements()
        self.journal_model = MovementTableModel(mv_data)
        self.journal_table.setModel(self.journal_model)

