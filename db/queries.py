from db.connection import get_connection, get_cursor

# Exemple minimal pour sélectionner tous les utilisateurs
def get_all_utilisateurs():
    conn = get_connection()
    if not conn:
        return []
    cur = get_cursor(conn)
    try:
        cur.execute("SELECT * FROM utilisateur ORDER BY id_utilisateur")
        result = cur.fetchall()
        return result
    except Exception as e:
        print("Erreur get_all_utilisateurs :", e)
        return []
    finally:
        cur.close()
        conn.close()
