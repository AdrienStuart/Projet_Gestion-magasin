#!/bin/bash

# Script de configuration pour le projet Gestion Magasin
# Ce script installe toutes les bibliothèques nécessaires

echo "----------------------------------------------------"
echo "🚀 CONFIGURATION DU PROJET GESTION MAGASIN"
echo "----------------------------------------------------"

# Vérification de Python
if ! command -v python3 &> /dev/null
then
    echo "❌ Erreur : Python3 n'est pas installé sur votre système."
    exit 1
fi

echo "📦 Mise à jour de pip..."
python3 -m pip install --upgrade pip

echo "📦 Installation des dépendances (requirements.txt)..."
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ INSTALLATION RÉUSSIE !"
    echo "----------------------------------------------------"
    echo "💡 PROCHAINE ÉTAPE : CONFIGURER LA BASE DE DONNÉES"
    echo "1. Allez dans le dossier 'MaBaseDeDonnees'"
    echo "2. Lancez : psql -U votre_user -d votre_db -f init_db.sql"
    echo "----------------------------------------------------"
    echo "Vous pouvez ensuite lancer l'application avec :"
    echo "   python3 main.py"
    echo "----------------------------------------------------"
else
    echo ""
    echo "❌ Une erreur est survenue lors de l'installation."
fi
