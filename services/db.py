import os
import sqlite3
import pymysql
from pymysql.cursors import DictCursor
from config import Config

_engine_type = 'sqlite'  # or 'mysql'

def get_connection():
    """
    Attempts to connect to MySQL. If MySQL is unreachable and fallback is enabled,
    connects to SQLite.
    """
    global _engine_type
    
    # Try MySQL first if credentials provided
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            charset='utf8mb4',
            cursorclass=DictCursor,
            connect_timeout=2,
            autocommit=False
        )
        _engine_type = 'mysql'
        return conn, 'mysql'
    except Exception as e:
        if Config.AUTO_SQLITE_FALLBACK:
            # Fallback to SQLite
            os.makedirs(os.path.dirname(Config.SQLITE_DB_PATH), exist_ok=True)
            conn = sqlite3.connect(Config.SQLITE_DB_PATH)
            conn.row_factory = sqlite3.Row
            _engine_type = 'sqlite'
            return conn, 'sqlite'
        else:
            raise ConnectionError(f"Could not connect to MySQL: {e}")

def get_engine():
    return _engine_type

def adapt_sql(sql: str, target_engine: str) -> str:
    """
    Converts SQL query placeholders between MySQL (%s) and SQLite (?).
    """
    if target_engine == 'sqlite':
        # Replace %s with ? for SQLite
        return sql.replace('%s', '?')
    return sql

def query(sql: str, params=(), fetchone=False):
    """
    Executes a SELECT query and returns list of dictionaries or single dictionary.
    """
    conn, engine = get_connection()
    try:
        cursor = conn.cursor()
        adapted = adapt_sql(sql, engine)
        cursor.execute(adapted, params or ())
        
        if fetchone:
            row = cursor.fetchone()
            if row is None:
                return None
            return dict(row)
        else:
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()

def execute(sql: str, params=(), commit=True):
    """
    Executes INSERT/UPDATE/DELETE. Returns dict with lastrowid and rowcount.
    """
    conn, engine = get_connection()
    try:
        cursor = conn.cursor()
        adapted = adapt_sql(sql, engine)
        cursor.execute(adapted, params or ())
        
        last_id = cursor.lastrowid
        rowcount = cursor.rowcount
        
        if commit:
            conn.commit()
            
        return {'lastrowid': last_id, 'rowcount': rowcount}
    finally:
        conn.close()

def execute_many(sql: str, seq_of_params, commit=True):
    """
    Executes batch operations.
    """
    conn, engine = get_connection()
    try:
        cursor = conn.cursor()
        adapted = adapt_sql(sql, engine)
        cursor.executemany(adapted, seq_of_params)
        if commit:
            conn.commit()
        return cursor.rowcount
    finally:
        conn.close()

def init_tables():
    """
    Initializes tables in either MySQL or SQLite.
    """
    conn, engine = get_connection()
    try:
        cursor = conn.cursor()
        if engine == 'sqlite':
            # Create SQLite compatible schema
            cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                icon TEXT DEFAULT 'fas fa-pills',
                image_url TEXT,
                description TEXT,
                is_featured INTEGER DEFAULT 0,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                logo_url TEXT,
                description TEXT,
                is_featured INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                brand_id INTEGER,
                category_id INTEGER NOT NULL,
                description TEXT,
                composition TEXT,
                uses TEXT,
                dosage TEXT,
                side_effects TEXT,
                packaging TEXT DEFAULT 'Strip of 10 Tablets',
                mrp REAL NOT NULL,
                price REAL NOT NULL,
                discount_percent INTEGER DEFAULT 0,
                stock INTEGER DEFAULT 100,
                rating REAL DEFAULT 4.5,
                reviews_count INTEGER DEFAULT 120,
                image_url TEXT,
                prescription_required INTEGER DEFAULT 0,
                is_trending INTEGER DEFAULT 0,
                is_deal INTEGER DEFAULT 0,
                is_spotlight INTEGER DEFAULT 0,
                is_new_launch INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (brand_id) REFERENCES brands(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS lab_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                category TEXT DEFAULT 'Full Body Checkup',
                description TEXT,
                included_tests TEXT,
                fasting_required TEXT DEFAULT 'No Fasting Required',
                test_count INTEGER DEFAULT 1,
                turnaround_time TEXT DEFAULT 'Reports within 24 hours',
                mrp REAL NOT NULL,
                price REAL NOT NULL,
                discount_percent INTEGER DEFAULT 0,
                image_url TEXT,
                is_frequently_booked INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                pincode TEXT NOT NULL,
                address_line1 TEXT NOT NULL,
                address_line2 TEXT DEFAULT '',
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                address_type TEXT DEFAULT 'Home',
                is_default INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                address_id INTEGER,
                total_mrp REAL NOT NULL,
                discount REAL DEFAULT 0.00,
                coupon_code TEXT,
                coupon_discount REAL DEFAULT 0.00,
                delivery_fee REAL DEFAULT 0.00,
                platform_fee REAL DEFAULT 5.00,
                total_amount REAL NOT NULL,
                payment_method TEXT DEFAULT 'COD',
                payment_status TEXT DEFAULT 'Paid',
                order_status TEXT DEFAULT 'Placed',
                delivery_slot TEXT DEFAULT 'Standard Delivery (24-48 Hours)',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (address_id) REFERENCES addresses(id)
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                subtotal REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                patient_name TEXT NOT NULL,
                patient_age INTEGER,
                patient_gender TEXT DEFAULT 'Male',
                phone TEXT NOT NULL,
                file_path TEXT NOT NULL,
                notes TEXT,
                delivery_pincode TEXT DEFAULT '110001',
                request_callback INTEGER DEFAULT 1,
                status TEXT DEFAULT 'Pending Review',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS lab_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_number TEXT NOT NULL UNIQUE,
                user_id INTEGER,
                test_id INTEGER NOT NULL,
                patient_name TEXT NOT NULL,
                patient_age INTEGER NOT NULL,
                patient_gender TEXT DEFAULT 'Male',
                phone TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                sample_collection_address TEXT NOT NULL,
                pincode TEXT NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'Confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (test_id) REFERENCES lab_tests(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS coupons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                description TEXT,
                discount_type TEXT DEFAULT 'percentage',
                discount_value REAL NOT NULL,
                min_order_value REAL DEFAULT 0.00,
                max_discount REAL DEFAULT 500.00,
                category TEXT DEFAULT 'All',
                is_active INTEGER DEFAULT 1,
                expires_at TEXT
            );

            CREATE TABLE IF NOT EXISTS banners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subtitle TEXT,
                tag TEXT DEFAULT 'FLAT 25% OFF',
                image_url TEXT NOT NULL,
                target_url TEXT DEFAULT '/products',
                bg_gradient TEXT DEFAULT 'linear-gradient(135deg, #10847e 0%, #005a54 100%)',
                display_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                category TEXT DEFAULT 'Health & Nutrition',
                read_time TEXT DEFAULT '4 min read',
                doctor_reviewed TEXT DEFAULT 'Dr. Ananya Sharma, MBBS, MD',
                image_url TEXT NOT NULL,
                excerpt TEXT NOT NULL,
                content TEXT NOT NULL,
                published_at TEXT DEFAULT CURRENT_DATE
            );
            ''')
            conn.commit()
        else:
            # Read schema.sql for MySQL
            schema_path = os.path.join(Config.BASE_DIR, 'database', 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    statements = f.read().split(';')
                    for stmt in statements:
                        stmt = stmt.strip()
                        if stmt and not stmt.lower().startswith('create database') and not stmt.lower().startswith('use '):
                            cursor.execute(stmt)
                conn.commit()
    finally:
        conn.close()

