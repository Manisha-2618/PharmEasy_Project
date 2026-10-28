import re
from services.db import query, execute

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text)

def get_products(category_slug=None, brand_slug=None, search=None, sort='popular', min_price=None, max_price=None, prescription_only=False, limit=None, offset=0):
    conditions = []
    params = []

    if category_slug and category_slug != 'all':
        conditions.append("c.slug = %s")
        params.append(category_slug)

    if brand_slug and brand_slug != 'all':
        conditions.append("b.slug = %s")
        params.append(brand_slug)

    if search:
        search_terms = f"%{search.strip()}%"
        conditions.append("(p.name LIKE %s OR p.description LIKE %s OR p.composition LIKE %s OR b.name LIKE %s OR c.name LIKE %s)")
        params.extend([search_terms, search_terms, search_terms, search_terms, search_terms])

    if min_price is not None:
        conditions.append("p.price >= %s")
        params.append(float(min_price))

    if max_price is not None:
        conditions.append("p.price <= %s")
        params.append(float(max_price))

    if prescription_only:
        conditions.append("p.prescription_required = 1")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    # Sorting
    order_clause = "ORDER BY p.rating DESC, p.reviews_count DESC"
    if sort == 'price_low':
        order_clause = "ORDER BY p.price ASC"
    elif sort == 'price_high':
        order_clause = "ORDER BY p.price DESC"
    elif sort == 'discount':
        order_clause = "ORDER BY p.discount_percent DESC"
    elif sort == 'newest':
        order_clause = "ORDER BY p.id DESC"

    limit_clause = ""
    if limit is not None:
        limit_clause = f"LIMIT {int(limit)} OFFSET {int(offset)}"

    sql = f"""
        SELECT 
            p.*, 
            c.name as category_name, c.slug as category_slug,
            b.name as brand_name, b.slug as brand_slug
        FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN brands b ON p.brand_id = b.id
        {where_clause}
        {order_clause}
        {limit_clause}
    """
    products = query(sql, tuple(params))
    return products

def get_product_by_slug(slug):
    sql = """
        SELECT 
            p.*, 
            c.name as category_name, c.slug as category_slug,
            b.name as brand_name, b.slug as brand_slug, b.logo_url as brand_logo
        FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN brands b ON p.brand_id = b.id
        WHERE p.slug = %s
    """
    return query(sql, (slug,), fetchone=True)

def get_product_by_id(product_id):
    sql = """
        SELECT 
            p.*, 
            c.name as category_name, c.slug as category_slug,
            b.name as brand_name, b.slug as brand_slug
        FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN brands b ON p.brand_id = b.id
        WHERE p.id = %s
    """
    return query(sql, (product_id,), fetchone=True)

def get_trending_products(limit=8):
    sql = """
        SELECT p.*, c.name as category_name, b.name as brand_name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN brands b ON p.brand_id = b.id
        WHERE p.is_trending = 1
        ORDER BY p.rating DESC
        LIMIT %s
    """
    return query(sql, (limit,))

def get_deals_of_the_day(limit=8):
    sql = """
        SELECT p.*, c.name as category_name, b.name as brand_name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN brands b ON p.brand_id = b.id
        WHERE p.is_deal = 1
        ORDER BY p.discount_percent DESC
        LIMIT %s
    """
    return query(sql, (limit,))

def get_spotlight_products(limit=6):
    sql = """
        SELECT p.*, c.name as category_name, b.name as brand_name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN brands b ON p.brand_id = b.id
        WHERE p.is_spotlight = 1
        LIMIT %s
    """
    return query(sql, (limit,))

def get_new_launches(limit=8):
    sql = """
        SELECT p.*, c.name as category_name, b.name as brand_name 
        FROM products p
        JOIN categories c ON p.category_id = c.id
        LEFT JOIN brands b ON p.brand_id = b.id
        WHERE p.is_new_launch = 1
        ORDER BY p.id DESC
        LIMIT %s
    """
    return query(sql, (limit,))

def get_categories(featured_only=False):
    sql = "SELECT * FROM categories"
    if featured_only:
        sql += " WHERE is_featured = 1"
    sql += " ORDER BY display_order ASC"
    return query(sql)

def get_brands(featured_only=False):
    sql = "SELECT * FROM brands"
    if featured_only:
        sql += " WHERE is_featured = 1"
    sql += " ORDER BY name ASC"
    return query(sql)

def get_banners(active_only=True):
    sql = "SELECT * FROM banners"
    if active_only:
        sql += " WHERE is_active = 1"
    sql += " ORDER BY display_order ASC"
    return query(sql)

def get_articles(limit=4):
    sql = "SELECT * FROM articles ORDER BY id DESC LIMIT %s"
    return query(sql, (limit,))

def get_article_by_slug(slug):
    sql = "SELECT * FROM articles WHERE slug = %s"
    return query(sql, (slug,), fetchone=True)

# Admin Operations
def create_product(data):
    slug = slugify(data.get('name', 'product'))
    # Ensure unique slug
    base_slug = slug
    counter = 1
    while query("SELECT id FROM products WHERE slug = %s", (slug,), fetchone=True):
        slug = f"{base_slug}-{counter}"
        counter += 1

    mrp = float(data.get('mrp', 0))
    discount = int(data.get('discount_percent', 0))
    price = round(mrp * (1 - (discount / 100)), 2)

    sql = """
        INSERT INTO products (
            name, slug, brand_id, category_id, description, composition,
            uses, dosage, side_effects, packaging, mrp, price, discount_percent,
            stock, image_url, prescription_required, is_trending, is_deal,
            is_spotlight, is_new_launch
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    res = execute(sql, (
        data['name'], slug, data.get('brand_id'), data['category_id'],
        data.get('description', ''), data.get('composition', ''),
        data.get('uses', ''), data.get('dosage', ''), data.get('side_effects', ''),
        data.get('packaging', 'Strip of 10 Tablets'), mrp, price, discount,
        int(data.get('stock', 50)), data.get('image_url', ''),
        1 if data.get('prescription_required') else 0,
        1 if data.get('is_trending') else 0,
        1 if data.get('is_deal') else 0,
        1 if data.get('is_spotlight') else 0,
        1 if data.get('is_new_launch') else 0
    ))
    return res['lastrowid']

def update_product(product_id, data):
    mrp = float(data.get('mrp', 0))
    discount = int(data.get('discount_percent', 0))
    price = round(mrp * (1 - (discount / 100)), 2)

    sql = """
        UPDATE products SET
            name = %s, brand_id = %s, category_id = %s, description = %s,
            composition = %s, uses = %s, dosage = %s, side_effects = %s,
            packaging = %s, mrp = %s, price = %s, discount_percent = %s,
            stock = %s, image_url = %s, prescription_required = %s,
            is_trending = %s, is_deal = %s, is_spotlight = %s, is_new_launch = %s
        WHERE id = %s
    """
    execute(sql, (
        data['name'], data.get('brand_id'), data['category_id'],
        data.get('description', ''), data.get('composition', ''),
        data.get('uses', ''), data.get('dosage', ''), data.get('side_effects', ''),
        data.get('packaging', 'Strip of 10 Tablets'), mrp, price, discount,
        int(data.get('stock', 50)), data.get('image_url', ''),
        1 if data.get('prescription_required') else 0,
        1 if data.get('is_trending') else 0,
        1 if data.get('is_deal') else 0,
        1 if data.get('is_spotlight') else 0,
        1 if data.get('is_new_launch') else 0,
        product_id
    ))
    return True

def delete_product(product_id):
    execute("DELETE FROM products WHERE id = %s", (product_id,))
    return True

