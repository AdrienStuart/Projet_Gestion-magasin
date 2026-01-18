
import sys
import os
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from views.login_view import LoginView

# Ensure we can find the styles and modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def load_stylesheet():
    style_path = os.path.join(current_dir, "styles.qss")
    with open(style_path, "r") as f:
        return f.read()

class AppController:
    def __init__(self, app):
        self.app = app
        self.current_theme = "dark"
        self.login_window = LoginView()
        self.main_window = None
        
        self.login_window.login_success.connect(self.show_main_window)
        self.apply_theme(self.current_theme)
        self.login_window.show()

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        qss_file = "dark_styles.qss" if theme_name == "dark" else "light_styles.qss"
        try:
            style_path = os.path.join(current_dir, "styles", qss_file)
            with open(style_path, "r") as f:
                self.app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading {theme_name} theme: {e}")

    def toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)

    def show_main_window(self, user):
        from views.caissier.cashier_view import CashierView
        from views.gestionnaire_stock.stock_manager_view import StockManagerView
        
        # Pour les caissiers
        if user['role'] == 'Caissier':
            self.main_window = CashierView(
                id_utilisateur=user.get('id_utilisateur', 1),
                nom_utilisateur=user['nom']
            )
            self.main_window.controller = self
            
        # Pour les gestionnaires de stock
        elif user['role'] == 'Gestionnaire':
            self.main_window = StockManagerView(
                id_utilisateur=user.get('id_utilisateur', 1),
                nom_utilisateur=user['nom']
            )
            self.main_window.controller = self
            
        else:
            # Pour Admin / Responsable Achats -> MainWindow
            self.main_window = MainWindow(
                user_role=user['role'], 
                user_name=user['nom'], 
                controller=self
            )
        
        self.main_window.show()
        self.login_window.close()

    def logout(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        
        # Reset login window fields
        self.login_window.email_input.clear()
        self.login_window.password_input.clear()
        self.login_window.show()

def main():
    app = QApplication(sys.argv)
    
    controller = AppController(app)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
