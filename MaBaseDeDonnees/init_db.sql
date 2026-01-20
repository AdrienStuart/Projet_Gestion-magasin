-- ====================================================
-- SCRIPT MASTER D'INITIALISATION DE LA BASE DE DONNEES
-- ====================================================
-- Ce script execute tous les fichiers SQL dans l'ordre requis.
-- Executez ceci dans votre terminal : psql -U votre_user -d votre_db -f init_db.sql

\i Tables.sql
\i Triggers_et_Fonctions.sql
\i Vues.sql
\i Vues_TVA.sql
\i Index.sql
\i Donnees_de_tests_Insertions.sql

-- Optionnel : Verifier les donnees
-- \i Verif_donnees.sql

SELECT '✅ Initialisation de la base de données terminée avec succès !' as status;
