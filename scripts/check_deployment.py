"""
Streamlit Deployment Checker and Initializer
Verify the deployment is working correctly
"""

import sys
import sqlite3
from pathlib import Path

def check_database():
    """Vérifier que la base de données SQLite existe et est accessible"""
    db_path = Path("kassua.db")
    
    if not db_path.exists():
        print("⚠️  Base de données non trouvée. Création en cours...")
        # La base de données sera créée automatiquement par SQLAlchemy lors du premier lancement
        return False
    
    try:
        conn = sqlite3.connect("kassua.db")
        cursor = conn.cursor()
        
        # Vérifier les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['users', 'products', 'purchases', 'carts']
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            print(f"⚠️  Tables manquantes: {', '.join(missing_tables)}")
            print("   Les tables seront créées automatiquement lors du lancement.")
            return False
        
        print(f"✅ Base de données vérifiée: {len(tables)} tables trouvées")
        
        # Afficher le nombre d'enregistrements
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count} enregistrement(s)")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"❌ Erreur d'accès à la base de données: {e}")
        return False

def check_requirements():
    """Vérifier que tous les packages requis sont installés"""
    required = ['streamlit', 'pandas', 'plotly', 'sqlalchemy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Packages manquants: {', '.join(missing)}")
        print("   Installez-les avec: pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("=" * 50)
    print("🚀 KASSUA - Vérification de déploiement")
    print("=" * 50)
    print()
    
    print("📦 Vérification des dépendances:")
    req_ok = check_requirements()
    print()
    
    print("🗄️  Vérification de la base de données:")
    db_ok = check_database()
    print()
    
    if req_ok and db_ok:
        print("✅ Déploiement prêt! Lancez l'app avec: streamlit run app.py")
    elif req_ok:
        print("⚠️  Les prérequis sont installés.")
        print("   Lancez 'streamlit run app.py' - la base de données sera initialisée automatiquement.")
    else:
        print("❌ Problèmes détectés. Veuillez corriger les erreurs ci-dessus.")
        sys.exit(1)

if __name__ == "__main__":
    main()
