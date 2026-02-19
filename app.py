
# app.py - KASSUA Marketplace (SQLite + Streamlit)
import streamlit as st
import json
import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import random
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import secrets

# Configuration de la page
st.set_page_config(
    page_title="Kassua - Marketplace ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("📊 KASSUA - Marketplace ")

# Données de catégories (similaire à ton fichier)
CATEGORIES = {
    "fruits_legumes": {
        "name": "🥦 Fruits & Légumes",
        "emoji": "🥦",
        "products": ["pomme", "banane", "orange", "tomate", "oignon", "carotte", "salade","raisin","ananas","poire", "choux", "pastèque", "aubergine", "concombre", "poivron", "piment", "pomme de terre", "haricot vert", "tchappata et guisma"]
    },
    "viandes_poissons": {
        "name": "🍗 Viandes & Poissons",
        "emoji": "🍗",
        "products": ["poulet", "boeuf", "poisson", "viande hachée", "pilon", "pintade", "dinde"]
    },
    "produits_laitiers": {
        "name": "🥛 Produits Laitiers",
        "emoji": "🥛",
        "products": ["lait", "fromage", "yaourt", "beurre", "crème"]
    },
    "epicerie": {
        "name": "🍚 Épicerie",
        "emoji": "🍚",
        "products": ["sel", "poivre", "piment sec", "percil et céleri", "soumbala", "yazi", "ail", "canelle", "clou de girofle"]
    },
    "boulangerie": {
        "name": "🥐 Boulangerie",
        "emoji": "🥐",
        "products": ["pain", "croissant", "gâteau", "cake"]
    },
    "boissons": {
        "name": "🥤 Boissons",
        "emoji": "🥤",
        "products": ["eau", "jus", "boisson énergissante", "jus naturel"]
    }
}

# Emojis pour produits
PRODUCT_EMOJIS = {
    'pomme de terre':'🥔','percil et céleri': '🍀', 'tomate': '🍅', 'oignon': '🧅', 'pomme': '🍎', 
    'ananas':'🍍', 'raisin':'🍇', 'poire':'🍐', 'choux':'🥦', 
    'pastèque':'🍉', 'aubergine':'🍆', 'concombre':'🥒', 'poivron':'🫑',
      'piment':'🌶️',  'haricot vert':'🫛',
     'tchappata et guisma':'🌿',
    'banane': '🍌', 'orange': '🍊', 'viande': '🍖', 'poisson': '🐟',
    'lait': '🥛', 'fromage': '🧀', 'gâteau': '🎂', 'soumbala': '🧆',
    'yazi': '', 'ail': '🧄', 'poulet': '🐔', 'boeuf': '🥩',
    'carotte': '🥕', 'salade': '🥬', 'viande hachée': '🥓', 
    'yaourt': '🥣', 'beurre': '🧈', 'crème': '🍦', 'canelle': '🪵',
    'jus naturel': '🍹','clou de girofle': '🍂', 'croissant': '🥐', 'pain': '🥖',
    'cake': '🥮', 'eau': '💧', 'jus': '🧃', 'boisson énergissante': '⚡',
     'sel':'🧂', 'poivre':'⚫', 'pilon':'🍗', 'pintade':'🦚',
      'dinde':'🦃'
}  

# Initialisation de l'état de session (valeurs par défaut)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'products' not in st.session_state:
    st.session_state.products = []

# Handle query param from badge link to open cart
try:
    params = st.query_params
    if params.get('open_cart'):
        st.session_state.page = 'cart'
        # clear query params to avoid loops
        try:
            st.set_query_params()
        except Exception:
            pass
        # rerun to apply the page change immediately
        try:
            st.experimental_rerun()
        except Exception:
            pass
except Exception:
    pass

# --- Database (SQLite via SQLAlchemy) ---
# Using SQLite for portability and Streamlit Cloud compatibility
DB_PATH = "kassua.db"

# Create SQLite engine (creates file if not exists)
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    created_at = Column(String)
    reset_token = Column(String, nullable=True)
    reset_expires = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    produit = Column(String, nullable=False)
    ville = Column(String, nullable=True)
    prix = Column(String, nullable=True)
    date = Column(String, nullable=True)
    categorie = Column(String, nullable=True)
    vendeur = Column(String, nullable=True)
    contact = Column(String, nullable=True)


class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True, index=True)
    produit = Column(String, nullable=False)
    prix = Column(String, nullable=True)
    vendeur = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    categorie = Column(String, nullable=True)
    date_achat = Column(String, nullable=True)
    acheteur = Column(String, nullable=True)


class Cart(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True)
    produit = Column(String, nullable=False)
    prix = Column(String, nullable=True)
    vendeur = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    categorie = Column(String, nullable=True)
    ville = Column(String, nullable=True)
    date = Column(String, nullable=True)
    quantity = Column(Integer, default=1)


def init_db():
    """Create DB tables if not present."""
    Base.metadata.create_all(bind=engine)


def migrate_json_to_db():
    """Migrate existing JSON files (users, products, purchases) into the SQLite DB.
    This is idempotent: it only writes data if the corresponding DB table is empty and
    a JSON file exists.
    """
    # Users
    try:
        db_users = load_users()
        if os.path.exists('users.json'):
            with open('users.json', 'r', encoding='utf-8') as f:
                try:
                    j_users = json.load(f)
                except Exception:
                    j_users = []
            if j_users and not db_users:
                save_users(j_users)
    except Exception:
        pass

    # Products
    try:
        db_products = load_products()
        if os.path.exists('p.json'):
            with open('p.json', 'r', encoding='utf-8') as f:
                try:
                    j_products = json.load(f)
                except Exception:
                    j_products = []
            if j_products and not db_products:
                save_products_to_db(j_products)
    except Exception:
        pass

    # Purchases
    try:
        db_purchases = load_purchases()
        if os.path.exists('purchases.json'):
            with open('purchases.json', 'r', encoding='utf-8') as f:
                try:
                    j_purchases = json.load(f)
                except Exception:
                    j_purchases = []
            if j_purchases and not db_purchases:
                save_purchases(j_purchases)
    # Note: carts do not have a JSON source by default. We keep carts in DB only.
    except Exception:
        pass


def load_purchases():
    try:
        db = SessionLocal()
        rows = db.query(Purchase).all()
        return [
            {k: getattr(r, k) for k in ['produit', 'prix', 'vendeur', 'contact', 'categorie', 'date_achat', 'acheteur']}
            for r in rows
        ]
    except SQLAlchemyError:
        return []
    finally:
        db.close()


def save_purchases(purchases):
    # overwrite purchases table for simplicity
    try:
        db = SessionLocal()
        db.query(Purchase).delete()
        for p in purchases:
            row = Purchase(
                produit=p.get('produit'),
                prix=str(p.get('prix', '')),
                vendeur=p.get('vendeur'),
                contact=p.get('contact'),
                categorie=p.get('categorie'),
                date_achat=p.get('date_achat') or p.get('date'),
                acheteur=p.get('acheteur')
            )
            db.add(row)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
    finally:
        db.close()


def load_users():
    try:
        db = SessionLocal()
        rows = db.query(User).all()
        return [
            {k: getattr(r, k) for k in ['username', 'email', 'password', 'created_at', 'reset_token', 'reset_expires', 'is_admin']}
            for r in rows
        ]
    except SQLAlchemyError:
        return []
    finally:
        db.close()


def save_users(users):
    # overwrite users table for simplicity — for small demo apps this is acceptable
    try:
        db = SessionLocal()
        db.query(User).delete()
        for u in users:
            user = User(
                username=u.get('username'),
                email=u.get('email'),
                password=u.get('password'),
                created_at=u.get('created_at'),
                reset_token=u.get('reset_token'),
                reset_expires=u.get('reset_expires'),
                is_admin=u.get('is_admin', False)
            )
            db.add(user)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
    finally:
        db.close()


def load_products():
    try:
        db = SessionLocal()
        rows = db.query(Product).all()
        return [
            {k: getattr(r, k) for k in ['produit', 'ville', 'prix', 'date', 'categorie', 'vendeur', 'contact']}
            for r in rows
        ]
    except SQLAlchemyError:
        return []
    finally:
        db.close()


def save_products_to_db(products):
    try:
        db = SessionLocal()
        db.query(Product).delete()
        for p in products:
            row = Product(
                produit=p.get('produit'),
                ville=p.get('ville'),
                prix=str(p.get('prix', '')),
                date=p.get('date'),
                categorie=p.get('categorie'),
                vendeur=p.get('vendeur'),
                contact=p.get('contact')
            )
            db.add(row)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
    finally:
        db.close()

# Provide backward-compatible function name used elsewhere
def save_products():
    # Try saving to the SQLite DB, fall back to JSON file if DB write fails.
    products = st.session_state.get('products', [])
    try:
        save_products_to_db(products)
    except Exception:
        try:
            with open("p.json", "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
        except Exception:
            # last-resort: ignore write errors to avoid crashing the app at runtime
            pass


# After models and DB helpers are defined, ensure DB exists and migrate JSON data
try:
    init_db()
    migrate_json_to_db()
    # load into session state if empty
    if not st.session_state.get('products'):
        st.session_state.products = load_products()
    if not st.session_state.get('users'):
        st.session_state.users = load_users()
    if not st.session_state.get('purchases'):
        st.session_state.purchases = load_purchases()
    # load carts from DB into session_state.user_carts
    try:
        def load_carts_from_db():
            try:
                db = SessionLocal()
                rows = db.query(Cart).all()
                carts = {}
                for r in rows:
                    user = r.username
                    item = {
                        'produit': getattr(r, 'produit'),
                        'prix': getattr(r, 'prix'),
                        'vendeur': getattr(r, 'vendeur'),
                        'contact': getattr(r, 'contact'),
                        'categorie': getattr(r, 'categorie'),
                        'ville': getattr(r, 'ville'),
                        'date': getattr(r, 'date'),
                        'quantity': getattr(r, 'quantity') or 1
                    }
                    carts.setdefault(user, []).append(item)
                return carts
            except SQLAlchemyError:
                return {}
            finally:
                try:
                    db.close()
                except Exception:
                    pass

        st.session_state.user_carts = load_carts_from_db()
    except Exception:
        # if anything goes wrong, ensure a dict exists
        if 'user_carts' not in st.session_state:
            st.session_state.user_carts = {}
except Exception:
    # in case anything fails during import-time DB setup, fall back to JSON-based behavior
    if not st.session_state.get('products'):
        if os.path.exists('p.json'):
            try:
                with open('p.json', 'r', encoding='utf-8') as f:
                    st.session_state.products = json.load(f)
            except Exception:
                st.session_state.products = []
    if not st.session_state.get('users'):
        if os.path.exists('users.json'):
            try:
                with open('users.json', 'r', encoding='utf-8') as f:
                    st.session_state.users = json.load(f)
            except Exception:
                st.session_state.users = []
    if not st.session_state.get('purchases'):
        if os.path.exists('purchases.json'):
            try:
                with open('purchases.json', 'r', encoding='utf-8') as f:
                    st.session_state.purchases = json.load(f)
            except Exception:
                st.session_state.purchases = []
    # ensure user_carts exists when DB unavailable
    if 'user_carts' not in st.session_state:
        st.session_state.user_carts = {}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

if 'users' not in st.session_state:
    st.session_state.users = load_users()

if 'purchases' not in st.session_state:
    st.session_state.purchases = load_purchases()
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Mini-panier
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Paniers par utilisateur (username -> list of items)
if 'user_carts' not in st.session_state:
    st.session_state.user_carts = {}

def add_to_cart_item(item):
    """Ajoute un item au panier de l'utilisateur connecté si présent,
    sinon dans le panier de session anonyme."""
    user = st.session_state.get('current_user')
    if user:
        if user not in st.session_state.user_carts:
            st.session_state.user_carts[user] = []
        # merge: if same produit+vendeur exists, increase quantity
        merged = False
        for it in st.session_state.user_carts[user]:
            if (it.get('produit') == item.get('produit') and it.get('vendeur') == item.get('vendeur')):
                # increment quantity
                try:
                    it['quantity'] = int(it.get('quantity', 1)) + int(item.get('quantity', 1))
                except Exception:
                    it['quantity'] = int(item.get('quantity', 1) or 1)
                merged = True
                break
        if not merged:
            # ensure quantity present
            if 'quantity' not in item:
                item['quantity'] = 1
            st.session_state.user_carts[user].append(item)
        # persist user's cart to DB
        try:
            db = SessionLocal()
            # delete existing cart rows for user, then reinsert
            db.query(Cart).filter(Cart.username == user).delete()
            for it in st.session_state.user_carts[user]:
                row = Cart(
                    username=user,
                    produit=it.get('produit'),
                    prix=str(it.get('prix','')),
                    vendeur=it.get('vendeur'),
                    contact=it.get('contact'),
                    categorie=it.get('categorie'),
                    ville=it.get('ville'),
                    date=it.get('date'),
                    quantity=int(it.get('quantity', 1))
                )
                db.add(row)
            db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
        finally:
            try:
                db.close()
            except Exception:
                pass
    else:
        st.session_state.cart.append(item)


def render_cart_badge():
    """Affiche un petit bouton/cart-badge aligné à droite avec le nombre d'articles.
    Utilise un vrai `st.button` pour être natif Streamlit et fiable.
    Quand on clique, bascule `st.session_state.page` sur 'cart' et rerun.
    """
    try:
        user = st.session_state.get('current_user')
        if user:
            count = len(st.session_state.user_carts.get(user, []))
        else:
            count = len(st.session_state.get('cart', []))

        if count and count > 0:
            # placer le bouton à droite en utilisant des colonnes
            cols = st.columns([9, 1])
            with cols[0]:
                st.write("")
            with cols[1]:
                label = f"🛒 {count}"
                # si cliqué, basculer l'affichage de l'aperçu du panier
                if st.button(label, key="cart_badge_button"):
                    st.session_state.show_cart_preview = not st.session_state.get('show_cart_preview', False)
                    try:
                        st.experimental_rerun()
                    except Exception:
                        pass
    except Exception:
        pass

# --- Réinitialisation de mot de passe ---
def generate_reset_token_for_email(email: str):
    users = st.session_state.get('users', [])
    user = next((u for u in users if u.get('email') == email), None)
    if not user:
        return None
    token = secrets.token_urlsafe(16)
    user['reset_token'] = token
    user['reset_expires'] = (datetime.now() + timedelta(hours=1)).isoformat()
    save_users(users)
    return token


def render_cart_preview():
    """Affiche un petit panneau d'aperçu du panier (liste courte) permettant
    de supprimer des éléments ou d'ouvrir la page complète du panier."""
    try:
        container = st.container()
        with container:
            st.markdown("**Aperçu du panier**")
            current_user = st.session_state.get('current_user')
            if current_user:
                cart = st.session_state.user_carts.get(current_user, [])
            else:
                cart = st.session_state.get('cart', [])

            if not cart:
                st.info("Votre panier est vide.")
                if st.button("Voir le panier", key="preview_view_cart"):
                    st.session_state.page = 'cart'
                    try:
                        st.experimental_rerun()
                    except Exception:
                        pass
                if st.button("Fermer", key="preview_close"):
                    st.session_state.show_cart_preview = False
                    try:
                        st.experimental_rerun()
                    except Exception:
                        pass
                return

            total_preview = 0.0
            for i, item in enumerate(cart):
                cols = st.columns([3,1,1])
                with cols[0]:
                    st.write(f"{item.get('produit')} — {item.get('vendeur','—')}")
                with cols[1]:
                    try:
                        price_val = float(item.get('prix', 0))
                    except Exception:
                        price_val = 0.0
                    st.write(f"{price_val:.0f} FCFA")
                with cols[2]:
                    if st.button("Supprimer", key=f"preview_remove_{i}"):
                        # remove item and persist if necessary
                        if current_user:
                            try:
                                st.session_state.user_carts[current_user].pop(i)
                                db = SessionLocal()
                                db.query(Cart).filter(Cart.username == current_user).delete()
                                for it in st.session_state.user_carts[current_user]:
                                    row = Cart(
                                        username=current_user,
                                        produit=it.get('produit'),
                                        prix=str(it.get('prix','')),
                                        vendeur=it.get('vendeur'),
                                        contact=it.get('contact'),
                                        categorie=it.get('categorie'),
                                        ville=it.get('ville'),
                                        date=it.get('date'),
                                        quantity=int(it.get('quantity', 1))
                                    )
                                    db.add(row)
                                db.commit()
                            except Exception:
                                try:
                                    db.rollback()
                                except Exception:
                                    pass
                            finally:
                                try:
                                    db.close()
                                except Exception:
                                    pass
                        else:
                            try:
                                st.session_state.cart.pop(i)
                            except Exception:
                                pass
                        st.success("Article supprimé du panier.")
                        st.session_state.show_cart_preview = True
                        try:
                            st.experimental_rerun()
                        except Exception:
                            pass
                try:
                    total_preview += float(item.get('prix', 0)) * int(item.get('quantity', 1))
                except Exception:
                    try:
                        total_preview += float(item.get('prix', 0))
                    except Exception:
                        pass

            st.markdown(f"**Total (aperçu)**: {total_preview:.0f} FCFA")
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("Voir le panier", key="preview_view_cart2"):
                    st.session_state.page = 'cart'
                    try:
                        st.experimental_rerun()
                    except Exception:
                        pass
            with col2:
                if st.button("Fermer", key="preview_close2"):
                    st.session_state.show_cart_preview = False
                    try:
                        st.experimental_rerun()
                    except Exception:
                        pass
    except Exception:
        pass

def verify_reset_token(email: str, token: str) -> bool:
    user = next((u for u in st.session_state.get('users', []) if u.get('email') == email and u.get('reset_token') == token), None)
    if not user:
        return False
    expires = user.get('reset_expires')
    if not expires:
        return False
    try:
        exp_dt = datetime.fromisoformat(expires)
    except Exception:
        return False
    return exp_dt >= datetime.now()

def clear_reset_token_for_user(user: dict):
    if 'reset_token' in user:
        del user['reset_token']
    if 'reset_expires' in user:
        del user['reset_expires']
    save_users(st.session_state.get('users', []))

# Fonctions utilitaires
def generate_sample_data():
    """Génère des données d'exemple"""
    products = []
    villes = ["Niamey"]
    dates = ["2024-11-01"]
   
    # Générer 2-3 produits par catégorie
    for cat_id, cat_info in CATEGORIES.items():
        for product_name in cat_info["products"][:3]:
            product = {
                "produit": product_name.capitalize(),
                "ville": random.choice(villes),
                "prix": str(random.randint(500, 10000)),
                "date": random.choice(dates),
                "categorie": cat_id,
                "vendeur": f"Vendeur_{random.randint(1, 5)}",
                "contact": f"+225{random.randint(20000000, 99999999)}"
            }
            products.append(product)
   
    return products


def get_emoji(product_name):
    """Retourne l'emoji correspondant au produit"""
    for key, emoji in PRODUCT_EMOJIS.items():
        if key in product_name.lower():
            return emoji
    return "📦"

def contact_link(contact: str) -> str:
    """Retourne un lien cliquable pour un contact.
    Priorise WhatsApp pour les numéros (via wa.me). Sinon utilise mailto: pour les emails.
    Retourne '#' si aucun lien valide n'est trouvé.
    """
    if not contact:
        return "#"
    s = str(contact).strip()
    import re

    # If there's a valid email, prefer mailto for email-only values or as fallback
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}", s)
    if "@" in s and email_match:
        return f"mailto:{email_match.group(0)}"

    # Extract digits and optional leading +
    digits = ''.join(c for c in s if c.isdigit() or c == '+')
    if digits:
        num = digits
        # Normalize international prefix
        if num.startswith('00'):
            num = num[2:]
        if num.startswith('+'):
            num = num[1:]
        # Construct WhatsApp link (works for WhatsApp app and web)
        return f"https://wa.me/{num}"

    # Fallback to any email found in the text
    if email_match:
        return f"mailto:{email_match.group(0)}"

    return "#"


def recommend_for_user(username: str, limit: int = 5):
    """Recommandations simples basées sur les achats de l'utilisateur.
    Retourne une liste de produit names.
    """
    if not username:
        return []
    purchases = st.session_state.get('purchases', [])
    user_p = [p for p in purchases if p.get('acheteur') == username]
    if not user_p:
        return []
    # compter catégories achetées
    from collections import Counter
    cat_counts = Counter([p.get('categorie') for p in user_p if p.get('categorie')])
    # prioriser produits dans les catégories les plus achetées
    cats_sorted = [c for c,_ in cat_counts.most_common()]
    recs = []
    for cat in cats_sorted:
        # trouver produits de cette catégorie
        for prod in st.session_state.get('products', []):
            if prod.get('categorie') == cat and prod.get('produit') not in recs:
                recs.append(prod.get('produit'))
                if len(recs) >= limit:
                    return recs
    # fallback: produits les plus achetés globalement
    prod_counts = Counter([p.get('produit') for p in purchases if p.get('produit')])
    for prod, _ in prod_counts.most_common():
        if prod not in recs:
            recs.append(prod)
            if len(recs) >= limit:
                break
    return recs


def get_purchase_counts():
    from collections import Counter
    purchases = st.session_state.get('purchases', [])
    return Counter([p.get('produit') for p in purchases if p.get('produit')])


def get_global_top_products(n=5):
    counts = get_purchase_counts()
    return [p for p,_ in counts.most_common(n)]


def get_user_recommendations(username, n=5):
    purchases = st.session_state.get('purchases', [])
    user_purchases = [p for p in purchases if p.get('acheteur') == username]
    if not user_purchases:
        return get_global_top_products(n)

    # catégories favorites de l'utilisateur
    from collections import Counter
    cat_counts = Counter([p.get('categorie') for p in user_purchases if p.get('categorie')])
    favorite_cats = [c for c,_ in cat_counts.most_common()]

    # produits déjà achetés
    bought = set(p.get('produit') for p in user_purchases)

    # recommander produits dans ces catégories non achetés par user, ordonnés par popularité
    prod_pop = get_purchase_counts()
    recs = []
    for cat in favorite_cats:
        for prod in st.session_state.get('products', []):
            if prod.get('categorie') == cat and prod.get('produit') not in bought:
                recs.append((prod.get('produit'), prod_pop.get(prod.get('produit'), 0)))

    # fallback: global top products
    if not recs:
        return get_global_top_products(n)

    # trier et retourner noms uniques
    recs_sorted = [p for p,_ in sorted(recs, key=lambda x: x[1], reverse=True)]
    seen = []
    for r in recs_sorted:
        if r not in seen:
            seen.append(r)
    return seen[:n]

# 🌐 **PAGES DE L'APPLICATION**

# Page d'accueil / Connexion
def login_page():
    st.markdown("""
    <style>
    .big-font {
        font-size: 50px !important;
        text-align: center;
    }
    .center {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="center">', unsafe_allow_html=True)
        st.markdown('<p class="big-font">📊</p>', unsafe_allow_html=True)
        st.markdown("# KASSUA")
        st.markdown("### Marketplace Intelligent")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # Boutons de connexion
        col_btn1, col_btn2, col_btn3 = st.columns([1,1,1])

        with col_btn1:
            if st.button("👨‍💼 Administrateur", use_container_width=True, type="primary"):
                st.session_state.show_admin_login = True
                st.rerun()

        with col_btn2:
            if st.button("🧑‍🌾 Espace Client", use_container_width=True, type="secondary"):
                st.session_state.show_client_auth = True
                st.rerun()


        st.markdown("---")
        st.markdown("Votre plateforme de confiance pour les prix")

        # (Bouton 'Quitter' supprimé pour éviter fermeture intempestive)

    # --- Admin login form (simple password) ---
    if 'show_admin_login' in st.session_state and st.session_state.get('show_admin_login'):
        st.subheader("Connexion Administrateur")
        adm_pwd = st.text_input("Mot de passe administrateur", type="password")
        if st.button("Se connecter en tant qu'administrateur"):
            if adm_pwd == "kassuaTa@2025":
                st.session_state.logged_in = True
                st.session_state.user_type = 'admin'
                # clear the flag
                st.session_state.show_admin_login = False
                st.rerun()
            else:
                st.error("Mot de passe administrateur incorrect.")

    # --- Client auth (login / register) ---
    if 'show_client_auth' in st.session_state and st.session_state.get('show_client_auth'):
        st.subheader("Espace Client - Connexion / Inscription")
        tabs = st.tabs(["Connexion", "Inscription", "Réinitialiser"])

        # Connexion
        with tabs[0]:
            login_input = st.text_input("Nom d'utilisateur ou Email", key="login_user")
            login_pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
            if st.button("Se connecter", key="login_btn"):
                hashed = hash_password(login_pwd)
                matched = next(
                    (
                        u for u in st.session_state.users
                        if (u.get('username') == login_input or u.get('email') == login_input) and u.get('password') == hashed
                    ),
                    None
                )
                if matched:
                    st.session_state.logged_in = True
                    st.session_state.user_type = 'buyer'
                    # store canonical username as current_user
                    st.session_state.current_user = matched.get('username') or matched.get('email')
                    # merge any anonymous session cart into the user's cart
                    anon_cart = st.session_state.get('cart', [])
                    if anon_cart:
                        user = st.session_state.current_user
                        if user not in st.session_state.user_carts:
                            st.session_state.user_carts[user] = []
                        st.session_state.user_carts[user].extend(anon_cart)
                        st.session_state.cart = []
                        # persist merged cart to DB
                        try:
                            db = SessionLocal()
                            db.query(Cart).filter(Cart.username == user).delete()
                            for it in st.session_state.user_carts[user]:
                                row = Cart(
                                    username=user,
                                    produit=it.get('produit'),
                                    prix=str(it.get('prix','')),
                                    vendeur=it.get('vendeur'),
                                    contact=it.get('contact'),
                                    categorie=it.get('categorie'),
                                    ville=it.get('ville'),
                                    date=it.get('date'),
                                    quantity=int(it.get('quantity', 1))
                                )
                                db.add(row)
                            db.commit()
                        except Exception:
                            try:
                                db.rollback()
                            except Exception:
                                pass
                        finally:
                            try:
                                db.close()
                            except Exception:
                                pass
                    st.session_state.show_client_auth = False
                    st.success(f"Bienvenue, {st.session_state.current_user} !")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects. Inscrivez-vous si vous n'avez pas de compte.")
            # Mot de passe oublié
            st.markdown("---")
            if st.checkbox("Mot de passe oublié ?"):
                email_for_reset = st.text_input("Entrez votre email pour réinitialiser le mot de passe", key="reset_email_input")
                if st.button("Envoyer la demande de réinitialisation", key="send_reset"):
                    if not email_for_reset:
                        st.error("Veuillez saisir votre email.")
                    else:
                        token = generate_reset_token_for_email(email_for_reset)
                        if token:
                            st.success("Demande enregistrée. Un lien de réinitialisation a été généré.")
                            st.info("Pour le moment, l'application affiche le token ci‑dessous (à remplacer par un envoi d'email en production).")
                            st.code(token)
                            st.markdown("Vous pouvez utiliser l'onglet 'Réinitialiser' pour renseigner votre email, coller ce token et définir un nouveau mot de passe.")
                        else:
                            st.error("Aucun compte trouvé pour cet email.")

        # Inscription
        with tabs[1]:
            reg_username = st.text_input("Nom utilisateur", key="reg_user")
            reg_email = st.text_input("Email", key="reg_email")
            reg_pwd = st.text_input("Mot de passe", type="password", key="reg_pwd")
            if st.button("S'inscrire", key="reg_btn"):
                if not reg_username or not reg_email or not reg_pwd:
                    st.error("Veuillez remplir tous les champs.")
                elif any(u['username'] == reg_username for u in st.session_state.users):
                    st.error("Ce nom d'utilisateur existe déjà.")
                else:
                    new_user = {
                        'username': reg_username,
                        'email': reg_email,
                        'password': hash_password(reg_pwd),
                        'created_at': str(datetime.now())
                    }
                    st.session_state.users.append(new_user)
                    save_users(st.session_state.users)
                    st.success("Inscription réussie. Vous pouvez maintenant vous connecter.")
                    # Auto-login to client area
                    st.session_state.logged_in = True
                    st.session_state.user_type = 'buyer'
                    st.session_state.current_user = reg_username
                    # merge any anonymous session cart into the new user's cart
                    anon_cart = st.session_state.get('cart', [])
                    if anon_cart:
                        if reg_username not in st.session_state.user_carts:
                            st.session_state.user_carts[reg_username] = []
                        st.session_state.user_carts[reg_username].extend(anon_cart)
                        st.session_state.cart = []
                        # persist merged cart to DB
                        try:
                            db = SessionLocal()
                            db.query(Cart).filter(Cart.username == reg_username).delete()
                            for it in st.session_state.user_carts[reg_username]:
                                row = Cart(
                                    username=reg_username,
                                    produit=it.get('produit'),
                                    prix=str(it.get('prix','')),
                                    vendeur=it.get('vendeur'),
                                    contact=it.get('contact'),
                                    categorie=it.get('categorie'),
                                    ville=it.get('ville'),
                                    date=it.get('date'),
                                    quantity=int(it.get('quantity', 1))
                                )
                                db.add(row)
                            db.commit()
                        except Exception:
                            try:
                                db.rollback()
                            except Exception:
                                pass
                        finally:
                            try:
                                db.close()
                            except Exception:
                                pass
                    st.session_state.show_client_auth = False
                    st.rerun()
        # Réinitialisation mot de passe (demande + confirmation)
        with tabs[2]:
            st.subheader("Réinitialiser le mot de passe")
            st.markdown("Entrez votre email, le token reçu, et choisissez un nouveau mot de passe.")
            reset_email = st.text_input("Email lié au compte", key="confirm_reset_email")
            reset_token = st.text_input("Token de réinitialisation", key="confirm_reset_token")
            new_pwd = st.text_input("Nouveau mot de passe", type="password", key="confirm_new_pwd")
            new_pwd2 = st.text_input("Confirmer le nouveau mot de passe", type="password", key="confirm_new_pwd2")
            if st.button("Réinitialiser le mot de passe", key="confirm_reset_btn"):
                if not reset_email or not reset_token or not new_pwd:
                    st.error("Veuillez remplir tous les champs.")
                elif new_pwd != new_pwd2:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    if verify_reset_token(reset_email, reset_token):
                        user = next((u for u in st.session_state.users if u.get('email') == reset_email and u.get('reset_token') == reset_token), None)
                        if user:
                            user['password'] = hash_password(new_pwd)
                            clear_reset_token_for_user(user)
                            save_users(st.session_state.users)
                            st.success("Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter.")
                        else:
                            st.error("Erreur: utilisateur introuvable.")
                    else:
                        st.error("Token invalide ou expiré. Veuillez redemander la réinitialisation.")

# Page du Marketplace (Client)
def marketplace_page():
    # afficher badge de panier (mis à jour dynamiquement)
    render_cart_badge()
    # si l'utilisateur a demandé l'aperçu, l'afficher
    try:
        if st.session_state.get('show_cart_preview'):
            render_cart_preview()
    except Exception:
        pass
    st.header("🛍️ Marketplace")
    # (Bouton 'Quitter' supprimé pour éviter fermeture intempestive)
   
    # Recommandations (personnalisées si utilisateur connecté, sinon top global)
    purchases = st.session_state.get('purchases', [])
    recs = []
    current_user = st.session_state.get('current_user')
    if current_user:
        recs = recommend_for_user(current_user, limit=5)
    if not recs and purchases:
        from collections import Counter
        prod_counts = Counter([p.get('produit') for p in purchases if p.get('produit')])
        recs = [p for p,_ in prod_counts.most_common(5)]

    if recs:
        with st.expander("💡 Recommandations pour vous"):
            cols = st.columns(len(recs))
            for i, rec in enumerate(recs):
                with cols[i]:
                    st.write(rec)
                    if st.button(f"Voir", key=f"rec_{i}"):
                        st.session_state.rec_query = rec
                        st.rerun()

    # Barre de recherche et filtres
    col1, col2 = st.columns([3, 1])
   
    with col1:
        # Si on vient d'une recommandation, appliquer la recherche
        if 'rec_query' in st.session_state:
            search_query = st.session_state.pop('rec_query')
        else:
            search_query = st.text_input("🔍 Rechercher produits, villes...", placeholder="Ex: pomme, Abidjan")
   
    with col2:
        selected_category = st.selectbox(
            "📁 Catégorie",
            ["Toutes"] + [cat_info["name"] for cat_info in CATEGORIES.values()]
        )
   
    # Boutons de catégorie rapide
    st.subheader("Catégories")
    category_cols = st.columns(len(CATEGORIES))
   
    for idx, (cat_id, cat_info) in enumerate(CATEGORIES.items()):
        with category_cols[idx]:
            if st.button(cat_info["name"], use_container_width=True):
                selected_category = cat_info["name"]
   
    # Filtrer les produits
    filtered_products = st.session_state.products
   
    if search_query:
        search_query = search_query.lower()
        filtered_products = [
            p for p in filtered_products
            if (search_query in p['produit'].lower() or
                search_query in p['ville'].lower())
        ]
   
    if selected_category != "Toutes":
        # Trouver l'ID de catégorie correspondant
        cat_id = next(
            (cid for cid, info in CATEGORIES.items()
             if info["name"] == selected_category),
            None
        )
        if cat_id:
            filtered_products = [
                p for p in filtered_products
                if p['categorie'] == cat_id
            ]
   
    # Afficher les produits
    if not filtered_products:
        st.warning("Aucun produit trouvé.")
    else:
        # Convertir en DataFrame pour meilleur affichage
        df = pd.DataFrame(filtered_products)
       
        # Ajouter la colonne emoji
        df['emoji'] = df['produit'].apply(get_emoji)
       
        # Afficher en grille
        cols_per_row = 3
        rows = [df.iloc[i:i+cols_per_row] for i in range(0, len(df), cols_per_row)]
       
        for row in rows:
            cols = st.columns(cols_per_row)
            for idx, (_, product) in enumerate(row.iterrows()):
                with cols[idx]:
                    # Carte produit
                    emoji = product['emoji']
                    with st.container():
                        st.markdown(f"""
                        <div style='
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            padding: 15px;
                            margin-bottom: 10px;
                            background-color: white;
                        '>
                            <div style='font-size: 40px; text-align: center;'>{emoji}</div>
                            <h3 style='text-align: center;'>{product['produit']}</h3>
                            <h2 style='color: #2E8B57; text-align: center;'>{product['prix']} FCFA</h2>
                            <p style='text-align: center;'>
                                📍 {product['ville']}<br>
                                📅 {product['date']}<br>
                                📁 {CATEGORIES[product['categorie']]['name']}<br>
                                
                            
                        </div>
                        """, unsafe_allow_html=True)
                       
                        # Bouton d'achat
                        # Générer une clé stable et unique pour chaque produit affiché
                        unique_key_source = f"{product.get('produit','')}-{product.get('vendeur','')}-{product.get('ville','')}-{product.get('prix','')}-{product.get('date','')}"
                        unique_key = hashlib.sha1(unique_key_source.encode('utf-8')).hexdigest()[:10]
                        # Ajouter au panier
                        if st.button("➕ Ajouter au panier", key=f"addcart_{unique_key}", use_container_width=True):
                            item = {
                                'produit': product['produit'],
                                'prix': product['prix'],
                                'vendeur': product.get('vendeur', '—'),
                                'contact': product.get('contact', '—'),
                                'categorie': product['categorie'],
                                'ville': product.get('ville','—'),
                                'date': product.get('date','')
                            }
                            add_to_cart_item(item)
                            st.success(f"Produit {product['produit']} ajouté au panier.")

                        # Acheter maintenant (checkout single item)
                        if st.button("🛒 Acheter Maintenant", key=f"buy_{unique_key}", use_container_width=True):
                            purchase = {
                                "produit": product['produit'],
                                "prix": product['prix'],
                                "vendeur": product.get('vendeur', '—'),
                                "contact": product.get('contact', '—'),
                                "categorie": product['categorie'],
                                "date_achat": str(datetime.now()),
                                "acheteur": st.session_state.get('current_user', 'Anonyme')
                            }
                            st.session_state.purchases.append(purchase)
                            save_purchases(st.session_state.purchases)
                            #afficher les informations de contact après l'achat                   
                            st.success(f"✅ Achat confirmé pour {product['produit']}!")
                            contact_info= product.get('contact', '_')
                            vendeur_info= product.get('vendeur', '_')

                            if contact_info != '_':
                                contact_url= contact_link(contact_info)

                                st.markdown("---")
                                st.markdown("###📞 Informations du vendeur")
                                st.markdown(f"**Vendeur :** {vendeur_info}  ")
                                
                                #Bouton pour ouvrir le chat avec le vendeur
                                if "wa.me" in contact_url or "whatsapp" in contact_url:
                                    st.markdown(f'<a href="{contact_url}" target="_blank" style="text-decoration: none;">'
                       f'<button style="background-color:#25D366;color:white;border:none;'
                       f'padding:10px 20px;border-radius:5px;cursor:pointer;margin-top:10px;">'
                       f'💬 Ouvrir WhatsApp avec le vendeur</button></a>',
                       unsafe_allow_html=True)
                                elif "mailto:" in contact_url:
                                    st.markdown(f'<a href="{contact_url}" target="_blank" style="text-decoration: none;">'
                                    f'<button style="background-color:#4285F4;color:white;border:none;'
                                    f'padding:10px 20px;border-radius:5px;cursor:pointer;margin-top:10px;">'
                                    f'📧 Contacter par email</button></a>',
                                                    unsafe_allow_html=True)
                                else:
                                    st.markdown(f"**Contactez le vendeur directement:** {contact_info}")
                            else:
                                st.warning("⚠️ Aucune information de contact disponible pour ce vendeur.")
        # Statistiques
        st.markdown("---")
        st.subheader("📈 Statistiques du marché")
       
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Produits disponibles", len(filtered_products))
        with col2:
            avg_price = df['prix'].astype(float).mean()
            st.metric("Prix moyen", f"{avg_price:.0f} FCFA")
        with col3:
            cities = df['ville'].nunique()
            st.metric("Villes", cities)

# Tableau de bord vendeur
def seller_dashboard():
    st.header("👨‍💼 Tableau de Bord Vendeur")
   
    # Statistiques
    col1, col2, col3, col4 = st.columns(4)
   
    with col1:
        st.metric("📦 Produits", len(st.session_state.products))
   
    with col2:
        total_revenue = sum(float(p['prix']) for p in st.session_state.products)
        st.metric("💰 Chiffre", f"{total_revenue:.0f} FCFA")
   
    with col3:
        st.metric("🏪 Ventes", "0")
   
    with col4:
        st.metric("⭐ Rating", "4.8")
   
    # Actions rapides
    st.subheader("Actions rapides")
    action_cols = st.columns(4)
   
    with action_cols[0]:
        if st.button("➕ Ajouter Produit", use_container_width=True):
            st.session_state.show_add_product = True
   
    with action_cols[1]:
        if st.button("📊 Mes Produits", use_container_width=True):
            st.session_state.show_my_products = True
   
    with action_cols[2]:
        if st.button("📈 Statistiques", use_container_width=True):
            st.session_state.show_stats = True
   
    with action_cols[3]:
        if st.button("⚙️ Paramètres", use_container_width=True):
            st.session_state.show_settings = True
   
    # Gestion des sous-pages vendeur
    if 'show_add_product' in st.session_state and st.session_state.show_add_product:
        add_product_page()
   
    elif 'show_my_products' in st.session_state and st.session_state.show_my_products:
        my_products_page()
   
    elif 'show_stats' in st.session_state and st.session_state.show_stats:
        seller_stats_page()
   
    else:
        # Vue par défaut : Derniers produits
        st.subheader("📋 Derniers produits ajoutés")
       
        if st.session_state.products:
            recent_products = pd.DataFrame(st.session_state.products[-5:])
            st.dataframe(
                recent_products[['produit', 'prix', 'ville', 'date', 'categorie']],
                column_config={
                    "produit": "Produit",
                    "prix": "Prix (FCFA)",
                    "ville": "Ville",
                    "date": "Date",
                    "categorie": "Catégorie"
                },
                hide_index=True
            )
        else:
            st.info("Aucun produit ajouté. Commencez par ajouter votre premier produit!")

# Page d'ajout de produit
def add_product_page():
    st.subheader("➕ Ajouter un nouveau produit")
   
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
       
        with col1:
            product_name = st.text_input("📦 Nom du produit")
            city = st.text_input("🏙️ Ville")
       
        with col2:
            price = st.number_input("💰 Prix (FCFA)", min_value=0, step=100)
            date = st.date_input("📅 Date")
       
        # Sélection de catégorie
        category_options = {info["name"]: cid for cid, info in CATEGORIES.items()}
        category_name = st.selectbox("📁 Catégorie", list(category_options.keys()))
        category_id = category_options[category_name]
       
        vendeur = st.text_input("👤 Nom du vendeur", value="Vendeur_1")
        contact = st.text_input("📞 Contact du vendeur (téléphone/email)", value="+22500000000")
       
        submitted = st.form_submit_button("✅ Publier le produit", type="primary")
       
        if submitted:
            if not all([product_name, city, price, vendeur]):
                st.error("Veuillez remplir tous les champs obligatoires.")
            else:
                new_product = {
                    "produit": product_name,
                    "ville": city,
                    "prix": str(price),
                    "date": str(date),
                    "categorie": category_id,
                    "vendeur": vendeur,
                    "contact": contact
                }
               
                st.session_state.products.append(new_product)
                save_products()
               
                st.success(f"Produit '{product_name}' ajouté avec succès!")
               
                # Option pour ajouter un autre produit
                if st.button("➕ Ajouter un autre produit"):
                    st.rerun()
                if st.button("📋 Retour au tableau de bord"):
                    st.session_state.show_add_product = False
                    st.rerun()

# Page des produits du vendeur
def my_products_page():
    st.subheader("📋 Mes produits")
   
    if st.session_state.products:
        df = pd.DataFrame(st.session_state.products)
       
        # Filtrer par vendeur (dans une vraie app, on filtrerait par utilisateur connecté)
        # Pour l'exemple, on montre tous les produits
       
        # Éditer/supprimer des produits
        for idx, product in enumerate(df.iterrows()):
            _, p = product
            col1, col2, col3 = st.columns([3, 1, 1])
           
            with col1:
                st.write(f"**{p['produit']}** - {p['prix']} FCFA - {p['ville']}")
           
            with col2:
                if st.button("✏️ Éditer", key=f"edit_{idx}"):
                    st.session_state.editing_product = idx
           
            with col3:
                if st.button("🗑️ Supprimer", key=f"delete_{idx}"):
                    st.session_state.products.pop(idx)
                    save_products()
                    st.rerun()
       
        # Statistiques de mes produits
        st.markdown("---")
        st.subheader("Mes statistiques")
       
        if len(df) > 0:
            col1, col2, col3 = st.columns(3)
           
            with col1:
                total_value = df['prix'].astype(float).sum()
                st.metric("Valeur totale", f"{total_value:.0f} FCFA")
           
            with col2:
                avg_price = df['prix'].astype(float).mean()
                st.metric("Prix moyen", f"{avg_price:.0f} FCFA")
           
            with col3:
                cities = df['ville'].nunique()
                st.metric("Villes couvertes", cities)
   
    if st.button("← Retour au tableau de bord"):
        st.session_state.show_my_products = False
        st.rerun()

# Statistiques du vendeur
def seller_stats_page():
    st.subheader("📈 Statistiques détaillées")
   
    if st.session_state.products:
        df = pd.DataFrame(st.session_state.products)
        df['prix'] = df['prix'].astype(float)
       
        # Graphique 1: Produits par catégorie
        st.subheader("Répartition par catégorie")
        category_counts = df['categorie'].value_counts()
       
        fig1 = px.pie(
            values=category_counts.values,
            names=[CATEGORIES[cat]['name'] for cat in category_counts.index],
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig1, use_container_width=True)
       
        # Graphique 2: Prix moyen par ville
        st.subheader("Prix moyen par ville")
        avg_price_by_city = df.groupby('ville')['prix'].mean().reset_index()
       
        fig2 = px.bar(
            avg_price_by_city,
            x='ville',
            y='prix',
            title="Prix moyen par ville",
            labels={'prix': 'Prix moyen (FCFA)', 'ville': 'Ville'}
        )
        st.plotly_chart(fig2, use_container_width=True)
       
        # Tableau des données
        st.subheader("Données brutes")
        st.dataframe(df, use_container_width=True)
   
    if st.button("← Retour au tableau de bord"):
        st.session_state.show_stats = False
        st.rerun()


def admin_dashboard():
    st.header("🔐 Tableau d'administration")
    tabs = st.tabs(["Utilisateurs", "Produits", "Statistiques"])

    # Utilisateurs
    with tabs[0]:
        st.subheader("Utilisateurs enregistrés")
        users = st.session_state.get('users', [])
        if not users:
            st.info("Aucun utilisateur enregistré.")
        else:
            # Préparer DataFrame sans mot de passe
            df = pd.DataFrame(users)
            if 'password' in df.columns:
                df = df.drop(columns=['password'])
            st.dataframe(df, use_container_width=True)

            st.markdown("**Actions**")
            # Afficher chaque utilisateur avec un bouton de suppression
            for idx, usr in enumerate(list(users)):
                cols = st.columns([4, 1])
                with cols[0]:
                    uname = usr.get('username') or usr.get('email')
                    role = 'Admin' if usr.get('is_admin') else 'User'
                    st.write(f"**{uname}** — {usr.get('email','—')} — {role}")
                with cols[1]:
                    if st.button("🗑️ Supprimer", key=f"admin_delete_user_{idx}"):
                        # Ne pas permettre la suppression du compte admin courant par inadvertance
                        current = st.session_state.get('current_user')
                        if current and (current == usr.get('username') or current == usr.get('email')):
                            st.error("Vous ne pouvez pas supprimer l'utilisateur actuellement connecté.")
                        else:
                            try:
                                st.session_state.users.pop(idx)
                                save_users(st.session_state.users)
                                st.success("Utilisateur supprimé.")
                                st.rerun()
                            except Exception:
                                st.error("Erreur lors de la suppression de l'utilisateur.")

    # Produits
    with tabs[1]:
        st.subheader("Gérer les produits")
        # Ajouter produit (admin)
        # options de catégorie accessibles pour l'ajout et l'édition
        category_options = {info["name"]: cid for cid, info in CATEGORIES.items()}

        with st.expander("➕ Ajouter un produit (Admin)"):
            with st.form("admin_add_product_form"):
                p_name = st.text_input("Nom du produit (admin)")
                p_city = st.text_input("Ville")
                p_price = st.number_input("Prix (FCFA)", min_value=0, step=100)
                p_date = st.date_input("Date")
                p_category_name = st.selectbox("Catégorie", list(category_options.keys()))
                p_category = category_options[p_category_name]
                p_vendeur = st.text_input("Nom du vendeur")
                p_contact = st.text_input("Contact du vendeur (téléphone/email)")
                add_sub = st.form_submit_button("Ajouter le produit")
                if add_sub:
                    new_product = {
                        "produit": p_name,
                        "ville": p_city,
                        "prix": str(p_price),
                        "date": str(p_date),
                        "categorie": p_category,
                        "vendeur": p_vendeur,
                        "contact": p_contact
                    }
                    st.session_state.products.append(new_product)
                    save_products()
                    st.success("Produit ajouté.")

        st.markdown("---")
        # Liste des produits avec actions
        if not st.session_state.products:
            st.info("Aucun produit disponible.")
        else:
            dfp = pd.DataFrame(st.session_state.products)
            # afficher tableau avec colonnes
            st.dataframe(dfp, use_container_width=True)

            st.markdown("**Actions**")
            for idx, prod in enumerate(st.session_state.products):
                cols = st.columns([3,1,1])
                with cols[0]:
                    st.write(f"{prod.get('produit','—')} — {prod.get('prix','—')} FCFA — {prod.get('ville','—')}")
                    st.write(f"Vendeur: {prod.get('vendeur','—')} — Contact: {prod.get('contact','—')}")
                with cols[1]:
                    if st.button("✏️ Éditer", key=f"admin_edit_{idx}"):
                        st.session_state.admin_edit_index = idx
                with cols[2]:
                    if st.button("🗑️ Supprimer", key=f"admin_delete_{idx}"):
                        st.session_state.products.pop(idx)
                        save_products()
                        st.rerun()

            # Si en cours d'édition
            if 'admin_edit_index' in st.session_state:
                i = st.session_state.admin_edit_index
                if i is not None and 0 <= i < len(st.session_state.products):
                    prod = st.session_state.products[i]
                    st.markdown("---")
                    st.subheader(f"Éditer le produit: {prod.get('produit')}")
                    with st.form("admin_edit_form"):
                        e_name = st.text_input("Nom du produit", value=prod.get('produit',''))
                        e_city = st.text_input("Ville", value=prod.get('ville',''))
                        # prix: assurer conversion sûre
                        try:
                            default_price = float(prod.get('prix', 0))
                        except Exception:
                            default_price = 0.0
                        e_price = st.number_input("Prix (FCFA)", value=default_price, step=100.0)
                        # date: fournir un objet date sûr
                        try:
                            default_date = datetime.fromisoformat(prod.get('date')) if prod.get('date') else datetime.now()
                        except Exception:
                            default_date = datetime.now()
                        e_date = st.date_input("Date", value=default_date)

                        # catégorie: calculer l'index de manière sûre
                        cat_names = list(category_options.keys())
                        prod_cat_id = prod.get('categorie')
                        prod_cat_name = None
                        if prod_cat_id in CATEGORIES:
                            prod_cat_name = CATEGORIES[prod_cat_id].get('name')
                        if prod_cat_name in cat_names:
                            default_cat_idx = cat_names.index(prod_cat_name)
                        else:
                            default_cat_idx = 0
                        e_category = st.selectbox("Catégorie", cat_names, index=default_cat_idx)
                        e_vendeur = st.text_input("Nom du vendeur", value=prod.get('vendeur',''))
                        e_contact = st.text_input("Contact du vendeur", value=prod.get('contact',''))

                        col_cancel, col_save = st.columns([1,2])
                        with col_cancel:
                            if st.form_submit_button("Annuler", key="cancel_edit"):
                                if 'admin_edit_index' in st.session_state:
                                    del st.session_state['admin_edit_index']
                                st.rerun()
                        with col_save:
                            if st.form_submit_button("Enregistrer les modifications", key="save_edit"):
                                # appliquer modifications
                                prod['produit'] = e_name
                                prod['ville'] = e_city
                                prod['prix'] = str(int(e_price))
                                prod['date'] = str(e_date)
                                # retrouver id catégorie
                                cat_id = next((cid for cid, info in CATEGORIES.items() if info['name'] == e_category), prod.get('categorie'))
                                prod['categorie'] = cat_id
                                prod['vendeur'] = e_vendeur
                                prod['contact'] = e_contact
                                save_products()
                                if 'admin_edit_index' in st.session_state:
                                    del st.session_state['admin_edit_index']
                                st.success("Produit mis à jour.")
                                st.rerun()

    # Statistiques
    with tabs[2]:
        admin_stats_tab()


def get_month_purchases(purchases, month_offset=0):
    """Retourne les achats d'un mois spécifique (0 = mois courant, -1 = mois précédent)."""
    from datetime import date, timedelta
    today = date.today()
    target_month = today.month + month_offset
    target_year = today.year
    if target_month <= 0:
        target_month += 12
        target_year -= 1
    elif target_month > 12:
        target_month -= 12
        target_year += 1
    
    month_purchases = []
    for p in purchases:
        try:
            p_date = datetime.fromisoformat(p.get('date_achat', '')).date()
            if p_date.month == target_month and p_date.year == target_year:
                month_purchases.append(p)
        except:
            pass
    return month_purchases


# Onglet Statistiques pour admin (à insérer dans admin_dashboard)
def admin_stats_tab():
    st.subheader("📊 Statistiques des achats")
    purchases = st.session_state.get('purchases', [])
    
    if not purchases:
        st.info("Aucun achat enregistré pour le moment.")
        return
    
    # Achats ce mois-ci vs mois précédent
    current_month = get_month_purchases(purchases, 0)
    previous_month = get_month_purchases(purchases, -1)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Achats totaux (tous les temps)", len(purchases))
    with col2:
        st.metric("Achats ce mois", len(current_month))
    with col3:
        st.metric("Achats mois précédent", len(previous_month))
    
    st.markdown("---")
    
    # Produits les plus achetés par catégorie
    st.subheader("Produits les plus achetés par catégorie")
    
    from collections import Counter
    cat_stats = {}
    for p in purchases:
        cat = p.get('categorie', 'inconnu')
        prod = p.get('produit', 'inconnu')
        if cat not in cat_stats:
            cat_stats[cat] = Counter()
        cat_stats[cat][prod] += 1
    
    # Afficher par onglets de catégories
    if cat_stats:
        cat_tabs = st.tabs([CATEGORIES[c].get('name', c) for c in cat_stats.keys() if c in CATEGORIES])
        for tab_idx, (cat, stats) in enumerate(cat_stats.items()):
            if cat in CATEGORIES and tab_idx < len(cat_tabs):
                with cat_tabs[tab_idx]:
                    top_products = stats.most_common(5)
                    for prod, count in top_products:
                        st.write(f"**{prod}**: {count} achats")
                    # Graphique
                    if top_products:
                        df_cat = pd.DataFrame(top_products, columns=['Produit', 'Achats'])
                        fig = px.bar(df_cat, x='Produit', y='Achats', title=f"Top produits - {CATEGORIES[cat].get('name', cat)}")
                        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Tableau complet des achats
    st.subheader("Liste complète des achats")
    df_purchases = pd.DataFrame(purchases)
    st.dataframe(df_purchases, use_container_width=True)

    st.markdown("**Actions sur les achats**")
    # Boutons pour supprimer des achats individuellement
    for i, p in enumerate(list(purchases)):
        cols = st.columns([4, 1])
        with cols[0]:
            st.write(f"**{p.get('produit','—')}** — {p.get('prix','—')} FCFA — Acheteur: {p.get('acheteur','—')} — Date: {p.get('date_achat','—')}")
        with cols[1]:
            if st.button("🗑️ Supprimer", key=f"admin_delete_purchase_{i}"):
                try:
                    st.session_state.purchases.pop(i)
                    save_purchases(st.session_state.purchases)
                    st.success("Achat supprimé.")
                    st.rerun()
                except Exception:
                    st.error("Erreur lors de la suppression de l'achat.")

    # Option pour supprimer tous les achats
    if st.button("🗑️ Supprimer tous les achats", key="admin_delete_all_purchases"):
        try:
            st.session_state.purchases = []
            save_purchases(st.session_state.purchases)
            st.success("Tous les achats ont été supprimés.")
            st.rerun()
        except Exception:
            st.error("Impossible de supprimer tous les achats.")


def cart_page():
    st.header("🧾 Mon Panier")
    current_user = st.session_state.get('current_user')
    if current_user:
        cart = st.session_state.user_carts.get(current_user, [])
    else:
        cart = st.session_state.get('cart', [])

    if not cart:
        if current_user:
            st.info("Votre panier est vide. Pour ajouter des produits, allez sur la page Marketplace.")
            if st.button("🛍️ Aller au Marketplace"):
                st.session_state.page = 'marketplace'
                st.rerun()
        else:
            st.info("Votre panier est vide. Connectez-vous pour sauvegarder votre panier et achetez des produits.")
            if st.button("🔑 Se connecter / S'inscrire"):
                st.session_state.page = 'login'
                st.rerun()
        return

    # Afficher les items
    # Mini-formulaire : ajouter un produit existant au panier
    st.subheader("Ajouter un produit au panier")
    products_list = st.session_state.get('products', [])
    if products_list:
        product_names = [p.get('produit', '—') for p in products_list]
        col_a, col_b = st.columns([3,1])
        with col_a:
            sel = st.selectbox("Choisir un produit à ajouter", ["-- Choisir --"] + product_names, key="cart_add_select")
        with col_b:
            if st.button("Ajouter au panier", key="cart_add_btn"):
                if sel and sel != "-- Choisir --":
                    # trouver premier produit correspondant
                    prod = next((p for p in products_list if p.get('produit') == sel), None)
                    if prod:
                        item = {
                            'produit': prod.get('produit'),
                            'prix': prod.get('prix'),
                            'vendeur': prod.get('vendeur','—'),
                            'contact': prod.get('contact','—'),
                            'categorie': prod.get('categorie'),
                            'ville': prod.get('ville','—'),
                            'date': prod.get('date','')
                        }
                        add_to_cart_item(item)
                        st.success(f"{item['produit']} ajouté au panier.")
                        st.rerun()
    else:
        st.info("Aucun produit disponible pour l'ajout.")

    # Afficher la liste des articles avec possibilité d'éditer la quantité
    total = 0.0
    for i, item in enumerate(list(cart)):
        cols = st.columns([3,1,1])
        with cols[0]:
            st.write(f"**{item.get('produit')}** — {item.get('vendeur','—')}")
            st.write(f"📍 {item.get('ville','—')} — 📅 {item.get('date','—')}")
        with cols[1]:
            # show price
            try:
                price_val = float(item.get('prix', 0))
            except Exception:
                price_val = 0.0
            st.write(f"{price_val:.0f} FCFA")
        with cols[2]:
            # quantity editor
            qty_key = f"qty_{'user' if current_user else 'anon'}_{i}"
            current_qty = int(item.get('quantity', 1)) if item.get('quantity') is not None else 1
            new_qty = st.number_input("Qté", min_value=1, value=current_qty, key=qty_key)
            if new_qty != current_qty:
                if st.button("Mettre à jour", key=f"update_qty_{i}"):
                    # apply update
                    item['quantity'] = int(new_qty)
                    # persist if user
                    if current_user:
                        try:
                            db = SessionLocal()
                            db.query(Cart).filter(Cart.username == current_user).delete()
                            for it in st.session_state.user_carts[current_user]:
                                row = Cart(
                                    username=current_user,
                                    produit=it.get('produit'),
                                    prix=str(it.get('prix','')),
                                    vendeur=it.get('vendeur'),
                                    contact=it.get('contact'),
                                    categorie=it.get('categorie'),
                                    ville=it.get('ville'),
                                    date=it.get('date'),
                                    quantity=int(it.get('quantity', 1))
                                )
                                db.add(row)
                            db.commit()
                        except Exception:
                            try:
                                db.rollback()
                            except Exception:
                                pass
                        finally:
                            try:
                                db.close()
                            except Exception:
                                pass
                    else:
                        # anonymous cart already updated in session
                        pass
                    st.success("Quantité mise à jour.")
                    st.rerun()

        # accumulate total
        try:
            total += float(item.get('prix', 0)) * int(item.get('quantity', 1))
        except Exception:
            try:
                total += float(item.get('prix', 0))
            except Exception:
                pass
    col1, col2 = st.columns([2,1])
    with col1:
        if st.button("Vider le panier"):
            # vider le panier approprié
            if current_user:
                st.session_state.user_carts[current_user] = []
                # persist empty cart
                try:
                    db = SessionLocal()
                    db.query(Cart).filter(Cart.username == current_user).delete()
                    db.commit()
                except Exception:
                    try:
                        db.rollback()
                    except Exception:
                        pass
                finally:
                    try:
                        db.close()
                    except Exception:
                        pass
            else:
                st.session_state.cart = []
            st.success("Panier vidé.")
            st.rerun()

    with col2:
        st.metric("Total", f"{total:.0f} FCFA")

    # Supprimer item
    st.markdown("---")
    st.subheader("Gérer les articles")
    for i, item in enumerate(list(cart)):
        cols = st.columns([3,1])
        with cols[0]:
            st.write(f"**{item.get('produit')}** — {item.get('prix')} FCFA — {item.get('vendeur')}")
        with cols[1]:
            if st.button("Supprimer", key=f"remove_{i}"):
                # remove from the correct cart
                if current_user:
                    try:
                        st.session_state.user_carts[current_user].pop(i)
                        # persist change
                        db = SessionLocal()
                        db.query(Cart).filter(Cart.username == current_user).delete()
                        for it in st.session_state.user_carts[current_user]:
                            row = Cart(
                                username=current_user,
                                produit=it.get('produit'),
                                prix=str(it.get('prix','')),
                                vendeur=it.get('vendeur'),
                                contact=it.get('contact'),
                                categorie=it.get('categorie'),
                                ville=it.get('ville'),
                                date=it.get('date'),
                                quantity=int(it.get('quantity', 1))
                            )
                            db.add(row)
                        db.commit()
                    except Exception:
                        try:
                            db.rollback()
                        except Exception:
                            pass
                    finally:
                        try:
                            db.close()
                        except Exception:
                            pass
                else:
                    try:
                        st.session_state.cart.pop(i)
                    except Exception:
                        pass
                st.success("Article supprimé du panier.")
                st.rerun()

    st.markdown("---")
    if st.button("Passer au paiement (simulation)"):
        # Créer achats pour chaque item du panier (utilisateur ou session)
        buyer = st.session_state.get('current_user', 'Anonyme')
        source_cart = st.session_state.user_carts.get(current_user, []) if current_user else st.session_state.get('cart', [])
        for item in list(source_cart):
            purchase = {
                'produit': item.get('produit'),
                'prix': item.get('prix'),
                'vendeur': item.get('vendeur'),
                'contact': item.get('contact'),
                'categorie': item.get('categorie'),
                'date_achat': str(datetime.now()),
                'acheteur': buyer
            }
            st.session_state.purchases.append(purchase)
        save_purchases(st.session_state.purchases)
        # vider le panier source and persist
        if current_user:
            st.session_state.user_carts[current_user] = []
            try:
                db = SessionLocal()
                db.query(Cart).filter(Cart.username == current_user).delete()
                db.commit()
            except Exception:
                try:
                    db.rollback()
                except Exception:
                    pass
            finally:
                try:
                    db.close()
                except Exception:
                    pass
        else:
            st.session_state.cart = []
        st.success("Paiement simulé réussi. Vos achats ont été enregistrés.")
        st.rerun()



def profile_page():
    """Affiche les informations de l'utilisateur connecté (sans mot de passe)."""
    st.header("👤 Mon Profil")
    current = st.session_state.get('current_user')
    if not current:
        st.info("Aucun utilisateur connecté. Veuillez vous connecter.")
        return

    user = next((u for u in st.session_state.get('users', []) if u.get('username') == current), None)
    if not user:
        st.error("Utilisateur introuvable.")
        return

    # Préparer affichage sans mot de passe
    safe_user = {k: v for k, v in user.items() if k != 'password' and not k.startswith('reset_')}
    # Afficher les champs principaux
    st.subheader(safe_user.get('username', '—'))
    cols = st.columns([1, 2])
    with cols[0]:
        st.write("**Email**")
        st.write("**Inscrit le**")
    with cols[1]:
        st.write(safe_user.get('email', '—'))
        st.write(safe_user.get('created_at', '—'))

    st.markdown("---")
    st.write("Vous pouvez mettre à jour vos informations ci-dessous :")
    with st.form("update_profile_form"):
        new_email = st.text_input("Email", value=safe_user.get('email', ''))
        submit = st.form_submit_button("Mettre à jour")
        if submit:
            # mettre à jour en mémoire et sauvegarder
            user['email'] = new_email
            save_users(st.session_state.get('users', []))
            st.success("Profil mis à jour.")
            st.rerun()

# 🎯 **LOGICIEL PRINCIPAL DE NAVIGATION**# Sidebar pour la navigation
with st.sidebar:
    st.markdown("# 📊 KASSUA")
   
    if st.session_state.logged_in:
        st.markdown(f"Connecté en tant que: **{st.session_state.user_type}**")
        st.markdown("---")
       
        if st.session_state.user_type == "buyer":
            if st.button("🛍️ Marketplace", use_container_width=True):
                st.session_state.page = "marketplace"
                st.rerun()
            # Afficher le nombre d'articles dans le libellé du bouton
            current_user_for_count = st.session_state.get('current_user')
            if current_user_for_count:
                count = len(st.session_state.user_carts.get(current_user_for_count, []))
            else:
                count = len(st.session_state.get('cart', []))
            cart_label = "📋 Mon Panier" + (f" ({count})" if count else "")
            if st.button(cart_label, use_container_width=True):
                st.session_state.page = "cart"
                st.rerun()
            if st.button("👤 Mon Profil", use_container_width=True):
                st.session_state.page = "profile"
                st.rerun()
       
        
        elif st.session_state.user_type == "admin":
            if st.button("👨‍💻 Tableau Admin", use_container_width=True):
                st.session_state.page = "admin"
                st.rerun()
       
        st.markdown("---")
        if st.button("🚪 Déconnexion", use_container_width=True, type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.current_user = None
            # préserver users et products
            preserve = ['logged_in', 'user_type', 'products', 'users', 'current_user']
            for key in list(st.session_state.keys()):
                if key not in preserve:
                    del st.session_state[key]
            st.rerun()
   
    else:
        st.markdown("Bienvenue sur Kassua!")
        st.markdown("---")
        st.markdown("### Connectez-vous pour accéder:")
        st.markdown("- 🛍️ **Espace Client**: Parcourir et acheter")

# Afficher la page appropriée
if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.user_type == "buyer":
        page = st.session_state.get('page', 'marketplace')
        if page == 'profile':
            profile_page()
        else:
            # default and other pages
            marketplace_page()
    elif st.session_state.user_type == "admin":
        admin_dashboard()
