# 🛒 Projet Gestion Magasin

Système complet de gestion de magasin incluant les modules **Caisse**, **Stock**, **Achats** et **Administration**.

## 🛠 Installation Rapide

Pour installer toutes les dépendances Python nécessaires (PySide6, Matplotlib, etc.), ouvrez un terminal dans ce dossier et lancez :

```bash
chmod +x setup.sh
./setup.sh
```

## 🗄 Configuration de la Base de Données

Ce projet utilise **PostgreSQL**. Voici comment configurer votre base de données :

1.  **Créer une base de données** vide (ex: `gestion_magasin`).
2.  **Initialiser le schéma et les données** :
    Allez dans le dossier `MaBaseDeDonnees` et exécutez le script d'initialisation :
    ```bash
    cd MaBaseDeDonnees
    psql -U votre_utilisateur -d gestion_magasin -f init_db.sql
    ```
    *Ce script va créer les tables, les fonctions, les triggers, les vues et insérer les données de test.*

3.  **Configurer la connexion** : 
    Ouvrez le fichier `db/database.py` (ou le fichier de configuration correspondant) et assurez-vous que les paramètres de connexion (host, port, user, password) correspondent à votre environnement local.

## 🚀 Lancement de l'Application

Une fois les dépendances installées et la base de données configurée, lancez simplement :

```bash
python3 main.py
```

## 📚 Documentation Additionnelle
Vous trouverez le détail des fonctionnalités implémentées dans le dossier `.gemini/antigravity/brain/` (Walkthrough et Plan d'implémentation).
