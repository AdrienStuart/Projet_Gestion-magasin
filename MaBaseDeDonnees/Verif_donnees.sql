-- ========================================
-- SCRIPT DE VÉRIFICATION DES DONNÉES
-- ========================================

-- En-tête du rapport
SELECT '============================================' AS "RAPPORT DE VÉRIFICATION";
SELECT 'Vérification de l''intégrité des données' AS "Description";
SELECT CURRENT_TIMESTAMP AS "Date de vérification";
SELECT '============================================' AS "SÉPARATEUR";

-- ========================================
-- 1. COMPTAGE DES ENREGISTREMENTS
-- ========================================
SELECT '1. COMPTAGE DES ENREGISTREMENTS' AS "Section";

SELECT 'Catégories' AS "Table", COUNT(*) AS "Nombre d''enregistrements" FROM Categorie
UNION ALL
SELECT 'Utilisateurs', COUNT(*) FROM Utilisateur
UNION ALL
SELECT 'Fournisseurs', COUNT(*) FROM Fournisseur
UNION ALL
SELECT 'Produits', COUNT(*) FROM Produit
UNION ALL
SELECT 'Relations Fournir', COUNT(*) FROM fournir
UNION ALL
SELECT 'Achats', COUNT(*) FROM Achat
UNION ALL
SELECT 'Lignes Achat', COUNT(*) FROM LigneAchat
UNION ALL
SELECT 'Ventes', COUNT(*) FROM Vente
UNION ALL
SELECT 'Lignes Vente', COUNT(*) FROM LigneVente
UNION ALL
SELECT 'Reçus', COUNT(*) FROM Recu
UNION ALL
SELECT 'Mouvements Stock', COUNT(*) FROM MouvementStock;

-- ========================================
-- 2. VÉRIFICATION DES STATUTS D'ACHAT
-- ========================================
SELECT '2. STATUTS DES ACHATS' AS "Section";

SELECT 
    Statut,
    COUNT(*) AS "Nombre",
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Achat), 2) AS "Pourcentage (%)"
FROM Achat
GROUP BY Statut
ORDER BY Statut;

-- ========================================
-- 3. ÉTAT DES STOCKS
-- ========================================
SELECT '3. ANALYSE DES STOCKS' AS "Section";

SELECT 
    'Total produits' AS "Indicateur",
    COUNT(*) AS "Valeur"
FROM Produit
UNION ALL
SELECT 
    'Produits en rupture (stock = 0)',
    COUNT(*)
FROM Produit
WHERE StockActuel = 0
UNION ALL
SELECT 
    'Produits en alerte (stock ≤ seuil)',
    COUNT(*)
FROM Produit
WHERE StockActuel > 0 AND StockActuel <= StockAlerte
UNION ALL
SELECT 
    'Produits en stock normal',
    COUNT(*)
FROM Produit
WHERE StockActuel > StockAlerte;

-- ========================================
-- 4. TOP 5 PRODUITS EN RUPTURE OU ALERTE
-- ========================================
SELECT '4. PRODUITS NÉCESSITANT ATTENTION' AS "Section";

SELECT 
    Id_Produit,
    Nom,
    StockActuel,
    StockAlerte,
    CASE 
        WHEN StockActuel = 0 THEN 'RUPTURE'
        WHEN StockActuel <= StockAlerte THEN 'ALERTE'
        ELSE 'NORMAL'
    END AS "État"
FROM Produit
WHERE StockActuel <= StockAlerte
ORDER BY StockActuel ASC
LIMIT 10;

-- ========================================
-- 5. ANALYSE DES VENTES
-- ========================================
SELECT '5. STATISTIQUES DES VENTES' AS "Section";

SELECT 
    'Nombre total de ventes' AS "Indicateur",
    COUNT(*) AS "Valeur"
FROM Vente
UNION ALL
SELECT 
    'Ventes aujourd''hui',
    COUNT(*)
FROM Vente
WHERE DATE(DateVente) = CURRENT_DATE
UNION ALL
SELECT 
    'Ventes hier',
    COUNT(*)
FROM Vente
WHERE DATE(DateVente) = CURRENT_DATE - INTERVAL '1 day'
UNION ALL
SELECT 
    'Ventes cette semaine',
    COUNT(*)
FROM Vente
WHERE DateVente >= CURRENT_DATE - INTERVAL '7 days';

-- ========================================
-- 6. CHIFFRE D'AFFAIRES
-- ========================================
SELECT '6. CHIFFRE D''AFFAIRES' AS "Section";

WITH ca_stats AS (
    SELECT 
        SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) AS ca_total,
        SUM(CASE WHEN DATE(v.DateVente) = CURRENT_DATE 
            THEN lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0) 
            ELSE 0 END) AS ca_aujourdhui,
        SUM(CASE WHEN DATE(v.DateVente) = CURRENT_DATE - INTERVAL '1 day' 
            THEN lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0) 
            ELSE 0 END) AS ca_hier,
        SUM(CASE WHEN v.DateVente >= CURRENT_DATE - INTERVAL '7 days' 
            THEN lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0) 
            ELSE 0 END) AS ca_semaine
    FROM Vente v
    JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
)
SELECT 
    'CA Total' AS "Période",
    ROUND(ca_total, 2) AS "Montant (FCFA)"
FROM ca_stats
UNION ALL
SELECT 
    'CA Aujourd''hui',
    ROUND(ca_aujourdhui, 2)
FROM ca_stats
UNION ALL
SELECT 
    'CA Hier',
    ROUND(ca_hier, 2)
FROM ca_stats
UNION ALL
SELECT 
    'CA Cette semaine',
    ROUND(ca_semaine, 2)
FROM ca_stats;

-- ========================================
-- 7. TOP 5 PRODUITS LES PLUS VENDUS
-- ========================================
SELECT '7. TOP 5 PRODUITS LES PLUS VENDUS' AS "Section";

SELECT 
    p.Id_Produit,
    p.Nom,
    SUM(lv.QteVendue) AS "Quantité vendue",
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2) AS "CA généré (FCFA)"
FROM Produit p
JOIN LigneVente lv ON p.Id_Produit = lv.Id_Produit
GROUP BY p.Id_Produit, p.Nom
ORDER BY SUM(lv.QteVendue) DESC
LIMIT 5;

-- ========================================
-- 8. PERFORMANCE DES VENDEURS
-- ========================================
SELECT '8. PERFORMANCE DES VENDEURS' AS "Section";

SELECT 
    u.Nom AS "Vendeur",
    u.Role AS "Rôle",
    COUNT(DISTINCT v.Id_Vente) AS "Nb ventes",
    ROUND(COALESCE(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 0), 2) AS "CA généré (FCFA)"
FROM Utilisateur u
LEFT JOIN Vente v ON u.Id_Utilisateur = v.Id_Utilisateur
LEFT JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
WHERE u.Role IN ('Caissier', 'Administrateur')
GROUP BY u.Id_Utilisateur, u.Nom, u.Role
ORDER BY COUNT(DISTINCT v.Id_Vente) DESC;

-- ========================================
-- 9. MODES DE PAIEMENT
-- ========================================
SELECT '9. RÉPARTITION DES MODES DE PAIEMENT' AS "Section";

SELECT 
    ModePaiement AS "Mode de paiement",
    COUNT(*) AS "Nombre de transactions",
    ROUND(SUM(MontantTotal), 2) AS "Montant total (FCFA)",
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Recu), 2) AS "Part (%)"
FROM Recu
GROUP BY ModePaiement
ORDER BY COUNT(*) DESC;

-- ========================================
-- 10. VALEUR DU STOCK
-- ========================================
SELECT '10. VALEUR DU STOCK' AS "Section";

SELECT 
    'Valeur stock PMP' AS "Indicateur",
    ROUND(SUM(StockActuel * PrixAchatMoyen), 2) AS "Montant (FCFA)"
FROM Produit
UNION ALL
SELECT 
    'Valeur stock Prix Vente',
    ROUND(SUM(StockActuel * PrixUnitaireActuel), 2)
FROM Produit
UNION ALL
SELECT 
    'Marge potentielle',
    ROUND(SUM(StockActuel * (PrixUnitaireActuel - PrixAchatMoyen)), 2)
FROM Produit;

-- ========================================
-- 11. VÉRIFICATION DES MOUVEMENTS DE STOCK
-- ========================================
SELECT '11. MOUVEMENTS DE STOCK' AS "Section";

SELECT 
    Type AS "Type de mouvement",
    COUNT(*) AS "Nombre de mouvements",
    SUM(Quantite) AS "Quantité totale"
FROM MouvementStock
GROUP BY Type
ORDER BY Type;

-- ========================================
-- 12. COHÉRENCE DES DONNÉES
-- ========================================
SELECT '12. TESTS DE COHÉRENCE' AS "Section";

-- Test 1: Vérifier que toutes les ventes ont un reçu
SELECT 
    'Ventes sans reçu' AS "Test",
    COUNT(*) AS "Résultat (0 = OK)"
FROM Vente v
LEFT JOIN Recu r ON v.Id_Vente = r.Id_Vente
WHERE r.Id_Recu IS NULL

UNION ALL

-- Test 2: Vérifier que toutes les lignes de vente référencent des produits existants
SELECT 
    'Lignes vente avec produits inexistants',
    COUNT(*)
FROM LigneVente lv
LEFT JOIN Produit p ON lv.Id_Produit = p.Id_Produit
WHERE p.Id_Produit IS NULL

UNION ALL

-- Test 3: Vérifier que tous les produits ont une catégorie
SELECT 
    'Produits sans catégorie',
    COUNT(*)
FROM Produit p
LEFT JOIN Categorie c ON p.Id_Categorie = c.Id_Categorie
WHERE c.Id_Categorie IS NULL

UNION ALL

-- Test 4: Vérifier les prix négatifs
SELECT 
    'Produits avec prix négatif',
    COUNT(*)
FROM Produit
WHERE PrixUnitaireActuel < 0

UNION ALL

-- Test 5: Vérifier les stocks négatifs
SELECT 
    'Produits avec stock négatif',
    COUNT(*)
FROM Produit
WHERE StockActuel < 0;

-- ========================================
-- RÉSUMÉ FINAL
-- ========================================
SELECT '============================================' AS "FIN DU RAPPORT";
SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM Produit WHERE StockActuel < 0 OR PrixUnitaireActuel < 0) = 0
        AND (SELECT COUNT(*) FROM Vente v LEFT JOIN Recu r ON v.Id_Vente = r.Id_Vente WHERE r.Id_Recu IS NULL) = 0
        THEN '✓ TOUTES LES VÉRIFICATIONS SONT PASSÉES'
        ELSE '✗ DES ANOMALIES ONT ÉTÉ DÉTECTÉES'
    END AS "Statut global";

SELECT CURRENT_TIMESTAMP AS "Fin de vérification";
SELECT '============================================' AS "SÉPARATEUR";