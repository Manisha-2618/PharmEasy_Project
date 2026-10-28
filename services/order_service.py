import time
import random
from services.db import query, execute
from services.cart_service import get_cart_summary, clear_cart

def generate_order_number():
    timestamp = int(time.time())
    rand = random.randint(100, 999)
    return f"PE-{timestamp}-{rand}"

def create_order(user_id, session_id, address_id, payment_method='UPI', coupon_code=None, delivery_slot='Standard Delivery (24-48 Hours)'):
    summary = get_cart_summary(session_id, user_id, coupon_code)
    if not summary['items']:
        return {'success': False, 'message': 'Cart is empty.'}

    order_number = generate_order_number()
    coupon_discount = summary['coupon_discount']
    
    order_res = execute(
        """INSERT INTO orders (
            order_number, user_id, address_id, total_mrp, discount,
            coupon_code, coupon_discount, delivery_fee, platform_fee,
            total_amount, payment_method, payment_status, order_status,
            delivery_slot
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            order_number, user_id, address_id, summary['total_mrp'], summary['total_savings'],
            coupon_code.upper() if coupon_code else None, coupon_discount,
            summary['delivery_fee'], summary['platform_fee'], summary['final_total'],
            payment_method, 'Paid' if payment_method != 'COD' else 'Pending',
            'Placed', delivery_slot
        )
    )
    order_id = order_res['lastrowid']

    # Insert items
    for item in summary['items']:
        execute(
            """INSERT INTO order_items (order_id, product_id, product_name, price, quantity, subtotal)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (order_id, item['product_id'], item['name'], item['price'], item['quantity'], item['item_subtotal'])
        )
        # Update stock
        execute(
            "UPDATE products SET stock = MAX(0, stock - %s) WHERE id = %s",
            (item['quantity'], item['product_id'])
        )

    # Clear user's cart
    clear_cart(session_id, user_id)

    return {
        'success': True,
        'order_id': order_id,
        'order_number': order_number,
        'total_amount': summary['final_total']
    }

def get_user_orders(user_id):
    orders = query(
        """SELECT o.*, a.full_name as recipient_name, a.city, a.pincode
        FROM orders o
        LEFT JOIN addresses a ON o.address_id = a.id
        WHERE o.user_id = %s
        ORDER BY o.id DESC""",
        (user_id,)
    )
    for ord in orders:
        items = query(
            """SELECT oi.*, p.image_url, p.packaging
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s""",
            (ord['id'],)
        )
        ord['items'] = items
        ord['order_items'] = items
    return orders

def get_order_by_id(order_id, user_id=None):
    if user_id:
        ord = query(
            """SELECT o.*, a.full_name as recipient_name, a.phone as recipient_phone,
               a.address_line1, a.address_line2, a.city, a.state, a.pincode
            FROM orders o
            LEFT JOIN addresses a ON o.address_id = a.id
            WHERE o.id = %s AND o.user_id = %s""",
            (order_id, user_id),
            fetchone=True
        )
    else:
        ord = query(
            """SELECT o.*, u.name as user_name, u.email as user_email, u.phone as user_phone,
               a.full_name as recipient_name, a.phone as recipient_phone,
               a.address_line1, a.address_line2, a.city, a.state, a.pincode
            FROM orders o
            JOIN users u ON o.user_id = u.id
            LEFT JOIN addresses a ON o.address_id = a.id
            WHERE o.id = %s""",
            (order_id,),
            fetchone=True
        )

    if ord:
        items = query(
            """SELECT oi.*, p.image_url, p.packaging, p.slug
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s""",
            (ord['id'],)
        )
        ord['items'] = items
        ord['order_items'] = items
    return ord

def get_all_orders():
    orders = query(
        """SELECT o.*, u.name as user_name, u.email as user_email,
           (SELECT COUNT(*) FROM order_items WHERE order_id = o.id) as item_count
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.id DESC"""
    )
    return orders

def update_order_status(order_id, new_status):
    valid_statuses = ['Placed', 'Processing', 'Dispatched', 'Delivered', 'Cancelled']
    if new_status not in valid_statuses:
        return {'success': False, 'message': 'Invalid status'}
    execute("UPDATE orders SET order_status = %s WHERE id = %s", (new_status, order_id))
    return {'success': True}

# Address helpers
def get_user_addresses(user_id):
    return query("SELECT * FROM addresses WHERE user_id = %s ORDER BY is_default DESC, id DESC", (user_id,))

def add_user_address(user_id, data):
    is_default = 1 if data.get('is_default') else 0
    if is_default:
        execute("UPDATE addresses SET is_default = 0 WHERE user_id = %s", (user_id,))

    res = execute(
        """INSERT INTO addresses (user_id, full_name, phone, pincode, address_line1, address_line2, city, state, address_type, is_default)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (user_id, data['full_name'], data['phone'], data['pincode'], data['address_line1'], data.get('address_line2', ''), data['city'], data['state'], data.get('address_type', 'Home'), is_default)
    )
    return res['lastrowid']
