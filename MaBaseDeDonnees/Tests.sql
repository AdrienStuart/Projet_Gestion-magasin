

-- DONNÉES DE TEST COMPLÈTES POUR DÉMONSTRATION

-- 1. CATÉGORIES (10 catégories variées)
INSERT INTO Categorie (Libelle) VALUES
('Boissons'),
('Épicerie'),
('Produits laitiers'),
('Viandes et poissons'),
('Fruits et légumes'),
('Boulangerie'),
('Hygiène et beauté'),
('Électronique'),
('Articles ménagers'),
('Snacks et confiseries');

-- 2. UTILISATEURS (différents rôles pour tester permissions)
INSERT INTO Utilisateur (Nom, Role, MotDePasse, email) VALUES
('Admin Principal', 'Administrateur', 'admin123', 'admin@supermarche.tg'),
('Marie Kouassi', 'Caissier', 'caisse123', 'marie.kouassi@supermarche.tg'),
('Jean Atayi', 'Caissier', 'caisse456', 'jean.atayi@supermarche.tg'),
('Sophie Agbeko', 'Gestionnaire', 'gestion789', 'sophie.agbeko@supermarche.tg'),
('Pierre Mensah', 'Responsable_Achats', 'achat999', 'pierre.mensah@supermarche.tg'),
('Emma Dzodzi', 'Caissier', 'caisse789', 'emma.dzodzi@supermarche.tg');

-- 3. FOURNISSEURS (8 fournisseurs)
INSERT INTO Fournisseur (Nom, Contact, Adresse) VALUES
('SODIGAZ Togo', '+228 22 23 45 67', 'Boulevard du 13 Janvier, Lomé'),
('Distributions Africaines SA', '+228 22 34 56 78', 'Zone Portuaire, Lomé'),
('Agro-Food Suppliers', '+228 90 12 34 56', 'Route de Kpalimé, Lomé'),
('Fresh Market Togo', '+228 91 23 45 67', 'Marché central, Lomé'),
('Tech Import SARL', '+228 92 34 56 78', 'Avedji, Lomé'),
('Cosmétiques et Hygiène', '+228 93 45 67 89', 'Hédzranawoé, Lomé'),
('Boulangerie Industrielle', '+228 94 56 78 90', 'Tokoin, Lomé'),
('Snack Distribution', '+228 95 67 89 01', 'Adidogomé, Lomé');

-- 4. PRODUITS (40 produits avec différents états de stock)
INSERT INTO Produit (Id_Produit, Nom, Description, Id_Categorie, PrixUnitaireActuel, StockActuel, StockAlerte) VALUES
-- Boissons (Catégorie 1)
('PROD001', 'Coca-Cola 1L', 'Boisson gazeuse cola 1 litre', 1, 1200, 45, 20),
('PROD002', 'Sprite 1L', 'Boisson gazeuse citron 1 litre', 1, 1100, 8, 20),  -- ALERTE
('PROD003', 'Fanta Orange 1L', 'Boisson gazeuse orange 1 litre', 1, 1100, 0, 15),  -- RUPTURE
('PROD004', 'Eau minérale 1.5L', 'Eau minérale naturelle', 1, 500, 120, 50),
('PROD005', 'Jus dorange Tropicana 1L', 'Jus 100% pur fruit', 1, 2500, 25, 15),

-- Épicerie (Catégorie 2)
('PROD006', 'Riz Uncle Bens 1kg', 'Riz long grain', 2, 1800, 150, 30),
('PROD007', 'Huile végétale 1L', 'Huile de tournesol', 2, 1500, 12, 25),  -- ALERTE
('PROD008', 'Pâtes Panzani 500g', 'Pâtes alimentaires', 2, 800, 80, 20),
('PROD009', 'Sucre en poudre 1kg', 'Sucre blanc cristallisé', 2, 1200, 5, 20),  -- ALERTE
('PROD010', 'Sel de cuisine 1kg', 'Sel fin iodé', 2, 400, 90, 15),

-- Produits laitiers (Catégorie 3)
('PROD011', 'Lait entier 1L', 'Lait UHT entier', 3, 1300, 35, 25),
('PROD012', 'Yaourt nature x4', 'Yaourts nature pack de 4', 3, 1800, 2, 15),  -- ALERTE CRITIQUE
('PROD013', 'Fromage Emmental 200g', 'Fromage à pâte pressée', 3, 3500, 18, 10),
('PROD014', 'Beurre doux 250g', 'Beurre de baratte', 3, 2200, 22, 12),

-- Viandes et poissons (Catégorie 4)
('PROD015', 'Poulet entier congelé', 'Poulet fermier 1.5kg environ', 4, 4500, 0, 10),  -- RUPTURE
('PROD016', 'Poisson tilapia 1kg', 'Tilapia frais du lac', 4, 3800, 15, 8),
('PROD017', 'Viande de bœuf 1kg', 'Bœuf pour grillade', 4, 6500, 8, 10),  -- ALERTE
('PROD018', 'Sardines en boîte x3', 'Sardines à l huile pack de 3', 4, 2500, 45, 15),

-- Fruits et légumes (Catégorie 5)
('PROD019', 'Tomates 1kg', 'Tomates fraîches', 5, 1200, 0, 20),  -- RUPTURE
('PROD020', 'Oignons 1kg', 'Oignons jaunes', 5, 800, 40, 15),
('PROD021', 'Pommes de terre 2kg', 'Pommes de terre locales', 5, 1500, 55, 20),
('PROD022', 'Bananes 1kg', 'Bananes plantain', 5, 600, 70, 25),

-- Boulangerie (Catégorie 6)
('PROD023', 'Pain de mie tranché', 'Pain de mie 500g', 6, 1200, 25, 15),
('PROD024', 'Croissants x6', 'Croissants au beurre pack de 6', 6, 2500, 3, 10),  -- ALERTE
('PROD025', 'Baguette tradition', 'Baguette française 250g', 6, 500, 18, 20),

-- Hygiène et beauté (Catégorie 7)
('PROD026', 'Savon Lux x3', 'Savon de toilette pack de 3', 7, 1500, 50, 20),
('PROD027', 'Dentifrice Colgate', 'Dentifrice protection complète', 7, 1800, 30, 15),
('PROD028', 'Shampoing Pantene 400ml', 'Shampoing réparateur', 7, 3500, 1, 12),  -- ALERTE CRITIQUE
('PROD029', 'Déodorant Nivea', 'Déodorant spray 150ml', 7, 2500, 22, 10),

-- Électronique (Catégorie 8)
('PROD030', 'Piles AA x4', 'Piles alcalines AA pack de 4', 8, 1500, 35, 15),
('PROD031', 'Ampoule LED 12W', 'Ampoule économique blanc chaud', 8, 2500, 20, 8),
('PROD032', 'Câble USB-C 1m', 'Câble de charge USB-C', 8, 1800, 12, 10),

-- Articles ménagers (Catégorie 9)
('PROD033', 'Liquide vaisselle 1L', 'Détergent vaisselle citron', 9, 1200, 40, 20),
('PROD034', 'Éponges x5', 'Éponges grattantes pack de 5', 9, 800, 6, 15),  -- ALERTE
('PROD035', 'Sacs poubelle x20', 'Sacs poubelle 50L rouleau de 20', 9, 2200, 28, 12),

-- Snacks et confiseries (Catégorie 10)
('PROD036', 'Chips Lay s 150g', 'Chips salées nature', 10, 1500, 45, 20),
('PROD037', 'Chocolat Milka 100g', 'Chocolat au lait', 10, 2000, 32, 15),
('PROD038', 'Biscuits Oreo 154g', 'Biscuits chocolat fourrés', 10, 1800, 28, 12),
('PROD039', 'Bonbons Haribo 200g', 'Bonbons gélifiés assortis', 10, 1200, 0, 15),  -- RUPTURE
('PROD040', 'Cacahuètes grillées 250g', 'Cacahuètes salées', 10, 1000, 50, 20);

-- 5. RELATION FOURNIR (Produits-Fournisseurs)
INSERT INTO fournir (Id_Produit, Id_Fournisseur, Quantite) VALUES
-- Boissons → SODIGAZ et Distributions Africaines
('PROD001', 1, 1000), ('PROD002', 1, 800), ('PROD003', 1, 800), ('PROD004', 2, 2000), ('PROD005', 2, 500),
-- Épicerie → Distributions Africaines et Agro-Food
('PROD006', 2, 1500), ('PROD007', 3, 800), ('PROD008', 2, 1000), ('PROD009', 3, 1200), ('PROD010', 2, 1500),
-- Produits laitiers → Fresh Market
('PROD011', 4, 500), ('PROD012', 4, 400), ('PROD013', 4, 300), ('PROD014', 4, 350),
-- Viandes et poissons → Fresh Market
('PROD015', 4, 200), ('PROD016', 4, 150), ('PROD017', 4, 100), ('PROD018', 2, 600),
-- Fruits et légumes → Fresh Market (certains sans fournisseur pour tester)
('PROD020', 4, 800), ('PROD021', 4, 600), ('PROD022', 4, 1000),
-- Boulangerie → Boulangerie Industrielle
('PROD023', 7, 400), ('PROD024', 7, 300), ('PROD025', 7, 500),
-- Hygiène → Cosmétiques et Hygiène
('PROD026', 6, 800), ('PROD027', 6, 500), ('PROD028', 6, 400), ('PROD029', 6, 450),
-- Électronique → Tech Import
('PROD030', 5, 600), ('PROD031', 5, 400), ('PROD032', 5, 500),
-- Articles ménagers → Distributions Africaines
('PROD033', 2, 700), ('PROD034', 2, 900), ('PROD035', 2, 500),
-- Snacks → Snack Distribution
('PROD036', 8, 800), ('PROD037', 8, 600), ('PROD038', 8, 700), ('PROD040', 8, 1000);

-- 6. ACHATS (10 achats avec différents statuts)
INSERT INTO Achat (DateAchat, Statut, Id_Utilisateur, Id_Fournisseur) VALUES
-- Achats REÇUS (pour tester le PMP et mouvements stock)
(CURRENT_TIMESTAMP - INTERVAL '15 days', 'RECU', 5, 1),
(CURRENT_TIMESTAMP - INTERVAL '12 days', 'RECU', 5, 2),
(CURRENT_TIMESTAMP - INTERVAL '8 days', 'RECU', 5, 4),
(CURRENT_TIMESTAMP - INTERVAL '5 days', 'RECU', 5, 6),
(CURRENT_TIMESTAMP - INTERVAL '2 days', 'RECU', 5, 8),
-- Achats EN_ATTENTE (pour tester la vue alertes)
(CURRENT_TIMESTAMP - INTERVAL '4 days', 'EN_ATTENTE', 5, 1),
(CURRENT_TIMESTAMP - INTERVAL '1 day', 'EN_ATTENTE', 5, 4),
-- Achats ANNULES
(CURRENT_TIMESTAMP - INTERVAL '20 days', 'ANNULE', 5, 3),
(CURRENT_TIMESTAMP - INTERVAL '18 days', 'ANNULE', 5, 7);

-- 7. LIGNES D'ACHAT
INSERT INTO LigneAchat (Id_Achat, Id_Produit, Quantite, PrixAchatNegocie) VALUES
-- Achat 1 (RECU)
(1, 'PROD001', 50, 800), (1, 'PROD002', 30, 750), (1, 'PROD003', 25, 750),
-- Achat 2 (RECU)
(2, 'PROD006', 100, 1200), (2, 'PROD007', 40, 1000), (2, 'PROD008', 60, 550),
-- Achat 3 (RECU)
(3, 'PROD011', 40, 900), (3, 'PROD012', 30, 1200), (3, 'PROD016', 20, 2500),
-- Achat 4 (RECU)
(4, 'PROD026', 60, 1000), (4, 'PROD027', 40, 1200), (4, 'PROD028', 25, 2300),
-- Achat 5 (RECU)
(5, 'PROD036', 50, 1000), (5, 'PROD037', 40, 1400), (5, 'PROD038', 35, 1200),
-- Achat 6 (EN_ATTENTE - pour tester alertes)
(6, 'PROD002', 50, 750), (6, 'PROD003', 40, 750),
-- Achat 7 (EN_ATTENTE)
(7, 'PROD015', 25, 3200), (7, 'PROD019', 50, 800);

-- Maintenant on met à jour les statuts pour déclencher les triggers PMP
UPDATE Achat SET Statut = 'RECU' WHERE Id_Achat IN (1, 2, 3, 4, 5);

-- 8. VENTES (20 ventes sur plusieurs jours)
INSERT INTO Vente (DateVente, Id_Utilisateur) VALUES
-- Ventes d'il y a 7 jours
(CURRENT_TIMESTAMP - INTERVAL '7 days' + INTERVAL '9 hours', 2),
(CURRENT_TIMESTAMP - INTERVAL '7 days' + INTERVAL '11 hours', 3),
(CURRENT_TIMESTAMP - INTERVAL '7 days' + INTERVAL '14 hours', 2),
-- Ventes d'il y a 5 jours
(CURRENT_TIMESTAMP - INTERVAL '5 days' + INTERVAL '10 hours', 6),
(CURRENT_TIMESTAMP - INTERVAL '5 days' + INTERVAL '15 hours', 3),
-- Ventes d'il y a 3 jours
(CURRENT_TIMESTAMP - INTERVAL '3 days' + INTERVAL '9 hours', 2),
(CURRENT_TIMESTAMP - INTERVAL '3 days' + INTERVAL '12 hours', 6),
(CURRENT_TIMESTAMP - INTERVAL '3 days' + INTERVAL '16 hours', 3),
-- Ventes d'hier
(CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '8 hours', 2),
(CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '10 hours', 6),
(CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '13 hours', 3),
(CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '17 hours', 2),
-- Ventes d'aujourd'hui
(CURRENT_TIMESTAMP - INTERVAL '2 hours', 2),
(CURRENT_TIMESTAMP - INTERVAL '1 hour 30 minutes', 6),
(CURRENT_TIMESTAMP - INTERVAL '1 hour', 3),
(CURRENT_TIMESTAMP - INTERVAL '45 minutes', 2),
(CURRENT_TIMESTAMP - INTERVAL '30 minutes', 6),
(CURRENT_TIMESTAMP - INTERVAL '15 minutes', 3),
(CURRENT_TIMESTAMP - INTERVAL '10 minutes', 2),
(CURRENT_TIMESTAMP - INTERVAL '5 minutes', 6);

-- 9. LIGNES DE VENTE (avec et sans remises)
INSERT INTO LigneVente (Id_Vente, Id_Produit, QteVendue, Remise) VALUES
-- Vente 1
(1, 'PROD001', 3, 0), (1, 'PROD006', 2, 0), (1, 'PROD011', 1, 0),
-- Vente 2
(2, 'PROD004', 6, 5), (2, 'PROD008', 3, 0), (2, 'PROD023', 2, 0),
-- Vente 3
(3, 'PROD001', 2, 0), (3, 'PROD005', 1, 0), (3, 'PROD013', 1, 10),
-- Vente 4
(4, 'PROD002', 4, 0), (4, 'PROD007', 2, 0), (4, 'PROD026', 3, 0),
-- Vente 5
(5, 'PROD006', 5, 0), (5, 'PROD010', 2, 0), (5, 'PROD033', 1, 0),
-- Vente 6
(6, 'PROD001', 2, 0), (6, 'PROD012', 5, 0), (6, 'PROD036', 2, 0),
-- Vente 7
(7, 'PROD004', 4, 0), (7, 'PROD014', 1, 0), (7, 'PROD027', 2, 0),
-- Vente 8
(8, 'PROD008', 4, 5), (8, 'PROD020', 3, 0), (8, 'PROD037', 2, 0),
-- Vente 9
(9, 'PROD001', 5, 0), (9, 'PROD011', 2, 0), (9, 'PROD030', 3, 0),
-- Vente 10
(10, 'PROD006', 3, 0), (10, 'PROD021', 2, 0), (10, 'PROD038', 1, 0),
-- Vente 11
(11, 'PROD002', 2, 0), (11, 'PROD012', 3, 0), (11, 'PROD026', 2, 0),
-- Vente 12
(12, 'PROD004', 8, 10), (12, 'PROD023', 3, 0), (12, 'PROD036', 3, 0),
-- Vente 13 (aujourd'hui)
(13, 'PROD001', 4, 0), (13, 'PROD005', 2, 0), (13, 'PROD031', 1, 0),
-- Vente 14 (aujourd'hui)
(14, 'PROD006', 2, 0), (14, 'PROD011', 3, 0), (14, 'PROD027', 1, 0),
-- Vente 15 (aujourd'hui)
(15, 'PROD008', 5, 0), (15, 'PROD021', 3, 0), (15, 'PROD037', 2, 0),
-- Vente 16 (aujourd'hui)
(16, 'PROD001', 3, 0), (16, 'PROD007', 1, 0), (16, 'PROD034', 2, 0),
-- Vente 17 (aujourd'hui)
(17, 'PROD004', 5, 0), (17, 'PROD012', 2, 0), (17, 'PROD033', 1, 0),
-- Vente 18 (aujourd'hui)
(18, 'PROD002', 3, 0), (18, 'PROD017', 1, 15), (18, 'PROD029', 1, 0),
-- Vente 19 (aujourd'hui)
(19, 'PROD006', 4, 0), (19, 'PROD014', 2, 0), (19, 'PROD032', 1, 0),
-- Vente 20 (aujourd'hui - grosse vente)
(20, 'PROD001', 8, 5), (20, 'PROD004', 12, 10), (20, 'PROD006', 6, 0), 
(20, 'PROD011', 4, 0), (20, 'PROD021', 5, 0), (20, 'PROD036', 5, 0);

-- 10. REÇUS (pour les ventes)
INSERT INTO Recu (DateEmission, ModePaiement, MontantTotal, Id_Utilisateur, Id_Vente) 
SELECT 
    v.DateVente,
    CASE (v.Id_Vente % 4)
        WHEN 0 THEN 'ESPECES'
        WHEN 1 THEN 'CARTE'
        WHEN 2 THEN 'VIREMENT'
        ELSE 'CHEQUE'
    END,
    ROUND(SUM(lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0)/100.0)), 2),
    v.Id_Utilisateur,
    v.Id_Vente
FROM Vente v
JOIN LigneVente lv ON v.Id_Vente = lv.Id_Vente
GROUP BY v.Id_Vente, v.DateVente, v.Id_Utilisateur;

-- Rafraîchir les vues matérialisées
REFRESH MATERIALIZED VIEW mv_stats_annuelles;
REFRESH MATERIALIZED VIEW mv_stats_historiques;

-- VÉRIFICATIONS RAPIDES
SELECT 'RÉSUMÉ DES DONNÉES INSÉRÉES' AS Info;
SELECT COUNT(*) AS Nb_Categories FROM Categorie;
SELECT COUNT(*) AS Nb_Utilisateurs FROM Utilisateur;
SELECT COUNT(*) AS Nb_Fournisseurs FROM Fournisseur;
SELECT COUNT(*) AS Nb_Produits FROM Produit;
SELECT COUNT(*) AS Nb_Achats FROM Achat;
SELECT COUNT(*) AS Nb_Ventes FROM Vente;
SELECT COUNT(*) AS Nb_Lignes_Vente FROM LigneVente;
SELECT COUNT(*) AS Nb_Reçus FROM Recu;
SELECT COUNT(*) AS Nb_Mouvements_Stock FROM MouvementStock;