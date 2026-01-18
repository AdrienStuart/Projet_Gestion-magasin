-- Pour rafraîchir les vues matérialisées :
-- REFRESH MATERIALIZED VIEW mv_stats_annuelles;
-- REFRESH MATERIALIZED VIEW mv_stats_historiques;

-- Vue: Facturation détaillée avec calculs TVA (Prix TTC -> HT)
CREATE OR REPLACE VIEW v_facturation_detaillee AS
SELECT 
    lv.Id_Vente,
    p.Nom AS Produit,
    lv.QteVendue,
    lv.PrixUnitaireVendu AS PU_TTC,
    lv.Remise,
    COALESCE(lv.TauxTVA, p.TauxTVA, 18.00) AS TauxTVA,
    -- Prix TTC après remise
    ROUND(lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0), 2) AS PU_TTC_Net,
    -- Calcul du HT (Formule : TTC / (1 + Taux/100))
    ROUND((lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) / (1 + COALESCE(lv.TauxTVA, p.TauxTVA, 18.00)/100), 2) AS PU_HT,
    -- Totaux de ligne
    ROUND((lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) * lv.QteVendue, 2) AS Total_Ligne_TTC,
    ROUND(((lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)) / (1 + COALESCE(lv.TauxTVA, p.TauxTVA, 18.00)/100)) * lv.QteVendue, 2) AS Total_Ligne_HT,
    p.PrixAchatMoyen
FROM LigneVente lv
JOIN Produit p ON lv.Id_Produit = p.Id_Produit;

-- Vue: Bilan mensuel (CA, Charges, Bénéfice)
CREATE OR REPLACE VIEW v_bilan_mensuel AS
WITH Recap_Ventes AS (
    SELECT 
        EXTRACT(MONTH FROM v.DateVente) as Mois,
        EXTRACT(YEAR FROM v.DateVente) as Annee,
        SUM(vfd.Total_Ligne_HT) as Total_CA_HT,
        SUM(vfd.Total_Ligne_HT - (vfd.QteVendue * vfd.PrixAchatMoyen)) as Marge_Brute
    FROM v_facturation_detaillee vfd
    JOIN LigneVente lv ON vfd.Id_Vente = lv.Id_Vente AND vfd.Produit = (SELECT Nom FROM Produit WHERE Id_Produit = lv.Id_Produit)
    JOIN Vente v ON vfd.Id_Vente = v.Id_Vente
    GROUP BY 1, 2
),
Recap_Depenses AS (
    SELECT 
        EXTRACT(MONTH FROM DateDepense) as Mois,
        EXTRACT(YEAR FROM DateDepense) as Annee,
        SUM(Montant) as Total_Charges
    FROM Depense
    GROUP BY 1, 2
)
SELECT 
    v.Annee, v.Mois,
    v.Total_CA_HT,
    v.Marge_Brute,
    COALESCE(d.Total_Charges, 0) as Total_Charges,
    (v.Marge_Brute - COALESCE(d.Total_Charges, 0)) as Benefice_Net_Poche
FROM Recap_Ventes v
LEFT JOIN Recap_Depenses d ON v.Mois = d.Mois AND v.Annee = d.Annee
ORDER BY v.Annee DESC, v.Mois DESC;
