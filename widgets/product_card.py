
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QColor
import qtawesome as qta
import os

class ProductCard(QFrame):
    clicked = Signal(str) # Emits product ID when clicked

    def __init__(self, product_id, name, price, stock=0, image_path='assets/default.png'):
        super().__init__()
        self.product_id = product_id
        self.setFixedSize(200, 240)
        
        # Styles for the card
        self.setObjectName("ProductCard")
        self.setStyleSheet("""
            #ProductCard {
                background-color: #2A2A40;
                border: 1px solid #3E3E5E;
                border-radius: 15px;
            }
            #ProductCard:hover {
                background-color: #32324A;
                border: 2px solid #00C853;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # 1. Product Image
        self.image_label = QLabel()
        self.image_label.setFixedSize(180, 140)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border-radius: 10px; background-color: #1E1E2E;")
        
        if not os.path.exists(image_path):
            image_path = 'assets/default.png' # Fallback
            
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
             # Fallback to icon if pixmap fails
             pixmap = qta.icon('fa5s.box', color='#A0A0B0').pixmap(100, 100)
        
        self.image_label.setPixmap(pixmap.scaled(180, 140, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        layout.addWidget(self.image_label)

        # 2. Product Name
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 11pt; border: none; background: transparent;")
        layout.addWidget(name_label)

        # 3. Price
        price_label = QLabel(f"{price:,.0f} FCFA")
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("color: #00C853; font-weight: bold; font-size: 14pt; border: none; background: transparent;")
        layout.addWidget(price_label)

        # 4. Stock Badge (Overlay if low)
        if stock <= 5:
             badge = QLabel(self)
             badge.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#FFD600').pixmap(24, 24))
             badge.setGeometry(165, 5, 30, 30)
             badge.setToolTip(f"Attention: Stock faible ({stock})")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Simple "pressed" visual effect
            self.setStyleSheet(self.styleSheet() + " #ProductCard { background-color: #1E1E2E; }")
            self.clicked.emit(self.product_id)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        # Restore hover style
        self.setStyleSheet(self.styleSheet().replace(" #ProductCard { background-color: #1E1E2E; }", ""))
        super().mouseReleaseEvent(event)
