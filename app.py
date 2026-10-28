import os
import uuid
from flask import (
    Flask, render_template, request, redirect, url_for,
    jsonify, session, flash, send_from_directory, abort
)
from flask_cors import CORS
from config import Config

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import services
from services.db import query, execute, get_engine, init_tables
from services.auth_service import register_user, authenticate_user, get_user_by_id, update_user_profile
from services.product_service import (
    get_products, get_product_by_slug, get_product_by_id,
    get_trending_products, get_deals_of_the_day, get_spotlight_products,
    get_new_launches, get_categories, get_brands, get_banners,
    get_articles, get_article_by_slug, create_product, update_product, delete_product
)
from services.cart_service import (
    get_cart_items, add_to_cart, update_cart_quantity,
    remove_from_cart, clear_cart, get_cart_summary
)
from services.order_service import (
    create_order, get_user_orders, get_order_by_id,
    get_all_orders, update_order_status, get_user_addresses, add_user_address
)
from services.lab_service import (
    get_lab_tests, get_lab_test_by_slug, get_lab_test_by_id,
    get_lab_categories, create_lab_booking, get_user_bookings, get_all_bookings
)
from services.prescription_service import (
    save_prescription, get_user_prescriptions, get_all_prescriptions, update_prescription_status
)

@app.before_request
def ensure_session_and_cart():
    if 'cart_session_id' not in session:
        session['cart_session_id'] = str(uuid.uuid4())
    if 'user_pincode' not in session:
        session['user_pincode'] = '110001'
    if 'user_city' not in session:
        session['user_city'] = 'New Delhi'

@app.context_processor
def inject_global_data():
    """Injects categories, cart count, and user data into all templates"""
    session_id = session.get('cart_session_id')
    user_id = session.get('user_id')
    cart_summary = get_cart_summary(session_id, user_id)
    categories = get_categories()
    
    current_user = None
    if user_id:
        current_user = get_user_by_id(user_id)
        
    return {
        'global_categories': categories,
        'global_cart_count': cart_summary['items_count'],
        'global_cart_total': cart_summary['final_total'],
        'current_user': current_user,
        'user_pincode': session.get('user_pincode', '110001'),
        'user_city': session.get('user_city', 'New Delhi'),
        'db_engine': get_engine()
    }

# -------------------------------------------------------------
# 1. PAGE ROUTES
# -------------------------------------------------------------

@app.route('/')
def home():
    """Homepage with all 16+ PharmEasy sections in exact reference order"""
    banners = get_banners(active_only=True)
    categories = get_categories()
    deals = get_deals_of_the_day(limit=8)
    trending = get_trending_products(limit=8)
    lab_tests = get_lab_tests(frequently_booked_only=True)
    brands = get_brands()
    new_launches = get_new_launches(limit=8)
    spotlight = get_spotlight_products(limit=6)
    articles = get_articles(limit=4)
    
    return render_template(
        'index.html',
        banners=banners,
        categories=categories,
        deals=deals,
        trending=trending,
        lab_tests=lab_tests,
        brands=brands,
        new_launches=new_launches,
        spotlight=spotlight,
        articles=articles
    )

@app.route('/products')
def products():
    """Medicine & Healthcare product listing page with filtering and sorting"""
    category_slug = request.args.get('category', 'all')
    brand_slug = request.args.get('brand', 'all')
    sort = request.args.get('sort', 'popular')
    search = request.args.get('search', '')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    prescription_only = request.args.get('rx') == '1'

    prods = get_products(
        category_slug=category_slug,
        brand_slug=brand_slug,
        search=search,
        sort=sort,
        min_price=min_price,
        max_price=max_price,
        prescription_only=prescription_only
    )
    categories = get_categories()
    brands = get_brands()

    active_category = None
    if category_slug != 'all':
        active_category = query("SELECT * FROM categories WHERE slug = %s", (category_slug,), fetchone=True)

    return render_template(
        'products.html',
        products=prods,
        categories=categories,
        brands=brands,
        selected_category=category_slug,
        selected_brand=brand_slug,
        selected_sort=sort,
        search_query=search,
        active_category=active_category,
        prescription_only=prescription_only
    )

@app.route('/product/<slug>')
def product_detail(slug):
    """Product details page with composition, uses, dosage, stock, related items"""
    product = get_product_by_slug(slug)
    if not product:
        abort(404)

    # Fetch related products from same category
    related_products = get_products(category_slug=product['category_slug'], limit=4)
    # Filter out current product
    related_products = [p for p in related_products if p['id'] != product['id']]

    return render_template(
        'product_detail.html',
        product=product,
        related_products=related_products
    )

@app.route('/search')
def search():
    """Search results page"""
    query_text = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'popular')
    category_slug = request.args.get('category', 'all')
    
    prods = []
    if query_text:
        prods = get_products(search=query_text, category_slug=category_slug, sort=sort)
        
    categories = get_categories()
    return render_template(
        'search.html',
        products=prods,
        query=query_text,
        categories=categories,
        selected_category=category_slug,
        selected_sort=sort,
        total_results=len(prods)
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        res = authenticate_user(email, password)
        if res['success']:
            user = res['user']
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f"Welcome back, {user['name']}!", 'success')
            
            # Associate guest cart items with user
            session_id = session.get('cart_session_id')
            if session_id:
                execute("UPDATE cart_items SET user_id = %s WHERE session_id = %s", (user['id'], session_id))
                
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('home'))
        else:
            flash(res['message'], 'error')

    return render_template('auth.html', mode='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        password = request.form.get('password', '')
        
        if not name or not email or not phone or not password:
            flash("All fields are required.", 'error')
            return render_template('auth.html', mode='register')

        res = register_user(name, email, phone, password)
        if res['success']:
            user = res['user']
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash(f"Account created successfully! Welcome to PharmEasy, {user['name']}.", 'success')
            return redirect(url_for('home'))
        else:
            flash(res['message'], 'error')

    return render_template('auth.html', mode='register')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    flash("You have been signed out successfully.", 'info')
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    """Shopping cart page with order summary and coupon application"""
    session_id = session.get('cart_session_id')
    user_id = session.get('user_id')
    coupon_code = request.args.get('coupon')
    
    summary = get_cart_summary(session_id, user_id, coupon_code)
    available_coupons = query("SELECT * FROM coupons WHERE is_active = 1 LIMIT 4")
    
    return render_template(
        'cart.html',
        summary=summary,
        coupons=available_coupons,
        active_coupon=coupon_code
    )

@app.route('/checkout')
def checkout():
    """Checkout demo page with address selector, delivery slots, and payment simulator"""
    session_id = session.get('cart_session_id')
    user_id = session.get('user_id')
    coupon_code = request.args.get('coupon')
    
    summary = get_cart_summary(session_id, user_id, coupon_code)
    if not summary['items']:
        flash("Your cart is empty. Add products before proceeding to checkout.", 'warning')
        return redirect(url_for('products'))

    addresses = []
    if user_id:
        addresses = get_user_addresses(user_id)

    return render_template(
        'checkout.html',
        summary=summary,
        addresses=addresses,
        active_coupon=coupon_code
    )

@app.route('/prescription', methods=['GET', 'POST'])
def prescription():
    """Prescription upload page with file validation and callback request"""
    if request.method == 'POST':
        user_id = session.get('user_id')
        file = request.files.get('prescription_file')
        patient_data = {
            'patient_name': request.form.get('patient_name', ''),
            'patient_age': request.form.get('patient_age', 30),
            'patient_gender': request.form.get('patient_gender', 'Male'),
            'phone': request.form.get('phone', ''),
            'notes': request.form.get('notes', ''),
            'delivery_pincode': request.form.get('delivery_pincode', '110001'),
            'request_callback': request.form.get('request_callback') == 'on'
        }
        res = save_prescription(user_id, file, patient_data)
        if res['success']:
            flash(res['message'], 'success')
            if user_id:
                return redirect(url_for('profile', tab='prescriptions'))
            return redirect(url_for('prescription_success', rx_id=res['prescription_id']))
        else:
            flash(res['message'], 'error')

    return render_template('prescription.html')

@app.route('/prescription/success/<int:rx_id>')
def prescription_success(rx_id):
    rx = query("SELECT * FROM prescriptions WHERE id = %s", (rx_id,), fetchone=True)
    return render_template('prescription_success.html', prescription=rx)

@app.route('/lab-tests')
def lab_tests():
    """Lab tests and full body checkups catalog"""
    category = request.args.get('category', 'all')
    tests = get_lab_tests(category=category)
    categories = get_lab_categories()
    
    return render_template(
        'lab_tests.html',
        lab_tests=tests,
        categories=categories,
        selected_category=category
    )

@app.route('/offers')
def offers():
    """Offers and coupons page"""
    category = request.args.get('category', 'All')
    sql = "SELECT * FROM coupons WHERE is_active = 1"
    params = []
    if category != 'All':
        sql += " AND (category = %s OR category = 'All')"
        params.append(category)
    sql += " ORDER BY discount_value DESC"
    coupons = query(sql, tuple(params))
    
    return render_template('offers.html', coupons=coupons, selected_category=category)

@app.route('/profile')
def profile():
    """User profile, order history, lab bookings, and saved addresses"""
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your profile and order history.", 'info')
        return redirect(url_for('login', next=request.path))

    tab = request.args.get('tab', 'orders')
    user = get_user_by_id(user_id)
    orders = get_user_orders(user_id)
    lab_bookings = get_user_bookings(user_id)
    prescriptions = get_user_prescriptions(user_id)
    addresses = get_user_addresses(user_id)

    return render_template(
        'profile.html',
        user=user,
        orders=orders,
        lab_bookings=lab_bookings,
        prescriptions=prescriptions,
        addresses=addresses,
        active_tab=tab
    )

@app.route('/order/<order_number>')
def order_success(order_number):
    """Order confirmation and tracking view"""
    ord = query("SELECT * FROM orders WHERE order_number = %s", (order_number,), fetchone=True)
    if not ord:
        abort(404)
    full_order = get_order_by_id(ord['id'])
    return render_template('order_success.html', order=full_order)

@app.route('/article/<slug>')
def article_detail(slug):
    """Full health article view"""
    art = get_article_by_slug(slug)
    if not art:
        abort(404)
    other_articles = [a for a in get_articles(limit=3) if a['id'] != art['id']]
    return render_template('article_detail.html', article=art, other_articles=other_articles)

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard for product & category management and orders"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    # Require admin role
    if not user_id or user_role != 'admin':
        flash("Admin credentials required to access the dashboard. Login as admin@pharmeasy.com (pw: admin123).", 'error')
        return redirect(url_for('login', next=request.path))

    total_revenue_row = query("SELECT SUM(total_amount) as total FROM orders WHERE payment_status = 'Paid'", fetchone=True)
    total_revenue = total_revenue_row['total'] or 0.0

    total_orders_row = query("SELECT COUNT(*) as cnt FROM orders", fetchone=True)
    total_products_row = query("SELECT COUNT(*) as cnt FROM products", fetchone=True)
    total_users_row = query("SELECT COUNT(*) as cnt FROM users WHERE role = 'customer'", fetchone=True)

    products_list = get_products(limit=100)
    categories = get_categories()
    brands = get_brands()
    orders_list = get_all_orders()
    bookings_list = get_all_bookings()
    prescriptions_list = get_all_prescriptions()

    return render_template(
        'admin.html',
        stats={
            'total_revenue': round(total_revenue, 2),
            'total_orders': total_orders_row['cnt'],
            'total_products': total_products_row['cnt'],
            'total_users': total_users_row['cnt']
        },
        products=products_list,
        categories=categories,
        brands=brands,
        orders=orders_list,
        bookings=bookings_list,
        prescriptions=prescriptions_list
    )

# Static file serving for uploads
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# -------------------------------------------------------------
# 2. REST API ENDPOINTS
# -------------------------------------------------------------

@app.route('/api/pincode/set', methods=['POST'])
def api_set_pincode():
    data = request.get_json() or {}
    pincode = str(data.get('pincode', '110001')).strip()
    city = data.get('city', 'New Delhi')
    if len(pincode) == 6 and pincode.isdigit():
        session['user_pincode'] = pincode
        session['user_city'] = city
        return jsonify({'success': True, 'pincode': pincode, 'city': city})
    return jsonify({'success': False, 'message': 'Please enter a valid 6-digit Indian PIN code.'}), 400

@app.route('/api/cart', methods=['GET'])
def api_get_cart():
    session_id = session.get('cart_session_id')
    user_id = session.get('user_id')
    coupon = request.args.get('coupon')
    summary = get_cart_summary(session_id, user_id, coupon)
    return jsonify({'success': True, 'cart': summary})

@app.route('/api/cart/add', methods=['POST'])
def api_add_to_cart():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID is required'}), 400
        
    session_id = session.get('cart_session_id')
    user_id = session.get('user_id')
    res = add_to_cart(session_id, product_id, quantity, user_id)
    summary = get_cart_summary(session_id, user_id)
    return jsonify({
        'success': True,
        'message': 'Product added to cart!',
        'cart_count': summary['items_count'],
        'cart_total': summary['final_total']
    })

@app.route('/api/cart/update', methods=['POST'])
def api_update_cart():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    session_id = session.get('cart_session_id')
    user_id = session.get('user_id')
    update_cart_quantity(session_id, product_id, quantity, user_id)
    summary = get_cart_summary(session_id, user_id)
    return jsonify({'success': True, 'cart': summary})

@app.route('/api/cart/remove', methods=['POST'])
def api_remove_from_cart():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    session_id = session.get('cart_session_id')
    user_id = session.get('user_id')
    remove_from_cart(session_id, product_id, user_id)
    summary = get_cart_summary(session_id, user_id)
    return jsonify({'success': True, 'cart': summary})

@app.route('/api/cart/clear', methods=['POST'])
def api_clear_cart():
    session_id = session.get('cart_session_id')
    user_id = session.get('user_id')
    clear_cart(session_id, user_id)
    return jsonify({'success': True, 'message': 'Cart cleared'})

@app.route('/api/coupons/apply', methods=['POST'])
def api_apply_coupon():
    data = request.get_json() or {}
    code = data.get('code', '').strip().upper()
    session_id = session.get('cart_session_id')
    user_id = session.get('user_id')
    summary = get_cart_summary(session_id, user_id, code)
    
    if summary['applied_coupon'] and 'error' not in summary['applied_coupon']:
        return jsonify({
            'success': True,
            'message': f"Coupon {code} applied successfully! You saved ₹{summary['coupon_discount']}",
            'cart': summary
        })
    elif summary['applied_coupon'] and 'error' in summary['applied_coupon']:
        return jsonify({'success': False, 'message': summary['applied_coupon']['error']}), 400
    else:
        return jsonify({'success': False, 'message': 'Invalid coupon code or expired.'}), 400

@app.route('/api/orders/create', methods=['POST'])
def api_create_order():
    data = request.get_json() or {}
    user_id = session.get('user_id')
    session_id = session.get('cart_session_id')
    
    # If not logged in, create a quick guest customer record or require login
    if not user_id:
        # Check if customer info provided
        customer_name = data.get('customer_name', 'Guest Customer')
        customer_email = data.get('customer_email', f"guest_{int(uuid.uuid4().int % 1000000)}@pharmeasy.com")
        customer_phone = data.get('customer_phone', '9876500000')
        res_user = register_user(customer_name, customer_email, customer_phone, 'guest123')
        if res_user['success']:
            user_id = res_user['user']['id']
            session['user_id'] = user_id
            session['user_name'] = customer_name
        else:
            existing = query("SELECT id FROM users WHERE email = %s OR phone = %s", (customer_email, customer_phone), fetchone=True)
            user_id = existing['id']
            session['user_id'] = user_id

    # Handle address
    address_id = data.get('address_id')
    if not address_id and 'address_data' in data:
        address_id = add_user_address(user_id, data['address_data'])

    payment_method = data.get('payment_method', 'UPI')
    coupon_code = data.get('coupon_code')
    delivery_slot = data.get('delivery_slot', 'Standard Delivery (24-48 Hours)')

    res = create_order(user_id, session_id, address_id, payment_method, coupon_code, delivery_slot)
    return jsonify(res)

@app.route('/api/lab-tests/book', methods=['POST'])
def api_book_lab_test():
    data = request.get_json() or {}
    user_id = session.get('user_id')
    if not user_id:
        # Auto register/find guest
        customer_name = data.get('patient_name', 'Guest')
        customer_phone = data.get('phone', '9876500000')
        customer_email = f"guest_lab_{int(uuid.uuid4().int % 1000000)}@pharmeasy.com"
        reg = register_user(customer_name, customer_email, customer_phone, 'guest123')
        if reg['success']:
            user_id = reg['user']['id']
            session['user_id'] = user_id
        else:
            existing = query("SELECT id FROM users WHERE phone = %s", (customer_phone,), fetchone=True)
            user_id = existing['id'] if existing else 1
            session['user_id'] = user_id

    res = create_lab_booking(user_id, data)
    return jsonify(res)

@app.route('/api/search/suggestions')
def api_search_suggestions():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    results = query(
        """SELECT name, slug, price, mrp, image_url, 'product' as type
        FROM products WHERE name LIKE %s OR composition LIKE %s
        LIMIT 6""",
        (f"%{q}%", f"%{q}%")
    )
    return jsonify(results)

# -------------------------------------------------------------
# 3. ADMIN API ENDPOINTS
# -------------------------------------------------------------

@app.route('/api/admin/products/create', methods=['POST'])
def api_admin_create_product():
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin unauthorized'}), 403
    data = request.get_json() or {}
    try:
        pid = create_product(data)
        return jsonify({'success': True, 'product_id': pid, 'message': 'Product added successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/admin/products/<int:id>/update', methods=['POST'])
def api_admin_update_product(id):
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin unauthorized'}), 403
    data = request.get_json() or {}
    try:
        update_product(id, data)
        return jsonify({'success': True, 'message': 'Product updated successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/admin/products/<int:id>/delete', methods=['POST'])
def api_admin_delete_product(id):
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin unauthorized'}), 403
    try:
        delete_product(id)
        return jsonify({'success': True, 'message': 'Product deleted successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/admin/orders/<int:id>/status', methods=['POST'])
def api_admin_update_order_status(id):
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin unauthorized'}), 403
    data = request.get_json() or {}
    new_status = data.get('status')
    res = update_order_status(id, new_status)
    return jsonify(res)

@app.route('/api/admin/prescriptions/<int:id>/status', methods=['POST'])
def api_admin_update_prescription_status(id):
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin unauthorized'}), 403
    data = request.get_json() or {}
    new_status = data.get('status')
    res = update_prescription_status(id, new_status)
    return jsonify(res)

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    traceback.print_exc()
    return f"<h1>Internal Server Error (500)</h1><pre>{traceback.format_exc()}</pre>", 500

# -------------------------------------------------------------
# APPLICATION ENTRYPOINT
# -------------------------------------------------------------

if __name__ == '__main__':
    # Initialize DB tables if they don't exist
    init_tables()
    print("=" * 60)
    print(" PharmEasy E-Commerce Website Server Starting")
    print(f" Database Mode: {get_engine().upper()}")
    print(" Local URL: http://127.0.0.1:5000")
    print(" Admin Login: admin@pharmeasy.com / admin123")
    print(" Demo Customer: user@pharmeasy.com / user123")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)

