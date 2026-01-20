#!/bin/bash

# =============================================================================
# 🚀 SCRIPT D'INSTALLATION COMPLÈTE - PROJET GESTION MAGASIN
# =============================================================================
# Ce script installe Git, PostgreSQL, pgAdmin et Python sur un système Debian/Ubuntu.
# Usage : chmod +x install_system_deps.sh && sudo ./install_system_deps.sh
# =============================================================================

echo "----------------------------------------------------"
echo "🌟 PRÉPARATION DE L'ENVIRONNEMENT SYSTÈME 🌟"
echo "----------------------------------------------------"

# Vérification des privilèges root
if [ "$EUID" -ne 0 ]; then 
  echo "❌ Veuillez lancer ce script avec sudo : sudo ./install_system_deps.sh"
  exit
fi

echo "🔄 Mise à jour des dépôts..."
apt update -y

# 1. Installation de Git
echo "📦 Installation de Git..."
apt install git -y

# 2. Installation de Python3 et pip
echo "📦 Installation de Python3 et pip..."
apt install python3 python3-pip -y

# 3. Installation de PostgreSQL
echo "📦 Installation de PostgreSQL..."
apt install postgresql postgresql-contrib libpq-dev -y
systemctl start postgresql
systemctl enable postgresql

# 4. Installation de pgAdmin 4
# On utilise le dépôt officiel
echo "📦 Configuration du dépôt pgAdmin 4..."
curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add
echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list
apt update -y
echo "📦 Installation de pgAdmin 4 (Mode Desktop)..."
apt install pgadmin4-desktop -y

echo "----------------------------------------------------"
echo "✅ INSTALLATION SYSTÈME TERMINÉE !"
echo "----------------------------------------------------"
echo "Résumé :"
echo " - Git : Installé"
echo " - Python3/Pip : Installés"
echo " - PostgreSQL : Installé et démarré"
echo " - pgAdmin 4 : Installé (disponible dans votre menu d'applications)"
echo ""
echo "💡 PROCHAINES ÉTAPES (en tant qu'utilisateur normal) :"
echo " 1. Configurer un mot de passe pour l'utilisateur postgres :"
echo "    sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'votre_mot_de_passe';\""
echo " 2. Lancer l'installation des dépendances Python :"
echo "    ./setup.sh"
echo "----------------------------------------------------"
