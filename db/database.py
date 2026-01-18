
import sys
import os

# Add parent directory to path to import 'db' module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from db import models
from db import connection

class Database:
    """
    Facade for the legacy database logic.
    Centralizes all backend calls for the Qt application.
    """

    @staticmethod
    def get_connection():
        return connection.get_connection()

    # ================= AUTH =================
    @staticmethod
    def login(email, password):
        """Returns user dict or None"""
        user = models.authenticate_user(email, password)
        # Convert keys to lowercase for UI compatibility (Nom -> nom, Role -> role)
        if user:
            return {k.lower(): v for k, v in user.items()}
        return None

    # ================= PRODUCTS =================
    @staticmethod
    def get_all_products():
        # Fetch directly since models.get_all_products might have wrong names
        conn = Database.get_connection()
        if not conn: return []
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT 
                    p.Id_Produit as id_produit,
                    p.Nom as nom_produit,
                    p.Description as description,
                    p.PrixUnitaireActuel as prix_unitaire,
                    p.StockActuel as quantite_stock,
                    p.StockAlerte as seuil_min_personnalise,
                    c.Libelle as nom_categorie
                FROM Produit p
                JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
                ORDER BY p.Nom
            """)
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def search_products(keyword):
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT 
                    p.Id_Produit as id_produit,
                    p.Nom as nom_produit,
                    p.Description as description,
                    p.PrixUnitaireActuel as prix_unitaire,
                    p.StockActuel as quantite_stock,
                    p.StockAlerte as seuil_min_personnalise,
                    c.Libelle as nom_categorie
                FROM Produit p
                JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
                WHERE p.Nom ILIKE %s OR p.Description ILIKE %s
                ORDER BY p.Nom
            """, (f"%{keyword}%", f"%{keyword}%"))
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_product_by_id(pid):
        conn = Database.get_connection()
        if not conn: return None
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT 
                    p.Id_Produit as id_produit,
                    p.Nom as nom_produit,
                    p.Description as description,
                    p.PrixUnitaireActuel as prix_unitaire,
                    p.StockActuel as quantite_stock,
                    p.StockAlerte as seuil_min_personnalise,
                    c.Libelle as nom_categorie
                FROM Produit p
                JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
                WHERE p.Id_Produit = %s
            """, (pid,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    # ================= SALES =================
    @staticmethod
    def process_sale(cart_items, user_id, mode_paiement='ESPECES'):
        # We need to bridge this to models.process_sale
        # Note: cart_items keys are already 'id', 'quantité', 'prix_unitaire'
        return models.process_sale(cart_items, user_id, mode_paiement)

    # ================= STOCK =================
    @staticmethod
    def get_stock_status():
        # Using the same mapping strategy
        return Database.get_all_products()

    @staticmethod
    def get_movements():
        conn = Database.get_connection()
        if not conn:
            return []
        cur = connection.get_cursor(conn)
        try:
            # Table MouvementStock: DateMouvement, Type, Quantite, Id_Utilisateur, Id_Produit
            cur.execute("""
                SELECT 
                    m.DateMouvement as date_mouvement,
                    p.Nom as nom_produit,
                    m.Type as type_mouvement,
                    m.Quantite as quantite,
                    u.Nom as nom_utilisateur
                FROM MouvementStock m
                JOIN Produit p ON m.Id_Produit = p.Id_Produit
                JOIN Utilisateur u ON m.Id_Utilisateur = u.Id_Utilisateur
                ORDER BY m.DateMouvement DESC
            """)
            return cur.fetchall()
        except Exception as e:
            print(f"Error fetching movements: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    # ================= PURCHASES =================
    @staticmethod
    def get_replenishment_needs():
        conn = Database.get_connection()
        if not conn:
            return []
        cur = connection.get_cursor(conn)
        try:
            # Based on Produit table directly if view is missing
            cur.execute("""
                SELECT 
                    p.Nom as nom_produit,
                    p.StockActuel as quantite_stock,
                    p.StockAlerte as seuil_min_personnalise,
                    (p.StockAlerte * 2 - p.StockActuel) as qte_suggeree,
                    'N/A' as nom_fournisseur_pref
                FROM Produit p
                WHERE p.StockActuel <= p.StockAlerte
            """)
            return cur.fetchall()
        except Exception as e:
            print(f"Error fetching restocking needs: {e}")
            return []
        finally:
            cur.close()
            conn.close()
            
    # ================= ADMIN =================
    @staticmethod
    def get_kpi_daily_revenue():
        conn = Database.get_connection()
        if not conn: return 0
        cur = connection.get_cursor(conn)
        try:
            # Vente table -> calculate total from LigneVente joined
            cur.execute("""
                SELECT SUM(lv.QteVendue * lv.PrixUnitaireVendu) as total
                FROM Vente v
                JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
                WHERE DATE(v.DateVente) = CURRENT_DATE
            """)
            row = cur.fetchone()
            return row['total'] if row and row['total'] else 0
        except Exception as e:
            print(f"Error kpi: {e}")
            return 0
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def refresh_materialized_views():
        # If no MVs, just return True
        return True

    @staticmethod
    def get_daily_sales_for_user(user_id):
        conn = Database.get_connection()
        if not conn: return 0
        cur = conn.cursor()
        try:
            # Sum from Recu table (Validation)
            cur.execute("""
                SELECT COALESCE(SUM(r.MontantTotal), 0)
                FROM Recu r
                WHERE r.Id_Utilisateur = %s 
                  AND DATE(r.DateEmission) = CURRENT_DATE
            """, (user_id,))
            val = cur.fetchone()[0]
            return val if val else 0
        except Exception as e:
            print("Erreur get_daily_sales_for_user:", e)
            return 0
        finally:
            cur.close()
            conn.close()
    
    # ================= CASHIER SPECIFIC =================
    @staticmethod
    def get_cashier_sales_history(user_id, filter_type='today'):
        """
        Récupère l'historique des ventes d'un caissier
        filter_type: 'today', 'yesterday', 'month'
        """
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            date_filter = ""
            if filter_type == 'today':
                date_filter = "AND DATE(v.DateVente) = CURRENT_DATE"
            elif filter_type == 'yesterday':
                date_filter = "AND DATE(v.DateVente) = CURRENT_DATE - INTERVAL '1 day'"
            elif filter_type == 'month':
                date_filter = "AND DATE_TRUNC('month', v.DateVente) = DATE_TRUNC('month', CURRENT_DATE)"
            
            query = f"""
                SELECT 
                    v.Id_Vente as id_vente,
                    v.DateVente as date_vente,
                    COUNT(lv.Id_Produit) as nb_articles,
                    SUM(lv.QteVendue * lv.PrixUnitaireVendu) as total_ht,
                    MAX(r.MontantTotal) as total_ttc,
                    MAX(r.ModePaiement) as mode_paiement
                FROM Vente v
                LEFT JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
                LEFT JOIN Recu r ON v.Id_Vente = r.Id_Vente
                WHERE v.Id_Utilisateur = %s {date_filter}
                GROUP BY v.Id_Vente, v.DateVente
                ORDER BY v.DateVente DESC
            """
            
            cur.execute(query, (user_id,))
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_cashier_sales_history: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_sale_details(sale_id):
        """Récupère les détails d'une vente spécifique"""
        conn = Database.get_connection()
        if not conn:
            return None
        
        cur = connection.get_cursor(conn)
        try:
            # Info vente
            cur.execute("""
                SELECT 
                    v.Id_Vente,
                    v.DateVente,
                    r.MontantTotal,
                    r.ModePaiement
                FROM Vente v
                LEFT JOIN Recu r ON v.Id_Vente = r.Id_Vente
                WHERE v.Id_Vente = %s
            """, (sale_id,))
            
            vente_info = cur.fetchone()
            if not vente_info:
                return None
            
            # Lignes de vente
            cur.execute("""
                SELECT 
                    p.Nom as nom_produit,
                    lv.QteVendue as qte_vendue,
                    lv.PrixUnitaireVendu as prix_unitaire,
                    lv.Remise as remise,
                    COALESCE(lv.TauxTVA, p.TauxTVA, 18.00) as tauxtva,
                    (lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0) / 100.0)) as total_ligne
                FROM LigneVente lv
                JOIN Produit p ON lv.Id_Produit = p.Id_Produit
                WHERE lv.Id_Vente = %s
            """, (sale_id,))
            
            lignes = cur.fetchall()
            
            return {
                'id_vente': vente_info['id_vente'],
                'date_vente': vente_info['datevente'],
                'total_ttc': vente_info.get('montanttotal', 0),
                'mode_paiement': vente_info.get('modepaiement', ''),
                'lignes': lignes
            }
        except Exception as e:
            print(f"Erreur get_sale_details: {e}")
            return None
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_cashier_stats(user_id, period='today'):
        """
        Récupère les statistiques du caissier
        period: 'today', 'week', 'month'
        """
        conn = Database.get_connection()
        if not conn:
            return None
        
        cur = connection.get_cursor(conn)
        try:
            date_filter = "AND DATE(v.DateVente) = CURRENT_DATE"
            if period == 'week':
                date_filter = "AND DATE_PART('week', v.DateVente) = DATE_PART('week', CURRENT_DATE)"
            elif period == 'month':
                date_filter = "AND DATE_TRUNC('month', v.DateVente) = DATE_TRUNC('month', CURRENT_DATE)"
            
            query = f"""
                SELECT 
                    COALESCE(SUM(r.MontantTotal), 0) as total_encaisse,
                    COUNT(DISTINCT v.Id_Vente) as nb_tickets,
                    CASE 
                        WHEN COUNT(DISTINCT v.Id_Vente) > 0 
                        THEN COALESCE(SUM(r.MontantTotal), 0) / COUNT(DISTINCT v.Id_Vente)
                        ELSE 0
                    END as panier_moyen
                FROM Vente v
                LEFT JOIN Recu r ON v.Id_Vente = r.Id_Vente
                WHERE v.Id_Utilisateur = %s
                {date_filter}
            """
            
            cur.execute(query, (user_id,))
            
            return cur.fetchone()
        except Exception as e:
            print(f"Erreur get_cashier_stats: {e}")
            return None
        finally:
            cur.close()
            conn.close()


