
# app.py — Kassua Marketplace (Supabase edition)
# ============================================================
# MIGRATION MySQL → Supabase (PostgreSQL)
#
# Ce qu'on a changé par rapport à la version MySQL :
#
# 1. SUPPRESSION de SQLAlchemy + pymysql
#    → remplacés par le client officiel Python de Supabase :
#      `supabase-py` (pip install supabase)
#
# 2. VARIABLES D'ENVIRONNEMENT
#    Au lieu de DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME,
#    on n'a besoin que de deux variables :
#      SUPABASE_URL  → URL du projet  (ex: https://xxxx.supabase.co)
#      SUPABASE_KEY  → clé anon/service_role du projet
#    Ces valeurs se trouvent dans :
#    Supabase Dashboard → Settings → API → "Project URL" et "API Keys"
#
# 3. TABLES SUPABASE (à créer UNE SEULE FOIS dans l'éditeur SQL Supabase)
#    Voir la section « SQL de création des tables » tout en bas de ce fichier.
#
# 4. LES FONCTIONS DB (load_*, save_*) utilisent maintenant
#    supabase.table("nom").select/insert/delete/update
#    à la place de sessions SQLAlchemy.
#
# 5. PANIER (Cart)
#    Même logique qu'avant, mais via la table "carts" Supabase.
#
# 6. INIT_DB / MIGRATE_JSON
#    Plus besoin de create_all() : les tables existent déjà dans Supabase.
#    migrate_json_to_db() reste présent pour copier d'éventuels JSON locaux.
# ============================================================

import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import random
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import secrets

# ── Supabase client ──────────────────────────────────────────
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ufwylvnlmasvbqcchmqj.supabase.co")   # à renseigner dans .env ou secrets Streamlit
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_f_9Pwhw_bQWsYA0-ciYWLA_ufZUQ5h2")   # clé anon (ou service_role si RLS désactivé)

@st.cache_resource          # crée le client une seule fois par session serveur
def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error(
            "⚠️ Variables SUPABASE_URL et SUPABASE_KEY manquantes. "
            "Ajoutez-les dans vos secrets Streamlit ou un fichier .env."
        )
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = get_supabase()
# ─────────────────────────────────────────────────────────────

# Configuration de la page
st.set_page_config(
    page_title="Kassua - Marketplace ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 KASSUA - Marketplace ")

# ── Données statiques ────────────────────────────────────────
CATEGORIES = {
    "fruits_legumes": {
        "name": "🥦 Fruits & Légumes",
        "emoji": "🥦",
        "products": ["pomme","banane","orange","tomate","oignon","carotte","salade",
                     "raisin","ananas","poire","choux","pastèque","aubergine","concombre",
                     "poivron","piment","pomme de terre","haricot vert","tchappata et guisma"]
    },
    "viandes_poissons": {
        "name": "🍗 Viandes & Poissons",
        "emoji": "🍗",
        "products": ["poulet","boeuf","poisson","viande hachée","pilon","pintade","dinde"]
    },
    "produits_laitiers": {
        "name": "🥛 Produits Laitiers",
        "emoji": "🥛",
        "products": ["lait","fromage","yaourt","beurre","crème"]
    },
    "epicerie": {
        "name": "🍚 Épicerie",
        "emoji": "🍚",
        "products": ["sel","poivre","piment sec","percil et céleri","soumbala",
                     "yazi","ail","canelle","clou de girofle"]
    },
    "boulangerie": {
        "name": "🥐 Boulangerie",
        "emoji": "🥐",
        "products": ["pain","croissant","gâteau","cake"]
    },
    "boissons": {
        "name": "🥤 Boissons",
        "emoji": "🥤",
        "products": ["eau","jus","boisson énergissante","jus naturel"]
    }
}

PRODUCT_EMOJIS = {
    'percil et céleri':'🍀','tomate':'🍅','oignon':'🧅','pomme':'🍎',
    'ananas':'🍍','raisin':'🍇','poire':'🍐','choux':'🥦',
    'pastèque':'🍉','aubergine':'🍆','concombre':'🥒','poivron':'🫑',
    'piment':'🌶️','pomme de terre':'🥔','haricot vert':'🫛',
    'tchappata et guisma':'🌿','banane':'🍌','orange':'🍊','viande':'🍖',
    'poisson':'🐟','lait':'🥛','fromage':'🧀','gâteau':'🎂','soumbala':'🏺',
    'yazi':'','ail':'🧄','poulet':'🐔','boeuf':'🥩','carotte':'🥕',
    'salade':'🥬','viande hachée':'🥓','yaourt':'🥣','beurre':'🧈',
    'crème':'🍦','canelle':'🪵','clou de girofle':'🍂','croissant':'🥐',
    'pain':'🥖','cake':'🥮','eau':'💧','jus':'🧃',
    'boisson énergissante':'⚡','jus naturel':'🍹','sel':'🧂','poivre':'⚫',
    'pilon':'🍗','pintade':'🦚','dinde':'🦃'
}

# ── Session state par défaut ──────────────────────────────────
for k, v in [
    ('logged_in', False), ('user_type', None),
    ('current_user', None), ('products', []),
    ('users', []), ('purchases', []),
    ('cart', []), ('user_carts', {})
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers query params ──────────────────────────────────────
try:
    params = st.query_params
    if params.get('open_cart'):
        st.session_state.page = 'cart'
        try:
            st.set_query_params()
        except Exception:
            pass
        try:
            st.experimental_rerun()
        except Exception:
            pass
except Exception:
    pass


# ═══════════════════════════════════════════════════════════════
#  COUCHE BASE DE DONNÉES — Supabase
# ═══════════════════════════════════════════════════════════════

def _rows(response) -> list:
    """Extrait les lignes d'une réponse Supabase (évite les erreurs None)."""
    try:
        return response.data or []
    except Exception:
        return []


# ── USERS ─────────────────────────────────────────────────────
def load_users() -> list:
    try:
        return _rows(supabase.table("users").select("*").execute())
    except Exception:
        return []


def save_users(users: list):
    """Remplace entièrement la table users (logique démo)."""
    try:
        supabase.table("users").delete().neq("id", 0).execute()
        if users:
            supabase.table("users").insert(users).execute()
    except Exception as e:
        st.warning(f"Erreur save_users: {e}")


def upsert_user(user: dict):
    """Insère ou met à jour un utilisateur par username."""
    try:
        supabase.table("users").upsert(user, on_conflict="username").execute()
    except Exception as e:
        st.warning(f"Erreur upsert_user: {e}")


# ── PRODUCTS ──────────────────────────────────────────────────
def load_products() -> list:
    try:
        return _rows(supabase.table("products").select("*").execute())
    except Exception:
        return []


def save_products_to_db(products: list):
    try:
        supabase.table("products").delete().neq("id", 0).execute()
        if products:
            # Supabase accepte jusqu'à 1000 lignes par insert ; on chunke si besoin
            for i in range(0, len(products), 500):
                supabase.table("products").insert(products[i:i+500]).execute()
    except Exception as e:
        st.warning(f"Erreur save_products_to_db: {e}")


def save_products():
    products = st.session_state.get('products', [])
    try:
        save_products_to_db(products)
    except Exception:
        try:
            with open("p.json", "w", encoding="utf-8") as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


# ── PURCHASES ─────────────────────────────────────────────────
def load_purchases() -> list:
    try:
        return _rows(supabase.table("purchases").select("*").execute())
    except Exception:
        return []


def save_purchases(purchases: list):
    try:
        supabase.table("purchases").delete().neq("id", 0).execute()
        if purchases:
            for i in range(0, len(purchases), 500):
                supabase.table("purchases").insert(purchases[i:i+500]).execute()
    except Exception as e:
        st.warning(f"Erreur save_purchases: {e}")


# ── CARTS ─────────────────────────────────────────────────────
def load_carts_from_db() -> dict:
    try:
        rows = _rows(supabase.table("carts").select("*").execute())
        carts: dict = {}
        for r in rows:
            user = r.get("username")
            item = {k: r.get(k) for k in
                    ['produit','prix','vendeur','contact','categorie','ville','date','quantity']}
            item['quantity'] = item.get('quantity') or 1
            carts.setdefault(user, []).append(item)
        return carts
    except Exception:
        return {}


def _persist_user_cart(username: str):
    """Écrase les lignes du panier d'un utilisateur dans Supabase."""
    try:
        supabase.table("carts").delete().eq("username", username).execute()
        items = st.session_state.user_carts.get(username, [])
        if items:
            rows = [
                {
                    "username": username,
                    "produit": it.get('produit'),
                    "prix": str(it.get('prix','')),
                    "vendeur": it.get('vendeur'),
                    "contact": it.get('contact'),
                    "categorie": it.get('categorie'),
                    "ville": it.get('ville'),
                    "date": it.get('date'),
                    "quantity": int(it.get('quantity', 1))
                }
                for it in items
            ]
            supabase.table("carts").insert(rows).execute()
    except Exception as e:
        st.warning(f"Erreur _persist_user_cart: {e}")


# ── INIT + MIGRATION ──────────────────────────────────────────
def migrate_json_to_db():
    """Importe les anciens fichiers JSON dans Supabase si les tables sont vides."""
    # Users
    if not load_users() and os.path.exists('users.json'):
        try:
            with open('users.json', encoding='utf-8') as f:
                save_users(json.load(f))
        except Exception:
            pass
    # Products
    if not load_products() and os.path.exists('p.json'):
        try:
            with open('p.json', encoding='utf-8') as f:
                save_products_to_db(json.load(f))
        except Exception:
            pass
    # Purchases
    if not load_purchases() and os.path.exists('purchases.json'):
        try:
            with open('purchases.json', encoding='utf-8') as f:
                save_purchases(json.load(f))
        except Exception:
            pass


try:
    migrate_json_to_db()
    if not st.session_state.get('products'):
        st.session_state.products = load_products()
    if not st.session_state.get('users'):
        st.session_state.users = load_users()
    if not st.session_state.get('purchases'):
        st.session_state.purchases = load_purchases()
    st.session_state.user_carts = load_carts_from_db()
except Exception as e:
    st.warning(f"Initialisation partielle: {e}")
    for k, file in [('products','p.json'), ('users','users.json'), ('purchases','purchases.json')]:
        if not st.session_state.get(k) and os.path.exists(file):
            try:
                with open(file, encoding='utf-8') as f:
                    st.session_state[k] = json.load(f)
            except Exception:
                st.session_state[k] = []
    if 'user_carts' not in st.session_state:
        st.session_state.user_carts = {}


# ═══════════════════════════════════════════════════════════════
#  UTILITAIRES (inchangés par rapport à la version MySQL)
# ═══════════════════════════════════════════════════════════════

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_emoji(product_name):
    for key, emoji in PRODUCT_EMOJIS.items():
        if key in product_name.lower():
            return emoji
    return "📦"


def contact_link(contact: str) -> str:
    if not contact:
        return "#"
    import re
    s = str(contact).strip()
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}", s)
    if "@" in s and email_match:
        return f"mailto:{email_match.group(0)}"
    digits = ''.join(c for c in s if c.isdigit() or c == '+')
    if digits:
        num = digits.lstrip('+').lstrip('0') if digits.startswith('00') else digits.lstrip('+')
        return f"https://wa.me/{num}"
    return "#"


def generate_sample_data():
    products = []
    for cat_id, cat_info in CATEGORIES.items():
        for product_name in cat_info["products"][:3]:
            products.append({
                "produit": product_name.capitalize(),
                "ville": "Niamey",
                "prix": str(random.randint(500, 10000)),
                "date": "2024-11-01",
                "categorie": cat_id,
                "vendeur": f"Vendeur_{random.randint(1,5)}",
                "contact": f"+227{random.randint(20000000,99999999)}"
            })
    return products


def recommend_for_user(username: str, limit: int = 5):
    if not username:
        return []
    purchases = st.session_state.get('purchases', [])
    user_p = [p for p in purchases if p.get('acheteur') == username]
    if not user_p:
        return []
    from collections import Counter
    cat_counts = Counter(p.get('categorie') for p in user_p if p.get('categorie'))
    recs = []
    for cat, _ in cat_counts.most_common():
        for prod in st.session_state.get('products', []):
            if prod.get('categorie') == cat and prod.get('produit') not in recs:
                recs.append(prod.get('produit'))
                if len(recs) >= limit:
                    return recs
    return recs


def get_purchase_counts():
    from collections import Counter
    return Counter(p.get('produit') for p in st.session_state.get('purchases', []) if p.get('produit'))


def get_global_top_products(n=5):
    return [p for p, _ in get_purchase_counts().most_common(n)]


# ── Panier ────────────────────────────────────────────────────
def add_to_cart_item(item):
    user = st.session_state.get('current_user')
    if user:
        if user not in st.session_state.user_carts:
            st.session_state.user_carts[user] = []
        merged = False
        for it in st.session_state.user_carts[user]:
            if it.get('produit') == item.get('produit') and it.get('vendeur') == item.get('vendeur'):
                try:
                    it['quantity'] = int(it.get('quantity', 1)) + int(item.get('quantity', 1))
                except Exception:
                    it['quantity'] = 1
                merged = True
                break
        if not merged:
            item.setdefault('quantity', 1)
            st.session_state.user_carts[user].append(item)
        _persist_user_cart(user)
    else:
        st.session_state.cart.append(item)


def render_cart_badge():
    try:
        user = st.session_state.get('current_user')
        count = len(st.session_state.user_carts.get(user, [])) if user else len(st.session_state.get('cart', []))
        if count:
            cols = st.columns([9, 1])
            with cols[1]:
                if st.button(f"🛒 {count}", key="cart_badge_button"):
                    st.session_state.show_cart_preview = not st.session_state.get('show_cart_preview', False)
                    try:
                        st.experimental_rerun()
                    except Exception:
                        pass
    except Exception:
        pass


def render_cart_preview():
    try:
        container = st.container()
        with container:
            st.markdown("**Aperçu du panier**")
            current_user = st.session_state.get('current_user')
            cart = st.session_state.user_carts.get(current_user, []) if current_user else st.session_state.get('cart', [])
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
                cols = st.columns([3, 1, 1])
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
                        if current_user:
                            st.session_state.user_carts[current_user].pop(i)
                            _persist_user_cart(current_user)
                        else:
                            try:
                                st.session_state.cart.pop(i)
                            except Exception:
                                pass
                        st.success("Article supprimé.")
                        st.session_state.show_cart_preview = True
                        try:
                            st.experimental_rerun()
                        except Exception:
                            pass
                try:
                    total_preview += float(item.get('prix', 0)) * int(item.get('quantity', 1))
                except Exception:
                    pass
            st.markdown(f"**Total (aperçu)**: {total_preview:.0f} FCFA")
            col1, col2 = st.columns([1, 1])
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


# ── Reset password ────────────────────────────────────────────
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


def verify_reset_token(email: str, token: str) -> bool:
    user = next((u for u in st.session_state.get('users', [])
                 if u.get('email') == email and u.get('reset_token') == token), None)
    if not user:
        return False
    try:
        return datetime.fromisoformat(user.get('reset_expires', '')) >= datetime.now()
    except Exception:
        return False


def clear_reset_token_for_user(user: dict):
    user.pop('reset_token', None)
    user.pop('reset_expires', None)
    save_users(st.session_state.get('users', []))


# ═══════════════════════════════════════════════════════════════
#  PAGES (inchangées dans la logique, uniquement la persistence DB diffère)
# ═══════════════════════════════════════════════════════════════

def login_page():
    st.markdown("""
    <style>
    .big-font { font-size:50px !important; text-align:center; }
    .center { display:flex; justify-content:center; align-items:center; flex-direction:column; }
    </style>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="center">', unsafe_allow_html=True)
        st.markdown('<p class="big-font">📊</p>', unsafe_allow_html=True)
        st.markdown("# KASSUA")
        st.markdown("### Marketplace Intelligent")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
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

    if st.session_state.get('show_admin_login'):
        st.subheader("Connexion Administrateur")
        adm_pwd = st.text_input("Mot de passe administrateur", type="password")
        if st.button("Se connecter en tant qu'administrateur"):
            if adm_pwd == "kassuaTa@2025":
                st.session_state.logged_in = True
                st.session_state.user_type = 'admin'
                st.session_state.show_admin_login = False
                st.rerun()
            else:
                st.error("Mot de passe administrateur incorrect.")

    if st.session_state.get('show_client_auth'):
        st.subheader("Espace Client - Connexion / Inscription")
        tabs = st.tabs(["Connexion", "Inscription", "Réinitialiser"])

        with tabs[0]:
            login_input = st.text_input("Nom d'utilisateur ou Email", key="login_user")
            login_pwd   = st.text_input("Mot de passe", type="password", key="login_pwd")
            if st.button("Se connecter", key="login_btn"):
                hashed = hash_password(login_pwd)
                matched = next(
                    (u for u in st.session_state.users
                     if (u.get('username') == login_input or u.get('email') == login_input)
                     and u.get('password') == hashed), None)
                if matched:
                    st.session_state.logged_in = True
                    st.session_state.user_type = 'buyer'
                    st.session_state.current_user = matched.get('username') or matched.get('email')
                    anon_cart = st.session_state.get('cart', [])
                    user = st.session_state.current_user
                    if anon_cart:
                        st.session_state.user_carts.setdefault(user, []).extend(anon_cart)
                        st.session_state.cart = []
                        _persist_user_cart(user)
                    st.session_state.show_client_auth = False
                    st.success(f"Bienvenue, {user} !")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")
            st.markdown("---")
            if st.checkbox("Mot de passe oublié ?"):
                email_for_reset = st.text_input("Email pour réinitialisation", key="reset_email_input")
                if st.button("Envoyer la demande", key="send_reset"):
                    if not email_for_reset:
                        st.error("Veuillez saisir votre email.")
                    else:
                        token = generate_reset_token_for_email(email_for_reset)
                        if token:
                            st.success("Demande enregistrée.")
                            st.code(token)
                        else:
                            st.error("Aucun compte trouvé pour cet email.")

        with tabs[1]:
            reg_username = st.text_input("Nom utilisateur", key="reg_user")
            reg_email    = st.text_input("Email", key="reg_email")
            reg_pwd      = st.text_input("Mot de passe", type="password", key="reg_pwd")
            if st.button("S'inscrire", key="reg_btn"):
                if not reg_username or not reg_email or not reg_pwd:
                    st.error("Veuillez remplir tous les champs.")
                elif any(u['username'] == reg_username for u in st.session_state.users):
                    st.error("Ce nom d'utilisateur existe déjà.")
                else:
                    new_user = {
                        'username': reg_username, 'email': reg_email,
                        'password': hash_password(reg_pwd),
                        'created_at': str(datetime.now()), 'is_admin': False
                    }
                    st.session_state.users.append(new_user)
                    save_users(st.session_state.users)
                    st.session_state.logged_in = True
                    st.session_state.user_type = 'buyer'
                    st.session_state.current_user = reg_username
                    anon_cart = st.session_state.get('cart', [])
                    if anon_cart:
                        st.session_state.user_carts.setdefault(reg_username, []).extend(anon_cart)
                        st.session_state.cart = []
                        _persist_user_cart(reg_username)
                    st.session_state.show_client_auth = False
                    st.success("Inscription réussie.")
                    st.rerun()

        with tabs[2]:
            st.subheader("Réinitialiser le mot de passe")
            reset_email  = st.text_input("Email lié au compte", key="confirm_reset_email")
            reset_token  = st.text_input("Token", key="confirm_reset_token")
            new_pwd      = st.text_input("Nouveau mot de passe", type="password", key="confirm_new_pwd")
            new_pwd2     = st.text_input("Confirmer", type="password", key="confirm_new_pwd2")
            if st.button("Réinitialiser", key="confirm_reset_btn"):
                if not reset_email or not reset_token or not new_pwd:
                    st.error("Remplissez tous les champs.")
                elif new_pwd != new_pwd2:
                    st.error("Les mots de passe ne correspondent pas.")
                elif verify_reset_token(reset_email, reset_token):
                    user = next((u for u in st.session_state.users
                                 if u.get('email') == reset_email and u.get('reset_token') == reset_token), None)
                    if user:
                        user['password'] = hash_password(new_pwd)
                        clear_reset_token_for_user(user)
                        st.success("Mot de passe réinitialisé.")
                    else:
                        st.error("Utilisateur introuvable.")
                else:
                    st.error("Token invalide ou expiré.")


def marketplace_page():
    render_cart_badge()
    if st.session_state.get('show_cart_preview'):
        render_cart_preview()

    st.header("🛍️ Marketplace")

    purchases   = st.session_state.get('purchases', [])
    recs        = []
    current_user = st.session_state.get('current_user')
    if current_user:
        recs = recommend_for_user(current_user, limit=5)
    if not recs and purchases:
        recs = get_global_top_products(5)

    if recs:
        with st.expander("💡 Recommandations pour vous"):
            cols = st.columns(len(recs))
            for i, rec in enumerate(recs):
                with cols[i]:
                    st.write(rec)
                    if st.button("Voir", key=f"rec_{i}"):
                        st.session_state.rec_query = rec
                        st.rerun()

    col1, col2 = st.columns([3, 1])
    with col1:
        if 'rec_query' in st.session_state:
            search_query = st.session_state.pop('rec_query')
        else:
            search_query = st.text_input("🔍 Rechercher produits, villes...", placeholder="Ex: pomme, Niamey")
    with col2:
        selected_category = st.selectbox(
            "📁 Catégorie",
            ["Toutes"] + [cat_info["name"] for cat_info in CATEGORIES.values()]
        )

    st.subheader("Catégories")
    category_cols = st.columns(len(CATEGORIES))
    for idx, (cat_id, cat_info) in enumerate(CATEGORIES.items()):
        with category_cols[idx]:
            if st.button(cat_info["name"], use_container_width=True):
                selected_category = cat_info["name"]

    filtered_products = st.session_state.products
    if search_query:
        sq = search_query.lower()
        filtered_products = [p for p in filtered_products
                             if sq in p['produit'].lower() or sq in p.get('ville','').lower()]
    if selected_category != "Toutes":
        cat_id = next((cid for cid, info in CATEGORIES.items() if info["name"] == selected_category), None)
        if cat_id:
            filtered_products = [p for p in filtered_products if p['categorie'] == cat_id]

    if not filtered_products:
        st.warning("Aucun produit trouvé.")
    else:
        df = pd.DataFrame(filtered_products)
        df['emoji'] = df['produit'].apply(get_emoji)
        cols_per_row = 3
        rows = [df.iloc[i:i+cols_per_row] for i in range(0, len(df), cols_per_row)]
        for row in rows:
            cols = st.columns(cols_per_row)
            for idx, (_, product) in enumerate(row.iterrows()):
                with cols[idx]:
                    emoji = product['emoji']
                    st.markdown(f"""
                    <div style='border:1px solid #ddd;border-radius:10px;padding:15px;
                                margin-bottom:10px;background-color:white;'>
                        <div style='font-size:40px;text-align:center;'>{emoji}</div>
                        <h3 style='text-align:center;'>{product['produit']}</h3>
                        <h2 style='color:#2E8B57;text-align:center;'>{product['prix']} FCFA</h2>
                        <p style='text-align:center;'>
                            📍 {product['ville']}<br>📅 {product['date']}<br>
                            📁 {CATEGORIES[product['categorie']]['name']}<br>
                            👤 Vendeur: {product.get('vendeur','—')}<br>
                            📞 Contact: {product.get('contact','—')}<br>
                            <a href="{contact_link(product.get('contact',''))}" target="_blank">
                                Contacter le vendeur</a>
                        </p>
                    </div>""", unsafe_allow_html=True)

                    unique_key = hashlib.sha1(
                        f"{product.get('produit','')}-{product.get('vendeur','')}-"
                        f"{product.get('ville','')}-{product.get('prix','')}-{product.get('date','')}".encode()
                    ).hexdigest()[:10]

                    if st.button("➕ Ajouter au panier", key=f"addcart_{unique_key}", use_container_width=True):
                        add_to_cart_item({
                            'produit': product['produit'], 'prix': product['prix'],
                            'vendeur': product.get('vendeur','—'), 'contact': product.get('contact','—'),
                            'categorie': product['categorie'], 'ville': product.get('ville','—'),
                            'date': product.get('date','')
                        })
                        st.success(f"{product['produit']} ajouté au panier.")

                    if st.button("🛒 Acheter Maintenant", key=f"buy_{unique_key}", use_container_width=True):
                        purchase = {
                            "produit": product['produit'], "prix": product['prix'],
                            "vendeur": product.get('vendeur','—'), "contact": product.get('contact','—'),
                            "categorie": product['categorie'],
                            "date_achat": str(datetime.now()),
                            "acheteur": st.session_state.get('current_user','Anonyme')
                        }
                        st.session_state.purchases.append(purchase)
                        save_purchases(st.session_state.purchases)
                        st.success(f"{product['produit']} acheté!")

        st.markdown("---")
        st.subheader("📈 Statistiques du marché")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Produits disponibles", len(filtered_products))
        with col2: st.metric("Prix moyen", f"{df['prix'].astype(float).mean():.0f} FCFA")
        with col3: st.metric("Villes", df['ville'].nunique())


def seller_dashboard():
    st.header("👨‍💼 Tableau de Bord Vendeur")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📦 Produits", len(st.session_state.products))
    with col2: st.metric("💰 Chiffre",
                          f"{sum(float(p['prix']) for p in st.session_state.products):.0f} FCFA")
    with col3: st.metric("🏪 Ventes", "0")
    with col4: st.metric("⭐ Rating", "4.8")

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

    if st.session_state.get('show_add_product'):
        add_product_page()
    elif st.session_state.get('show_my_products'):
        my_products_page()
    elif st.session_state.get('show_stats'):
        seller_stats_page()
    else:
        st.subheader("📋 Derniers produits ajoutés")
        if st.session_state.products:
            st.dataframe(
                pd.DataFrame(st.session_state.products[-5:])[['produit','prix','ville','date','categorie']],
                hide_index=True)
        else:
            st.info("Aucun produit. Ajoutez votre premier produit!")


def add_product_page():
    st.subheader("➕ Ajouter un nouveau produit")
    category_options = {info["name"]: cid for cid, info in CATEGORIES.items()}
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("📦 Nom du produit")
            city = st.text_input("🏙️ Ville")
        with col2:
            price = st.number_input("💰 Prix (FCFA)", min_value=0, step=100)
            date = st.date_input("📅 Date")
        category_name = st.selectbox("📁 Catégorie", list(category_options.keys()))
        vendeur = st.text_input("👤 Nom du vendeur", value="Vendeur_1")
        contact = st.text_input("📞 Contact", value="+22700000000")
        if st.form_submit_button("✅ Publier", type="primary"):
            if not all([product_name, city, price, vendeur]):
                st.error("Veuillez remplir tous les champs.")
            else:
                new_product = {
                    "produit": product_name, "ville": city, "prix": str(price),
                    "date": str(date), "categorie": category_options[category_name],
                    "vendeur": vendeur, "contact": contact
                }
                st.session_state.products.append(new_product)
                save_products()
                st.success(f"Produit '{product_name}' ajouté!")


def my_products_page():
    st.subheader("📋 Mes produits")
    if st.session_state.products:
        df = pd.DataFrame(st.session_state.products)
        for idx, (_, p) in enumerate(df.iterrows()):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1: st.write(f"**{p['produit']}** - {p['prix']} FCFA - {p['ville']}")
            with col2:
                if st.button("✏️ Éditer", key=f"edit_{idx}"):
                    st.session_state.editing_product = idx
            with col3:
                if st.button("🗑️ Supprimer", key=f"delete_{idx}"):
                    st.session_state.products.pop(idx)
                    save_products()
                    st.rerun()
        st.markdown("---")
        st.subheader("Mes statistiques")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Valeur totale", f"{df['prix'].astype(float).sum():.0f} FCFA")
        with col2: st.metric("Prix moyen",    f"{df['prix'].astype(float).mean():.0f} FCFA")
        with col3: st.metric("Villes",         df['ville'].nunique())
    if st.button("← Retour"):
        st.session_state.show_my_products = False
        st.rerun()


def seller_stats_page():
    st.subheader("📈 Statistiques détaillées")
    if st.session_state.products:
        df = pd.DataFrame(st.session_state.products)
        df['prix'] = df['prix'].astype(float)
        fig1 = px.pie(values=df['categorie'].value_counts().values,
                      names=[CATEGORIES[c]['name'] for c in df['categorie'].value_counts().index],
                      color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig1, use_container_width=True)
        fig2 = px.bar(df.groupby('ville')['prix'].mean().reset_index(),
                      x='ville', y='prix', title="Prix moyen par ville")
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(df, use_container_width=True)
    if st.button("← Retour"):
        st.session_state.show_stats = False
        st.rerun()


def admin_dashboard():
    st.header("🔐 Tableau d'administration")
    tabs = st.tabs(["Utilisateurs", "Produits", "Statistiques"])

    with tabs[0]:
        st.subheader("Utilisateurs enregistrés")
        users = st.session_state.get('users', [])
        if not users:
            st.info("Aucun utilisateur.")
        else:
            df = pd.DataFrame(users)
            if 'password' in df.columns:
                df = df.drop(columns=['password'])
            st.dataframe(df, use_container_width=True)

    with tabs[1]:
        st.subheader("Gérer les produits")
        category_options = {info["name"]: cid for cid, info in CATEGORIES.items()}
        with st.expander("➕ Ajouter un produit (Admin)"):
            with st.form("admin_add_product_form"):
                p_name   = st.text_input("Nom du produit")
                p_city   = st.text_input("Ville")
                p_price  = st.number_input("Prix (FCFA)", min_value=0, step=100)
                p_date   = st.date_input("Date")
                p_cat_n  = st.selectbox("Catégorie", list(category_options.keys()))
                p_vendeur = st.text_input("Vendeur")
                p_contact = st.text_input("Contact")
                if st.form_submit_button("Ajouter"):
                    new_product = {
                        "produit": p_name, "ville": p_city, "prix": str(p_price),
                        "date": str(p_date), "categorie": category_options[p_cat_n],
                        "vendeur": p_vendeur, "contact": p_contact
                    }
                    st.session_state.products.append(new_product)
                    save_products()
                    st.success("Produit ajouté.")

        st.markdown("---")
        if not st.session_state.products:
            st.info("Aucun produit.")
        else:
            st.dataframe(pd.DataFrame(st.session_state.products), use_container_width=True)
            for idx, prod in enumerate(st.session_state.products):
                cols = st.columns([3, 1, 1])
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

            if 'admin_edit_index' in st.session_state:
                i = st.session_state.admin_edit_index
                if 0 <= i < len(st.session_state.products):
                    prod = st.session_state.products[i]
                    st.markdown("---")
                    st.subheader(f"Éditer: {prod.get('produit')}")
                    cat_names = list(category_options.keys())
                    prod_cat_id   = prod.get('categorie')
                    prod_cat_name = CATEGORIES.get(prod_cat_id, {}).get('name')
                    default_idx   = cat_names.index(prod_cat_name) if prod_cat_name in cat_names else 0
                    try:
                        default_price = float(prod.get('prix', 0))
                    except Exception:
                        default_price = 0.0
                    try:
                        default_date = datetime.fromisoformat(prod.get('date')) if prod.get('date') else datetime.now()
                    except Exception:
                        default_date = datetime.now()
                    with st.form("admin_edit_form"):
                        e_name    = st.text_input("Nom",     value=prod.get('produit',''))
                        e_city    = st.text_input("Ville",   value=prod.get('ville',''))
                        e_price   = st.number_input("Prix",  value=default_price, step=100.0)
                        e_date    = st.date_input("Date",    value=default_date)
                        e_cat     = st.selectbox("Catégorie", cat_names, index=default_idx)
                        e_vendeur = st.text_input("Vendeur", value=prod.get('vendeur',''))
                        e_contact = st.text_input("Contact", value=prod.get('contact',''))
                        col_c, col_s = st.columns([1, 2])
                        with col_c:
                            if st.form_submit_button("Annuler"):
                                del st.session_state['admin_edit_index']
                                st.rerun()
                        with col_s:
                            if st.form_submit_button("Enregistrer"):
                                prod.update({
                                    'produit': e_name, 'ville': e_city, 'prix': str(int(e_price)),
                                    'date': str(e_date),
                                    'categorie': next(
                                        (cid for cid, info in CATEGORIES.items() if info['name'] == e_cat),
                                        prod.get('categorie')),
                                    'vendeur': e_vendeur, 'contact': e_contact
                                })
                                save_products()
                                del st.session_state['admin_edit_index']
                                st.success("Produit mis à jour.")
                                st.rerun()

    with tabs[2]:
        admin_stats_tab()


def get_month_purchases(purchases, month_offset=0):
    from datetime import date
    today  = date.today()
    tm     = today.month + month_offset
    ty     = today.year
    if tm <= 0:
        tm += 12; ty -= 1
    elif tm > 12:
        tm -= 12; ty += 1
    result = []
    for p in purchases:
        try:
            d = datetime.fromisoformat(p.get('date_achat', '')).date()
            if d.month == tm and d.year == ty:
                result.append(p)
        except Exception:
            pass
    return result


def admin_stats_tab():
    st.subheader("📊 Statistiques des achats")
    purchases = st.session_state.get('purchases', [])
    if not purchases:
        st.info("Aucun achat enregistré.")
        return
    curr  = get_month_purchases(purchases, 0)
    prev  = get_month_purchases(purchases, -1)
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Total achats",         len(purchases))
    with col2: st.metric("Achats ce mois",        len(curr))
    with col3: st.metric("Achats mois précédent", len(prev))

    st.markdown("---")
    st.subheader("Produits les plus achetés par catégorie")
    from collections import Counter
    cat_stats = {}
    for p in purchases:
        cat  = p.get('categorie','inconnu')
        prod = p.get('produit','inconnu')
        cat_stats.setdefault(cat, Counter())[prod] += 1

    valid_cats = [c for c in cat_stats if c in CATEGORIES]
    if valid_cats:
        cat_tabs = st.tabs([CATEGORIES[c]['name'] for c in valid_cats])
        for tab, cat in zip(cat_tabs, valid_cats):
            with tab:
                top = cat_stats[cat].most_common(5)
                for prod, count in top:
                    st.write(f"**{prod}**: {count} achats")
                if top:
                    fig = px.bar(pd.DataFrame(top, columns=['Produit','Achats']),
                                 x='Produit', y='Achats',
                                 title=f"Top produits — {CATEGORIES[cat]['name']}")
                    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Liste complète des achats")
    st.dataframe(pd.DataFrame(purchases), use_container_width=True)


def cart_page():
    st.header("🧾 Mon Panier")
    current_user = st.session_state.get('current_user')
    cart = st.session_state.user_carts.get(current_user, []) if current_user else st.session_state.get('cart', [])

    if not cart:
        if current_user:
            st.info("Panier vide.")
            if st.button("🛍️ Aller au Marketplace"):
                st.session_state.page = 'marketplace'; st.rerun()
        else:
            st.info("Connectez-vous pour sauvegarder votre panier.")
            if st.button("🔑 Se connecter"):
                st.session_state.page = 'login'; st.rerun()
        return

    st.subheader("Ajouter un produit au panier")
    products_list = st.session_state.get('products', [])
    if products_list:
        product_names = [p.get('produit','—') for p in products_list]
        col_a, col_b = st.columns([3, 1])
        with col_a:
            sel = st.selectbox("Choisir un produit", ["-- Choisir --"] + product_names, key="cart_add_select")
        with col_b:
            if st.button("Ajouter", key="cart_add_btn"):
                if sel and sel != "-- Choisir --":
                    prod = next((p for p in products_list if p.get('produit') == sel), None)
                    if prod:
                        add_to_cart_item({
                            'produit': prod.get('produit'), 'prix': prod.get('prix'),
                            'vendeur': prod.get('vendeur','—'), 'contact': prod.get('contact','—'),
                            'categorie': prod.get('categorie'), 'ville': prod.get('ville','—'),
                            'date': prod.get('date','')
                        })
                        st.success(f"{sel} ajouté au panier.")
                        st.rerun()

    total = 0.0
    for i, item in enumerate(list(cart)):
        cols = st.columns([3, 1, 1])
        with cols[0]:
            st.write(f"**{item.get('produit')}** — {item.get('vendeur','—')}")
            st.write(f"📍 {item.get('ville','—')} — 📅 {item.get('date','—')}")
        with cols[1]:
            try:
                price_val = float(item.get('prix', 0))
            except Exception:
                price_val = 0.0
            st.write(f"{price_val:.0f} FCFA")
        with cols[2]:
            qty_key = f"qty_{'user' if current_user else 'anon'}_{i}"
            current_qty = int(item.get('quantity', 1)) if item.get('quantity') else 1
            new_qty = st.number_input("Qté", min_value=1, value=current_qty, key=qty_key)
            if new_qty != current_qty and st.button("Mettre à jour", key=f"update_qty_{i}"):
                item['quantity'] = int(new_qty)
                if current_user:
                    _persist_user_cart(current_user)
                st.success("Quantité mise à jour.")
                st.rerun()
        try:
            total += float(item.get('prix', 0)) * int(item.get('quantity', 1))
        except Exception:
            pass

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Vider le panier"):
            if current_user:
                st.session_state.user_carts[current_user] = []
                supabase.table("carts").delete().eq("username", current_user).execute()
            else:
                st.session_state.cart = []
            st.success("Panier vidé.")
            st.rerun()
    with col2:
        st.metric("Total", f"{total:.0f} FCFA")

    st.markdown("---")
    st.subheader("Gérer les articles")
    for i, item in enumerate(list(cart)):
        cols = st.columns([3, 1])
        with cols[0]:
            st.write(f"**{item.get('produit')}** — {item.get('prix')} FCFA — {item.get('vendeur')}")
        with cols[1]:
            if st.button("Supprimer", key=f"remove_{i}"):
                if current_user:
                    st.session_state.user_carts[current_user].pop(i)
                    _persist_user_cart(current_user)
                else:
                    try:
                        st.session_state.cart.pop(i)
                    except Exception:
                        pass
                st.success("Article supprimé.")
                st.rerun()

    st.markdown("---")
    if st.button("Passer au paiement (simulation)"):
        buyer       = st.session_state.get('current_user', 'Anonyme')
        source_cart = (st.session_state.user_carts.get(current_user, [])
                       if current_user else st.session_state.get('cart', []))
        for item in list(source_cart):
            st.session_state.purchases.append({
                'produit': item.get('produit'), 'prix': item.get('prix'),
                'vendeur': item.get('vendeur'), 'contact': item.get('contact'),
                'categorie': item.get('categorie'),
                'date_achat': str(datetime.now()), 'acheteur': buyer
            })
        save_purchases(st.session_state.purchases)
        if current_user:
            st.session_state.user_carts[current_user] = []
            supabase.table("carts").delete().eq("username", current_user).execute()
        else:
            st.session_state.cart = []
        st.success("Paiement simulé réussi.")
        st.rerun()


def profile_page():
    st.header("👤 Mon Profil")
    current = st.session_state.get('current_user')
    if not current:
        st.info("Aucun utilisateur connecté.")
        return
    user = next((u for u in st.session_state.get('users', []) if u.get('username') == current), None)
    if not user:
        st.error("Utilisateur introuvable.")
        return
    safe_user = {k: v for k, v in user.items() if k != 'password' and not k.startswith('reset_')}
    st.subheader(safe_user.get('username','—'))
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("**Email**"); st.write("**Inscrit le**")
    with col2:
        st.write(safe_user.get('email','—')); st.write(safe_user.get('created_at','—'))
    st.markdown("---")
    with st.form("update_profile_form"):
        new_email = st.text_input("Email", value=safe_user.get('email',''))
        if st.form_submit_button("Mettre à jour"):
            user['email'] = new_email
            save_users(st.session_state.get('users', []))
            st.success("Profil mis à jour.")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
#  NAVIGATION PRINCIPALE
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("# 📊 KASSUA")
    if st.session_state.logged_in:
        st.markdown(f"Connecté en tant que: **{st.session_state.user_type}**")
        st.markdown("---")
        if st.session_state.user_type == "buyer":
            if st.button("🛍️ Marketplace", use_container_width=True):
                st.session_state.page = "marketplace"; st.rerun()
            cu = st.session_state.get('current_user')
            count = len(st.session_state.user_carts.get(cu, [])) if cu else len(st.session_state.get('cart', []))
            cart_label = "📋 Mon Panier" + (f" ({count})" if count else "")
            if st.button(cart_label, use_container_width=True):
                st.session_state.page = "cart"; st.rerun()
            if st.button("👤 Mon Profil", use_container_width=True):
                st.session_state.page = "profile"; st.rerun()
        elif st.session_state.user_type == "admin":
            if st.button("👨‍💻 Tableau Admin", use_container_width=True):
                st.session_state.page = "admin"; st.rerun()
        st.markdown("---")
        if st.button("🚪 Déconnexion", use_container_width=True, type="secondary"):
            preserve = ['logged_in','user_type','products','users','current_user']
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.current_user = None
            for key in list(st.session_state.keys()):
                if key not in preserve:
                    del st.session_state[key]
            st.rerun()
    else:
        st.markdown("Bienvenue sur Kassua!")
        st.markdown("---")
        st.markdown("### Connectez-vous pour accéder:")
        st.markdown("- 🛍️ **Espace Client**: Parcourir et acheter")

if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.user_type == "buyer":
        page = st.session_state.get('page','marketplace')
        if page == 'profile':
            profile_page()
        elif page == 'cart':
            cart_page()
        else:
            marketplace_page()
    elif st.session_state.user_type == "admin":
        admin_dashboard()


# ═══════════════════════════════════════════════════════════════
#  SQL À EXÉCUTER UNE SEULE FOIS DANS SUPABASE (SQL Editor)
# ═══════════════════════════════════════════════════════════════
#
# -- Table users
# create table if not exists users (
#   id           bigint generated always as identity primary key,
#   username     text unique not null,
#   email        text unique not null,
#   password     text not null,
#   created_at   text,
#   reset_token  text,
#   reset_expires text,
#   is_admin     boolean default false
# );
#
# -- Table products
# create table if not exists products (
#   id        bigint generated always as identity primary key,
#   produit   text not null,
#   ville     text,
#   prix      text,
#   date      text,
#   categorie text,
#   vendeur   text,
#   contact   text
# );
#
# -- Table purchases
# create table if not exists purchases (
#   id         bigint generated always as identity primary key,
#   produit    text not null,
#   prix       text,
#   vendeur    text,
#   contact    text,
#   categorie  text,
#   date_achat text,
#   acheteur   text
# );
#
# -- Table carts
# create table if not exists carts (
#   id        bigint generated always as identity primary key,
#   username  text not null,
#   produit   text not null,
#   prix      text,
#   vendeur   text,
#   contact   text,
#   categorie text,
#   ville     text,
#   date      text,
#   quantity  integer default 1
# );

