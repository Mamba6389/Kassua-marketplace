#!/bin/bash
# Script de démarrage rapide pour KASSUA sur Streamlit

# Vérifier Python
python --version

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Vérifier le déploiement
echo ""
echo "🔍 Vérification du déploiement..."
python check_deployment.py

# Lancer l'application
echo ""
echo "🚀 Lancement de l'application KASSUA..."
streamlit run app.py
