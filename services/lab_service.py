import time
import random
from services.db import query, execute

def get_lab_tests(category=None, frequently_booked_only=False):
    sql = "SELECT * FROM lab_tests"
    conditions = []
    params = []

    if category and category.lower() != 'all':
        conditions.append("LOWER(category) = LOWER(%s)")
        params.append(category)

    if frequently_booked_only:
        conditions.append("is_frequently_booked = 1")

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY price ASC"
    return query(sql, tuple(params))

def get_lab_test_by_slug(slug):
    return query("SELECT * FROM lab_tests WHERE slug = %s", (slug,), fetchone=True)

def get_lab_test_by_id(test_id):
    return query("SELECT * FROM lab_tests WHERE id = %s", (test_id,), fetchone=True)

def get_lab_categories():
    rows = query("SELECT DISTINCT category FROM lab_tests ORDER BY category ASC")
    return [r['category'] for r in rows]

def create_lab_booking(user_id, data):
    test_id = data['test_id']
    test = get_lab_test_by_id(test_id)
    if not test:
        return {'success': False, 'message': 'Lab test not found.'}

    timestamp = int(time.time())
    rand = random.randint(100, 999)
    booking_number = f"LAB-{timestamp}-{rand}"

    res = execute(
        """INSERT INTO lab_bookings (
            booking_number, user_id, test_id, patient_name, patient_age,
            patient_gender, phone, booking_date, time_slot,
            sample_collection_address, pincode, total_amount, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            booking_number, user_id, test_id, data['patient_name'], int(data['patient_age']),
            data.get('patient_gender', 'Male'), data['phone'], data['booking_date'],
            data['time_slot'], data['address'], data['pincode'], test['price'], 'Confirmed'
        )
    )
    return {
        'success': True,
        'booking_id': res['lastrowid'],
        'booking_number': booking_number,
        'test_name': test['name'],
        'amount': test['price']
    }

def get_user_bookings(user_id):
    sql = """
        SELECT b.*, t.name as test_name, t.category, t.fasting_required, t.test_count, t.turnaround_time, t.image_url
        FROM lab_bookings b
        JOIN lab_tests t ON b.test_id = t.id
        WHERE b.user_id = %s
        ORDER BY b.id DESC
    """
    return query(sql, (user_id,))

def get_all_bookings():
    sql = """
        SELECT b.*, t.name as test_name, t.category, u.name as user_name, u.email as user_email
        FROM lab_bookings b
        JOIN lab_tests t ON b.test_id = t.id
        LEFT JOIN users u ON b.user_id = u.id
        ORDER BY b.id DESC
    """
    return query(sql)

