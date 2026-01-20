# =============================================================================
# 🚀 SCRIPT D'INSTALLATION COMPLÈTE (WINDOWS) - PROJET GESTION MAGASIN
# =============================================================================
# Ce script installe Git, Python, PostgreSQL et pgAdmin via winget.
# Exécutez dans un terminal PowerShell en tant qu'Administrateur.
# =============================================================================

Write-Host "----------------------------------------------------" -ForegroundColor Cyan
Write-Host "🌟 PRÉPARATION DE L'ENVIRONNEMENT WINDOWS 🌟" -ForegroundColor Cyan
Write-Host "----------------------------------------------------" -ForegroundColor Cyan

# 1. Installation de Git
Write-Host "📦 Installation de Git..."
winget install --id Git.Git -e --source winget

# 2. Installation de Python 3
Write-Host "📦 Installation de Python 3..."
winget install --id Python.Python.3 -e --source winget

# 3. Installation de PostgreSQL (inclus pgAdmin)
Write-Host "📦 Installation de PostgreSQL & pgAdmin..."
winget install --id PostgreSQL.PostgreSQL -e --source winget

Write-Host "----------------------------------------------------" -ForegroundColor Green
Write-Host "✅ INSTALLATION SYSTÈME TERMINÉE !" -ForegroundColor Green
Write-Host "----------------------------------------------------"
Write-Host "Veuillez REDÉMARRER votre terminal pour appliquer les changements."
Write-Host "Ensuite, lancez 'setup_windows.bat' pour les dépendances Python."
Write-Host "----------------------------------------------------"
