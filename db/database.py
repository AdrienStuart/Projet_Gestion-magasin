
import sys
import os

# Add parent directory to path to import 'db' module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from datetime import datetime

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

    @staticmethod
    def get_cashier_hourly_stats(user_id):
        """
        Récupère le CA et nb tickets par heure pour le caissier (aujourd'hui)
        """
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            query = """
                SELECT 
                    EXTRACT(HOUR FROM v.DateVente) as heure,
                    COALESCE(SUM(r.MontantTotal), 0) as total,
                    COUNT(DISTINCT v.Id_Vente) as nb_tickets
                FROM Vente v
                LEFT JOIN Recu r ON v.Id_Vente = r.Id_Vente
                WHERE v.Id_Utilisateur = %s
                AND DATE(v.DateVente) = CURRENT_DATE
                GROUP BY heure
                ORDER BY heure
            """
            cur.execute(query, (user_id,))
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_cashier_hourly_stats: {e}")
            return []
        finally:
            connection.close_connection(conn)

    # ================= STOCK MANAGER SPECIFIC =================
    
    @staticmethod
    def get_stock_overview():
        """Récupère la vue d'ensemble du stock avec statuts"""
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT 
                    p.Id_Produit as id_produit,
                    p.Nom as nom,
                    c.Libelle as categorie,
                    p.Id_Categorie as id_categorie,
                    p.StockActuel as stockactuel,
                    p.StockAlerte as stockalerte,
                    CASE 
                        WHEN p.StockActuel = 0 THEN 'RUPTURE'
                        WHEN p.StockActuel <= p.StockAlerte THEN 'CRITIQUE'
                        ELSE 'OK'
                    END as statut
                FROM Produit p
                JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
                ORDER BY p.Nom
            """)
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_stock_overview: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_stock_movements(filters=None):
        """Récupère l'historique des mouvements de stock"""
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            # Base query
            query = """
                SELECT 
                    m.DateMouvement as datemouvement,
                    p.Nom as nom_produit,
                    m.Type as type,
                    m.Quantite as quantite,
                    u.Nom as nom_utilisateur,
                    m.Commentaire as commentaire
                FROM MouvementStock m
                JOIN Produit p ON m.Id_Produit = p.Id_Produit
                JOIN Utilisateur u ON m.Id_Utilisateur = u.Id_Utilisateur
                ORDER BY m.DateMouvement DESC
                LIMIT 100
            """
            
            cur.execute(query)
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_stock_movements: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def create_stock_movement(product_id, type, quantity, user_id, comment=""):
        """Crée un mouvement de stock (ENTREE/SORTIE)"""
        conn = Database.get_connection()
        if not conn:
            return False, "Erreur de connexion"
        
        cur = connection.get_cursor(conn)
        try:
            # Validation du type
            if type not in ['ENTREE', 'SORTIE', 'AJUSTEMENT']:
                return False, "Type de mouvement invalide"
            
            # Insérer le mouvement
            cur.execute("""
                INSERT INTO MouvementStock (Type, Quantite, Id_Produit, Id_Utilisateur, Commentaire)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING Id_Mouvement
            """, (type, quantity, product_id, user_id, comment))
            
            mvt_id = cur.fetchone()['id_mouvement']
            
            # Mettre à jour le stock
            if type == 'ENTREE':
                cur.execute("""
                    UPDATE Produit 
                    SET StockActuel = StockActuel + %s
                    WHERE Id_Produit = %s
                """, (quantity, product_id))
            elif type == 'SORTIE':
                # Vérifier qu'il y a assez de stock
                cur.execute("SELECT StockActuel FROM Produit WHERE Id_Produit = %s", (product_id,))
                stock_actuel = cur.fetchone()['stockactuel']
                
                if stock_actuel < quantity:
                    conn.rollback()
                    return False, f"Stock insuffisant (actuel: {stock_actuel})"
                
                cur.execute("""
                    UPDATE Produit 
                    SET StockActuel = StockActuel - %s
                    WHERE Id_Produit = %s
                """, (quantity, product_id))
            
            conn.commit()
            return True, mvt_id
            
        except Exception as e:
            conn.rollback()
            print(f"Erreur create_stock_movement: {e}")
            return False, str(e)
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_stock_alerts():
        """Récupère les alertes de stock (ruptures + critiques)"""
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT 
                    p.Id_Produit as id_produit,
                    p.Nom as nom,
                    c.Libelle as categorie,
                    p.StockActuel as stockactuel,
                    p.StockAlerte as stockalerte,
                    COALESCE(
                        EXTRACT(DAY FROM CURRENT_DATE - MAX(m.DateMouvement)),
                        0
                    ) as jours_rupture
                FROM Produit p
                JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
                LEFT JOIN MouvementStock m ON p.Id_Produit = m.Id_Produit AND m.Type = 'ENTREE'
                WHERE p.StockActuel <= p.StockAlerte
                GROUP BY p.Id_Produit, p.Nom, c.Libelle, p.StockActuel, p.StockAlerte
                ORDER BY p.StockActuel ASC, p.Nom
            """)
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_stock_alerts: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_products_to_restock():
        """Liste intelligente des produits à réapprovisionner"""
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT 
                    p.Id_Produit as id_produit,
                    p.Nom as nom,
                    c.Libelle as categorie,
                    p.StockActuel as stockactuel,
                    p.StockAlerte as stockalerte,
                    (p.StockAlerte * 2 - p.StockActuel) as qte_suggere
                FROM Produit p
                JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
                WHERE p.StockActuel <= p.StockAlerte
                ORDER BY 
                    CASE WHEN p.StockActuel = 0 THEN 0 ELSE 1 END,
                    p.StockActuel ASC
            """)
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_products_to_restock: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_stock_stats(period_days=30):
        """Récupère les statistiques de stock pour une période"""
        conn = Database.get_connection()
        if not conn:
            return None
        
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN Type = 'ENTREE' THEN Quantite ELSE 0 END) as total_entrees,
                    SUM(CASE WHEN Type = 'SORTIE' THEN Quantite ELSE 0 END) as total_sorties,
                    COUNT(*) as total_mouvements,
                    (SELECT COUNT(*) FROM Produit WHERE StockActuel > 0) as produits_actifs
                FROM MouvementStock
                WHERE DateMouvement >= CURRENT_DATE - INTERVAL '%s days'
            """, (period_days,))
            
            return cur.fetchone()
        except Exception as e:
            print(f"Erreur get_stock_stats: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_stock_history_daily(period_days=7):
        """Récupère l'historique journalier des entrées/sorties pour les graphiques"""
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                WITH dates AS (
                    SELECT generate_series(
                        CURRENT_DATE - INTERVAL '%s days', 
                        CURRENT_DATE, 
                        '1 day'::interval
                    )::date as jour
                )
                SELECT 
                    d.jour,
                    COALESCE(SUM(CASE WHEN m.Type = 'ENTREE' THEN m.Quantite ELSE 0 END), 0) as entrees,
                    COALESCE(SUM(CASE WHEN m.Type = 'SORTIE' THEN m.Quantite ELSE 0 END), 0) as sorties
                FROM dates d
                LEFT JOIN MouvementStock m ON DATE(m.DateMouvement) = d.jour
                GROUP BY d.jour
                ORDER BY d.jour ASC
            """, (period_days,))
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_stock_history_daily: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_stock_history_hourly():
        """Récupère l'historique horaire des entrées/sorties pour aujourd'hui"""
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT 
                    EXTRACT(HOUR FROM DateMouvement) as heure,
                    COALESCE(SUM(CASE WHEN Type = 'ENTREE' THEN Quantite ELSE 0 END), 0) as entrees,
                    COALESCE(SUM(CASE WHEN Type = 'SORTIE' THEN Quantite ELSE 0 END), 0) as sorties
                FROM MouvementStock
                WHERE DATE(DateMouvement) = CURRENT_DATE
                GROUP BY heure
                ORDER BY heure ASC
            """)
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_stock_history_hourly: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_persistent_alerts():
        """Récupère les alertes persistantes de la table AlerteStock"""
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT 
                    a.Id_Alerte as id_alerte,
                    a.Id_Produit as id_produit,
                    p.Nom as nom_produit,
                    a.Stock_Au_Moment_Alerte as stock_alerte,
                    a.Seuil_Alerte_Vise as seuil_vise,
                    a.Priorite as priorite,
                    a.Statut as statut,
                    a.Commentaire as commentaire,
                    a.Date_Creation as date_creation,
                    a.Date_Traitement as date_traitement
                FROM AlerteStock a
                JOIN Produit p ON a.Id_Produit = p.Id_Produit
                ORDER BY 
                    CASE 
                        WHEN a.Priorite = 'CRITICAL' THEN 1
                        WHEN a.Priorite = 'HIGH' THEN 2
                        WHEN a.Priorite = 'MEDIUM' THEN 3
                        ELSE 4
                    END,
                    a.Date_Creation DESC
            """)
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_persistent_alerts: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def create_manual_alert(id_produit, priorite, commentaire, id_utilisateur):
        """Crée manuellement une alerte preventative"""
        conn = Database.get_connection()
        if not conn:
            return False, "Erreur de connexion"
        
        cur = connection.get_cursor(conn)
        try:
            # Récupérer le stock actuel pour le log
            cur.execute("SELECT StockActuel, StockAlerte FROM Produit WHERE Id_Produit = %s", (id_produit,))
            p = cur.fetchone()
            if not p:
                return False, "Produit non trouvé"
            
            stock_actuel = p['stockactuel']
            seuil_vise = p['stockalerte']
            
            # Formater le commentaire pour inclure l'auteur
            full_comment = f"{commentaire} | Créé manuellement"
            
            cur.execute("""
                INSERT INTO AlerteStock (Id_Produit, Stock_Au_Moment_Alerte, Seuil_Alerte_Vise, Priorite, Statut, Commentaire)
                VALUES (%s, %s, %s, %s, 'NON_LUE', %s)
                RETURNING Id_Alerte
            """, (id_produit, stock_actuel, seuil_vise, priorite, full_comment))
            
            conn.commit()
            return True, "Alerte créée avec succès"
        except Exception as e:
            conn.rollback()
            print(f"Erreur create_manual_alert: {e}")
            return False, str(e)
        finally:
            connection.close_connection(conn)

    @staticmethod
    def update_alert_status(alert_id, new_status, comment=None):
        """Met à jour le statut d'une alerte"""
        conn = Database.get_connection()
        if not conn:
            return False
        
        cur = connection.get_cursor(conn)
        try:
            date_traitement = "NULL"
            if new_status in ['EN_COURS', 'COMMANDE_PASSEE', 'ARCHIVEE']:
                date_traitement = "CURRENT_TIMESTAMP"
                
            query = f"""
                UPDATE AlerteStock 
                SET Statut = %s,
                    Date_Traitement = {date_traitement}
            """
            
            if comment:
                query += ", Commentaire = COALESCE(Commentaire, '') || ' | ' || %s"
                cur.execute(query + " WHERE Id_Alerte = %s", (new_status, comment, alert_id))
            else:
                cur.execute(query + " WHERE Id_Alerte = %s", (new_status, alert_id))
                
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erreur update_alert_status: {e}")
            return False
        finally:
            connection.close_connection(conn)

    @staticmethod
    def get_all_categories():
        """Récupère toutes les catégories"""
        conn = Database.get_connection()
        if not conn:
            return []
        
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT Id_Categorie as id_categorie, Libelle as libelle
                FROM Categorie
                ORDER BY Libelle
            """)
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_all_categories: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    # =========================================================================
    # MODULE RESPONSABLE ACHATS
    # =========================================================================

    @staticmethod
    @staticmethod
    def get_purchasing_dashboard_summary():
        """
        Récupère le résumé complet pour le Command Center (Dashboard V2)
        Retourne : urgences, kpis, finance, risques, trends
        """
        conn = Database.get_connection()
        if not conn: return None
        cur = connection.get_cursor(conn) # RealDictCursor
        
        summary = {
            'urgences': {'critical': 0, 'ruptures': 0, 'retards': 0},
            'kpis': {'actives': 0, 'avg_time': 0.0, 'reactivity': 0.0, 'commandes_cours': 0, 'valeur_commandes_cours': 0},
            'finance': {'budget': 10000000, 'depenses': 0, 'cout_urgences': 0}, # Budget 10M FCFA par défaut
            'risques': [], # [{'nom':, 'stock':, 'seuil':}]
            'trends': [] # [{'jour':, 'count':}]
        }
        
        try:
            # 1. URGENCES
            # Alertes Critiques
            cur.execute("SELECT COUNT(*) as count FROM AlerteStock WHERE Statut IN ('NON_LUE', 'VU', 'EN_COURS') AND Priorite = 'CRITICAL'")
            summary['urgences']['critical'] = cur.fetchone()['count']
            
            # Ruptures (Produits à 0)
            cur.execute("SELECT COUNT(*) as count FROM Produit WHERE StockActuel = 0")
            summary['urgences']['ruptures'] = cur.fetchone()['count']
            
            # Commandes en retard (> 7 jours et non reçues)
            cur.execute("SELECT COUNT(*) as count FROM Achat WHERE Statut = 'EN_ATTENTE' AND DateAchat < CURRENT_DATE - INTERVAL '7 days'")
            summary['urgences']['retards'] = cur.fetchone()['count']
            
            # 2. KPIS EXECUTION
            # Alertes Actives
            cur.execute("SELECT COUNT(*) as count FROM AlerteStock WHERE Statut IN ('NON_LUE', 'VU', 'EN_COURS')")
            summary['kpis']['actives'] = cur.fetchone()['count']
            
            # Temps moyen traitement (24h rolling) - éviter division par zéro
            cur.execute("""
                SELECT COALESCE(EXTRACT(EPOCH FROM AVG(Date_Traitement - Date_Creation))/3600, 0) as avg_time
                FROM AlerteStock 
                WHERE Date_Traitement >= CURRENT_DATE - INTERVAL '24 hours'
            """)
            summary['kpis']['avg_time'] = round(cur.fetchone()['avg_time'], 1)
            
            # Réactivité Critique (< 24h)
            cur.execute("""
                SELECT 
                    (COUNT(CASE WHEN (Date_Traitement - Date_Creation) < INTERVAL '24 hours' THEN 1 END)::float / 
                    NULLIF(COUNT(*), 0) * 100) as reactivity
                FROM AlerteStock
                WHERE Statut IN ('ARCHIVEE', 'COMMANDE_PASSEE')
                AND Priorite = 'CRITICAL'
                AND Date_Traitement >= CURRENT_DATE - INTERVAL '30 days'
            """)
            row = cur.fetchone()
            summary['kpis']['reactivity'] = round(row['reactivity'], 1) if row and row['reactivity'] else 0.0

            # Commandes en cours
            cur.execute("""
                SELECT 
                    COUNT(*) as count, 
                    COALESCE(SUM(la.Quantite * la.PrixAchatNegocie), 0) as val
                FROM Achat a
                JOIN LigneAchat la ON a.Id_Achat = la.Id_Achat
                WHERE a.Statut = 'EN_ATTENTE'
            """)
            res_cmd = cur.fetchone()
            summary['kpis']['commandes_cours'] = res_cmd['count']
            summary['kpis']['valeur_commandes_cours'] = res_cmd['val']

            # 3. FINANCE
            # Dépenses engagées (Mois courant)
            cur.execute("""
                SELECT COALESCE(SUM(la.Quantite * la.PrixAchatNegocie), 0) as total
                FROM Achat a
                JOIN LigneAchat la ON a.Id_Achat = la.Id_Achat
                WHERE DATE_TRUNC('month', a.DateAchat) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            summary['finance']['depenses'] = cur.fetchone()['total']
            
            # Coût Urgences (Commandes générées par alertes CRITICAL ce mois)
            cur.execute("""
                SELECT COALESCE(SUM(la.Quantite * la.PrixAchatNegocie), 0) as total
                FROM Achat a
                JOIN LigneAchat la ON a.Id_Achat = la.Id_Achat
                JOIN AlerteStock al ON al.Id_Achat_Genere = a.Id_Achat
                WHERE al.Priorite = 'CRITICAL'
                AND DATE_TRUNC('month', a.DateAchat) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            summary['finance']['cout_urgences'] = cur.fetchone()['total']

            # 4. RISQUES (Anticipation)
            # Produits proches seuil (Stock < Seuil * 1.1 mais > Seuil)
            cur.execute("""
                SELECT Nom, StockActuel, StockAlerte
                FROM Produit
                WHERE StockActuel <= (StockAlerte * 1.1) AND StockActuel > StockAlerte
                ORDER BY StockActuel ASC
                LIMIT 5
            """)
            summary['risques'] = cur.fetchall()

            # 5. TRENDS (7 derniers jours)
            # Évolution des alertes créées
            cur.execute("""
                WITH Days AS (
                    SELECT generate_series(CURRENT_DATE - INTERVAL '6 days', CURRENT_DATE, '1 day')::date as jour
                )
                SELECT d.jour, COUNT(a.Id_Alerte) as count
                FROM Days d
                LEFT JOIN AlerteStock a ON DATE(a.Date_Creation) = d.jour
                GROUP BY d.jour
                ORDER BY d.jour
            """)
            summary['trends'] = cur.fetchall()

            return summary

        except Exception as e:
            print(f"Erreur get_purchasing_dashboard_summary: {e}")
            conn.rollback()
            return None # L'UI gérera le None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_alert_purchasing_context(product_id):
        """Récupère le contexte décisionnel pour un produit en alerte"""
        conn = Database.get_connection()
        if not conn: return None
        cur = connection.get_cursor(conn)
        try:
            context = {}
            
            # 1. Ventes 30 derniers jours
            cur.execute("""
                SELECT COALESCE(SUM(lv.QteVendue), 0) as sales_30d
                FROM LigneVente lv
                JOIN Vente v ON lv.Id_Vente = v.Id_Vente
                WHERE lv.Id_Produit = %s
                AND v.DateVente > CURRENT_DATE - INTERVAL '30 days'
            """, (product_id,))
            context['sales_30d'] = cur.fetchone()['sales_30d']

            # 2. Dernière commande fournisseur
            cur.execute("""
                SELECT MAX(a.DateAchat) as last_order
                FROM Achat a
                JOIN LigneAchat la ON a.Id_Achat = la.Id_Achat
                WHERE la.Id_Produit = %s
            """, (product_id,))
            context['last_supplier_order'] = cur.fetchone()['last_order']

            # 3. Fréquence ruptures (Alertes créées 90 derniers jours)
            cur.execute("""
                SELECT COUNT(*) as alert_count
                FROM AlerteStock
                WHERE Id_Produit = %s
                AND Date_Creation > CURRENT_DATE - INTERVAL '90 days'
            """, (product_id,))
            context['shortage_freq_90d'] = cur.fetchone()['alert_count']
            
            return context
        except Exception as e:
            print(f"Erreur get_alert_purchasing_context: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def create_purchase_order(user_id, supplier_id, lines, linked_alert_ids=None):
        """
        Crée une commande fournisseur et met à jour les alertes liées
        lines: list of dict {'product_id': str, 'qty': int, 'price': float}
        linked_alert_ids: list of int (Alert IDs to update)
        """
        conn = Database.get_connection()
        if not conn: return False
        cur = connection.get_cursor(conn)
        try:
            # 1. Créer la commande
            cur.execute("""
                INSERT INTO Achat (Id_Utilisateur, Id_Fournisseur, Statut, DateAchat)
                VALUES (%s, %s, 'EN_ATTENTE', CURRENT_TIMESTAMP)
                RETURNING Id_Achat
            """, (user_id, supplier_id))
            purchase_id = cur.fetchone()['id_achat']

            # 2. Insérer les lignes
            for line in lines:
                cur.execute("""
                    INSERT INTO LigneAchat (Id_Achat, Id_Produit, Quantite, PrixAchatNegocie)
                    VALUES (%s, %s, %s, %s)
                """, (purchase_id, line['product_id'], line['qty'], line['price']))

            # 3. Mettre à jour les alertes liées
            if linked_alert_ids:
                for alert_id in linked_alert_ids:
                    # On ne met à jour QUE si l'alerte n'est pas déjà archivée
                    cur.execute("""
                        UPDATE AlerteStock
                        SET Statut = 'COMMANDE_PASSEE',
                            Id_Achat_Genere = %s,
                            Date_Traitement = CURRENT_TIMESTAMP,
                            Commentaire = COALESCE(Commentaire, '') || ' [Auto: Commande #' || %s || ' créée]'
                        WHERE Id_Alerte = %s AND Statut IN ('NON_LUE', 'VU', 'EN_COURS')
                    """, (purchase_id, purchase_id, alert_id))

            conn.commit()
            return purchase_id
        except Exception as e:
            conn.rollback()
            print(f"Erreur create_purchase_order: {e}")
            return False
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_suppliers():
        """Liste simple des fournisseurs"""
        conn = Database.get_connection()
        if not conn: return []
        cur = connection.get_cursor(conn)
        try:
            cur.execute("SELECT Id_Fournisseur, Nom, Contact FROM Fournisseur ORDER BY Nom")
            return cur.fetchall()
        except: return []
        finally: cur.close(); conn.close()

    @staticmethod
    def create_supplier(nom, contact, adresse):
        """Ajoute un nouveau fournisseur dans la base"""
        conn = Database.get_connection()
        if not conn: return False
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                INSERT INTO Fournisseur (Nom, Contact, Adresse) 
                VALUES (%s, %s, %s)
            """, (nom, contact, adresse))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erreur create_supplier: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_supplier_orders(status_filter=None, period_days=None, category_id=None):
        """Récupère les commandes fournisseurs avec filtres avancés"""
        conn = Database.get_connection()
        if not conn: return []
        cur = connection.get_cursor(conn)
        try:
            query = """
                SELECT DISTINCT a.Id_Achat as id_achat, a.DateAchat as date_achat, 
                       a.Statut as statut, f.Nom as fournisseur,
                       (SELECT STRING_AGG(p.Nom, ', ') FROM LigneAchat la JOIN Produit p ON la.Id_Produit = p.Id_Produit WHERE la.Id_Achat = a.Id_Achat) as produits,
                       (SELECT COUNT(*) FROM LigneAchat la WHERE la.Id_Achat = a.Id_Achat) as nb_lignes,
                       (SELECT COALESCE(SUM(la.Quantite * la.PrixAchatNegocie), 0) FROM LigneAchat la WHERE la.Id_Achat = a.Id_Achat) as total_amount
                FROM Achat a
                JOIN Fournisseur f ON a.Id_Fournisseur = f.Id_Fournisseur
                LEFT JOIN LigneAchat la_filter ON a.Id_Achat = la_filter.Id_Achat
                LEFT JOIN Produit p ON la_filter.Id_Produit = p.Id_Produit
                WHERE 1=1
            """
            params = []
            
            if status_filter:
                query += " AND a.Statut = %s"
                params.append(status_filter)
                
            if period_days is not None:
                query += " AND a.DateAchat >= CURRENT_DATE - (%s || ' days')::interval"
                params.append(period_days)
                
            if category_id:
                query += " AND p.Id_Categorie = %s"
                params.append(category_id)
            
            query += " ORDER BY a.DateAchat DESC"
            
            cur.execute(query, tuple(params))
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_supplier_orders: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def get_order_details(id_achat):
        """Récupère les détails d'une commande (lignes d'achat)"""
        conn = Database.get_connection()
        if not conn: return []
        cur = connection.get_cursor(conn)
        try:
            cur.execute("""
                SELECT la.Id_Produit as id_produit, p.Nom as nom, 
                       la.Quantite as quantite, la.PrixAchatNegocie as prixachatnegocie
                FROM LigneAchat la
                JOIN Produit p ON la.Id_Produit = p.Id_Produit
                WHERE la.Id_Achat = %s
            """, (id_achat,))
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_order_details: {e}")
            return []
        finally:
            connection.close_connection(conn)

    # ================= ADMIN MODULE =================
    
    @staticmethod
    def get_admin_dashboard_kpis():
        """
        Dashboard stratégique - KPIs exécutifs
        Returns: dict with ca_today, ca_month, ca_year, marge_brute, 
                 top_products, low_rotation, critical_alerts, stock_value
        """
        conn = Database.get_connection()
        if not conn: return None
        cur = connection.get_cursor(conn)
        
        try:
            result = {}
            
            # CA Aujourd'hui
            cur.execute("""
                SELECT COALESCE(SUM(MontantTotal), 0) as ca_today
                FROM Recu
                WHERE DATE(DateEmission) = CURRENT_DATE
            """)
            result['ca_today'] = cur.fetchone()['ca_today']
            
            # CA Mois
            cur.execute("""
                SELECT COALESCE(SUM(MontantTotal), 0) as ca_month
                FROM Recu
                WHERE DATE_TRUNC('month', DateEmission) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            result['ca_month'] = cur.fetchone()['ca_month']
            
            # CA Année
            cur.execute("""
                SELECT COALESCE(SUM(MontantTotal), 0) as ca_year
                FROM Recu
                WHERE DATE_TRUNC('year', DateEmission) = DATE_TRUNC('year', CURRENT_DATE)
            """)
            result['ca_year'] = cur.fetchone()['ca_year']
            
            # Marge brute estimée (CA - Coût achat estimé des ventes du mois)
            cur.execute("""
                SELECT 
                    COALESCE(SUM(lv.QteVendue * (lv.PrixUnitaireVendu - COALESCE(la.PrixAchatNegocie, p.PrixUnitaireActuel * 0.6))), 0) as marge
                FROM LigneVente lv
                JOIN Vente v ON lv.Id_Vente = v.Id_Vente
                JOIN Produit p ON lv.Id_Produit = p.Id_Produit
                LEFT JOIN LATERAL (
                    SELECT PrixAchatNegocie 
                    FROM LigneAchat la2 
                    WHERE la2.Id_Produit = lv.Id_Produit 
                    ORDER BY Id_Achat DESC LIMIT 1
                ) la ON true
                WHERE DATE_TRUNC('month', v.DateVente) = DATE_TRUNC('month', CURRENT_DATE)
            """)
            result['marge_brute'] = cur.fetchone()['marge']
            
            # Top 5 produits vendus (mois)
            cur.execute("""
                SELECT p.Nom, SUM(lv.QteVendue) as qty
                FROM LigneVente lv
                JOIN Vente v ON lv.Id_Vente = v.Id_Vente
                JOIN Produit p ON lv.Id_Produit = p.Id_Produit
                WHERE DATE_TRUNC('month', v.DateVente) = DATE_TRUNC('month', CURRENT_DATE)
                GROUP BY p.Nom
                ORDER BY qty DESC
                LIMIT 5
            """)
            result['top_products'] = cur.fetchall()
            
            # Produits faible rotation (pas vendus depuis 30j)
            cur.execute("""
                SELECT p.Nom, p.StockActuel
                FROM Produit p
                WHERE NOT EXISTS (
                    SELECT 1 FROM LigneVente lv
                    JOIN Vente v ON lv.Id_Vente = v.Id_Vente
                    WHERE lv.Id_Produit = p.Id_Produit
                    AND v.DateVente >= CURRENT_DATE - INTERVAL '30 days'
                )
                AND p.StockActuel > 0
                ORDER BY p.StockActuel DESC
                LIMIT 5
            """)
            result['low_rotation'] = cur.fetchall()
            
            # Alertes critiques actives
            cur.execute("""
                SELECT COUNT(*) as count
                FROM AlerteStock
                WHERE Priorite = 'CRITICAL'
                AND Statut IN ('NON_LUE', 'VU', 'EN_COURS')
            """)
            result['critical_alerts'] = cur.fetchone()['count']
            
            # Valeur stock immobilisé
            cur.execute("""
                SELECT COALESCE(SUM(StockActuel * PrixUnitaireActuel), 0) as value
                FROM Produit
            """)
            result['stock_value'] = cur.fetchone()['value']
            
            return result
            
        except Exception as e:
            print(f"Error in get_admin_dashboard_kpis: {e}")
            return None
        finally:
            connection.close_connection(conn)
    
    @staticmethod
    def get_sales_by_period(start_date=None, end_date=None):
        """Performance commerciale - CA par période"""
        conn = Database.get_connection()
        if not conn: return []
        cur = connection.get_cursor(conn)
        
        try:
            query = """
                SELECT 
                    DATE(v.DateVente) as date,
                    COUNT(DISTINCT v.Id_Vente) as nb_ventes,
                    COALESCE(SUM(r.MontantTotal), 0) as ca
                FROM Vente v
                LEFT JOIN Recu r ON v.Id_Vente = r.Id_Vente
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND v.DateVente >= %s"
                params.append(start_date)
            if end_date:
                query += " AND v.DateVente <= %s"
                params.append(end_date)
                
            query += " GROUP BY DATE(v.DateVente) ORDER BY date DESC"
            
            cur.execute(query, tuple(params))
            return cur.fetchall()
            
        except Exception as e:
            print(f"Error in get_sales_by_period: {e}")
            return []
        finally:
            connection.close_connection(conn)
    
    @staticmethod
    def get_sales_by_product(limit=10):
        """Performance - Top produits par CA"""
        conn = Database.get_connection()
        if not conn: return []
        cur = connection.get_cursor(conn)
        
        try:
            cur.execute("""
                SELECT 
                    p.Nom as produit,
                    SUM(lv.QteVendue) as qty_vendue,
                    SUM(lv.QteVendue * lv.PrixUnitaireVendu) as ca
                FROM LigneVente lv
                JOIN Produit p ON lv.Id_Produit = p.Id_Produit
                JOIN Vente v ON lv.Id_Vente = v.Id_Vente
                WHERE v.DateVente >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY p.Nom
                ORDER BY ca DESC
                LIMIT %s
            """, (limit,))
            return cur.fetchall()
            
        except Exception as e:
            print(f"Error in get_sales_by_product: {e}")
            return []
        finally:
            connection.close_connection(conn)
    
    @staticmethod
    def get_sales_by_cashier():
        """Performance - CA par caissier"""
        conn = Database.get_connection()
        if not conn: return []
        cur = connection.get_cursor(conn)
        
        try:
            cur.execute("""
                SELECT 
                    u.Nom as caissier,
                    COUNT(DISTINCT v.Id_Vente) as nb_ventes,
                    COALESCE(SUM(r.MontantTotal), 0) as ca,
                    COALESCE(AVG(r.MontantTotal), 0) as panier_moyen
                FROM Vente v
                LEFT JOIN Recu r ON v.Id_Vente = r.Id_Vente
                JOIN Utilisateur u ON v.Id_Utilisateur = u.Id_Utilisateur
                WHERE v.DateVente >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY u.Nom
                ORDER BY ca DESC
                LIMIT 5
            """)
            return cur.fetchall()
            
        except Exception as e:
            print(f"Error in get_sales_by_cashier: {e}")
            return []
        finally:
            connection.close_connection(conn)
    
    @staticmethod
    def get_stock_analysis():
        """Pilotage stocks - Analyse complète"""
        conn = Database.get_connection()
        if not conn: return None
        cur = connection.get_cursor(conn)
        
        try:
            result = {}
            
            # Valeur totale stock
            cur.execute("""
                SELECT COALESCE(SUM(StockActuel * PrixUnitaireActuel), 0) as total
                FROM Produit
            """)
            result['total_value'] = cur.fetchone()['total']
            
            # Produits dormants (pas vendus 30j)
            cur.execute("""
                SELECT p.Nom, p.StockActuel, p.PrixUnitaireActuel,
                       (p.StockActuel * p.PrixUnitaireActuel) as valeur_immobilisee
                FROM Produit p
                WHERE NOT EXISTS (
                    SELECT 1 FROM LigneVente lv
                    JOIN Vente v ON lv.Id_Vente = v.Id_Vente
                    WHERE lv.Id_Produit = p.Id_Produit
                    AND v.DateVente >= CURRENT_DATE - INTERVAL '30 days'
                )
                AND p.StockActuel > 0
                ORDER BY valeur_immobilisee DESC
            """)
            result['dormant_products'] = cur.fetchall()
            
            # Ruptures récurrentes (>2 alertes en 90j)
            cur.execute("""
                SELECT p.Nom, COUNT(*) as nb_ruptures
                FROM AlerteStock a
                JOIN Produit p ON a.Id_Produit = p.Id_Produit
                WHERE a.Date_Creation >= CURRENT_DATE - INTERVAL '90 days'
                AND a.Priorite IN ('CRITICAL', 'HIGH')
                GROUP BY p.Nom
                HAVING COUNT(*) > 2
                ORDER BY nb_ruptures DESC
            """)
            result['recurring_stockouts'] = cur.fetchall()
            
            # Surstocks (stock > 3x seuil)
            cur.execute("""
                SELECT Nom, StockActuel, StockAlerte,
                       (StockActuel * PrixUnitaireActuel) as valeur
                FROM Produit
                WHERE StockActuel > (StockAlerte * 3)
                ORDER BY valeur DESC
            """)
            result['overstocked'] = cur.fetchall()
            
            return result
            
        except Exception as e:
            print(f"Error in get_stock_analysis: {e}")
            return None
        finally:
            connection.close_connection(conn)
    
    @staticmethod
    def get_audit_log(action_type=None, user_id=None, limit=100):
        """Audit - Log des actions système"""
        conn = Database.get_connection()
        if not conn: return []
        cur = connection.get_cursor(conn)
        
        try:
            # Pour une vraie prod, on aurait une table AuditLog
            # Ici on simule avec les tables existantes
            logs = []
            
            # Ventes
            cur.execute("""
                SELECT 
                    'VENTE' as action,
                    u.Nom as user,
                    v.DateVente as timestamp,
                    CONCAT('Vente #', v.Id_Vente, ' - ', r.MontantTotal, ' FCFA') as details
                FROM Vente v
                JOIN Utilisateur u ON v.Id_Utilisateur = u.Id_Utilisateur
                LEFT JOIN Recu r ON v.Id_Vente = r.Id_Vente
                WHERE v.DateVente >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY v.DateVente DESC
                LIMIT %s
            """, (limit,))
            logs.extend(cur.fetchall())
            
            # Achats
            cur.execute("""
                SELECT 
                    'ACHAT' as action,
                    u.Nom as user,
                    a.DateAchat as timestamp,
                    CONCAT('Achat #', a.Id_Achat, ' - ', f.Nom) as details
                FROM Achat a
                JOIN Utilisateur u ON a.Id_Utilisateur = u.Id_Utilisateur
                JOIN Fournisseur f ON a.Id_Fournisseur = f.Id_Fournisseur
                WHERE a.DateAchat >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY a.DateAchat DESC
                LIMIT %s
            """, (limit,))
            logs.extend(cur.fetchall())
            
            # Trier par timestamp
            logs.sort(key=lambda x: x['timestamp'], reverse=True)
            return logs[:limit]
            
        except Exception as e:
            print(f"Error in get_audit_log: {e}")
            return []
        finally:
            connection.close_connection(conn)
    
    @staticmethod
    def get_system_users():
        """Gouvernance - Liste utilisateurs"""
        conn = Database.get_connection()
        if not conn: return []
        cur = connection.get_cursor(conn)
        
        try:
            cur.execute("""
                SELECT Id_Utilisateur, Nom, Role, email
                FROM Utilisateur
                ORDER BY Role, Nom
            """)
            return cur.fetchall()
            
        except Exception as e:
            print(f"Error in get_system_users: {e}")
            return []
        finally:
            connection.close_connection(conn)
    
    @staticmethod
    def update_product_threshold(product_id, new_threshold):
        """Gouvernance - Modifier seuil produit"""
        conn = Database.get_connection()
        if not conn: return False
        cur = connection.get_cursor(conn)
        
        try:
            cur.execute("""
                UPDATE Produit
                SET StockAlerte = %s
                WHERE Id_Produit = %s
            """, (new_threshold, product_id))
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error in update_product_threshold: {e}")
            conn.rollback()
            return False
        finally:
            connection.close_connection(conn)

    @staticmethod
    def get_order_recommendation(product_id):
        """
        Calcule la recommandation de commande pour un produit.
        Logique:
        - Quantité suggérée = Seuil Alerte * 3 (Sécurité + Rotation)
        - Fournisseur = Celui défini dans 'fournir' ou le dernier utilisé
        - Prix = Dernier Prix Achat ou PMP
        """
        conn = Database.get_connection()
        if not conn: return None
        
        cur = connection.get_cursor(conn)
        try:
            # 1. Infos Produit & Seuil
            cur.execute("""
                SELECT Nom, StockActuel, StockAlerte, DernierPrixAchat, PrixAchatMoyen
                FROM Produit WHERE Id_Produit = %s
            """, (product_id,))
            prod = cur.fetchone()
            if not prod: return None
            
            # Algorithme Qty
            seuil = prod['stockalerte']
            suggested_qty = seuil * 3 if seuil > 0 else 10 # Fallback default
            
            # 2. Fournisseur Recommandé
            # Priorité: Celui de la table de liaison 'fournir', sinon le plus fréquent dans l'historique
            cur.execute("""
                SELECT f.Id_Fournisseur, f.Nom
                FROM fournir l
                JOIN Fournisseur f ON l.Id_Fournisseur = f.Id_Fournisseur
                WHERE l.Id_Produit = %s
                LIMIT 1
            """, (product_id,))
            supp = cur.fetchone()
            
            if not supp:
                # Fallback: Dernier fournisseur utilisé
                cur.execute("""
                    SELECT f.Id_Fournisseur, f.Nom
                    FROM Achat a
                    JOIN LigneAchat la ON a.Id_Achat = la.Id_Achat
                    JOIN Fournisseur f ON a.Id_Fournisseur = f.Id_Fournisseur
                    WHERE la.Id_Produit = %s
                    ORDER BY a.DateAchat DESC
                    LIMIT 1
                """, (product_id,))
                supp = cur.fetchone()
            
            # 3. Prix Estimé
            unit_price = prod['dernierprixachat'] if prod['dernierprixachat'] > 0 else prod['prixachatmoyen']
            
            return {
                'product_id': product_id,
                'product_name': prod['nom'],
                'suggested_qty': suggested_qty,
                'supplier_id': supp['id_fournisseur'] if supp else None,
                'supplier_name': supp['nom'] if supp else "Inconnu",
                'unit_price': float(unit_price) if unit_price else 0.0,
                'total_cost': float(unit_price * suggested_qty) if unit_price else 0.0,
                'lead_time_days': 3 # Valeur par défaut (pourrait être dans la DB plus tard)
            }
            
        except Exception as e:
            print(f"Erreur get_order_recommendation: {e}")
            return None
        finally:
            connection.close_connection(conn)

    @staticmethod
    def create_purchase_order_advanced(user_id, supplier_id, lines, linked_alert_ids=None):
        """
        Crée une commande fournisseur et met à jour les alertes liées.
        lines: liste de dict {'product_id', 'qty', 'price'}
        linked_alert_ids: liste d'IDs d'alertes à passer en 'COMMANDE_PASSEE'
        """
        conn = Database.get_connection()
        if not conn: return False
        
        cur = connection.get_cursor(conn)
        try:
            # 1. Créer Achat
            cur.execute("""
                INSERT INTO Achat (Id_Utilisateur, Id_Fournisseur, DateAchat, Statut)
                VALUES (%s, %s, CURRENT_TIMESTAMP, 'EN_ATTENTE')
                RETURNING Id_Achat
            """, (user_id, supplier_id))
            achat_id = cur.fetchone()['id_achat']
            
            # 2. Insérer Lignes
            for line in lines:
                cur.execute("""
                    INSERT INTO LigneAchat (Id_Achat, Id_Produit, Quantite, PrixAchatNegocie)
                    VALUES (%s, %s, %s, %s)
                """, (achat_id, line['product_id'], line['qty'], line['price']))
                
            # 3. Mettre à jour les alertes liées
            if linked_alert_ids:
                cur.execute("""
                    UPDATE AlerteStock
                    SET Statut = 'COMMANDE_PASSEE',
                        Date_Traitement = CURRENT_TIMESTAMP,
                        Id_Achat_Genere = %s,
                        Commentaire = COALESCE(Commentaire, '') || ' | Commande générée #' || %s
                    WHERE Id_Alerte = ANY(%s)
                """, (achat_id, achat_id, linked_alert_ids))
                
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erreur create_purchase_order_advanced: {e}")
            return False
        finally:
            connection.close_connection(conn)

    @staticmethod
    def get_purchasing_stats(period_days=30):
        """
        Récupère les statistiques détaillées pour le Responsable Achats.
        Retourne un dictionnaire avec KPIs et données graphiques.
        """
        conn = Database.get_connection()
        if not conn: return None
        
        cur = connection.get_cursor(conn)
        stats = {
            'performance': {},
            'ruptures': {},
            'finance': {},
            'fournisseurs': [],
            'charts': {'alerts_trend': [], 'orders_vs_risk': [], 'supplier_repartition': []}
        }
        
        try:
            # --- 1. PERFORMANCE ---
            # Alertes traitées sur la période
            cur.execute("""
                SELECT COUNT(*) as count FROM AlerteStock 
                WHERE Date_Traitement >= CURRENT_DATE - (%s || ' days')::interval
                AND Statut IN ('ARCHIVEE', 'COMMANDE_PASSEE')
            """, (period_days,))
            stats['performance']['processed_alerts'] = cur.fetchone()['count'] or 0
            
            # Temps moyen de traitement (en heures)
            cur.execute("""
                SELECT EXTRACT(EPOCH FROM AVG(Date_Traitement - Date_Creation))/3600 as avg_time
                FROM AlerteStock
                WHERE Date_Traitement >= CURRENT_DATE - (%s || ' days')::interval
                AND Date_Traitement IS NOT NULL
            """, (period_days,))
            row = cur.fetchone()
            avg_time = row['avg_time'] if row else None
            stats['performance']['avg_process_time'] = round(avg_time, 1) if avg_time is not None else 0
            
            # % Critiques traitées < 24h
            cur.execute("""
                SELECT 
                    (COUNT(CASE WHEN (Date_Traitement - Date_Creation) < INTERVAL '24 hours' THEN 1 END)::float / 
                    NULLIF(COUNT(*), 0) * 100) as reactivity
                FROM AlerteStock
                WHERE Date_Traitement >= CURRENT_DATE - (%s || ' days')::interval
                AND Priorite = 'CRITICAL'
                AND Statut IN ('ARCHIVEE', 'COMMANDE_PASSEE')
            """, (period_days,))
            row = cur.fetchone()
            reactivity = row['reactivity'] if row else None
            stats['performance']['critical_reactivity'] = round(reactivity, 1) if reactivity is not None else 0.0

            # --- 2. RUPTURES & RISQUES ---
            # Ruptures réelles (Stock au moment alerte = 0)
            cur.execute("""
                SELECT COUNT(*) as count FROM AlerteStock
                WHERE Date_Creation >= CURRENT_DATE - (%s || ' days')::interval
                AND Stock_Au_Moment_Alerte = 0
            """, (period_days,))
            stats['ruptures']['real_shortages'] = cur.fetchone()['count'] or 0
            
            # Ruptures évités (Commandes passées alors que Stock > 0)
            cur.execute("""
                SELECT COUNT(*) as count FROM AlerteStock
                WHERE Date_Traitement >= CURRENT_DATE - (%s || ' days')::interval
                AND Statut = 'COMMANDE_PASSEE'
                AND Stock_Au_Moment_Alerte > 0
            """, (period_days,))
            stats['ruptures']['avoided_shortages'] = cur.fetchone()['count'] or 0
            
            # Top produits à risque (nombre d'alertes)
            cur.execute("""
               SELECT p.Nom, COUNT(*) as nb
               FROM AlerteStock a
               JOIN Produit p ON a.Id_Produit = p.Id_Produit
               WHERE a.Date_Creation >= CURRENT_DATE - (%s || ' days')::interval
               GROUP BY p.Nom
               ORDER BY nb DESC
               LIMIT 5
            """, (period_days,))
            stats['ruptures']['top_risks'] = cur.fetchall()

            # --- 3. FINANCE ---
            # Valeur totale commandée
            cur.execute("""
                SELECT COALESCE(SUM(la.Quantite * la.PrixAchatNegocie), 0) as total
                FROM Achat a
                JOIN LigneAchat la ON a.Id_Achat = la.Id_Achat
                WHERE a.DateAchat >= CURRENT_DATE - (%s || ' days')::interval
            """, (period_days,))
            stats['finance']['total_ordered'] = cur.fetchone()['total']
            
            # Coût des commandes liées à des urgences (CRITICAL)
            cur.execute("""
                SELECT COALESCE(SUM(la.Quantite * la.PrixAchatNegocie), 0) as total
                FROM Achat a
                JOIN LigneAchat la ON a.Id_Achat = la.Id_Achat
                JOIN AlerteStock al ON al.Id_Achat_Genere = a.Id_Achat
                WHERE a.DateAchat >= CURRENT_DATE - (%s || ' days')::interval
                AND al.Priorite = 'CRITICAL'
            """, (period_days,))
            stats['finance']['emergency_cost'] = cur.fetchone()['total']

            # --- 4. CHARTS DATA ---
            # Graph 1: Alertes par jour et priorité
            cur.execute("""
                SELECT DATE(Date_Creation) as jour, Priorite as priorite, COUNT(*) as count
                FROM AlerteStock
                WHERE Date_Creation >= CURRENT_DATE - (%s || ' days')::interval
                GROUP BY jour, Priorite
                ORDER BY jour
            """, (period_days,))
            stats['charts']['alerts_trend'] = cur.fetchall()
            
            # Graph 2: Commandes par jour vs Ruptures (Alertes stock 0)
            cur.execute("""
                WITH Days AS (
                    SELECT generate_series(CURRENT_DATE - (%s || ' days')::interval, CURRENT_DATE, '1 day')::date as jour
                )
                SELECT 
                    d.jour,
                    COUNT(DISTINCT a.Id_Achat) as nb_cdes,
                    COUNT(DISTINCT CASE WHEN al.Stock_Au_Moment_Alerte = 0 THEN al.Id_Alerte END) as nb_ruptures
                FROM Days d
                LEFT JOIN Achat a ON DATE(a.DateAchat) = d.jour
                LEFT JOIN AlerteStock al ON DATE(al.Date_Creation) = d.jour
                GROUP BY d.jour
                ORDER BY d.jour
            """, (period_days,))
            stats['charts']['orders_vs_risk'] = cur.fetchall()
            
            # Graph 3: Volumétrie par fournisseur
            cur.execute("""
                SELECT f.Nom as nom, COUNT(*) as nb
                FROM Achat a
                JOIN Fournisseur f ON a.Id_Fournisseur = f.Id_Fournisseur
                WHERE a.DateAchat >= CURRENT_DATE - (%s || ' days')::interval
                GROUP BY f.Nom
                ORDER BY nb DESC
                LIMIT 5
            """, (period_days,))
            stats['charts']['supplier_repartition'] = cur.fetchall()

            return stats
            
        except Exception as e:
            print(f"Erreur get_purchasing_stats: {e}")
            return None
        finally:
            connection.close_connection(conn)

    # =========================================================================
    #                    GESTIONNAIRE DE STOCK - RÉCEPTION
    # =========================================================================

    @staticmethod
    def get_pending_purchases():
        """Récupère les commandes fournisseurs en attente de réception"""
        conn = Database.get_connection()
        if not conn: return []
        cur = connection.get_cursor(conn) # RealDictCursor
        try:
            # On récupère les infos principales + le nombre de produits
            query = """
                SELECT 
                    a.Id_Achat, 
                    a.DateAchat, 
                    f.Nom as NomFournisseur, 
                    COUNT(la.Id_Produit) as NbProduits,
                    SUM(la.Quantite * la.PrixAchatNegocie) as MontantTotal
                FROM Achat a
                JOIN Fournisseur f ON a.Id_Fournisseur = f.Id_Fournisseur
                LEFT JOIN LigneAchat la ON a.Id_Achat = la.Id_Achat
                WHERE a.Statut = 'EN_ATTENTE'
                GROUP BY a.Id_Achat, a.DateAchat, f.Nom
                ORDER BY a.DateAchat ASC
            """
            cur.execute(query)
            return cur.fetchall()
        except Exception as e:
            print(f"Erreur get_pending_purchases: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def confirm_purchase_receipt(purchase_id, user_id):
        """
        Valide la réception d'une commande :
        1. Passage statut Achat -> RECU
        2. Mise à jour Stock (+ Quantité)
        3. Création Mouvements (ENTREE)
        4. Archivage Alertes liées
        """
        conn = Database.get_connection()
        if not conn: return False
        cur = connection.get_cursor(conn)
        try:
            # 1. Récupérer les lignes de la commande
            cur.execute("""
                SELECT Id_Produit, Quantite, PrixAchatNegocie 
                FROM LigneAchat 
                WHERE Id_Achat = %s
            """, (purchase_id,))
            lignes = cur.fetchall()
            
            if not lignes:
                print(f"Aucune ligne trouvée pour Achat {purchase_id}")
                return False

            # 2. Pour chaque produit
            for ligne in lignes:
                pid = ligne['id_produit']
                qty = ligne['quantite']
                prix = ligne['prixachatnegocie']
                
                # A. Update Stock + Dernier Prix
                cur.execute("""
                    UPDATE Produit 
                    SET StockActuel = StockActuel + %s,
                        DernierPrixAchat = %s
                    WHERE Id_Produit = %s
                """, (qty, prix, pid))
                
                # B. Créer Mouvement
                cur.execute("""
                    INSERT INTO MouvementStock (Type, Quantite, Id_Utilisateur, Id_Produit, Id_Achat, Commentaire)
                    VALUES ('ENTREE', %s, %s, %s, %s, 'Réception Commande Fournisseur')
                """, (qty, user_id, pid, purchase_id))

            # 3. Update Statut Achat
            cur.execute("UPDATE Achat SET Statut = 'RECU' WHERE Id_Achat = %s", (purchase_id,))
            
            # 4. Archiver les alertes liées (Celles qui ont généré cet achat)
            # On suppose qu'on peut lier via Id_Achat si stocké, sinon on archive les alertes 'COMMANDE_PASSEE' pour ces produits
            # Si AlerteStock a une colonne Id_Achat_Genere, on l'utilise.
            # Vérifions le schéma : OUI, Id_Achat_Genere INTEGER REFERENCES Achat(Id_Achat) existe
            
            cur.execute("""
                UPDATE AlerteStock 
                SET Statut = 'ARCHIVEE', Date_Traitement = CURRENT_TIMESTAMP
                WHERE Id_Achat_Genere = %s
            """, (purchase_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Erreur confirm_purchase_receipt: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()
