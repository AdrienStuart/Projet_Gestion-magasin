-- ========================================
-- SCRIPT D'INSERTION DE DONNÉES - MAGASIN
-- Produits alimentaires et consommation courante
-- ========================================

-- NETTOYAGE PRÉALABLE (optionnel - décommenter si besoin)
TRUNCATE TABLE fournir, Recu, MouvementStock, LigneVente, LigneAchat, Vente, Achat, Produit, Fournisseur, Utilisateur, Categorie RESTART IDENTITY CASCADE;

-- ========================================
-- 1. CATÉGORIES (10 catégories)
-- ========================================
INSERT INTO Categorie (Libelle) VALUES
('Boissons'),
('Épicerie sèche'),
('Produits laitiers'),
('Viandes et poissons'),
('Fruits et légumes'),
('Boulangerie et pâtisserie'),
('Hygiène et beauté'),
('Électronique et piles'),
('Articles ménagers'),
('Snacks et confiseries');

-- ========================================
-- 2. UTILISATEURS (6 utilisateurs)
-- ========================================
INSERT INTO Utilisateur (Nom, Role, MotDePasse, email) VALUES
('Admin Principal', 'Administrateur', 'admin123', 'admin@supermarche.tg'),
('Marie Kouassi', 'Caissier', 'caisse123', 'marie.kouassi@supermarche.tg'),
('Jean Atayi', 'Caissier', 'caisse456', 'jean.atayi@supermarche.tg'),
('Sophie Agbeko', 'Gestionnaire', 'gestion789', 'sophie.agbeko@supermarche.tg'),
('Pierre Mensah', 'Responsable_Achats', 'achat999', 'pierre.mensah@supermarche.tg'),
('Emma Dzodzi', 'Caissier', 'caisse789', 'emma.dzodzi@supermarche.tg');

-- ========================================
-- 3. FOURNISSEURS (8 fournisseurs)
-- ========================================
INSERT INTO Fournisseur (Nom, Contact, Adresse) VALUES
('SODIGAZ Togo', '+228 22 23 45 67', 'Boulevard du 13 Janvier, Lomé'),
('Distributions Africaines SA', '+228 22 34 56 78', 'Zone Portuaire, Lomé'),
('Agro-Food Suppliers', '+228 90 12 34 56', 'Route de Kpalimé, Lomé'),
('Fresh Market Togo', '+228 91 23 45 67', 'Marché central, Lomé'),
('Tech Import SARL', '+228 92 34 56 78', 'Avedji, Lomé'),
('Cosmétiques et Hygiène', '+228 93 45 67 89', 'HédzranawoÈ, Lomé'),
('Boulangerie Industrielle', '+228 94 56 78 90', 'Tokoin, Lomé'),
('Snack Distribution', '+228 95 67 89 01', 'AdidogomÊ, Lomé');

-- ========================================
-- 4. PRODUITS (45 produits avec stocks variés)
-- ========================================
INSERT INTO Produit (Id_Produit, Nom, Description, Id_Categorie, PrixUnitaireActuel, StockActuel, StockAlerte) VALUES
-- === BOISSONS (Catégorie 1) ===
('BV001', 'Coca-Cola 1L', 'Boisson gazeuse cola 1 litre', 1, 1200, 85, 20),
('BV002', 'Sprite 1L', 'Boisson gazeuse citron 1 litre', 1, 1100, 12, 20),
('BV003', 'Fanta Orange 1L', 'Boisson gazeuse orange 1 litre', 1, 1100, 3, 15),
('BV004', 'Eau minérale 1.5L', 'Eau minérale naturelle', 1, 500, 150, 50),
('BV005', 'Jus d''orange Tropicana 1L', 'Jus 100% pur fruit', 1, 2500, 35, 15),
('BV006', 'Jus d''ananas 1L', 'Jus tropical 100% fruit', 1, 2300, 28, 12),

-- === ÉPICERIE SÈCHE (Catégorie 2) ===
('EP001', 'Riz Uncle Bens 1kg', 'Riz long grain de qualité', 2, 1800, 200, 40),
('EP002', 'Huile végétale 1L', 'Huile de tournesol raffinée', 2, 1500, 8, 25),
('EP003', 'Pâtes Panzani 500g', 'Pâtes alimentaires spaghetti', 2, 800, 95, 20),
('EP004', 'Sucre en poudre 1kg', 'Sucre blanc cristallisé', 2, 1200, 7, 20),
('EP005', 'Sel de cuisine 1kg', 'Sel fin iodé', 2, 400, 110, 15),
('EP006', 'Farine de blé 1kg', 'Farine tout usage', 2, 900, 65, 25),
('EP007', 'Haricots secs 500g', 'Haricots blancs secs', 2, 1100, 45, 15),
('EP008', 'Lentilles 1kg', 'Lentilles vertes', 2, 1400, 32, 12),

-- === PRODUITS LAITIERS (Catégorie 3) ===
('PL001', 'Lait entier 1L', 'Lait UHT entier', 3, 1300, 55, 25),
('PL002', 'Yaourt nature x4', 'Yaourts nature pack de 4', 3, 1800, 4, 15),
('PL003', 'Fromage Emmental 200g', 'Fromage à pâte pressée', 3, 3500, 22, 10),
('PL004', 'Beurre doux 250g', 'Beurre de baratte', 3, 2200, 28, 12),
('PL005', 'Crème fraîche 20cl', 'Crème fraîche épaisse', 3, 1500, 18, 10),

-- === VIANDES ET POISSONS (Catégorie 4) ===
('VP001', 'Poulet entier congelé', 'Poulet fermier 1.5kg environ', 4, 4500, 2, 10),
('VP002', 'Poisson tilapia 1kg', 'Tilapia frais du lac', 4, 3800, 18, 8),
('VP003', 'Viande de bœuf 1kg', 'Bœuf pour grillade', 4, 6500, 6, 10),
('VP004', 'Sardines en boîte x3', 'Sardines à l''huile pack de 3', 4, 2500, 55, 15),
('VP005', 'Thon en boîte 160g', 'Thon au naturel', 4, 1800, 42, 20),

-- === FRUITS ET LÉGUMES (Catégorie 5) ===
('FL001', 'Tomates 1kg', 'Tomates fraîches locales', 5, 1200, 1, 20),
('FL002', 'Oignons 1kg', 'Oignons jaunes', 5, 800, 60, 15),
('FL003', 'Pommes de terre 2kg', 'Pommes de terre locales', 5, 1500, 75, 20),
('FL004', 'Bananes 1kg', 'Bananes plantain', 5, 600, 90, 25),
('FL005', 'Carottes 1kg', 'Carottes fraîches', 5, 1000, 38, 15),

-- === BOULANGERIE (Catégorie 6) ===
('BP001', 'Pain de mie tranché', 'Pain de mie 500g', 6, 1200, 32, 15),
('BP002', 'Croissants x6', 'Croissants au beurre pack de 6', 6, 2500, 5, 10),
('BP003', 'Baguette tradition', 'Baguette française 250g', 6, 500, 25, 20),
('BP004', 'Brioches x4', 'Brioches individuelles', 6, 1800, 15, 8),

-- === HYGIÈNE ET BEAUTÉ (Catégorie 7) ===
('HB001', 'Savon Lux x3', 'Savon de toilette pack de 3', 7, 1500, 68, 20),
('HB002', 'Dentifrice Colgate', 'Dentifrice protection complète', 7, 1800, 42, 15),
('HB003', 'Shampoing Pantene 400ml', 'Shampoing réparateur', 7, 3500, 2, 12),
('HB004', 'Déodorant Nivea', 'Déodorant spray 150ml', 7, 2500, 28, 10),
('HB005', 'Gel douche 500ml', 'Gel douche hydratant', 7, 2200, 35, 15),

-- === ÉLECTRONIQUE (Catégorie 8) ===
('EL001', 'Piles AA x4', 'Piles alcalines AA pack de 4', 8, 1500, 48, 15),
('EL002', 'Ampoule LED 12W', 'Ampoule économique blanc chaud', 8, 2500, 25, 8),
('EL003', 'Câble USB-C 1m', 'Câble de charge USB-C', 8, 1800, 18, 10),

-- === ARTICLES MÉNAGERS (Catégorie 9) ===
('AM001', 'Liquide vaisselle 1L', 'Détergent vaisselle citron', 9, 1200, 52, 20),
('AM002', 'Éponges x5', 'Éponges grattantes pack de 5', 9, 800, 9, 15),
('AM003', 'Sacs poubelle x20', 'Sacs poubelle 50L rouleau de 20', 9, 2200, 35, 12),
('AM004', 'Javel 1L', 'Eau de javel concentrée', 9, 1000, 28, 10),

-- === SNACKS ET CONFISERIES (Catégorie 10) ===
('SC001', 'Chips Lay''s 150g', 'Chips salées nature', 10, 1500, 62, 20),
('SC002', 'Chocolat Milka 100g', 'Chocolat au lait', 10, 2000, 45, 15),
('SC003', 'Biscuits Oreo 154g', 'Biscuits chocolat fourrés', 10, 1800, 38, 12),
('SC004', 'Bonbons Haribo 200g', 'Bonbons gélifiés assortis', 10, 1200, 0, 15),
('SC005', 'Cacahuètes grillées 250g', 'Cacahuètes salées', 10, 1000, 58, 20);

-- ========================================
-- 5. RELATION FOURNIR (Produits-Fournisseurs)
-- ========================================
INSERT INTO fournir (Id_Produit, Id_Fournisseur, Quantite) VALUES
-- Boissons → SODIGAZ et Distributions Africaines
('BV001', 1, 1000), ('BV002', 1, 800), ('BV003', 1, 800), 
('BV004', 2, 2000), ('BV005', 2, 500), ('BV006', 2, 600),

-- Épicerie → Distributions Africaines et Agro-Food
('EP001', 2, 1500), ('EP002', 3, 800), ('EP003', 2, 1000), 
('EP004', 3, 1200), ('EP005', 2, 1500), ('EP006', 3, 900),
('EP007', 3, 700), ('EP008', 3, 600),

-- Produits laitiers → Fresh Market
('PL001', 4, 500), ('PL002', 4, 400), ('PL003', 4, 300), 
('PL004', 4, 350), ('PL005', 4, 250),

-- Viandes et poissons → Fresh Market
('VP001', 4, 200), ('VP002', 4, 150), ('VP003', 4, 100), 
('VP004', 2, 600), ('VP005', 2, 500),

-- Fruits et légumes → Fresh Market
('FL002', 4, 800), ('FL003', 4, 600), ('FL004', 4, 1000), ('FL005', 4, 500),

-- Boulangerie → Boulangerie Industrielle
('BP001', 7, 400), ('BP002', 7, 300), ('BP003', 7, 500), ('BP004', 7, 350),

-- Hygiène → Cosmétiques et Hygiène
('HB001', 6, 800), ('HB002', 6, 500), ('HB003', 6, 400), 
('HB004', 6, 450), ('HB005', 6, 600),

-- Électronique → Tech Import
('EL001', 5, 600), ('EL002', 5, 400), ('EL003', 5, 500),

-- Articles ménagers → Distributions Africaines
('AM001', 2, 700), ('AM002', 2, 900), ('AM003', 2, 500), ('AM004', 2, 600),

-- Snacks → Snack Distribution
('SC001', 8, 800), ('SC002', 8, 600), ('SC003', 8, 700), ('SC005', 8, 1000);

-- ========================================
-- 6. ACHATS DÉJÀ REÇUS (pour avoir du stock initial)
-- ========================================
-- IMPORTANT: On insère directement en statut RECU pour éviter les erreurs de modification
INSERT INTO Achat (DateAchat, Statut, Id_Utilisateur, Id_Fournisseur) VALUES
(CURRENT_TIMESTAMP - INTERVAL '20 days', 'RECU', 5, 1),
(CURRENT_TIMESTAMP - INTERVAL '18 days', 'RECU', 5, 2),
(CURRENT_TIMESTAMP - INTERVAL '15 days', 'RECU', 5, 4),
(CURRENT_TIMESTAMP - INTERVAL '12 days', 'RECU', 5, 6),
(CURRENT_TIMESTAMP - INTERVAL '8 days', 'RECU', 5, 8),
(CURRENT_TIMESTAMP - INTERVAL '5 days', 'RECU', 5, 3);

-- ========================================
-- 7. LIGNES D'ACHAT (liées aux achats REÇUS)
-- ========================================
INSERT INTO LigneAchat (Id_Achat, Id_Produit, Quantite, PrixAchatNegocie) VALUES
-- Achat 1 - Boissons
(1, 'BV001', 100, 800),
(1, 'BV002', 50, 750),
(1, 'BV003', 40, 750),

-- Achat 2 - Épicerie
(2, 'EP001', 150, 1200),
(2, 'EP002', 60, 1000),
(2, 'EP003', 80, 550),
(2, 'EP005', 100, 280),

-- Achat 3 - Produits laitiers et viandes
(3, 'PL001', 60, 900),
(3, 'PL002', 40, 1200),
(3, 'PL004', 35, 1500),
(3, 'VP002', 25, 2500),

-- Achat 4 - Hygiène
(4, 'HB001', 80, 1000),
(4, 'HB002', 50, 1200),
(4, 'HB003', 30, 2300),
(4, 'HB005', 45, 1500),

-- Achat 5 - Snacks
(5, 'SC001', 70, 1000),
(5, 'SC002', 50, 1400),
(5, 'SC003', 45, 1200),
(5, 'SC005', 65, 700),

-- Achat 6 - Divers
(6, 'EP006', 70, 600),
(6, 'FL002', 80, 550),
(6, 'FL003', 90, 1000),
(6, 'AM001', 60, 800);

-- ========================================
-- 8. ACHATS EN ATTENTE (pour démo)
-- ========================================
INSERT INTO Achat (DateAchat, Statut, Id_Utilisateur, Id_Fournisseur) VALUES
(CURRENT_TIMESTAMP - INTERVAL '4 days', 'EN_ATTENTE', 5, 1),
(CURRENT_TIMESTAMP - INTERVAL '2 days', 'EN_ATTENTE', 5, 4);

-- Lignes des achats en attente
INSERT INTO LigneAchat (Id_Achat, Id_Produit, Quantite, PrixAchatNegocie) VALUES
(7, 'BV002', 60, 750),
(7, 'BV003', 50, 750),
(8, 'VP001', 30, 3200),
(8, 'FL001', 60, 800);

-- ========================================
-- 9. VENTES (25 ventes sur plusieurs jours)
-- ========================================
INSERT INTO Vente (DateVente, Id_Utilisateur) VALUES
-- Ventes d'il y a 10 jours
(CURRENT_TIMESTAMP - INTERVAL '10 days' + INTERVAL '9 hours', 2),
(CURRENT_TIMESTAMP - INTERVAL '10 days' + INTERVAL '14 hours', 3),

-- Ventes d'il y a 7 jours
(CURRENT_TIMESTAMP - INTERVAL '7 days' + INTERVAL '10 hours', 6),
(CURRENT_TIMESTAMP - INTERVAL '7 days' + INTERVAL '15 hours', 2),
(CURRENT_TIMESTAMP - INTERVAL '7 days' + INTERVAL '17 hours', 3),

-- Ventes d'il y a 5 jours
(CURRENT_TIMESTAMP - INTERVAL '5 days' + INTERVAL '9 hours', 2),
(CURRENT_TIMESTAMP - INTERVAL '5 days' + INTERVAL '12 hours', 6),
(CURRENT_TIMESTAMP - INTERVAL '5 days' + INTERVAL '16 hours', 3),

-- Ventes d'il y a 3 jours
(CURRENT_TIMESTAMP - INTERVAL '3 days' + INTERVAL '10 hours', 2),
(CURRENT_TIMESTAMP - INTERVAL '3 days' + INTERVAL '13 hours', 6),
(CURRENT_TIMESTAMP - INTERVAL '3 days' + INTERVAL '16 hours', 3),

-- Ventes d'hier
(CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '8 hours', 2),
(CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '11 hours', 6),
(CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '14 hours', 3),
(CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '17 hours', 2),

-- Ventes d'aujourd'hui
(CURRENT_TIMESTAMP - INTERVAL '3 hours', 2),
(CURRENT_TIMESTAMP - INTERVAL '2 hours 30 minutes', 6),
(CURRENT_TIMESTAMP - INTERVAL '2 hours', 3),
(CURRENT_TIMESTAMP - INTERVAL '1 hour 30 minutes', 2),
(CURRENT_TIMESTAMP - INTERVAL '1 hour', 6),
(CURRENT_TIMESTAMP - INTERVAL '45 minutes', 3),
(CURRENT_TIMESTAMP - INTERVAL '30 minutes', 2),
(CURRENT_TIMESTAMP - INTERVAL '20 minutes', 6),
(CURRENT_TIMESTAMP - INTERVAL '10 minutes', 3),
(CURRENT_TIMESTAMP - INTERVAL '5 minutes', 2);

-- ========================================
-- 10. LIGNES DE VENTE
-- ========================================
INSERT INTO LigneVente (Id_Vente, Id_Produit, QteVendue, Remise) VALUES
-- Vente 1
(1, 'BV001', 3, 0), (1, 'EP001', 2, 0), (1, 'PL001', 1, 0),

-- Vente 2
(2, 'BV004', 6, 5), (2, 'EP003', 3, 0), (2, 'BP001', 2, 0),

-- Vente 3
(3, 'BV001', 2, 0), (3, 'BV005', 1, 0), (3, 'PL003', 1, 10),

-- Vente 4
(4, 'BV002', 4, 0), (4, 'EP002', 2, 0), (4, 'HB001', 3, 0),

-- Vente 5
(5, 'EP001', 5, 0), (5, 'EP005', 2, 0), (5, 'AM001', 1, 0),

-- Vente 6
(6, 'BV001', 2, 0), (6, 'PL002', 3, 0), (6, 'SC001', 2, 0),

-- Vente 7
(7, 'BV004', 4, 0), (7, 'PL004', 1, 0), (7, 'HB002', 2, 0),

-- Vente 8
(8, 'EP003', 4, 5), (8, 'FL002', 3, 0), (8, 'SC002', 2, 0),

-- Vente 9
(9, 'BV001', 5, 0), (9, 'PL001', 2, 0), (9, 'EL001', 3, 0),

-- Vente 10
(10, 'EP001', 3, 0), (10, 'FL003', 2, 0), (10, 'SC003', 1, 0),

-- Vente 11
(11, 'BV002', 2, 0), (11, 'PL002', 1, 0), (11, 'HB001', 2, 0),

-- Vente 12
(12, 'BV004', 8, 10), (12, 'BP001', 3, 0), (12, 'SC001', 3, 0),

-- Vente 13
(13, 'BV001', 4, 0), (13, 'BV005', 2, 0), (13, 'EL002', 1, 0),

-- Vente 14
(14, 'EP001', 2, 0), (14, 'PL001', 3, 0), (14, 'HB002', 1, 0),

-- Vente 15
(15, 'EP003', 5, 0), (15, 'FL003', 3, 0), (15, 'SC002', 2, 0),

-- Vente 16 (aujourd'hui)
(16, 'BV001', 3, 0), (16, 'EP002', 1, 0), (16, 'AM002', 2, 0),

-- Vente 17 (aujourd'hui)
(17, 'BV004', 5, 0), (17, 'AM001', 1, 0),

-- Vente 18 (aujourd'hui)
(18, 'BV002', 3, 0), (18, 'VP003', 1, 15), (18, 'HB004', 1, 0),

-- Vente 19 (aujourd'hui)
(19, 'EP001', 4, 0), (19, 'PL004', 2, 0), (19, 'EL003', 1, 0),

-- Vente 20 (aujourd'hui)
(20, 'BV001', 6, 0), (20, 'FL004', 3, 0), (20, 'SC001', 2, 0),

-- Vente 21 (aujourd'hui)
(21, 'EP003', 3, 0), (21, 'BP003', 4, 0), (21, 'SC003', 2, 0),

-- Vente 22 (aujourd'hui)
(22, 'BV004', 10, 5), (22, 'PL001', 2, 0), (22, 'HB005', 1, 0),

-- Vente 23 (aujourd'hui)
(23, 'EP001', 3, 0), (23, 'FL002', 2, 0), (23, 'SC005', 3, 0),

-- Vente 24 (aujourd'hui - grosse vente)
(24, 'BV001', 8, 5), (24, 'BV004', 12, 10), (24, 'EP001', 6, 0), 
(24, 'PL001', 4, 0), (24, 'FL003', 5, 0), (24, 'SC001', 5, 0),

-- Vente 25 (aujourd'hui - dernière vente)
(25, 'BV005', 2, 0), (25, 'VP004', 3, 0), (25, 'BP002', 1, 0), (25, 'SC002', 2, 0);

-- ========================================
-- 11. REÇUS (pour toutes les ventes)
-- ========================================
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

-- ========================================
-- FIN DU SCRIPT D'INSERTION
-- ========================================

-- Message de confirmation
SELECT 'Données insérées avec succès!' AS Statut;