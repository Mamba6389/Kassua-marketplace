# 📊 KASSUA - Marketplace Intelligent - Guide de Déploiement

## Changements effectués

### 1. **Migration de la base de données**
- ✅ Changement de **MySQL** vers **SQLite**
- ✅ SQLite est plus portable et compatible avec Streamlit Cloud
- ✅ Aucune dépendance externe requise (pymysql supprimé)
- ✅ Toutes les données sont conservées dans le fichier `kassua.db`

### 2. **Optimisation pour Streamlit**
- ✅ Remodelé le code pour une meilleure gestion de l'état de session
- ✅ Supprimé les dépendances MySQL complexes
- ✅ Ajout d'un fichier de configuration `.streamlit/config.toml`
- ✅ Code optimisé pour le déploiement cloud

### 3. **Migration des données**

#### Option A: Migrer les données depuis habou.sql
```bash
python migrate_sql_to_sqlite.py
```

Cela créera automatiquement `kassua.db` avec toutes les données du fichier `habou.sql`.

#### Option B: Démarrer avec une base de données vierge
Lancez simplement Streamlit - la base de données SQLite se créera automatiquement.

## 📥 Installation locale

### Prérequis
- Python 3.8+
- pip

### Étapes

1. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

2. **Migrer les données (optionnel)**
```bash
python migrate_sql_to_sqlite.py
```

3. **Lancer l'application**
```bash
streamlit run app.py
```

L'application sera accessible à: `http://localhost:8501`

## 🚀 Déploiement sur Streamlit Cloud

### Prérequis
- Compte GitHub
- Compte Streamlit Cloud

### Étapes

1. **Pousser le code sur GitHub**
```bash
git add .
git commit -m "Migrate to SQLite and optimize for Streamlit Cloud"
git push origin main
```

2. **Créer l'application sur Streamlit Cloud**
   - Allez sur [share.streamlit.io](https://share.streamlit.io)
   - Cliquez sur "New app"
   - Sélectionnez votre repository
   - Définissez le chemin: `app.py`
   - Cliquez sur "Deploy"

3. **Configuration (optionnel)**
   - Les secrets peuvent être gérés via l'interface Streamlit Cloud
   - Aucune configuration supplémentaire n'est requise pour SQLite

## 📊 Identifiants par défaut

### Admin
- **Mot de passe**: `kassuaTa@2025`

### Utilisateur test
- **Nom d'utilisateur**: `azerty`
- **Email**: `azerty@gmail.com`
- **Mot de passe**: (sera défini lors de l'inscription)

## 🗄️ Structure de la base de données

### Tables

#### `users`
- id (INTEGER PRIMARY KEY)
- username (VARCHAR UNIQUE)
- email (VARCHAR UNIQUE)
- password (VARCHAR)
- created_at (VARCHAR)
- reset_token (VARCHAR)
- reset_expires (VARCHAR)
- is_admin (BOOLEAN)

#### `products`
- id (INTEGER PRIMARY KEY)
- produit (VARCHAR)
- ville (VARCHAR)
- prix (VARCHAR)
- date (VARCHAR)
- categorie (VARCHAR)
- vendeur (VARCHAR)
- contact (VARCHAR)

#### `purchases`
- id (INTEGER PRIMARY KEY)
- produit (VARCHAR)
- prix (VARCHAR)
- vendeur (VARCHAR)
- contact (VARCHAR)
- categorie (VARCHAR)
- date_achat (VARCHAR)
- acheteur (VARCHAR)

#### `carts`
- id (INTEGER PRIMARY KEY)
- username (VARCHAR)
- produit (VARCHAR)
- prix (VARCHAR)
- vendeur (VARCHAR)
- contact (VARCHAR)
- categorie (VARCHAR)
- ville (VARCHAR)
- date (VARCHAR)
- quantity (INTEGER)

## 🔄 Fonctionnalités

### Pour les clients
- ✅ Parcourir les produits par catégorie
- ✅ Recherche et filtrage
- ✅ Ajouter au panier
- ✅ Gestion du panier
- ✅ Historique d'achats
- ✅ Profil utilisateur

### Pour l'admin
- ✅ Gestion des produits
- ✅ Gestion des utilisateurs
- ✅ Statistiques des ventes
- ✅ Tableau de bord complet

## 📱 Catégories de produits

1. 🥦 Fruits & Légumes
2. 🍗 Viandes & Poissons
3. 🥛 Produits Laitiers
4. 🍚 Épicerie
5. 🥐 Boulangerie
6. 🥤 Boissons

## 🐛 Dépannage

### Erreur: "Database is locked"
- Cela peut se produire lors de modifications simultanées
- SQLite gère généralement cela automatiquement

### Les données ne se chargent pas
- Vérifiez que `kassua.db` existe
- Exécutez `python migrate_sql_to_sqlite.py`

### Problème de port 8501
- Changez le port dans `.streamlit/config.toml`
- Ou utilisez: `streamlit run app.py --server.port 8502`

## 📝 Notes

- Les données sont sauvegardées en temps réel dans SQLite
- Les panier utilisateur sont persistants
- Les mots de passe sont hashés avec SHA-256
- Les tokens de réinitialisation expirent après 1 heure

## 📞 Support

Pour tout problème ou question, consultez la documentation Streamlit:
https://docs.streamlit.io

---

**Version**: 2.0 (SQLite + Streamlit optimisé)
**Date**: Février 2026
