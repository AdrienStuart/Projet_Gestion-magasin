
-- INDEX ESSENTIELS

-- PRODUIT
CREATE INDEX IF NOT EXISTS idx_produit_categorie ON Produit(Id_Categorie);
CREATE INDEX IF NOT EXISTS idx_produit_nom ON Produit(Nom);
CREATE INDEX IF NOT EXISTS idx_produit_prix_achat ON Produit(PrixAchatMoyen);
CREATE INDEX IF NOT EXISTS idx_produit_prix_vente ON Produit(PrixUnitaireActuel);

-- Index partiel pour alertes stock 
CREATE INDEX IF NOT EXISTS idx_produit_stock_alerte 
ON Produit(StockActuel, StockAlerte) 
WHERE StockActuel <= StockAlerte;

-- Index pour recherches rapides
CREATE INDEX IF NOT EXISTS idx_produit_stock_low 
ON Produit(StockActuel) 
WHERE StockActuel < 10;

-- VENTE
CREATE INDEX IF NOT EXISTS idx_vente_date ON Vente(DateVente);
CREATE INDEX IF NOT EXISTS idx_vente_utilisateur ON Vente(Id_Utilisateur);

-- Index composite pour rapports
CREATE INDEX IF NOT EXISTS idx_vente_date_utilisateur_role 
ON Vente(DateVente, Id_Utilisateur);

-- LIGNE VENTE
CREATE INDEX IF NOT EXISTS idx_lignevente_vente ON LigneVente(Id_Vente);
CREATE INDEX IF NOT EXISTS idx_lignevente_produit ON LigneVente(Id_Produit);
CREATE INDEX IF NOT EXISTS idx_lignevente_remise ON LigneVente(Remise) WHERE Remise > 0;

-- Index composite pour analyses
CREATE INDEX IF NOT EXISTS idx_lignevente_vente_produit_qte 
ON LigneVente(Id_Vente, Id_Produit, QteVendue);

-- ACHAT
CREATE INDEX IF NOT EXISTS idx_achat_date ON Achat(DateAchat);
CREATE INDEX IF NOT EXISTS idx_achat_fournisseur ON Achat(Id_Fournisseur);
CREATE INDEX IF NOT EXISTS idx_achat_utilisateur ON Achat(Id_Utilisateur);

-- Index composite 
CREATE INDEX IF NOT EXISTS idx_achat_statut_date 
ON Achat(Statut, DateAchat) 
WHERE Statut = 'EN_ATTENTE';

-- LIGNE ACHAT
CREATE INDEX IF NOT EXISTS idx_ligneachat_achat ON LigneAchat(Id_Achat);
CREATE INDEX IF NOT EXISTS idx_ligneachat_produit ON LigneAchat(Id_Produit);

-- MOUVEMENT STOCK
CREATE INDEX IF NOT EXISTS idx_mouvementstock_produit ON MouvementStock(Id_Produit);
CREATE INDEX IF NOT EXISTS idx_mouvementstock_date ON MouvementStock(DateMouvement);

-- Index composite pour historique produit
CREATE INDEX IF NOT EXISTS idx_mouvementstock_produit_date 
ON MouvementStock(Id_Produit, DateMouvement DESC);

-- Index partiels pour optimisation
CREATE INDEX IF NOT EXISTS idx_mouvementstock_vente 
ON MouvementStock(Id_Vente) 
WHERE Id_Vente IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_mouvementstock_achat 
ON MouvementStock(Id_Achat) 
WHERE Id_Achat IS NOT NULL;

-- RECU
CREATE INDEX IF NOT EXISTS idx_recu_vente ON Recu(Id_Vente);
CREATE INDEX IF NOT EXISTS idx_recu_date ON Recu(DateEmission);

-- UTILISATEUR
CREATE INDEX IF NOT EXISTS idx_utilisateur_email ON Utilisateur(email);

-- FOURNISSEUR
CREATE INDEX IF NOT EXISTS idx_fournisseur_nom ON Fournisseur(Nom);

-- TABLE DE LIAISON FOURNIR
CREATE INDEX IF NOT EXISTS idx_fournir_fournisseur ON fournir(Id_Fournisseur);
CREATE INDEX IF NOT EXISTS idx_fournir_produit ON fournir(Id_Produit);


-- INDEX POUR VUES IMPORTANTES

-- Pour vue_tableau_bord_admin
CREATE INDEX IF NOT EXISTS idx_vente_date_courante 
ON Vente((DateVente::date)) ;
--WHERE DateVente::date = CURRENT_DATE;

CREATE INDEX IF NOT EXISTS idx_vente_mois_courant 
ON Vente((EXTRACT(MONTH FROM DateVente)), (EXTRACT(YEAR FROM DateVente))) ;
/*WHERE EXTRACT(MONTH FROM DateVente) = EXTRACT(MONTH FROM CURRENT_DATE) 
AND EXTRACT(YEAR FROM DateVente) = EXTRACT(YEAR FROM CURRENT_DATE);*/

-- Pour vue_ca_par_heure
CREATE INDEX IF NOT EXISTS idx_vente_heure 
ON Vente((EXTRACT(HOUR FROM DateVente))); 
--WHERE DateVente::date = CURRENT_DATE;

-- Pour vue_ca_30_derniers_jours
CREATE INDEX IF NOT EXISTS idx_vente_30jours 
ON Vente(DateVente);
--WHERE DateVente >= CURRENT_DATE - INTERVAL '30 days';


-- INDEX POUR VUES MATÉRIALISÉES

-- Index pour mv_stats_annuelles
CREATE INDEX IF NOT EXISTS idx_mv_stats_annuelles_annee ON mv_stats_annuelles(Annee);
CREATE INDEX IF NOT EXISTS idx_mv_stats_annuelles_ca ON mv_stats_annuelles(Chiffre_Affaires DESC);
CREATE INDEX IF NOT EXISTS idx_mv_stats_annuelles_marge ON mv_stats_annuelles(Marge_Totale DESC);

-- Index pour mv_stats_historiques
CREATE INDEX IF NOT EXISTS idx_mv_stats_historiques_date ON mv_stats_historiques(Date_Vente);
CREATE INDEX IF NOT EXISTS idx_mv_stats_historiques_annee_mois ON mv_stats_historiques(Annee, Mois);
CREATE INDEX IF NOT EXISTS idx_mv_stats_historiques_ca ON mv_stats_historiques(Chiffre_Affaires DESC);
CREATE INDEX IF NOT EXISTS idx_mv_stats_historiques_annee ON mv_stats_historiques(Annee DESC);


-- OPTIMISATIONS SUPPLÉMENTAIRES


-- Augmenter les statistiques pour optimiseur de requêtes
ALTER TABLE Produit ALTER COLUMN StockActuel SET STATISTICS 1000;
ALTER TABLE Vente ALTER COLUMN DateVente SET STATISTICS 1000;
ALTER TABLE Achat ALTER COLUMN Statut SET STATISTICS 100;

-- Nettoyage automatique (vacuum) recommandations
-- À exécuter périodiquement dans pgAdmin ou via tâche planifiée :
-- VACUUM ANALYZE Produit;
-- VACUUM ANALYZE Vente;
-- VACUUM ANALYZE LigneVente;