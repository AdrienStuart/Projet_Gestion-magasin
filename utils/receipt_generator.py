"""
Générateur de reçus PDF pour les ventes
Utilise reportlab pour créer des reçus formatés professionnellement
"""

import os
from datetime import datetime
from typing import Dict, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle


class ReceiptGenerator:
    """Génère des reçus PDF pour les ventes"""
    
    # Chemins
    RECEIPTS_DIR = "receipts"
    
    # Configuration magasin (à personnaliser)
    STORE_NAME = "SUPERMARCHÉ"
    STORE_ADDRESS = "Rue du Commerce, Lomé"
    STORE_PHONE = "Tel: +228 XX XX XX XX"
    STORE_EMAIL = "contact@supermarche.tg"
    
    @classmethod
    def generate_receipt(cls, vente_data: Dict, totaux: Dict, mode_paiement: str = "ESPECES") -> str:
        """
        Génère un reçu PDF et retourne le chemin du fichier
        
        Args:
            vente_data: Dict contenant id_vente, date_vente, caissier, articles (list)
            totaux: Dict avec subtotal_ttc, total_remises, total_ht, montant_tva, total_ttc
            mode_paiement: Mode de paiement utilisé
            
        Returns:
            Chemin complet du fichier PDF généré
        """
        # Créer le dossier receipts si nécessaire
        if not os.path.exists(cls.RECEIPTS_DIR):
            os.makedirs(cls.RECEIPTS_DIR)
        
        # Nom du fichier
        id_vente = vente_data['id_vente']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"receipt_{id_vente}_{timestamp}.pdf"
        filepath = os.path.join(cls.RECEIPTS_DIR, filename)
        
        # Créer le PDF
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # Position Y (de haut en bas)
        y = height - 2*cm
        
        # === EN-TÊTE ===
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, y, cls.STORE_NAME)
        y -= 0.5*cm
        
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, y, cls.STORE_ADDRESS)
        y -= 0.4*cm
        c.drawCentredString(width/2, y, cls.STORE_PHONE)
        y -= 0.4*cm
        c.drawCentredString(width/2, y, cls.STORE_EMAIL)
        y -= 1*cm
        
        # === LIGNE SÉPARATRICE ===
        c.line(2*cm, y, width-2*cm, y)
        y -= 0.8*cm
        
        # === INFOS VENTE ===
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y, f"REÇU N° {id_vente}")
        y -= 0.6*cm
        
        c.setFont("Helvetica", 10)
        date_str = vente_data.get('date_vente', datetime.now()).strftime("%d/%m/%Y %H:%M")
        c.drawString(2*cm, y, f"Date: {date_str}")
        y -= 0.5*cm
        c.drawString(2*cm, y, f"Caissier: {vente_data.get('caissier', 'N/A')}")
        y -= 0.5*cm
        c.drawString(2*cm, y, f"Mode: {mode_paiement}")
        y -= 1*cm
        
        # === TABLE ARTICLES ===
        # Données du tableau
        table_data = [['Article', 'Qté', 'P.U. TTC', 'Remise', 'Total TTC']]
        
        for article in vente_data.get('articles', []):
            nom = article['nom_produit'][:30]  # Limiter longueur
            qte = str(article['quantite'])
            pu_ttc = f"{article['prix_unitaire']:,.0f}"
            remise = f"-{article['remise']:.1f}%" if article['remise'] > 0 else ""
            total = f"{article['total_ligne']:,.0f}"
            table_data.append([nom, qte, pu_ttc, remise, total])
        
        # Créer le tableau
        table = Table(table_data, colWidths=[8*cm, 1.5*cm, 2.5*cm, 2*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        # Dessiner le tableau
        table_width, table_height = table.wrap(width, height)
        table.drawOn(c, 2*cm, y - table_height)
        y -= (table_height + 1*cm)
        
        # === LIGNE SÉPARATRICE ===
        c.line(2*cm, y, width-2*cm, y)
        y -= 0.8*cm
        
        # === TOTAUX ===
        x_label = width - 10*cm
        x_value = width - 3*cm
        
        c.setFont("Helvetica", 10)
        c.drawString(x_label, y, "Sous-total TTC:")
        c.drawRightString(x_value, y, f"{totaux['subtotal_ttc']:,.0f} FCFA")
        y -= 0.5*cm
        
        if totaux['total_remises'] > 0:
            c.setFillColor(colors.red)
            c.drawString(x_label, y, "Remises:")
            c.drawRightString(x_value, y, f"-{totaux['total_remises']:,.0f} FCFA")
            c.setFillColor(colors.black)
            y -= 0.5*cm
        
        c.drawString(x_label, y, "Total HT:")
        c.drawRightString(x_value, y, f"{totaux['total_ht']:,.0f} FCFA")
        y -= 0.5*cm
        
        c.drawString(x_label, y, "TVA collectée:")
        c.drawRightString(x_value, y, f"{totaux['montant_tva']:,.0f} FCFA")
        y -= 0.8*cm
        
        # Total final (gros et gras)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_label, y, "TOTAL TTC:")
        c.setFillColor(colors.green)
        c.drawRightString(x_value, y, f"{totaux['total_ttc']:,.0f} FCFA")
        c.setFillColor(colors.black)
        y -= 1.5*cm
        
        # === PIED DE PAGE ===
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(width/2, y, "Merci de votre visite !")
        y -= 0.4*cm
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, y, f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        
        # Sauvegarder
        c.save()
        
        return filepath
