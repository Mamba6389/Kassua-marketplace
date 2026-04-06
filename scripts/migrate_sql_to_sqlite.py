#!/usr/bin/env python3
"""
Migration script: Convert MySQL habou.sql dump to SQLite database
This script reads the SQL file and creates an equivalent SQLite database
"""

import sqlite3
import re
from pathlib import Path

def extract_insert_data(sql_content):
    """Extract INSERT statements and parse them"""
    inserts = {}
    
    # Find all INSERT statements
    insert_pattern = r"INSERT INTO `(\w+)`.*?VALUES\s*(.*?)(?:;|(?=INSERT)|$)"
    matches = re.finditer(insert_pattern, sql_content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        table_name = match.group(1)
        values_str = match.group(2)
        
        if table_name not in inserts:
            inserts[table_name] = []
        
        # Parse value tuples
        value_pattern = r"\(([^)]+)\)"
        value_matches = re.finditer(value_pattern, values_str)
        
        for v_match in value_matches:
            raw_values = v_match.group(1)
            # Split by comma, but respect quoted strings
            values = []
            current = ""
            in_quotes = False
            
            for char in raw_values:
                if char == "'" and (not current or current[-1] != "\\"):
                    in_quotes = not in_quotes
                    current += char
                elif char == "," and not in_quotes:
                    values.append(current.strip())
                    current = ""
                else:
                    current += char
            
            if current:
                values.append(current.strip())
            
            # Clean values (remove quotes, handle NULL)
            cleaned = []
            for val in values:
                if val.upper() == "NULL":
                    cleaned.append(None)
                elif val.startswith("'") and val.endswith("'"):
                    # Remove quotes and unescape
                    cleaned.append(val[1:-1].replace("\\'", "'").replace("\\\\", "\\"))
                else:
                    try:
                        cleaned.append(int(val))
                    except:
                        try:
                            cleaned.append(float(val))
                        except:
                            cleaned.append(val)
            
            inserts[table_name].append(cleaned)
    
    return inserts

def create_sqlite_db(sql_file_path, output_db_path):
    """Convert SQL file to SQLite database"""
    
    # Read SQL file
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Create SQLite connection
    conn = sqlite3.connect(output_db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(100) UNIQUE NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at VARCHAR(100),
        reset_token VARCHAR(255),
        reset_expires VARCHAR(100),
        is_admin BOOLEAN DEFAULT 0
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produit VARCHAR(150) NOT NULL,
        ville VARCHAR(100),
        prix VARCHAR(50),
        date VARCHAR(50),
        categorie VARCHAR(100),
        vendeur VARCHAR(150),
        contact VARCHAR(150)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produit VARCHAR(150) NOT NULL,
        prix VARCHAR(50),
        vendeur VARCHAR(150),
        contact VARCHAR(150),
        categorie VARCHAR(100),
        date_achat VARCHAR(100),
        acheteur VARCHAR(100)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(150) NOT NULL,
        produit VARCHAR(150) NOT NULL,
        prix VARCHAR(50),
        vendeur VARCHAR(150),
        contact VARCHAR(150),
        categorie VARCHAR(150),
        ville VARCHAR(100),
        date VARCHAR(50),
        quantity INTEGER DEFAULT 1
    )
    ''')
    
    conn.commit()
    
    # Extract and insert data
    inserts = extract_insert_data(sql_content)
    
    # Map MySQL table names to columns
    table_columns = {
        'users': ['id', 'username', 'email', 'password', 'created_at', 'reset_token', 'reset_expires', 'is_admin'],
        'products': ['id', 'produit', 'ville', 'prix', 'date', 'categorie', 'vendeur', 'contact'],
        'purchases': ['id', 'produit', 'prix', 'vendeur', 'contact', 'categorie', 'date_achat', 'acheteur'],
        'carts': ['id', 'username', 'produit', 'prix', 'vendeur', 'contact', 'categorie', 'ville', 'date', 'quantity']
    }
    
    for table_name, rows in inserts.items():
        if table_name in table_columns:
            columns = table_columns[table_name]
            placeholders = ','.join(['?' for _ in columns])
            
            for row in rows:
                # Ensure we have the right number of columns
                if len(row) == len(columns):
                    insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                    cursor.execute(insert_sql, row)
    
    conn.commit()
    conn.close()
    
    print(f"✅ SQLite database created successfully: {output_db_path}")
    print(f"Tables migrated: {', '.join(inserts.keys())}")

if __name__ == "__main__":
    sql_file = "habou.sql"
    sqlite_db = "kassua.db"
    
    if Path(sql_file).exists():
        create_sqlite_db(sql_file, sqlite_db)
    else:
        print(f"❌ File not found: {sql_file}")
