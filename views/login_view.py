
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFrame, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize
import qtawesome as qta
from db.database import Database

class LoginView(QWidget):
    login_success = Signal(dict) # Emits user info dict on success

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connexion - Gestion Magasin")
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Login Container (Card)
        self.card = QFrame()
        self.card.setFixedSize(380, 450)
        self.card.setStyleSheet("""
            QFrame {
                background-color: #2A2A40;
                border-radius: 15px;
                border: 1px solid #3E3E5E;
            }
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)
        
        # Logo / Title
        logo = QLabel()
        logo.setPixmap(qta.icon("fa5s.unlock-alt", color="#00C853").pixmap(80, 80))
        logo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(logo)
        
        title = QLabel("CONNEXION")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: white; border: none;")
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        # Fields
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedHeight(50)
        # For dev convenience, pre-fill if possible or just focus
        card_layout.addWidget(self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(50)
        
        # Add Show/Hide Password Toggle
        self.show_password_action = self.password_input.addAction(
            qta.icon("fa5s.eye", color="#A0A0B0"), QLineEdit.TrailingPosition
        )
        self.show_password_action.triggered.connect(self.toggle_password_visibility)
        self.is_password_visible = False
        
        card_layout.addWidget(self.password_input)
        
        # Login Button
        self.btn_login = QPushButton("Se Connecter")
        self.btn_login.setProperty("class", "primary")
        self.btn_login.setFixedHeight(60)
        self.btn_login.setStyleSheet("font-size: 14pt; font-weight: bold;")
        self.btn_login.clicked.connect(self.handle_login)
        card_layout.addWidget(self.btn_login)
        
        card_layout.addStretch()
        
        # Footer
        footer = QLabel("Système de Gestion de Stock v1.0")
        footer.setStyleSheet("color: #A0A0B0; font-size: 9pt; border: none;")
        footer.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(footer)
        
        layout.addWidget(self.card)
        
        # Enable Enter key
        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return
            
        # Call Database
        user = Database.login(email, password)
        
        if user:
            self.login_success.emit(user)
        else:
            QMessageBox.critical(self, "Erreur", "Email ou mot de passe incorrect.")

    def toggle_password_visibility(self):
        self.is_password_visible = not self.is_password_visible
        if self.is_password_visible:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_action.setIcon(qta.icon("fa5s.eye-slash", color="#00C853"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_action.setIcon(qta.icon("fa5s.eye", color="#A0A0B0"))

