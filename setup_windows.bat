@echo off
TITLE Configuration Projet Gestion Magasin - Windows

echo ----------------------------------------------------
echo rocket CONFIGURATION DU PROJET GESTION MAGASIN (WINDOWS)
echo ----------------------------------------------------

echo [1/2] Mise a jour de pip...
python -m pip install --upgrade pip

echo [2/2] Installation des dependances (requirements.txt)...
python -m pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo check INSTALLATION REUSSIE !
    echo ----------------------------------------------------
    echo Prochaine etape : Initialiser la base de donnes dans pgAdmin
    echo ou via ligne de commande :
    echo    cd MaBaseDeDonnees
    echo    psql -U postgres -d votre_db -f init_db.sql
    echo ----------------------------------------------------
    echo Lancement : python main.py
    echo ----------------------------------------------------
) else (
    echo.
    echo cross Une erreur est survenue lors de l'installation.
)
pause
