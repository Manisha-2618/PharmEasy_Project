from werkzeug.security import generate_password_hash, check_password_hash
from services.db import query, execute

def register_user(name, email, phone, password, role='customer'):
    email = email.strip().lower()
    phone = phone.strip()
    
    # Check if email or phone exists
    existing = query("SELECT id FROM users WHERE email = %s OR phone = %s", (email, phone), fetchone=True)
    if existing:
        return {'success': False, 'message': 'An account with this email or phone number already exists.'}
        
    pw_hash = generate_password_hash(password)
    res = execute(
        "INSERT INTO users (name, email, phone, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
        (name.strip(), email, phone, pw_hash, role)
    )
    user_id = res['lastrowid']
    return {
        'success': True,
        'user': {'id': user_id, 'name': name, 'email': email, 'phone': phone, 'role': role}
    }

def authenticate_user(email, password):
    email = email.strip().lower()
    user = query("SELECT * FROM users WHERE email = %s", (email,), fetchone=True)
    if not user:
        return {'success': False, 'message': 'Invalid email or password.'}
        
    if not check_password_hash(user['password_hash'], password):
        return {'success': False, 'message': 'Invalid email or password.'}
        
    return {
        'success': True,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone'],
            'role': user['role']
        }
    }

def get_user_by_id(user_id):
    user = query("SELECT id, name, email, phone, role, created_at FROM users WHERE id = %s", (user_id,), fetchone=True)
    return user

def update_user_profile(user_id, name, phone):
    execute("UPDATE users SET name = %s, phone = %s WHERE id = %s", (name.strip(), phone.strip(), user_id))
    return get_user_by_id(user_id)

