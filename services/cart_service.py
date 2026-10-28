from services.db import query, execute

def get_cart_items(session_id, user_id=None):
    if user_id:
        sql = """
            SELECT 
                ci.id as cart_item_id, ci.quantity, ci.product_id,
                p.name, p.slug, p.mrp, p.price, p.discount_percent,
                p.image_url, p.packaging, p.prescription_required, p.stock,
                (p.price * ci.quantity) as item_subtotal,
                (p.mrp * ci.quantity) as item_mrp_total
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.user_id = %s OR ci.session_id = %s
            ORDER BY ci.id DESC
        """
        return query(sql, (user_id, session_id))
    else:
        sql = """
            SELECT 
                ci.id as cart_item_id, ci.quantity, ci.product_id,
                p.name, p.slug, p.mrp, p.price, p.discount_percent,
                p.image_url, p.packaging, p.prescription_required, p.stock,
                (p.price * ci.quantity) as item_subtotal,
                (p.mrp * ci.quantity) as item_mrp_total
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.session_id = %s
            ORDER BY ci.id DESC
        """
        return query(sql, (session_id,))

def add_to_cart(session_id, product_id, quantity=1, user_id=None):
    quantity = max(1, int(quantity))
    
    # Check if item exists
    if user_id:
        existing = query(
            "SELECT id, quantity FROM cart_items WHERE (user_id = %s OR session_id = %s) AND product_id = %s",
            (user_id, session_id, product_id),
            fetchone=True
        )
    else:
        existing = query(
            "SELECT id, quantity FROM cart_items WHERE session_id = %s AND product_id = %s",
            (session_id, product_id),
            fetchone=True
        )

    if existing:
        new_qty = existing['quantity'] + quantity
        execute("UPDATE cart_items SET quantity = %s WHERE id = %s", (new_qty, existing['id']))
        cart_id = existing['id']
    else:
        res = execute(
            "INSERT INTO cart_items (user_id, session_id, product_id, quantity) VALUES (%s, %s, %s, %s)",
            (user_id, session_id, product_id, quantity)
        )
        cart_id = res['lastrowid']

    return {'success': True, 'cart_item_id': cart_id}

def update_cart_quantity(session_id, product_id, quantity, user_id=None):
    quantity = int(quantity)
    if quantity <= 0:
        return remove_from_cart(session_id, product_id, user_id)

    if user_id:
        execute(
            "UPDATE cart_items SET quantity = %s WHERE (user_id = %s OR session_id = %s) AND product_id = %s",
            (quantity, user_id, session_id, product_id)
        )
    else:
        execute(
            "UPDATE cart_items SET quantity = %s WHERE session_id = %s AND product_id = %s",
            (quantity, session_id, product_id)
        )
    return {'success': True}

def remove_from_cart(session_id, product_id, user_id=None):
    if user_id:
        execute(
            "DELETE FROM cart_items WHERE (user_id = %s OR session_id = %s) AND product_id = %s",
            (user_id, session_id, product_id)
        )
    else:
        execute(
            "DELETE FROM cart_items WHERE session_id = %s AND product_id = %s",
            (session_id, product_id)
        )
    return {'success': True}

def clear_cart(session_id, user_id=None):
    if user_id:
        execute("DELETE FROM cart_items WHERE user_id = %s OR session_id = %s", (user_id, session_id))
    else:
        execute("DELETE FROM cart_items WHERE session_id = %s", (session_id,))
    return {'success': True}

def get_cart_summary(session_id, user_id=None, coupon_code=None):
    items = get_cart_items(session_id, user_id)
    
    total_mrp = sum(item['item_mrp_total'] for item in items)
    total_selling = sum(item['item_subtotal'] for item in items)
    total_savings = total_mrp - total_selling
    items_count = sum(item['quantity'] for item in items)

    # Delivery charge rule: Free delivery above ₹500, else ₹40
    delivery_fee = 0.00 if (total_selling >= 500 or total_selling == 0) else 40.00
    platform_fee = 5.00 if items_count > 0 else 0.00
    
    coupon_discount = 0.00
    applied_coupon = None
    
    if coupon_code and total_selling > 0:
        coupon = query("SELECT * FROM coupons WHERE code = %s AND is_active = 1", (coupon_code.strip().upper(),), fetchone=True)
        if coupon:
            if total_selling >= coupon['min_order_value']:
                if coupon['discount_type'] == 'percentage':
                    calc_disc = (total_selling * coupon['discount_value']) / 100.0
                    coupon_discount = min(calc_disc, coupon['max_discount'])
                else:
                    coupon_discount = min(coupon['discount_value'], coupon['max_discount'])
                applied_coupon = coupon
            else:
                applied_coupon = {'error': f"Minimum order value of ₹{coupon['min_order_value']} required for {coupon['code']}"}

    final_total = max(0.00, round(total_selling - coupon_discount + delivery_fee + platform_fee, 2))

    has_prescription_item = any(item.get('prescription_required', 0) == 1 for item in items)

    return {
        'items': items,
        'cart_items': items,
        'items_count': items_count,
        'total_mrp': round(total_mrp, 2),
        'total_selling': round(total_selling, 2),
        'total_savings': round(total_savings, 2),
        'delivery_fee': delivery_fee,
        'platform_fee': platform_fee,
        'coupon_discount': round(coupon_discount, 2),
        'applied_coupon': applied_coupon,
        'final_total': final_total,
        'has_prescription_item': has_prescription_item
    }
