from db.connection import get_connection, get_cursor

# Authentification
def authenticate_user(email, password):
    conn = get_connection()
    if not conn:
        return None
    cur = get_cursor(conn)
    try:
        cur.execute("""
            SELECT id_utilisateur, nom, role, email 
            FROM utilisateur 
            WHERE email = %s AND motdepasse = %s
        """, (email, password))
        return cur.fetchone()
    except Exception as e:
        print("Erreur authenticate_user :", e)
        return None
    finally:
        cur.close()
        conn.close()

# Ventes
def process_sale(cart_items, user_id, mode_paiement='ESPECES'):
    conn = get_connection()
    if not conn:
        return False, "Erreur de connexion"
    cur = get_cursor(conn)
    try:
        # 1. Créer la vente
        cur.execute("INSERT INTO Vente (Id_Utilisateur) VALUES (%s) RETURNING Id_Vente", (user_id,))
        id_vente = cur.fetchone()['id_vente']

        total_general = 0
        # 2. Insérer les lignes
        for item in cart_items:
            pid = item['id']
            qty = item['quantité']
            remise = item.get('remise', 0)
            prix_u = item['prix_unitaire']
            taux_tva = item.get('taux_tva', 18.00)  # Taux TVA au moment de la vente
            
            cur.execute("""
                INSERT INTO LigneVente (Id_Vente, Id_Produit, QteVendue, Remise, PrixUnitaireVendu, TauxTVA)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_vente, pid, qty, remise, prix_u, taux_tva))
            
            total_general += qty * prix_u * (1 - remise/100.0)

        # 3. Créer le reçu
        cur.execute("""
            INSERT INTO Recu (ModePaiement, MontantTotal, Id_Utilisateur, Id_Vente)
            VALUES (%s, %s, %s, %s)
        """, (mode_paiement, total_general, user_id, id_vente))

        conn.commit()
        return True, id_vente
    except Exception as e:
        conn.rollback()
        print("Erreur process_sale :", e)
        return False, str(e)
    finally:
        cur.close()
        conn.close()

# Exemple minimal pour l'insertion
def add_utilisateur(nom, email, mot_de_passe, role):
    conn = get_connection()
    if not conn:
        return False
    cur = get_cursor(conn)
    try:
        cur.execute("""
            INSERT INTO utilisateur (nom, email, motdepasse, role)
            VALUES (%s, %s, %s, %s)
        """, (nom, email, mot_de_passe, role))
        conn.commit()
        return True
    except Exception as e:
        print("Erreur add_utilisateur :", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
