
-- SUPPRESSION DES TABLES EXISTANTES 

DROP TABLE IF EXISTS fournir CASCADE;
DROP TABLE IF EXISTS Recu CASCADE;
DROP TABLE IF EXISTS MouvementStock CASCADE;
DROP TABLE IF EXISTS LigneVente CASCADE;
DROP TABLE IF EXISTS LigneAchat CASCADE;
DROP TABLE IF EXISTS Vente CASCADE;
DROP TABLE IF EXISTS Achat CASCADE;
DROP TABLE IF EXISTS Produit CASCADE;
DROP TABLE IF EXISTS Fournisseur CASCADE;
DROP TABLE IF EXISTS Utilisateur CASCADE;
DROP TABLE IF EXISTS Categorie CASCADE;


-- Table Catégorie
CREATE TABLE Categorie(
   Id_Categorie SERIAL,
   Libelle VARCHAR(100) NOT NULL,
   PRIMARY KEY(Id_Categorie)
);

-- Table Utilisateur
CREATE TABLE Utilisateur(
   Id_Utilisateur SERIAL,
   Nom VARCHAR(50) NOT NULL,
   Role VARCHAR(20) NOT NULL CHECK (Role IN ('Administrateur', 'Caissier', 'Gestionnaire', 'Responsable_Achats')),
   MotDePasse VARCHAR(255) NOT NULL,
   email VARCHAR(50) NOT NULL,
   PRIMARY KEY(Id_Utilisateur),
   UNIQUE(email)
);

-- Table Fournisseur
CREATE TABLE Fournisseur(
   Id_Fournisseur SERIAL,
   Nom VARCHAR(50) NOT NULL,
   Contact VARCHAR(20) NOT NULL,
   Adresse VARCHAR(50) NOT NULL,
   PRIMARY KEY(Id_Fournisseur),
   UNIQUE(Nom),
   UNIQUE(Contact)
);


-- Table Produit (AVEC PMP)
CREATE TABLE Produit(
   Id_Produit VARCHAR(20),
   Nom VARCHAR(100) NOT NULL,
   Description TEXT,
   Id_Categorie INT NOT NULL,
   PrixUnitaireActuel NUMERIC(10,2) NOT NULL CHECK (PrixUnitaireActuel > 0),
   -- CHAMPS PMP calculés via Triggers
   PrixAchatMoyen NUMERIC(10,2) DEFAULT 0 CHECK (PrixAchatMoyen >= 0),
   DernierPrixAchat NUMERIC(10,2) DEFAULT 0 CHECK (DernierPrixAchat >= 0),
   QuantiteTotaleAchetee INT DEFAULT 0 CHECK (QuantiteTotaleAchetee >= 0),
   --
   DateAjout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   StockActuel INT NOT NULL DEFAULT 0 CHECK (StockActuel >= 0),
   StockAlerte INT DEFAULT 5,
   ImagePath VARCHAR(255) DEFAULT 'assets/default.png',
   -- On ajoute le taux de TVA (ex: 18.00, 5.5, 0)
   TauxTVA DECIMAL(5,2) DEFAULT 18.00,
   PRIMARY KEY(Id_Produit),
   UNIQUE(Nom),
   FOREIGN KEY (Id_Categorie) REFERENCES Categorie(Id_Categorie)
);

-- Table Achat
CREATE TABLE Achat(
   Id_Achat SERIAL,
   DateAchat TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   Statut VARCHAR(20) NOT NULL DEFAULT 'EN_ATTENTE' CHECK (Statut IN ('EN_ATTENTE', 'RECU', 'ANNULE')),
   Id_Utilisateur INT NOT NULL,
   Id_Fournisseur INT NOT NULL,
   PRIMARY KEY(Id_Achat),
   FOREIGN KEY(Id_Utilisateur) REFERENCES Utilisateur(Id_Utilisateur),
   FOREIGN KEY(Id_Fournisseur) REFERENCES Fournisseur(Id_Fournisseur)
);

-- Table LigneAchat
CREATE TABLE LigneAchat(
   Id_Achat INT NOT NULL,
   Id_Produit VARCHAR(20) NOT NULL,
   Quantite INT NOT NULL CHECK (Quantite > 0),
   PrixAchatNegocie NUMERIC(10,2) NOT NULL CHECK (PrixAchatNegocie >= 0),
   PRIMARY KEY(Id_Achat, Id_Produit),
   FOREIGN KEY(Id_Achat) REFERENCES Achat(Id_Achat) ON DELETE CASCADE,
   FOREIGN KEY(Id_Produit) REFERENCES Produit(Id_Produit)
);

-- Table Vente
CREATE TABLE Vente(
   Id_Vente SERIAL,
   DateVente TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   /*Prix NUMERIC(10,2) NOT NULL DEFAULT 0,
        Le prix sera calculé par une vue.
   */
   Id_Utilisateur INT NOT NULL,
   PRIMARY KEY(Id_Vente),
   FOREIGN KEY(Id_Utilisateur) REFERENCES Utilisateur(Id_Utilisateur)
);

-- Table LigneVente
CREATE TABLE LigneVente(
   Id_Vente INT NOT NULL,
   Id_Produit VARCHAR(20) NOT NULL,
   QteVendue INT NOT NULL CHECK (QteVendue > 0),
   Remise NUMERIC(5,2) DEFAULT 0 CHECK (Remise >= 0 AND Remise <= 100),
   PrixUnitaireVendu NUMERIC(10,2) NOT NULL CHECK (PrixUnitaireVendu >= 0),  -- Prix TTC d'une unité de ce produit figé lors de la vente.
   TauxTVA DECIMAL(5,2) DEFAULT 18.00,  -- Taux TVA au moment de la vente (pour historique)
   PRIMARY KEY(Id_Vente, Id_Produit),
   FOREIGN KEY(Id_Vente) REFERENCES Vente(Id_Vente) ON DELETE CASCADE,
   FOREIGN KEY(Id_Produit) REFERENCES Produit(Id_Produit)
);

CREATE TABLE MouvementStock(
   Id_Mouvement SERIAL,
   DateMouvement TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   Type VARCHAR(10) NOT NULL CHECK (Type IN ('ENTREE', 'SORTIE', 'AJUSTEMENT')),
   Quantite INT NOT NULL CHECK (Quantite > 0),
   Id_Utilisateur INT NOT NULL,
   Id_Produit VARCHAR(20) NOT NULL,
   Id_Vente INT,
   Id_Achat INT,
   Commentaire TEXT,
   PRIMARY KEY(Id_Mouvement),
   FOREIGN KEY(Id_Utilisateur) REFERENCES Utilisateur(Id_Utilisateur),
   FOREIGN KEY(Id_Produit) REFERENCES Produit(Id_Produit),
   FOREIGN KEY(Id_Vente) REFERENCES Vente(Id_Vente),
   FOREIGN KEY(Id_Achat) REFERENCES Achat(Id_Achat),
   
   -- Contrainte : Impossible d'être lié à une Vente ET un Achat en même temps
   CHECK (NOT (Id_Vente IS NOT NULL AND Id_Achat IS NOT NULL))
);

-- Table Reçu
CREATE TABLE Recu(
   Id_Recu SERIAL,
   DateEmission TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   ModePaiement VARCHAR(20) NOT NULL CHECK (ModePaiement IN ('ESPECES', 'CARTE', 'CHEQUE', 'VIREMENT')),
   MontantTotal NUMERIC(10,2) NOT NULL CHECK (MontantTotal >= 0),
   Id_Utilisateur INT NOT NULL,
   Id_Vente INT NOT NULL,
   PRIMARY KEY(Id_Recu),
   FOREIGN KEY(Id_Utilisateur) REFERENCES Utilisateur(Id_Utilisateur),
   FOREIGN KEY(Id_Vente) REFERENCES Vente(Id_Vente)
);

-- Table de liaison Produit-Fournisseur
CREATE TABLE fournir(
   Id_Produit VARCHAR(20),
   Id_Fournisseur INT,
   Quantite INT NOT NULL DEFAULT 1 CHECK (Quantite > 0),
   PRIMARY KEY(Id_Produit, Id_Fournisseur),
   FOREIGN KEY(Id_Produit) REFERENCES Produit(Id_Produit),
   FOREIGN KEY(Id_Fournisseur) REFERENCES Fournisseur(Id_Fournisseur)
);

-- Table Depense (Charges et dépenses)
CREATE TABLE Depense (
    Id_Depense SERIAL PRIMARY KEY,
    Libelle VARCHAR(100) NOT NULL, -- ex: 'Salaire Janvier - Marie'
    Categorie VARCHAR(50) CHECK (Categorie IN ('SALAIRE', 'LOYER', 'ELECTRICITE', 'INTERNET', 'AUTRE')),
    Montant DECIMAL(12,2) NOT NULL,
    DateDepense TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Id_Utilisateur INTEGER REFERENCES Utilisateur(Id_Utilisateur) -- Qui a enregistré la dépense ?
);

CREATE INDEX idx_depense_date ON Depense(DateDepense);

-- SÉQUENCES

CREATE SEQUENCE IF NOT EXISTS seq_mouvement START 1;