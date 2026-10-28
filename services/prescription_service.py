import os
import time
from werkzeug.utils import secure_filename
from config import Config
from services.db import query, execute

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_prescription(user_id, file_obj, patient_data):
    if not file_obj or file_obj.filename == '':
        return {'success': False, 'message': 'No file was selected.'}

    if not allowed_file(file_obj.filename):
        return {'success': False, 'message': 'Invalid file format. Please upload JPG, PNG, WEBP, or PDF.'}

    orig_filename = secure_filename(file_obj.filename)
    extension = orig_filename.rsplit('.', 1)[1].lower()
    timestamp = int(time.time())
    unique_filename = f"rx_{user_id or 'guest'}_{timestamp}.{extension}"
    
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    target_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
    file_obj.save(target_path)

    relative_file_path = f"/uploads/{unique_filename}"

    res = execute(
        """INSERT INTO prescriptions (
            user_id, patient_name, patient_age, patient_gender, phone,
            file_path, notes, delivery_pincode, request_callback, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            user_id, patient_data['patient_name'], int(patient_data.get('patient_age', 30)),
            patient_data.get('patient_gender', 'Male'), patient_data['phone'],
            relative_file_path, patient_data.get('notes', ''),
            patient_data.get('delivery_pincode', '110001'),
            1 if patient_data.get('request_callback', True) else 0,
            'Pending Review'
        )
    )

    return {
        'success': True,
        'prescription_id': res['lastrowid'],
        'file_path': relative_file_path,
        'message': 'Prescription uploaded successfully. Our pharmacist will review it within 15 minutes.'
    }

def get_user_prescriptions(user_id):
    sql = "SELECT * FROM prescriptions WHERE user_id = %s ORDER BY id DESC"
    return query(sql, (user_id,))

def get_all_prescriptions():
    sql = """
        SELECT p.*, u.name as user_name, u.email as user_email
        FROM prescriptions p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.id DESC
    """
    return query(sql)

def update_prescription_status(rx_id, status):
    execute("UPDATE prescriptions SET status = %s WHERE id = %s", (status, rx_id))
    return {'success': True}

