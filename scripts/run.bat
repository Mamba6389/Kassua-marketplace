@echo off
REM Script de démarrage rapide pour KASSUA sur Streamlit (Windows)

echo Verification de Python...
python --version

echo.
echo Packages en installation...
pip install -r requirements.txt

echo.
echo Verification du deploiement...
python check_deployment.py

echo.
echo Lancement de l'application KASSUA...
streamlit run app.py
