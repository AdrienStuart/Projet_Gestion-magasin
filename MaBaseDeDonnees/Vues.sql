
-- VUES ESSENTIELLES

-- Vue 1: Produits disponibles pour le caissier 
CREATE OR REPLACE VIEW vue_produits_disponibles AS
SELECT 
    Id_Produit,
    Nom,
    PrixUnitaireActuel,
    StockActuel
FROM Produit
WHERE StockActuel > 0
ORDER BY Nom;

-- Vue 2: État du stock pour le gestionnaire 
CREATE OR REPLACE VIEW vue_etat_stock AS
SELECT 
    p.Id_Produit,
    p.Nom,
    c.Libelle AS Categorie,
    p.StockActuel,
    p.StockAlerte,
    CASE 
        WHEN p.StockActuel <= 0 THEN 'RUPTURE'
        WHEN p.StockActuel <= p.StockAlerte THEN 'ALERTE'
        ELSE 'NORMAL'
    END AS Etat
FROM Produit p
JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
ORDER BY p.StockActuel ASC;

-- Vue 3: Ventes du jour pour le caissier 
CREATE OR REPLACE VIEW vue_ventes_jour AS
SELECT 
    v.Id_Vente,
    v.DateVente AS Date,
    u.Nom AS Vendeur,
    COUNT(DISTINCT lv.Id_Produit) AS Nb_Produits,
    SUM(lv.QteVendue) AS Total_Articles,
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS Total
FROM Vente v
JOIN Utilisateur u ON v.Id_Utilisateur = u.Id_Utilisateur
JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
WHERE DATE(v.DateVente) = CURRENT_DATE
GROUP BY v.Id_Vente, v.DateVente, u.Nom
ORDER BY v.DateVente DESC;

-- Vue 4: Mouvements récents pour le gestionnaire 
CREATE OR REPLACE VIEW vue_mouvements_recents AS
SELECT 
    m.DateMouvement AS Date,
    p.Nom AS Produit,
    m.Type,
    m.Quantite,
    CASE 
        WHEN m.Id_Vente IS NOT NULL THEN 'VENTE'
        WHEN m.Id_Achat IS NOT NULL THEN 'ACHAT'
        ELSE 'AJUSTEMENT'
    END AS Source,
    m.Commentaire
FROM MouvementStock m
JOIN Produit p ON m.Id_Produit = p.Id_Produit
ORDER BY m.DateMouvement DESC
LIMIT 100;

-- Vue 5: Besoins en réapprovisionnement et alertes stock
CREATE OR REPLACE VIEW vue_alertes_stock AS
SELECT 
    p.Id_Produit,
    p.Nom,
    c.Libelle AS Categorie,
    f.Nom AS Fournisseur_Principal,
    p.StockActuel,
    p.StockAlerte,
    (p.StockAlerte * 2 - p.StockActuel) AS Quantite_A_Commander,
    CASE 
        WHEN p.StockActuel <= 0 THEN 'RUPTURE'
        WHEN p.StockActuel <= p.StockAlerte THEN 'CRITIQUE'
        ELSE 'NORMAL'
    END AS Niveau_Urgence
FROM Produit p
JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
LEFT JOIN fournir fr ON p.Id_Produit = fr.Id_Produit
LEFT JOIN Fournisseur f ON fr.Id_Fournisseur = f.Id_Fournisseur
WHERE p.StockActuel <= p.StockAlerte
ORDER BY p.StockActuel ASC;

-- Vue 6: Performance des vendeurs et caissiers
CREATE OR REPLACE VIEW vue_performance_vendeurs AS
SELECT 
    u.Id_Utilisateur,
    u.Nom,
    u.Role,
    u.email,
    COUNT(DISTINCT v.Id_Vente) AS Nb_Ventes,
    COALESCE(SUM(lv.QteVendue), 0) AS Articles_Vendus,
    ROUND(COALESCE(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 0), 2) AS Chiffre_Affaires,
    CASE 
        WHEN COUNT(DISTINCT v.Id_Vente) > 0 
        THEN ROUND(COALESCE(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 0) / COUNT(DISTINCT v.Id_Vente), 2)
        ELSE 0
    END AS Panier_Moyen,
    MIN(v.DateVente) AS Premiere_Vente,
    MAX(v.DateVente) AS Derniere_Vente
FROM Utilisateur u
LEFT JOIN Vente v ON u.Id_Utilisateur = v.Id_Utilisateur
LEFT JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
WHERE u.Role IN ('Caissier', 'Administrateur')
GROUP BY u.Id_Utilisateur, u.Nom, u.Role, u.email
ORDER BY Chiffre_Affaires DESC;

-- Vue 7: Top 10 produits par CA et marge
CREATE OR REPLACE VIEW vue_top_produits AS
SELECT 
    p.Id_Produit,
    p.Nom,
    c.Libelle AS Categorie,
    SUM(lv.QteVendue) AS Quantite_Vendue,
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS Chiffre_Affaires,
    ROUND(SUM(lv.QteVendue * (lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0) - p.PrixAchatMoyen)), 2) AS Marge_Totale,
    ROUND(AVG(lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0) - p.PrixAchatMoyen), 2) AS Marge_Unitaire,
    CASE 
        WHEN SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) > 0
        THEN ROUND(SUM(lv.QteVendue * (lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0) - p.PrixAchatMoyen)) / 
                   SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) * 100, 2)
        ELSE 0
    END AS Taux_Marge_Pourcent
FROM Produit p
JOIN LigneVente lv ON p.Id_Produit = lv.Id_Produit
JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
GROUP BY p.Id_Produit, p.Nom, c.Libelle
ORDER BY Chiffre_Affaires DESC
LIMIT 10;

-- Vue 8: Performance périodique (mensuelle)
CREATE OR REPLACE VIEW vue_performance_periodique AS
SELECT 
    EXTRACT(YEAR FROM v.DateVente) AS Annee,
    EXTRACT(MONTH FROM v.DateVente) AS Mois,
    COUNT(DISTINCT v.Id_Vente) AS Nb_Ventes,
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS Chiffre_Affaires,
    SUM(lv.QteVendue) AS Total_Articles_Vendus,
    CASE 
        WHEN COUNT(DISTINCT v.Id_Vente) > 0 
        THEN ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) / COUNT(DISTINCT v.Id_Vente), 2)
        ELSE 0
    END AS Panier_Moyen
FROM Vente v
JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
GROUP BY EXTRACT(YEAR FROM v.DateVente), EXTRACT(MONTH FROM v.DateVente)
ORDER BY Annee DESC, Mois DESC;

-- Vue 9: Facturation des ventes (ticket de caisse)
CREATE OR REPLACE VIEW vue_ticket_vente AS
SELECT 
    v.Id_Vente,
    v.DateVente,
    u.Nom AS Vendeur,
    p.Nom AS Produit,
    lv.QteVendue,
    lv.PrixUnitaireVendu AS Prix_Unitaire,
    lv.Remise,
    ROUND(lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0), 2) AS Prix_Remise,
    ROUND(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0), 2) AS Total_Ligne
FROM Vente v
JOIN Utilisateur u ON v.Id_Utilisateur = u.Id_Utilisateur
JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
JOIN Produit p ON lv.Id_Produit = p.Id_Produit
ORDER BY v.DateVente DESC, v.Id_Vente, p.Nom;

-- Vue 10: Interface de vente rapide
CREATE OR REPLACE VIEW vue_vente_rapide AS
SELECT 
    p.Id_Produit,
    p.Nom,
    p.PrixUnitaireActuel AS Prix,
    p.StockActuel,
    c.Libelle AS Categorie
FROM Produit p
JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
WHERE p.StockActuel > 0
ORDER BY c.Libelle, p.Nom;

-- Vue 11: Tableau de bord admin
CREATE OR REPLACE VIEW vue_tableau_bord_admin AS
WITH 
stats_ventes AS (
    SELECT 
        COUNT(DISTINCT CASE WHEN DATE(v.DateVente) = CURRENT_DATE THEN v.Id_Vente END) AS Ventes_Aujourdhui,
        COALESCE(SUM(CASE WHEN DATE(v.DateVente) = CURRENT_DATE THEN lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0) END), 0) AS CA_Aujourdhui,
        COUNT(DISTINCT CASE WHEN DATE(v.DateVente) = CURRENT_DATE - 1 THEN v.Id_Vente END) AS Ventes_Hier,
        COALESCE(SUM(CASE WHEN DATE(v.DateVente) = CURRENT_DATE - 1 THEN lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0) END), 0) AS CA_Hier,
        COUNT(DISTINCT CASE WHEN EXTRACT(MONTH FROM v.DateVente) = EXTRACT(MONTH FROM CURRENT_DATE) 
                            AND EXTRACT(YEAR FROM v.DateVente) = EXTRACT(YEAR FROM CURRENT_DATE) 
                            THEN v.Id_Vente END) AS Ventes_Ce_Mois,
        COALESCE(SUM(CASE WHEN EXTRACT(MONTH FROM v.DateVente) = EXTRACT(MONTH FROM CURRENT_DATE) 
                          AND EXTRACT(YEAR FROM v.DateVente) = EXTRACT(YEAR FROM CURRENT_DATE) 
                          THEN lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0) END), 0) AS CA_Ce_Mois,
        COUNT(DISTINCT v.Id_Vente) AS Ventes_Total,
        COALESCE(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 0) AS CA_Total
    FROM Vente v
    LEFT JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
),
stats_stock AS (
    SELECT 
        COUNT(*) AS Total_Produits,
        SUM(CASE WHEN StockActuel <= StockAlerte AND StockActuel > 0 THEN 1 ELSE 0 END) AS Produits_Alerte,
        SUM(CASE WHEN StockActuel = 0 THEN 1 ELSE 0 END) AS Produits_Rupture,
        SUM(StockActuel) AS Total_Articles_Stock,
        ROUND(SUM(StockActuel * PrixAchatMoyen), 2) AS Valeur_Stock_PMP,
        ROUND(SUM(StockActuel * PrixUnitaireActuel), 2) AS Valeur_Stock_Vente
    FROM Produit
),
stats_achats AS (
    SELECT 
        COUNT(DISTINCT a.Id_Achat) AS Achats_En_Attente,
        COALESCE(SUM(la.Quantite * la.PrixAchatNegocie), 0) AS Valeur_Achats_Attente
    FROM Achat a
    JOIN LigneAchat la ON a.Id_Achat = la.Id_Achat
    WHERE a.Statut = 'EN_ATTENTE'
)
SELECT 
    sv.CA_Aujourdhui,
    sv.CA_Hier,
    sv.CA_Ce_Mois,
    sv.CA_Total,
    CASE 
        WHEN sv.CA_Hier > 0 
        THEN ROUND(((sv.CA_Aujourdhui - sv.CA_Hier) / sv.CA_Hier * 100), 2)
        ELSE 0 
    END AS Evolution_CA_Pourcent,
    sv.Ventes_Aujourdhui,
    sv.Ventes_Hier,
    sv.Ventes_Ce_Mois,
    sv.Ventes_Total,
    CASE 
        WHEN sv.Ventes_Aujourdhui > 0 
        THEN ROUND(sv.CA_Aujourdhui / sv.Ventes_Aujourdhui, 2)
        ELSE 0 
    END AS Panier_Moyen_Aujourdhui,
    ss.Total_Produits,
    ss.Produits_Alerte,
    ss.Produits_Rupture,
    ss.Total_Articles_Stock,
    ss.Valeur_Stock_PMP,
    ss.Valeur_Stock_Vente,
    ROUND(ss.Valeur_Stock_Vente - ss.Valeur_Stock_PMP, 2) AS Marge_Potentielle_Stock,
    sa.Achats_En_Attente,
    sa.Valeur_Achats_Attente
FROM stats_ventes sv, stats_stock ss, stats_achats sa;

-- Vue 12: CA par heure (pour graphique temps réel)
CREATE OR REPLACE VIEW vue_ca_par_heure AS
SELECT 
    EXTRACT(HOUR FROM v.DateVente) AS Heure,
    COUNT(DISTINCT v.Id_Vente) AS Nombre_Ventes,
    SUM(lv.QteVendue) AS Articles_Vendus,
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS Chiffre_Affaires,
    ROUND(AVG(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS Panier_Moyen
FROM Vente v
JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
WHERE DATE(v.DateVente) = CURRENT_DATE
GROUP BY EXTRACT(HOUR FROM v.DateVente)
ORDER BY Heure;

-- Vue 13: CA par jour des 30 derniers jours
CREATE OR REPLACE VIEW vue_ca_30_derniers_jours AS
SELECT 
    DATE(v.DateVente) AS Date,
    COUNT(DISTINCT v.Id_Vente) AS Nombre_Ventes,
    SUM(lv.QteVendue) AS Articles_Vendus,
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS Chiffre_Affaires,
    ROUND(AVG(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS Panier_Moyen
FROM Vente v
JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
WHERE v.DateVente >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(v.DateVente)
ORDER BY Date DESC;

-- Vue 14: CA par catégorie
CREATE OR REPLACE VIEW vue_ca_par_categorie AS
SELECT 
    c.Id_Categorie,
    c.Libelle AS Categorie,
    COUNT(DISTINCT v.Id_Vente) AS Nombre_Ventes,
    SUM(lv.QteVendue) AS Articles_Vendus,
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS Chiffre_Affaires,
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) * 100.0 / NULLIF(
        (SELECT SUM(lv2.QteVendue * lv2.PrixUnitaireVendu * (1 - COALESCE(lv2.Remise, 0)/100.0))
         FROM LigneVente lv2), 0), 2) AS Pourcentage_CA
FROM Categorie c
JOIN Produit p ON c.Id_Categorie = p.Id_Categorie
JOIN LigneVente lv ON p.Id_Produit = lv.Id_Produit
JOIN Vente v ON lv.Id_Vente = v.Id_Vente
GROUP BY c.Id_Categorie, c.Libelle
ORDER BY Chiffre_Affaires DESC;

-- Vue 15: Alertes critiques pour admin
CREATE OR REPLACE VIEW vue_alertes_critiques AS
SELECT 
    'STOCK' AS Type_Alerte,
    p.Id_Produit,
    p.Nom AS Produit,
    c.Libelle AS Categorie,
    p.StockActuel,
    p.StockAlerte,
    CASE 
        WHEN p.StockActuel = 0 THEN 'RUPTURE DE STOCK'
        ELSE 'STOCK CRITIQUE'
    END AS Message,
    'Reapprovisionnement urgent' AS Action_Recommandee
FROM Produit p
JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
WHERE p.StockActuel <= p.StockAlerte
UNION ALL
SELECT 
    'ACHAT' AS Type_Alerte,
    NULL AS Id_Produit,
    'Commande #' || a.Id_Achat AS Produit,
    f.Nom AS Categorie,
    NULL AS StockActuel,
    NULL AS StockAlerte,
    'Commande en attente depuis ' || EXTRACT(DAY FROM CURRENT_TIMESTAMP - a.DateAchat) || ' jours' AS Message,
    'Réceptionner la commande' AS Action_Recommandee
FROM Achat a
JOIN Fournisseur f ON a.Id_Fournisseur = f.Id_Fournisseur
WHERE a.Statut = 'EN_ATTENTE' AND a.DateAchat < CURRENT_TIMESTAMP - INTERVAL '3 days'
ORDER BY Type_Alerte, StockActuel;

-- Vue 16: Besoins en réapprovisionnement détaillés
CREATE OR REPLACE VIEW vue_besoin_reappro AS
SELECT DISTINCT ON (p.Id_Produit)
    p.Id_Produit,
    p.Nom AS Produit,
    p.StockActuel,
    p.StockAlerte,
    (p.StockAlerte * 3) - p.StockActuel AS Quantite_Suggeree,  -- Commande pour avoir 3x le seuil
    COALESCE(f.Nom, 'AUCUN FOURNISSEUR') AS Fournisseur_Principal,
    COALESCE(f.Contact, 'À RENSEIGNER') AS Contact_Fournisseur,
    COALESCE(f.Adresse, 'À RENSEIGNER') AS Adresse_Fournisseur
FROM Produit p
LEFT JOIN fournir fr ON p.Id_Produit = fr.Id_Produit
LEFT JOIN Fournisseur f ON fr.Id_Fournisseur = f.Id_Fournisseur
WHERE p.StockActuel <= p.StockAlerte
ORDER BY p.Id_Produit, fr.Quantite DESC NULLS LAST;  -- Les produits sans fournisseur apparaissent à la fin


-- Vue 17: Journal complet des mouvements de stock
CREATE OR REPLACE VIEW vue_journal_mouvements AS
SELECT 
    m.Id_Mouvement,
    m.DateMouvement,
    m.Type,
    p.Nom AS Produit,
    m.Quantite,
    u.Nom AS Utilisateur,
    u.Role AS Role_Utilisateur,
    CASE 
        WHEN m.Id_Vente IS NOT NULL THEN 'Vente #' || m.Id_Vente
        WHEN m.Id_Achat IS NOT NULL THEN 'Achat #' || m.Id_Achat
        ELSE 'Manuel'
    END AS Operation,
    m.Commentaire
FROM MouvementStock m
JOIN Produit p ON m.Id_Produit = p.Id_Produit
JOIN Utilisateur u ON m.Id_Utilisateur = u.Id_Utilisateur
ORDER BY m.DateMouvement DESC;

-- Vue matérialisée 1: Stats annuelles avec TVA (à rafraîchir 1x/jour)
DROP MATERIALIZED VIEW IF EXISTS mv_stats_annuelles;
CREATE MATERIALIZED VIEW mv_stats_annuelles AS
SELECT 
    EXTRACT(YEAR FROM v.DateVente) AS Annee,
    COUNT(DISTINCT v.Id_Vente) AS Nb_Ventes,
    SUM(lv.QteVendue) AS Articles_Vendus,
    -- CA TTC (Argent encaissé)
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS CA_TTC,
    -- CA HT (Argent réel du magasin)
    ROUND(SUM((lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) / (1 + COALESCE(lv.TauxTVA, p.TauxTVA, 18.00)/100)), 2) AS CA_HT,
    -- TVA à reverser (La différence)
    ROUND(SUM(
        (lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) - 
        ((lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) / (1 + COALESCE(lv.TauxTVA, p.TauxTVA, 18.00)/100))
    ), 2) AS TVA_Collectee,
    -- Marge réelle (Basée sur le HT)
    ROUND(SUM(
        ((lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) / (1 + COALESCE(lv.TauxTVA, p.TauxTVA, 18.00)/100)) 
        - (lv.QteVendue * p.PrixAchatMoyen)
    ), 2) AS Marge_Nette_HT
FROM Vente v
JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
JOIN Produit p ON lv.Id_Produit = p.Id_Produit
GROUP BY EXTRACT(YEAR FROM v.DateVente)
ORDER BY Annee DESC;

-- Vue matérialisée 2: Stats historiques journalières
CREATE MATERIALIZED VIEW mv_stats_historiques AS
SELECT 
    DATE(v.DateVente) AS Date_Vente,
    EXTRACT(YEAR FROM v.DateVente) AS Annee,
    EXTRACT(MONTH FROM v.DateVente) AS Mois,
    EXTRACT(DAY FROM v.DateVente) AS Jour,
    COUNT(DISTINCT v.Id_Vente) AS Nb_Ventes,
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS Chiffre_Affaires
FROM Vente v
JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
GROUP BY DATE(v.DateVente), EXTRACT(YEAR FROM v.DateVente), EXTRACT(MONTH FROM v.DateVente), EXTRACT(DAY FROM v.DateVente)
ORDER BY Date_Vente DESC;

-- Pour rafraîchir les vues matérialisées :
-- REFRESH MATERIALIZED VIEW mv_stats_annuelles;
-- REFRESH MATERIALIZED VIEW mv_stats_historiques;