-- =========================================================================
-- SCRIPT DE SYNCHRONISATION ET MISE À JOUR DU CENTRE DE SIGNALEMENT
-- =========================================================================
-- 1. Mise à jour de la logique de surveillance (Trigger intelligent)
-- 2. Synchronisation rétroactive des stocks bas (Initialisation)
-- =========================================================================

-- PARTIE 1 : MISE À JOUR DU TRIGGER (Archivage automatique amélioré)
-- archive désormais aussi les alertes 'EN_COURS' si le stock remonte
CREATE OR REPLACE FUNCTION fn_surveillance_stock_intelligente()
RETURNS TRIGGER AS $$
DECLARE
    v_priorite VARCHAR(20);
BEGIN
    -- CAS 1 : LE STOCK PASSE SOUS LE SEUIL (Alerte)
    IF NEW.StockActuel <= NEW.StockAlerte THEN
        IF NOT EXISTS (
            SELECT 1 FROM AlerteStock 
            WHERE Id_Produit = NEW.Id_Produit 
            AND Statut NOT IN ('ARCHIVEE', 'COMMANDE_PASSEE')
        ) THEN
            IF NEW.StockActuel = 0 THEN v_priorite := 'CRITICAL';
            ELSIF NEW.StockActuel <= (NEW.StockAlerte / 2) THEN v_priorite := 'HIGH';
            ELSE v_priorite := 'MEDIUM';
            END IF;

            INSERT INTO AlerteStock (Id_Produit, Stock_Au_Moment_Alerte, Seuil_Alerte_Vise, Priorite, Commentaire)
            VALUES (NEW.Id_Produit, NEW.StockActuel, NEW.StockAlerte, v_priorite, 'Alerte automatique : Stock critique détecté.');
        END IF;

    -- CAS 2 : LE STOCK REPASSE AU-DESSUS DU SEUIL (Auto-guérison)
    ELSIF NEW.StockActuel > NEW.StockAlerte AND OLD.StockActuel <= OLD.StockAlerte THEN
        UPDATE AlerteStock
        SET Statut = 'ARCHIVEE',
            Date_Traitement = CURRENT_TIMESTAMP,
            Commentaire = COALESCE(Commentaire, '') || ' [Fermeture automatique : Stock réapprovisionné]'
        WHERE Id_Produit = NEW.Id_Produit 
        AND Statut IN ('NON_LUE', 'VU', 'EN_COURS');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- PARTIE 2 : SYNCHRONISATION INITIALE
-- Insère les alertes pour les produits déjà sous le seuil
INSERT INTO AlerteStock (Id_Produit, Stock_Au_Moment_Alerte, Seuil_Alerte_Vise, Priorite, Statut, Commentaire)
SELECT 
    Id_Produit, StockActuel, StockAlerte,
    CASE 
        WHEN StockActuel = 0 THEN 'CRITICAL'
        WHEN StockActuel <= StockAlerte / 2 THEN 'HIGH'
        ELSE 'MEDIUM'
    END,
    'NON_LUE',
    'Initialisation automatique : Synchronisation rétroactive des stocks bas.'
FROM Produit
WHERE StockActuel < StockAlerte
ON CONFLICT (Id_Produit, Statut) DO NOTHING;
