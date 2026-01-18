-- TRIGGERS ET FONCTIONS

-- TRIGGER 0 : Sécurité et Automatisme du prix 
CREATE OR REPLACE FUNCTION fn_pre_remplir_prix_vente()
RETURNS TRIGGER AS $$
BEGIN
    -- On va chercher le prix actuel dans la table Produit
    SELECT PrixUnitaireActuel INTO NEW.PrixUnitaireVendu 
    FROM Produit WHERE Id_Produit = NEW.Id_Produit;
    
    -- Si le produit n'existe pas, on bloque tout
    IF NEW.PrixUnitaireVendu IS NULL THEN
        RAISE EXCEPTION 'Produit introuvable : %', NEW.Id_Produit;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pre_remplir_prix
BEFORE INSERT ON LigneVente
FOR EACH ROW
EXECUTE FUNCTION fn_pre_remplir_prix_vente();

-- 1. TRIGGER : Vérification de Remise (AVANT insertion/modification)

CREATE OR REPLACE FUNCTION fn_verifier_remise()
RETURNS TRIGGER AS $$
DECLARE
    v_prix_produit NUMERIC(10,2);
    v_prix_apres_remise NUMERIC(10,2);
BEGIN
    -- Récupérer le prix du produit
    SELECT PrixUnitaireActuel INTO v_prix_produit
    FROM Produit
    WHERE Id_Produit = NEW.Id_Produit;
    
    -- Calculer le prix après remise
    v_prix_apres_remise := v_prix_produit * (1 - COALESCE(NEW.Remise, 0) / 100.0);
    
    -- Vérifier que le prix après remise n'est pas négatif ou nul
    IF v_prix_apres_remise <= 0 THEN
        RAISE EXCEPTION 'Remise trop élevée: le prix devient négatif (%.2f - %.2f%% remise) = %.2f', 
                        v_prix_produit, NEW.Remise, v_prix_apres_remise;
    END IF;
    
    -- Vérifier que la remise ne dépasse pas 100%
    IF NEW.Remise > 100 THEN
        RAISE EXCEPTION 'Remise impossible: %.2f%%, maximum 100%%', NEW.Remise;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verifier_remise
BEFORE INSERT OR UPDATE OF Remise ON LigneVente
FOR EACH ROW
EXECUTE FUNCTION fn_verifier_remise();


-- 2. TRIGGER : Mise à Jour du Stock et Alerte Stock (APRÈS insertion vente)

CREATE OR REPLACE FUNCTION fn_maj_stock_vente()
RETURNS TRIGGER AS $$
DECLARE
    v_stock_actuel INT;
    v_nouveau_stock INT;
    v_stock_alerte INT;
    v_id_utilisateur INT;
BEGIN
    -- Récupérer le stock actuel, l'alerte et l'utilisateur
    SELECT StockActuel, StockAlerte INTO v_stock_actuel, v_stock_alerte
    FROM Produit 
    WHERE Id_Produit = NEW.Id_Produit
    FOR UPDATE;
	
    SELECT Id_Utilisateur INTO v_id_utilisateur
    FROM Vente 
    WHERE Id_Vente = NEW.Id_Vente;
    
    -- Vérifier le stock disponible
    IF v_stock_actuel < NEW.QteVendue THEN
        RAISE EXCEPTION 'Stock insuffisant pour le produit ID: % (Stock: %, Demandé: %)', 
                        NEW.Id_Produit, v_stock_actuel, NEW.QteVendue;
    END IF;

    -- Calculer le nouveau stock
    v_nouveau_stock := v_stock_actuel - NEW.QteVendue;

    -- Mettre à jour le stock du produit
    UPDATE Produit 
    SET StockActuel = v_nouveau_stock
    WHERE Id_Produit = NEW.Id_Produit;

    -- ALERTE STOCK : Vérifier si le stock devient critique
    IF v_nouveau_stock <= v_stock_alerte THEN
        RAISE NOTICE 'ALERTE : Stock critique pour le produit % (Stock: %, Seuil alerte: %)', 
                     NEW.Id_Produit, v_nouveau_stock, v_stock_alerte;
    END IF;

    -- Créer un mouvement de stock
    INSERT INTO MouvementStock (
        DateMouvement, Type, Quantite, Id_Utilisateur, 
        Id_Produit, Id_Vente, Commentaire
    ) VALUES (
        CURRENT_TIMESTAMP, 
        'SORTIE', 
        NEW.QteVendue,
        v_id_utilisateur,
        NEW.Id_Produit,
        NEW.Id_Vente,
        'Vente enregistrée - Produit: ' || NEW.Id_Produit
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_stock_vente
AFTER INSERT ON LigneVente
FOR EACH ROW
EXECUTE FUNCTION fn_maj_stock_vente();


-- 3. TRIGGER : Anti-Fraude - Blocage du prix de vente historisé

CREATE OR REPLACE FUNCTION fn_verrou_prix_historique()
RETURNS TRIGGER AS $$
BEGIN
    IF (OLD.PrixUnitaireVendu <> NEW.PrixUnitaireVendu) THEN
        RAISE EXCEPTION 'Interdiction de modifier un prix de vente historisé ! (Ancien: %, Nouveau: %)', 
                        OLD.PrixUnitaireVendu, NEW.PrixUnitaireVendu;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verrou_prix
BEFORE UPDATE ON LigneVente
FOR EACH ROW 
EXECUTE FUNCTION fn_verrou_prix_historique();


-- 4. TRIGGER : Annulation/Suppression de Vente - Retour au Stock

CREATE OR REPLACE FUNCTION fn_retour_stock_annulation()
RETURNS TRIGGER AS $$
DECLARE
    v_id_utilisateur INT;
BEGIN
    -- Récupérer l'utilisateur de la vente
    SELECT Id_Utilisateur INTO v_id_utilisateur
    FROM Vente
    WHERE Id_Vente = OLD.Id_Vente;

    -- Rendre les produits au stock
    UPDATE Produit 
    SET StockActuel = StockActuel + OLD.QteVendue 
    WHERE Id_Produit = OLD.Id_Produit;
    
    -- Tracer l'annulation dans les mouvements de stock
    INSERT INTO MouvementStock (
        DateMouvement, Type, Quantite, Id_Utilisateur, 
        Id_Produit, Commentaire
    ) VALUES (
        CURRENT_TIMESTAMP, 
        'AJUSTEMENT', 
        OLD.QteVendue, 
        COALESCE(v_id_utilisateur, 1), 
        OLD.Id_Produit, 
        'ANNULATION VENTE ID: ' || OLD.Id_Vente
    );
    
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_annulation_vente
AFTER DELETE ON LigneVente
FOR EACH ROW 
EXECUTE FUNCTION fn_retour_stock_annulation();


-- 5. TRIGGER : Mise à Jour du Stock et PMP lors de Réception d'Achat

CREATE OR REPLACE FUNCTION fn_maj_stock_et_pmp_achat()
RETURNS TRIGGER AS $$
DECLARE
    rec RECORD;
    v_ancien_pmp NUMERIC(10,2);
    v_ancienne_qte INT;
BEGIN
    -- Seulement si le statut passe à 'RECU'
    IF NEW.Statut = 'RECU' AND OLD.Statut != 'RECU' THEN
        -- Parcourir toutes les lignes d'achat pour cet achat
        FOR rec IN (
            SELECT la.Id_Produit, la.Quantite, la.PrixAchatNegocie
            FROM LigneAchat la
            WHERE la.Id_Achat = NEW.Id_Achat
        )
        LOOP
            -- Récupérer les anciennes valeurs
            SELECT PrixAchatMoyen, QuantiteTotaleAchetee 
            INTO v_ancien_pmp, v_ancienne_qte
            FROM Produit
            WHERE Id_Produit = rec.Id_Produit;

            -- FORMULE PMP (Prix Moyen Pondéré) :
            -- Nouveau PMP = (Ancien PMP × Ancienne Qté Totale + Prix Achat × Qté Achetée) 
            --               / Nouvelle Qté Totale
            UPDATE Produit
            SET 
                -- 1. Mettre à jour le stock physique
                StockActuel = StockActuel + rec.Quantite,
                
                -- 2. Mettre à jour le dernier prix d'achat
                DernierPrixAchat = rec.PrixAchatNegocie,
                
                -- 3. Incrémenter la quantité totale achetée (historique)
                QuantiteTotaleAchetee = v_ancienne_qte + rec.Quantite,
                
                -- 4. Calculer le nouveau PMP
                PrixAchatMoyen = 
                    CASE 
                        -- Si c'est le premier achat
                        WHEN v_ancienne_qte = 0 THEN rec.PrixAchatNegocie
                        -- Sinon, appliquer la formule PMP
                        ELSE (
                            (v_ancien_pmp * v_ancienne_qte) + 
                            (rec.PrixAchatNegocie * rec.Quantite)
                        ) / (v_ancienne_qte + rec.Quantite)
                    END
            WHERE Id_Produit = rec.Id_Produit;

            -- Créer un mouvement de stock
            INSERT INTO MouvementStock (
                DateMouvement, Type, Quantite, Id_Utilisateur,
                Id_Produit, Id_Achat, Commentaire
            ) VALUES (
                CURRENT_TIMESTAMP,
                'ENTREE',
                rec.Quantite,
                NEW.Id_Utilisateur,
                rec.Id_Produit,
                NEW.Id_Achat,
                'Achat reçu - Prix unitaire: ' || rec.PrixAchatNegocie
            );
        END LOOP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_stock_et_pmp_achat
AFTER UPDATE OF Statut ON Achat
FOR EACH ROW
EXECUTE FUNCTION fn_maj_stock_et_pmp_achat();


-- 6. TRIGGER : Validation du Montant du Reçu

CREATE OR REPLACE FUNCTION fn_valider_recu()
RETURNS TRIGGER AS $$
DECLARE
    total_vente NUMERIC(10,2);
BEGIN
    -- Calculer le total de la vente
    SELECT COALESCE(SUM(
        lv.QteVendue * lv.PrixUnitaireVendu * (1 - COALESCE(lv.Remise, 0) / 100.0)
    ), 0) INTO total_vente
    FROM LigneVente lv
    WHERE lv.Id_Vente = NEW.Id_Vente;

    -- Vérifier la correspondance (tolérance de 0.01 pour arrondis)
    IF ABS(NEW.MontantTotal - total_vente) > 0.01 THEN
        RAISE EXCEPTION 'Le montant du reçu (%) ne correspond pas au total de la vente (%)', 
                        NEW.MontantTotal, total_vente;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_valider_recu
BEFORE INSERT ON Recu
FOR EACH ROW
EXECUTE FUNCTION fn_valider_recu();


-- 7. TRIGGER : Validation des Rôles pour les Achats (Sécurité métier)

CREATE OR REPLACE FUNCTION fn_verif_role_achat()
RETURNS TRIGGER AS $$
DECLARE
    v_role VARCHAR(20);
BEGIN
    SELECT Role INTO v_role 
    FROM Utilisateur 
    WHERE Id_Utilisateur = NEW.Id_Utilisateur;
    
    IF v_role NOT IN ('Administrateur', 'Responsable_Achats') THEN
        RAISE EXCEPTION 'Accès refusé : Seul un Responsable Achats ou un Administrateur peut créer une commande. (Rôle actuel: %)', v_role;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_role_achat
BEFORE INSERT ON Achat
FOR EACH ROW 
EXECUTE FUNCTION fn_verif_role_achat();


-- 8. TRIGGER : Définir automatiquement la DateAjout d'un Produit

CREATE OR REPLACE FUNCTION fn_set_date_ajout()
RETURNS TRIGGER AS $$
BEGIN
    -- Si DateAjout n'est pas spécifiée, mettre la date actuelle
    IF NEW.DateAjout IS NULL THEN
        NEW.DateAjout := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_set_date_ajout
BEFORE INSERT ON Produit
FOR EACH ROW
EXECUTE FUNCTION fn_set_date_ajout();

-- 9. TRIGGER: Verrouiller les achats. 

CREATE OR REPLACE FUNCTION fn_verrou_achat_recu()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.Statut = 'RECU' THEN
        RAISE EXCEPTION 'Impossible de modifier une commande déjà réceptionnée !';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verrou_achat
BEFORE UPDATE OR DELETE ON Achat
FOR EACH ROW
WHEN (OLD.Statut = 'RECU')
EXECUTE FUNCTION fn_verrou_achat_recu();
