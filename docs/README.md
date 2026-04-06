# Kassua - Marketplace (Streamlit)

Petite marketplace construite avec Streamlit. Cette version utilise SQLite (via SQLAlchemy) pour stocker utilisateurs, produits et achats.

## Pré-requis
- Python 3.10+
- pip

## Installation

```bash
pip install -r requirements.txt
```

## Exécution

Lancer l'application en local :

```bash
streamlit run app.py
```

# Kassua — Marketplace (Streamlit)

Ce dépôt contient une petite marketplace construite avec Streamlit. L'application principale est [app.py](app.py) et utilise SQLAlchemy pour persister utilisateurs, produits, achats. Par défaut l'application tente d'utiliser une base MySQL nommée `habou` (créée automatiquement si nécessaire) — voir configuration ci‑dessous.

**Important :** ce README décrit la version actuelle du projet (migration depuis JSON vers MySQL, paniers par utilisateur en mémoire et fusion du panier anonyme à la connexion).

## Pré-requis
- Python 3.10 ou supérieur
- pip
- Serveur MySQL (par exemple XAMPP/MariaDB sur Windows)

## Installation
Depuis la racine du projet :

```bash
pip install -r requirements.txt
```

## Configuration (MySQL)
L'application lit les paramètres de connexion MySQL depuis les variables d'environnement suivantes (valeurs par défaut adaptées à une installation XAMPP locale) :

- `DB_USER` (default: `root`)
- `DB_PASSWORD` (default: empty)
- `DB_HOST` (default: `127.0.0.1`)
- `DB_PORT` (default: `3306`)
- `DB_NAME` (default: `habou`)

Exemple (PowerShell) :

```powershell
$env:DB_USER = 'root'
$env:DB_PASSWORD = ''
$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '3306'
$env:DB_NAME = 'habou'
```

Au démarrage, l'application crée la base `habou` si elle n'existe pas, puis utilise SQLAlchemy (`mysql+pymysql`) pour créer les tables nécessaires.

## Migration JSON → Base
Si vous aviez des données dans `users.json`, `p.json` (produits) ou `purchases.json`, l'application tente automatiquement de migrer ces fichiers vers la base de données lors du premier lancement (si les tables sont vides). Les fichiers de backup sont présents dans le dossier `backups/`.

## Fonctionnalités importantes
- Fichier principal : [app.py](app.py)
- Dépendances : [requirements.txt](requirements.txt)
- Fichiers JSON initiaux : [users.json](users.json), [p.json](p.json), [purchases.json](purchases.json)

- Paniers : l'application gère des paniers par utilisateur en mémoire (`st.session_state['user_carts']`).
	- Si un visiteur anonyme ajoute des articles, ils vont dans un panier de session temporaire.
	- À la connexion / inscription, le panier anonyme est fusionné automatiquement dans le panier de l'utilisateur connecté.
	- La page "Mon Panier" affiche le panier réel de l'utilisateur connecté et propose des actions (vider, supprimer article, passer au paiement simulé).

- Base par défaut : MySQL `habou` (créée automatiquement). Si vous ne souhaitez pas MySQL, vous pouvez adapter `app.py` pour revenir à SQLite.

## Lancer l'application

```bash
streamlit run app.py
```

Puis ouvrez l'URL fournie par Streamlit (généralement http://localhost:8501).

## Exécution et test rapide
- Assurez-vous que MySQL est démarré (XAMPP Control Panel).
- Installez les dépendances, puis lancez `streamlit run app.py`.
- Connectez-vous / inscrivez-vous depuis la sidebar pour voir le comportement du panier utilisateur (la fusion du panier anonyme s'effectue automatiquement).

## Persistance des paniers (optionnel)
Actuellement les paniers sont en mémoire par utilisateur (session). Si vous souhaitez que les paniers persistent entre redémarrages, je peux :

1. Ajouter une table `carts` en base MySQL et sauvegarder/charger les paniers automatiquement, ou
2. Enregistrer les paniers dans un fichier JSON par utilisateur.

Dites-moi quelle option vous préférez et je l'implémente.

## Fichiers utiles
- [app.py](app.py) — logique principale (marketplace, panier, migrations JSON→DB)
- [requirements.txt](requirements.txt) — dépendances (inclut `PyMySQL`)
- `users.json`, `p.json`, `purchases.json` — fichiers JSON sources (présents si vous aviez des données locales)

## Sécurité & production
- Ne laissez pas de mot de passe d'admin codé en dur en production.
- Utilisez TLS pour vos connexions et un stockage sécurisé des mots de passe (avec salage).

---

Si vous voulez, je peux maintenant :

- Lancer rapidement une vérification locale (installer dépendances + démarrer l'app). 
- Ou ajouter la persistance des paniers en base MySQL.

Indiquez ce que vous préférez.
