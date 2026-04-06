# Kassua Marketplace

## Structure du projet

- `src/` : Code source Python
  - `app.py` : Application principale Streamlit
  - `streamlit_app.py` : Point d'entrée Streamlit
  - `kassua.db` : Base de données SQLite

- `docs/` : Documentation
  - `README.md` : Documentation principale
  - `QUICKSTART.md` : Guide de démarrage rapide
  - `DEPLOYMENT.md` : Guide de déploiement

- `scripts/` : Scripts utilitaires
  - `check_deployment.py` : Vérification du déploiement
  - `migrate_sql_to_sqlite.py` : Migration vers SQLite
  - `run.bat` : Script de lancement Windows
  - `run_li.sh` : Script de lancement Linux

- `sql/` : Fichiers SQL
  - `habou.sql` : Schéma de base de données

- `config/` : Configuration
  - `.streamlit/` : Configuration Streamlit

- `requirements/` : Dépendances
  - `requirements.txt` : Dépendances principales
  - `requirements-dev.txt` : Dépendances de développement

- `backups/` : Sauvegardes des données JSON

- `.devcontainer/` : Configuration Dev Container
- `.git/` : Contrôle de version
- `.gitignore` : Fichiers ignorés par Git