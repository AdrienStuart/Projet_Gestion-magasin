
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QStackedWidget, QFrame, 
                               QSizePolicy, QMessageBox, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QIcon, QAction, QColor
import qtawesome as qta
from datetime import datetime

# Import Views
from views.caissier.cashier_view import CashierView
from views.gestionnaire_stock.stock_manager_view import StockManagerView
from views.gestionnaire_achat.purchase_view import PurchaseView
from views.admin.admin_view import AdminView

class MainWindow(QMainWindow):
    def __init__(self, user_role="Administrateur", user_name="Admin User", controller=None):
        super().__init__()
        self.setWindowTitle("Supermarché - Gestion Magasin")
        self.resize(1280, 720)
        
        self.user_role = user_role
        self.user_name = user_name
        self.controller = controller
        
        self.is_sidebar_collapsed = False
        self.sidebar_animation = None

        # Main Layout Container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Sidebar (Left)
        self.setup_sidebar()

        # 2. Right Content Area (Header + Stacked Content)
        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)
        self.main_layout.addWidget(self.right_container)

        # 3. Header (Top)
        self.setup_header()

        # 4. Main Content (Center)
        self.stacked_widget = QStackedWidget()
        self.right_layout.addWidget(self.stacked_widget)
        
        # Initialize Views
        self.init_views()

        # 5. Status Bar (Bottom)
        self.setup_statusbar()

    def setup_sidebar(self):
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(250)
        self.sidebar_frame.setMinimumWidth(250)
        self.sidebar_frame.setObjectName("Sidebar")
        
        self.sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_layout.setContentsMargins(5, 20, 5, 20)
        self.sidebar_layout.setSpacing(10)

        # App Logo / Title
        self.logo_label = QLabel("MAGASIN")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #FFFFFF; margin-bottom: 20px;")
        self.sidebar_layout.addWidget(self.logo_label)
        
        # Role-based Menu Items
        if self.user_role == "Caissier":
            self.add_menu_item("Vente", "fa5s.cash-register", 0)
            self.add_menu_item("Historique", "fa5s.history", 1) # Placeholder index
            self.add_menu_item("Mon Profil", "fa5s.user", 2)    # Placeholder index
        else:
            # Full menu for Admin
            self.add_menu_item("Caisse", "fa5s.cash-register", 0)
            self.add_menu_item("Stock", "fa5s.boxes", 1)
            self.add_menu_item("Achats", "fa5s.shopping-cart", 2)
            self.add_menu_item("Admin", "fa5s.chart-line", 3)

        self.sidebar_layout.addStretch()
        
        # Logout Button
        logout_btn = self.add_menu_item("Déconnexion", "fa5s.sign-out-alt", -1)
        logout_btn.setStyleSheet("""
            QPushButton { color: #FF3D00; border: 1px solid #FF3D00; }
            QPushButton:hover { background-color: rgba(255, 61, 0, 0.1); }
        """)
        # Connect to controller logout if available
        if self.controller:
            logout_btn.clicked.connect(self.controller.logout)
        else:
            logout_btn.clicked.connect(self.close)

        self.main_layout.addWidget(self.sidebar_frame)

    def setup_header(self):
        self.header_frame = QFrame()
        self.header_frame.setObjectName("Header")
        self.header_frame.setFixedHeight(60)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        # Left: Collapse Toggle
        self.btn_collapse = QPushButton()
        self.btn_collapse.setFixedSize(40, 40)
        self.btn_collapse.setIcon(qta.icon("fa5s.bars", color="#00C853"))
        self.btn_collapse.setCursor(Qt.PointingHandCursor)
        self.btn_collapse.setStyleSheet("background: transparent; border: none;")
        self.btn_collapse.clicked.connect(self.toggle_sidebar)
        header_layout.addWidget(self.btn_collapse)

        self.page_title = QLabel("TABLEAU DE BORD")
        self.page_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: white; margin-left: 10px;")
        header_layout.addWidget(self.page_title)
        
        header_layout.addStretch()

        # User Info
        user_info = QLabel(f"{self.user_name} ({self.user_role})")
        user_info.setStyleSheet("font-weight: bold; font-size: 11pt; color: white; margin-right: 15px;")
        header_layout.addWidget(user_info)

        # Right: Time
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #A0A0B0; font-size: 11pt; margin-right: 15px;")
        header_layout.addWidget(self.time_label)
        
        # Theme Toggle
        self.btn_theme = QPushButton()
        self.btn_theme.setFixedSize(35, 35)
        self.btn_theme.setIcon(qta.icon("fa5s.adjust", color="#00C853"))
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.setToolTip("Changer le thème")
        self.btn_theme.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.btn_theme)
        
        self.right_layout.addWidget(self.header_frame)

        self.right_layout.addWidget(self.header_frame)

        # Timer for clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def setup_statusbar(self):
        self.status = self.statusBar()
        self.status.showMessage("Système prêt - Connecté à PostgreSQL")
        self.status.setStyleSheet("background-color: #1E1E2E; color: #A0A0B0;")

    def init_views(self):
        # Create Placeholders for now
        self.views = []
        
        # 1. Cashier
        self.cashier_view = CashierView()
        self.stacked_widget.addWidget(self.cashier_view)
        self.views.append(self.cashier_view)
        
        # 2. Stock
        # Pass user_name from MainWindow
        self.stock_view = StockManagerView(nom_utilisateur=self.user_name)
        self.stacked_widget.addWidget(self.stock_view)
        self.views.append(self.stock_view)
        
        # 3. Purchase (NOUVEAU MODULE)
        # Note: PurchasingManagerView est un QWidget autonome avec sa propre sidebar.
        # Pour l'intégrer dans MainWindow (qui a DÉJÀ une sidebar), nous pouvons soit :
        # A) L'afficher telle quelle (double sidebar, moche)
        # B) Masquer sa sidebar (si possible)
        # C) Utiliser seulement le Dashboard pour l'Admin
        # Pour l'instant, on instancie la vue complète mais on sait que ça fera double emploi.
        # Idéalement, on refactoriserait pour extraire le contenu.
        # SOLUTION RAPIDE: On met la nouvelle vue, c'est mieux que l'ancienne buggée.
        
        from views.responsable_achats.purchasing_manager_view import PurchasingManagerView
        # On passe un ID user dummy ou celui de l'admin
        self.purchase_view = PurchasingManagerView(id_utilisateur=1, nom_utilisateur=self.user_name)
        # Hack pour masquer la sidebar interne si on est dans MainWindow ?
        if hasattr(self.purchase_view, 'sidebar'):
            self.purchase_view.sidebar.hide()
            
        self.stacked_widget.addWidget(self.purchase_view)
        self.views.append(self.purchase_view)
        
        # 4. Admin
        self.admin_view = AdminView()
        self.stacked_widget.addWidget(self.admin_view)
        self.views.append(self.admin_view)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        # Update Title based on index logic or button text
        titles = ["Caisse", "Gestion Stock", "Centre Approvisionnement", "Tableau de Bord"]
        if 0 <= index < len(titles):
            self.page_title.setText(titles[index])

    def update_time(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%d/%m/%Y %H:%M:%S"))

    def toggle_sidebar(self):
        width = self.sidebar_frame.width()
        new_width = 60 if width > 200 else 250
        self.is_sidebar_collapsed = new_width == 60

        # Animation
        self.sidebar_animation = QPropertyAnimation(self.sidebar_frame, b"minimumWidth")
        self.sidebar_animation.setDuration(300)
        self.sidebar_animation.setStartValue(width)
        self.sidebar_animation.setEndValue(new_width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.sidebar_animation.start()
        
        # Update button icons and text visibility
        for i in range(self.sidebar_layout.count()):
            widget = self.sidebar_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                if self.is_sidebar_collapsed:
                    widget.setText("")
                    widget.setToolTip(widget.property("title"))
                else:
                    widget.setText(widget.property("title"))
                    widget.setToolTip("")

    def add_menu_item(self, title, icon, index):
        btn = QPushButton(title)
        btn.setProperty("title", title)
        btn.setIcon(qta.icon(icon, color="white"))
        btn.setIconSize(QSize(24, 24))
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedHeight(50)
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 15px;
                font-size: 13pt;
                border: none;
                border-radius: 8px;
                color: white;
            }
            QPushButton:checked { background-color: #00C853; }
            QPushButton:hover { background-color: #3E3E5E; }
        """)
        if index != -1:
            btn.clicked.connect(lambda: self.switch_page(index))
        self.sidebar_layout.addWidget(btn)
        return btn

    def toggle_theme(self):
        if self.controller:
            self.controller.toggle_theme()

