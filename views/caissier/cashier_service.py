"""
Service métier pour le module Caissier
Gère la logique métier (panier, calculs, validations)
Sépare la logique de l'interface utilisateur
"""

from typing import Dict, List, Tuple, Optional
from decimal import Decimal

# ==================== GESTION DU PANIER ====================

class PanierService:
    """
    Service de gestion du panier de vente
    Maintient l'état du panier et effectue les calculs
    """
    
    def __init__(self):
        # Structure: {id_produit: {'produit': dict, 'quantite': int, 'remise': float}}
        self.articles: Dict = {}
    
    def ajouter_produit(self, produit: dict, quantite: int = 1) -> None:
        """
        Ajoute un produit au panier ou incrémente sa quantité
        
        Args:
            produit: Dictionnaire contenant les infos du produit
            quantite: Quantité à ajouter (défaut: 1)
        """
        id_produit = produit['id_produit']
        
        if id_produit in self.articles:
            self.articles[id_produit]['quantite'] += quantite
        else:
            self.articles[id_produit] = {
                'produit': produit,
                'quantite': quantite,
                'remise': 0.0  # Pas de remise par défaut
            }
    
    def retirer_produit(self, id_produit: str) -> None:
        """Retire complètement un produit du panier"""
        if id_produit in self.articles:
            del self.articles[id_produit]
    
    def modifier_quantite(self, id_produit: str, nouvelle_quantite: int) -> bool:
        """
        Modifie la quantité d'un article
        
        Returns:
            True si succès, False si échec
        """
        if id_produit not in self.articles:
            return False
        
        if nouvelle_quantite <= 0:
            self.retirer_produit(id_produit)
        else:
            self.articles[id_produit]['quantite'] = nouvelle_quantite
        
        return True
    
    def appliquer_remise(self, id_produit: str, pourcentage_remise: float) -> bool:
        """
        Applique une remise sur un article (0-100%)
        
        Returns:
            True si succès, False si échec
        """
        if id_produit not in self.articles:
            return False
        
        if 0 <= pourcentage_remise <= 100:
            self.articles[id_produit]['remise'] = pourcentage_remise
            return True
        
        return False
    
    def vider_panier(self) -> None:
        """Vide complètement le panier"""
        self.articles = {}
    
    def est_vide(self) -> bool:
        """Vérifie si le panier est vide"""
        return len(self.articles) == 0
    
    def obtenir_articles(self) -> Dict:
        """Retourne tous les articles du panier"""
        return self.articles


# ==================== CALCULS ====================

class CalculateurVente:
    """
    Service de calcul pour les ventes
    Gère les calculs de totaux, TVA (extraction depuis TTC), remises
    Note: Les prix en DB sont TTC (Toutes Taxes Comprises)
    """
    
    @staticmethod
    def calculer_total_ligne(prix_unitaire: float, quantite: int, remise: float = 0.0) -> float:
        """
        Calcule le total d'une ligne de vente
        
        Args:
            prix_unitaire: Prix unitaire du produit
            quantite: Quantité vendue
            remise: Pourcentage de remise (0-100)
        
        Returns:
            Total de la ligne après remise
        """
        sous_total = prix_unitaire * quantite
        montant_remise = sous_total * (remise / 100.0)
        return sous_total - montant_remise
    
    
    @classmethod
    def calculer_totaux_panier(cls, articles: Dict) -> Dict[str, float]:
        """
        Calcule les totaux pour tout le panier (Prix TTC -> extraction HT et TVA)
        
        Args:
            articles: Dictionnaire des articles du panier
        
        Returns:
            Dict avec: subtotal_ttc, total_remises, total_ht, montant_tva, total_ttc
        """
        subtotal_ttc = 0.0
        total_remises = 0.0
        total_ht = 0.0
        montant_tva = 0.0
        
        for article in articles.values():
            produit = article['produit']
            quantite = article['quantite']
            remise = article['remise']
            prix_unitaire_ttc = float(produit['prix_unitaire'])
            taux_tva = float(produit.get('tauxtva', 18.00))  # Défaut 18%
            
            # Prix TTC sans remise
            ligne_ttc_sans_remise = prix_unitaire_ttc * quantite
            
            # Prix TTC avec remise
            ligne_ttc_avec_remise = ligne_ttc_sans_remise * (1 - remise / 100.0)
            
            # Extraction du HT depuis le TTC: HT = TTC / (1 + Taux/100)
            ligne_ht = ligne_ttc_avec_remise / (1 + taux_tva / 100.0)
            
            # TVA = TTC - HT
            ligne_tva = ligne_ttc_avec_remise - ligne_ht
            
            subtotal_ttc += ligne_ttc_sans_remise
            total_remises += (ligne_ttc_sans_remise - ligne_ttc_avec_remise)
            total_ht += ligne_ht
            montant_tva += ligne_tva
        
        total_ttc = total_ht + montant_tva
        
        return {
            'subtotal_ttc': round(subtotal_ttc, 2),      # Total TTC avant remises
            'total_remises': round(total_remises, 2),
            'total_ht': round(total_ht, 2),               # Total HT (après remises)
            'montant_tva': round(montant_tva, 2),         # TVA collectée
            'total_ttc': round(total_ttc, 2)              # Total TTC final (à payer)
        }


# ==================== VALIDATION ====================

class ValidationVente:
    """
    Service de validation des données de vente
    Vérifie la cohérence avant envoi à la DB
    """
    
    @staticmethod
    def valider_panier(articles: Dict) -> Tuple[bool, str]:
        """
        Valide qu'un panier peut être vendu
        
        Returns:
            (succès, message_erreur)
        """
        if not articles:
            return False, "Le panier est vide"
        
        for id_produit, article in articles.items():
            produit = article['produit']
            quantite = article['quantite']
            
            # Vérifier stock disponible
            stock_disponible = produit.get('quantite_stock', 0)
            if quantite > stock_disponible:
                nom = produit.get('nom_produit', id_produit)
                return False, f"Stock insuffisant pour {nom} (disponible: {stock_disponible})"
        
        return True, ""
    
    @staticmethod
    def valider_montant_paiement(total_a_payer: float, montant_recu: float) -> Tuple[bool, str]:
        """
        Valide qu'un montant de paiement est suffisant
        
        Returns:
            (succès, message_erreur)
        """
        if montant_recu < total_a_payer:
            return False, f"Montant insuffisant (manque: {total_a_payer - montant_recu:.2f})"
        
        return True, ""


# ==================== FORMATAGE ====================

class FormateurDevise:
    """Utilitaires de formatage pour l'affichage"""
    
    @staticmethod
    def formater_fcfa(montant: float) -> str:
        """Formate un montant en FCFA"""
        return f"{montant:,.0f} FCFA"
    
    @staticmethod
    def calculer_monnaie(total: float, montant_recu: float) -> float:
        """Calcule la monnaie à rendre"""
        return max(0, montant_recu - total)
