import sys
import os

# Add root folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
from services.db import query, execute, init_tables

def seed_all():
    print("Initializing database tables...")
    init_tables()
    
    # Check if products already seeded
    existing_products = query("SELECT COUNT(*) as count FROM products", fetchone=True)
    if existing_products and existing_products['count'] > 0:
        print(f"Database already contains {existing_products['count']} products. Skipping seed.")
        return

    print("Seeding database with realistic PharmEasy pharmacy data...")

    # 1. Users
    admin_pw = generate_password_hash("admin123")
    user_pw = generate_password_hash("user123")
    
    execute(
        "INSERT INTO users (name, email, phone, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
        ("Admin Pharmacist", "admin@pharmeasy.com", "9876543210", admin_pw, "admin")
    )
    user_res = execute(
        "INSERT INTO users (name, email, phone, password_hash, role) VALUES (%s, %s, %s, %s, %s)",
        ("Rahul Sharma", "user@pharmeasy.com", "9876543211", user_pw, "customer")
    )
    demo_user_id = user_res['lastrowid']

    # 2. Categories
    categories_data = [
        ("Medicines", "medicines", "fas fa-pills", "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&q=80", "100% Genuine Prescription & OTC Medicines", 1, 1),
        ("Personal Care", "personal-care", "fas fa-pump-soap", "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&q=80", "Daily hygiene, skin & hair care essentials", 1, 2),
        ("Healthcare Devices", "healthcare-devices", "fas fa-heartbeat", "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&q=80", "BP monitors, glucometers, thermometers & more", 1, 3),
        ("Health Food & Drinks", "health-food-drinks", "fas fa-apple-alt", "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=500&q=80", "Protein, nutrition powders, organic juices & foods", 1, 4),
        ("Skin Care", "skin-care", "fas fa-spa", "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=500&q=80", "Dermatologist approved creams, cleansers & sunscreens", 1, 5),
        ("Ayurvedic Care", "ayurvedic-care", "fas fa-leaf", "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=500&q=80", "Natural herbs, chyawanprash & herbal remedies", 1, 6),
        ("Mother & Baby Care", "mother-baby-care", "fas fa-baby", "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80", "Baby wipes, gentle diapers, baby wash & nutrition", 1, 7),
        ("Diabetic Care", "diabetic-care", "fas fa-tint", "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500&q=80", "Sugar substitutes, monitors, test strips & supplements", 1, 8),
        ("Fitness & Supplements", "fitness-supplements", "fas fa-dumbbell", "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80", "Vitamins, minerals, whey proteins & multivitamins", 1, 9),
        ("Elderly Care", "elderly-care", "fas fa-blind", "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?w=500&q=80", "Adult diapers, walking aids, joint pain relief", 1, 10),
    ]

    for cat in categories_data:
        execute(
            "INSERT INTO categories (name, slug, icon, image_url, description, is_featured, display_order) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            cat
        )

    cat_map = {c['slug']: c['id'] for c in query("SELECT id, slug FROM categories")}

    # 3. Brands
    brands_data = [
        ("Cipla", "cipla", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Cipla_logo.svg/320px-Cipla_logo.svg.png", "Caring for Life - Top Indian Pharmaceutical Leader"),
        ("Abbott", "abbott", "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Abbott_Laboratories_logo.svg/320px-Abbott_Laboratories_logo.svg.png", "Life to the Fullest - Global Healthcare Leader"),
        ("Himalaya", "himalaya", "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Himalaya_Wellness_logo.svg/320px-Himalaya_Wellness_logo.svg.png", "Since 1930 - Pure Herbal & Ayurvedic Care"),
        ("Dabur", "dabur", "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Dabur_Logo.svg/320px-Dabur_Logo.svg.png", "Celebrate Life - India's Trusted Natural Healthcare Brand"),
        ("Dr. Morepen", "dr-morepen", "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=200&q=80", "Health in Your Hands - Smart Diagnostic Devices"),
        ("Cetaphil", "cetaphil", "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=200&q=80", "Gentle skin care trusted by dermatologists"),
        ("Dettol", "dettol", "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Dettol_logo.svg/320px-Dettol_logo.svg.png", "100% Protection from Illness-causing Germs"),
        ("Baidyanath", "baidyanath", "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=200&q=80", "Asli Ayurveda - Traditional Indian Healing"),
        ("Horlicks", "horlicks", "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=200&q=80", "Taller, Stronger, Sharper Nutrition for All"),
        ("Sebamed", "sebamed", "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=200&q=80", "Science for Healthy Skin - pH 5.5 Medical Skin Care")
    ]

    for b in brands_data:
        execute(
            "INSERT INTO brands (name, slug, logo_url, description) VALUES (%s, %s, %s, %s)",
            b
        )

    brand_map = {b['slug']: b['id'] for b in query("SELECT id, slug FROM brands")}

    # 4. Products (40+ items with rich attributes)
    # (name, slug, brand, category, description, composition, uses, dosage, side_effects, packaging, mrp, price, discount_percent, stock, rating, reviews_count, image_url, prescription_required, is_trending, is_deal, is_spotlight, is_new_launch)
    products_data = [
        # Medicines & Pain Relief
        (
            "Dolo 650mg Tablet", "dolo-650mg-tablet", "cipla", "medicines",
            "Dolo 650 Tablet is an analgesic (pain reliever) and antipyretic (fever reducer) used to relieve mild to moderate pain including headache, toothache, muscle aches, and fever.",
            "Paracetamol (650mg)", "Fever reduction, headache, body aches, post-vaccination fever",
            "1 tablet every 4 to 6 hours as prescribed by physician. Do not exceed 4 tablets in 24 hours.",
            "Nausea, allergic skin rash, liver toxicity in overdose",
            "Strip of 15 Tablets", 34.00, 27.20, 20, 250, 4.8, 1420,
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&q=80",
            0, 1, 1, 0, 0
        ),
        (
            "Pan 40mg Tablet", "pan-40mg-tablet", "cipla", "medicines",
            "Pan 40 Tablet is a proton pump inhibitor (PPI) that reduces stomach acid production. It is used to treat acid reflux (GERD), peptic ulcer disease, and heartburn.",
            "Pantoprazole (40mg)", "Acidity, GERD, heartburn, stomach ulcers",
            "Take 1 tablet in the morning on an empty stomach at least 30 minutes before breakfast.",
            "Headache, diarrhea, nausea, abdominal pain",
            "Strip of 15 Tablets", 175.00, 140.00, 20, 180, 4.7, 890,
            "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&q=80",
            1, 1, 0, 0, 0
        ),
        (
            "Azithral 500mg Tablet", "azithral-500mg-tablet", "cipla", "medicines",
            "Azithral 500 Tablet is an antibiotic used to treat various bacterial infections of the respiratory tract, ear, nose, throat, lungs, skin, and eye in adults and children.",
            "Azithromycin (500mg)", "Bacterial infections, bronchitis, sinusitis, throat infections",
            "1 tablet once daily for 3 to 5 days, preferably 1 hour before or 2 hours after meals.",
            "Vomiting, nausea, stomach upset, mild diarrhea",
            "Strip of 5 Tablets", 132.00, 105.60, 20, 95, 4.6, 640,
            "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=500&q=80",
            1, 0, 0, 1, 0
        ),
        (
            "Shelcal 500mg Tablet", "shelcal-500mg-tablet", "abbott", "medicines",
            "Shelcal 500 is a calcium and vitamin D3 supplement that helps maintain strong bones, prevent osteopenia and osteoporosis, and treat calcium deficiencies.",
            "Calcium (500mg) + Vitamin D3 (250 IU)", "Bone health, calcium deficiency, osteoporosis, joint support",
            "1 tablet daily after lunch or dinner with water.",
            "Constipation, bloating, mild stomach fullness",
            "Bottle of 15 Tablets", 144.00, 115.20, 20, 310, 4.9, 2150,
            "https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=500&q=80",
            0, 1, 1, 0, 0
        ),
        (
            "Becosules Z Capsule", "becosules-z-capsule", "abbott", "medicines",
            "Becosules Z is a multivitamin capsule enriched with Vitamin B-complex, Vitamin C, and Zinc to combat weakness, mouth ulcers, and boost immune defenses.",
            "B-Complex Vitamins, Vitamin C (50mg), Zinc Sulphate (41.4mg)", "Mouth ulcers, fatigue, immunity booster, hair & skin wellness",
            "1 capsule daily after a meal.",
            "Mild nausea or bright yellow urine (harmless)",
            "Strip of 20 Capsules", 55.00, 44.00, 20, 400, 4.8, 1780,
            "https://images.unsplash.com/photo-1577401239170-897942555fb3?w=500&q=80",
            0, 1, 0, 0, 0
        ),
        (
            "Telma 40mg Tablet", "telma-40mg-tablet", "cipla", "medicines",
            "Telma 40 Tablet contains Telmisartan, an angiotensin receptor blocker used for lowering blood pressure and protecting heart and kidney health.",
            "Telmisartan (40mg)", "Hypertension (high blood pressure), cardiovascular risk reduction",
            "1 tablet daily at the same time every morning, with or without food.",
            "Dizziness, tiredness, back pain, sinus congestion",
            "Strip of 15 Tablets", 248.00, 198.40, 20, 160, 4.7, 520,
            "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=500&q=80",
            1, 0, 0, 1, 0
        ),
        (
            "Glycomet GP 1 Tablet", "glycomet-gp-1-tablet", "abbott", "diabetic-care",
            "Glycomet-GP 1 Tablet is a combination of Glimepiride and Metformin used to control blood sugar levels in patients with type 2 diabetes mellitus.",
            "Glimepiride (1mg) + Metformin (500mg)", "Type 2 Diabetes Mellitus glycemic control",
            "Take with meals to minimize stomach upset, as prescribed by doctor.",
            "Hypoglycemia (low blood sugar), metallic taste, nausea",
            "Strip of 15 Tablets", 112.00, 89.60, 20, 220, 4.6, 910,
            "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500&q=80",
            1, 0, 0, 0, 1
        ),
        (
            "Augmentin 625 Duo Tablet", "augmentin-625-duo-tablet", "cipla", "medicines",
            "Augmentin 625 Duo Tablet is a broad-spectrum penicillin-type antibiotic that fights bacteria in the body, treating infections of the lungs, ears, sinuses, and skin.",
            "Amoxicillin (500mg) + Clavulanic Acid (125mg)", "Bacterial infections, pneumonia, ear infections, urinary infections",
            "1 tablet twice daily with food to avoid stomach distress.",
            "Loose stools, mild nausea, rash",
            "Strip of 10 Tablets", 229.00, 183.20, 20, 140, 4.7, 1100,
            "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=500&q=80",
            1, 0, 0, 0, 1
        ),
        (
            "Allegra 120mg Tablet", "allegra-120mg-tablet", "abbott", "medicines",
            "Allegra 120 Tablet is a non-drowsy anti-allergy medication used to treat allergic rhinitis, runny nose, sneezing, itchy eyes, and chronic skin hives.",
            "Fexofenadine (120mg)", "Allergic rhinitis, seasonal allergies, urticaria, itchy rash",
            "1 tablet once daily with water before food.",
            "Headache, mild drowsiness, dry mouth",
            "Strip of 10 Tablets", 218.00, 174.40, 20, 190, 4.8, 830,
            "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&q=80",
            0, 1, 0, 0, 0
        ),
        (
            "Combiflam Tablet", "combiflam-tablet", "cipla", "medicines",
            "Combiflam Tablet is a trusted combination of Ibuprofen and Paracetamol providing fast relief from toothaches, backaches, muscular pain, and fever.",
            "Ibuprofen (400mg) + Paracetamol (325mg)", "Dental pain, body ache, arthritic flare, migraine relief",
            "1 tablet after meals when pain occurs. Max 3 tablets in 24h.",
            "Gastric irritation, heartburn, dizziness",
            "Strip of 20 Tablets", 52.00, 41.60, 20, 350, 4.7, 1600,
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&q=80",
            0, 1, 1, 0, 0
        ),

        # OTC Healthcare & Wellness Essentials
        (
            "Revital H Daily Health Supplement", "revital-h-daily-health-supplement", "dabur", "fitness-supplements",
            "Revital H is India's leading daily multivitamin with Ginseng, 10 essential vitamins, and 9 minerals that combats everyday fatigue and keeps you energized all day.",
            "Natural Ginseng, Vitamin A, B-Complex, C, D3, E, Zinc, Iron", "Physical stamina, mental alertness, immunity defense",
            "1 capsule daily with a glass of milk or water after breakfast.",
            "No known side effects when taken at recommended dosage",
            "Bottle of 60 Capsules", 550.00, 412.50, 25, 200, 4.8, 3400,
            "https://images.unsplash.com/photo-1577401239170-897942555fb3?w=500&q=80",
            0, 1, 1, 1, 0
        ),
        (
            "Volini Pain Relief Gel 75g", "volini-pain-relief-gel-75g", "cipla", "personal-care",
            "Volini Pain Relief Gel uses micro-particles to penetrate deeply and relieve neck pain, shoulder pain, sprains, muscle stiffness, and joint aches instantly.",
            "Diclofenac Diethylamine (1.16%), Methyl Salicylate, Menthol, Linseed Oil", "Sprains, joint pain, back pain, sports injuries, neck stiffness",
            "Gently massage a thin layer onto the affected area 3-4 times daily.",
            "Mild skin redness or tingling at the application site",
            "Tube of 75g", 245.00, 183.75, 25, 280, 4.9, 2900,
            "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&q=80",
            0, 1, 1, 0, 0
        ),
        (
            "Evion 400mg Vitamin E Capsule", "evion-400mg-capsule", "abbott", "skin-care",
            "Evion 400 contains pure Vitamin E (Tocopheryl Acetate), a powerful antioxidant that nourishes skin cells, restores hair vitality, and protects muscles from oxidative stress.",
            "Vitamin E / Tocopheryl Acetate (400mg)", "Glowing skin, hair nourishment, muscle cramps, antioxidant protection",
            "1 capsule daily after food or pierce and apply oil topically on skin/hair.",
            "Very well tolerated; mild stomach fullness if taken on empty stomach",
            "Strip of 10 Capsules", 38.00, 30.40, 20, 500, 4.9, 4800,
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&q=80",
            0, 1, 1, 0, 0
        ),
        (
            "Fast&Up Charge Natural Vitamin C 1000mg", "fastandup-charge-vitamin-c", "cipla", "fitness-supplements",
            "Fast&Up Charge is a world-class effervescent Vitamin C and Zinc supplement made from natural Amla extract to boost daily immunity and reduce fatigue.",
            "Phyllanthus Emblica L. Extract (Amla 1000mg) + Elemental Zinc (10mg)", "Immunity boost, glowing skin, antioxidant defence, collagen synthesis",
            "Drop 1 effervescent tablet in 250ml water, let it fizz and drink after breakfast.",
            "Mild citrus acidity if consumed on an empty stomach",
            "Tube of 20 Effervescent Tablets", 390.00, 273.00, 30, 150, 4.7, 1820,
            "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80",
            0, 1, 0, 1, 1
        ),
        (
            "Dabur Chyawanprash 1kg", "dabur-chyawanprash-1kg", "dabur", "ayurvedic-care",
            "Dabur Chyawanprash is an authentic Ayurvedic formulation with over 41 proven herbs that doubles immunity, improves stamina, and strengthens the respiratory system.",
            "Amla, Ashwagandha, Pippali, Shatavari, Giloy, Mulethi", "Seasonal cold prevention, immunity enhancement, stamina building",
            "1-2 teaspoons twice daily with warm milk or directly.",
            "None reported",
            "Jar of 1000g", 415.00, 332.00, 20, 210, 4.9, 3950,
            "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=500&q=80",
            0, 1, 1, 0, 0
        ),

        # Healthcare Devices & Diagnostics
        (
            "Omron HEM 7120 Fully Automatic Digital BP Monitor", "omron-hem-7120-bp-monitor", "dr-morepen", "healthcare-devices",
            "Omron HEM 7120 is a clinically validated, precise upper arm blood pressure monitor featuring IntelliSense technology for comfortable and rapid readings.",
            "IntelliSense Blood Pressure Sensing Unit, Arm Cuff, 4 AA Batteries", "Hypertension monitoring, pulse rate check, irregular heartbeat detection",
            "Wrap cuff snugly around upper arm at heart level, sit calmly and press Start.",
            "Non-invasive diagnostic device",
            "Box with Monitor, Cuff & 3 Year Warranty", 2460.00, 1722.00, 30, 85, 4.8, 1250,
            "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&q=80",
            0, 0, 1, 1, 0
        ),
        (
            "Dr. Morepen BG-03 Blood Glucose Monitor with 25 Strips", "dr-morepen-bg03-glucometer", "dr-morepen", "diabetic-care",
            "Dr. Morepen BG-03 Glucometer gives accurate blood glucose measurements in just 5 seconds using a tiny 0.5 microlitre blood droplet with no coding required.",
            "Biosensor Glucometer, Lancing Device, 10 Lancets, 25 Test Strips", "Daily blood sugar tracking for diabetic management",
            "Insert test strip, prick finger with lancet, apply blood drop to strip tip.",
            "Non-invasive diagnostic device",
            "Complete Diabetic Kit with 25 Strips", 999.00, 699.30, 30, 120, 4.7, 2410,
            "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500&q=80",
            0, 1, 1, 1, 0
        ),
        (
            "Accu-Chek Active 50 Test Strips Box", "accu-chek-active-50-test-strips", "dr-morepen", "diabetic-care",
            "Accu-Chek Active test strips provide high accuracy matching ISO 15197:2013 standards. Features visual double check and underdose detection.",
            "Glucose Dehydrogenase Enzyme coated strips", "Capillary blood glucose testing with Accu-Chek Active meter",
            "Use only with Accu-Chek Active meter. Keep vial tightly closed.",
            "None",
            "Pack of 50 Test Strips", 1099.00, 824.25, 25, 220, 4.9, 3100,
            "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=500&q=80",
            0, 1, 1, 0, 0
        ),
        (
            "Fingertip Pulse Oximeter with OLED Display", "fingertip-pulse-oximeter-oled", "dr-morepen", "healthcare-devices",
            "Accurate and rapid digital pulse oximeter that monitors blood oxygen saturation (SpO2), pulse rate, and perfusion index in seconds.",
            "Dual-wavelength optical sensor & high-res dual color OLED display", "SpO2 oxygen level tracking, pulse rate measurement, respiratory monitoring",
            "Insert index finger into rubber chamber, press power button, remain still.",
            "None",
            "Box with Oximeter, Lanyard & Batteries", 1299.00, 649.50, 50, 95, 4.6, 980,
            "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&q=80",
            0, 0, 1, 1, 0
        ),
        (
            "Beurer FT 09 Digital Clinical Thermometer", "beurer-ft09-digital-thermometer", "dr-morepen", "healthcare-devices",
            "High precision German engineered digital thermometer with waterproof tip, fever alert beep, and memory recall for home use.",
            "Medical grade digital sensor with LCD display", "Oral, axillary, and rectal temperature measurement",
            "Place under tongue or armpit until beep sounds.",
            "None",
            "Pack of 1 Unit with Protective Case", 350.00, 245.00, 30, 175, 4.8, 760,
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&q=80",
            0, 0, 0, 0, 1
        ),

        # Skin & Personal Care
        (
            "Cetaphil Gentle Skin Cleanser 250ml", "cetaphil-gentle-skin-cleanser-250ml", "cetaphil", "skin-care",
            "Award-winning, dermatologist-recommended creamy cleanser with hydrating glycerin, niacinamide, and panthenol to cleanse sensitive skin without stripping natural moisture.",
            "Purified Water, Glycerin, Niacinamide, Panthenol, Cetearyl Alcohol", "Gentle everyday cleansing for dry, normal, and sensitive skin types",
            "Apply without water and wipe with soft cloth, or apply with water and rinse gently.",
            "Hypoallergenic and fragrance-free; zero irritation",
            "Bottle of 250ml", 445.00, 378.25, 15, 260, 4.9, 5400,
            "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500&q=80",
            0, 1, 0, 1, 0
        ),
        (
            "Dettol Antiseptic Liquid 1000ml", "dettol-antiseptic-liquid-1000ml", "dettol", "personal-care",
            "Trusted for over 80 years, Dettol Antiseptic Liquid provides 100% protection against germs causing infection, cuts, scratches, insect bites, and personal hygiene.",
            "Chloroxylenol (B.P. 4.8% w/v), Terpineol, Absolute Alcohol", "First aid for cuts, surface disinfection, bathing water, shaving antiseptic",
            "Dilute 1 capful in a mug of water for first aid; 1 capful in bath water.",
            "Do not use undiluted on open wounds or sensitive mucous membranes",
            "Bottle of 1000ml (1 Litre)", 420.00, 357.00, 15, 300, 4.9, 6200,
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&q=80",
            0, 1, 1, 0, 0
        ),
        (
            "Himalaya Purifying Neem Face Wash 150ml", "himalaya-purifying-neem-face-wash-150ml", "himalaya", "skin-care",
            "Himalaya Purifying Neem Face Wash is a soap-free, herbal formulation that cleans impurities and helps clear pimples and blemishes using Neem and Turmeric.",
            "Neem Oil, Turmeric Root Extract, Glycerin", "Pimple prevention, excess oil control, deep pore cleansing",
            "Moisten face, apply small quantity and gently work up a lather using circular motion.",
            "None; herbal soap-free formula",
            "Tube of 150ml", 220.00, 176.00, 20, 320, 4.8, 4100,
            "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=500&q=80",
            0, 1, 0, 0, 0
        ),
        (
            "Sebamed Baby Gentle Wash 400ml", "sebamed-baby-gentle-wash-400ml", "sebamed", "mother-baby-care",
            "Made in Germany with exact pH 5.5, Sebamed Baby Gentle Wash promotes the development of baby's natural acid mantle, preventing dryness and cradle cap.",
            "Sugar tenside complex, Allantoin, Chamomile extract", "Ultra-gentle daily bathing for newborns and sensitive infant skin",
            "Put 2-3 drops into bath water or apply gently onto baby's wet skin with hands.",
            "Tear-free, 100% soap and alkali-free",
            "Dispenser Bottle of 400ml", 850.00, 680.00, 20, 140, 4.9, 1950,
            "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80",
            0, 0, 1, 1, 0
        ),
        (
            "Pampers All Round Protection Baby Diaper Pants (L)", "pampers-baby-diaper-pants-l", "sebamed", "mother-baby-care",
            "India's best diapers with anti-rash lotion with Aloe Vera, ultra absorb core providing up to 12 hours dryness, and soft stretchy waistband.",
            "Cotton-like breathable soft materials, Aloe Vera lotion, Absorbent polymers", "12-hour overnight leakage protection for babies 9-14 kg",
            "Pull up like pants. Tear sides for easy removal.",
            "None",
            "Mega Pack of 64 Diapers", 1199.00, 899.25, 25, 180, 4.8, 3800,
            "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=500&q=80",
            0, 1, 0, 0, 0
        ),

        # Nutrition & Health Drinks
        (
            "Horlicks Health & Nutrition Drink Chocolate 1kg", "horlicks-chocolate-health-drink-1kg", "horlicks", "health-food-drinks",
            "Clinically proven to make kids taller, stronger, and sharper with 27 vital nutrients including Zinc, Vitamin C, Iron, and Calcium.",
            "Malted Barley, Wheat Flour, Milk Solids, Cocoa, Minerals, Vitamins", "Daily child growth nutrition, bone density, micronutrient replenishment",
            "Add 3 heaped teaspoons (27g) to 200ml of hot or cold milk and stir well.",
            "None",
            "Jar of 1000g (1kg)", 480.00, 408.00, 15, 230, 4.8, 2750,
            "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=500&q=80",
            0, 1, 0, 0, 0
        ),
        (
            "Optimum Nutrition Gold Standard 100% Whey Protein 2lb", "on-gold-standard-whey-protein-2lb", "horlicks", "fitness-supplements",
            "The world's bestselling whey protein with 24g of high quality whey protein isolate per serving, 5.5g naturally occurring BCAAs, and 4g Glutamine.",
            "Whey Protein Isolates, Whey Protein Concentrate, Whey Peptides", "Lean muscle building, post-workout recovery, daily protein requirement",
            "Mix 1 rounded scoop with 200-250ml of cold water or milk 30-60 minutes post workout.",
            "Contains milk and soy ingredients",
            "Tub of 907g (2 lbs) Double Rich Chocolate", 3899.00, 3119.20, 20, 75, 4.9, 4100,
            "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&q=80",
            0, 1, 0, 1, 1
        ),
        (
            "Ensure Complete Balanced Nutrition Vanilla 400g", "ensure-nutrition-powder-vanilla-400g", "abbott", "elderly-care",
            "Ensure is scientifically designed with 32 essential nutrients including high quality protein, calcium, and vitamin D to support bone and muscle strength in adults 40+.",
            "Skim Milk Powder, Maltodextrin, Sucrose, Vegetable Oils, Inulin, FOS, Minerals", "Active adulthood nutrition, muscle strength maintenance, stamina booster",
            "Add 6 level scoops (approx. 53.8g) to 190ml of water and stir until dissolved.",
            "Gluten free; not for individuals with galactosemia",
            "Tin of 400g", 740.00, 629.00, 15, 160, 4.8, 1850,
            "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?w=500&q=80",
            0, 0, 1, 1, 0
        ),
        (
            "Friends Classic Adult Diapers Pant Style (L)", "friends-classic-adult-diaper-pants-l", "sebamed", "elderly-care",
            "Premium adult pull-up diaper pants designed with high absorbent gel core, odor lock technology, and wetness indicator for senior dignity and comfort.",
            "Super Absorbent Polymer (SAP), Antibacterial non-woven top sheet", "Incontinence protection for seniors and mobility-impaired patients",
            "Step into like underwear and pull up. Tear side seams to dispose.",
            "None",
            "Pack of 10 Diapers (Waist 30-45 inches)", 550.00, 412.50, 25, 130, 4.7, 920,
            "https://images.unsplash.com/photo-1576765608535-5f04d1e3f289?w=500&q=80",
            0, 0, 0, 0, 1
        ),

        # Ayurvedic Essentials
        (
            "Himalaya Liv.52 DS Tablet 60s", "himalaya-liv-52-ds-tablet-60s", "himalaya", "ayurvedic-care",
            "Liv.52 DS is a clinically validated hepatoprotective herbal formulation that restores functional efficiency of the liver, protects against alcohol-induced toxins, and improves appetite.",
            "Himsra (Capparis spinosa 130mg), Kasani (Cichorium intybus 130mg), Mandur bhasma", "Liver health, appetite restoration, jaundice recovery, fatty liver support",
            "1-2 tablets twice daily before meals.",
            "Safe Ayurvedic herbal formulation with no reported adverse effects",
            "Bottle of 60 Tablets", 195.00, 156.00, 20, 280, 4.9, 3600,
            "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=500&q=80",
            0, 1, 1, 0, 0
        ),
        (
            "Dabur 100% Pure Honey 500g (Buy 1 Get 1 Free)", "dabur-pure-honey-500g-bogo", "dabur", "health-food-drinks",
            "100% pure NMR tested indigenous honey with zero added sugar or adulteration. Great for morning warm water detox, weight management, and cough relief.",
            "Pure Multiflora Forest Honey (100%)", "Natural sweetener, immunity booster, morning fitness detox, sore throat relief",
            "1 tablespoon daily with warm water and lemon, or in green tea.",
            "Natural pure honey may crystallize at cool temperatures (liquefy in warm water)",
            "Pack of 2 Glass Jars (500g + 500g)", 430.00, 322.50, 25, 190, 4.9, 5100,
            "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=500&q=80",
            0, 1, 1, 1, 0
        ),
        (
            "Baidyanath Triphala Churna 500g", "baidyanath-triphala-churna-500g", "baidyanath", "ayurvedic-care",
            "Classic Ayurvedic digestive combination of Amla, Haritaki, and Bibhitaki that cleanses colon, relieves chronic constipation, and improves nutrient absorption.",
            "Emblica officinalis (Amla), Terminalia chebula (Haritaki), Terminalia bellirica", "Constipation, digestive detoxification, eye health, acidity balance",
            "1-2 teaspoons (5-10g) at bedtime with lukewarm water.",
            "Mild laxative effect; avoid during acute diarrhea",
            "Jar of 500g", 210.00, 168.00, 20, 170, 4.8, 1450,
            "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=500&q=80",
            0, 0, 0, 0, 1
        )
    ]

    for p in products_data:
        b_id = brand_map.get(p[2])
        c_id = cat_map.get(p[3], 1)
        execute(
            """INSERT INTO products (
                name, slug, brand_id, category_id, description, composition, uses, dosage,
                side_effects, packaging, mrp, price, discount_percent, stock, rating,
                reviews_count, image_url, prescription_required, is_trending, is_deal,
                is_spotlight, is_new_launch
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (p[0], p[1], b_id, c_id, p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12], p[13], p[14], p[15], p[16], p[17], p[18], p[19], p[20], p[21])
        )

    # 5. Lab Tests
    lab_tests_data = [
        (
            "Comprehensive Full Body Health Checkup", "comprehensive-full-body-health-checkup",
            "Full Body Checkup", "Complete preventive health assessment covering Liver, Kidney, Heart, Thyroid, Blood count, and vital vitamins.",
            "CBC (24 tests), Lipid Profile (8 tests), Liver Function Test (12 tests), Kidney Function Test (8 tests), Thyroid Profile (3 tests), Blood Glucose Fasting, Urine Routine (10 tests)",
            "10-12 hours fasting mandatory", 63, "Reports within 24 hours",
            2199.00, 899.00, 59, "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=500&q=80", 1
        ),
        (
            "Thyroid Profile Total (T3, T4, TSH)", "thyroid-profile-total-t3-t4-tsh",
            "Thyroid", "Evaluates thyroid gland metabolism function, diagnosing hypothyroidism or hyperthyroidism.",
            "Total Triiodothyronine (T3), Total Thyroxine (T4), Thyroid Stimulating Hormone (TSH)",
            "No Fasting Required (Early morning sample preferred)", 3, "Reports within 12 hours",
            600.00, 249.00, 58, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=500&q=80", 1
        ),
        (
            "Diabetes Screen Advanced (HbA1c + Fasting Blood Sugar)", "diabetes-screen-advanced-hba1c",
            "Diabetes", "Measures average blood sugar levels over the last 3 months along with instant morning fasting glucose.",
            "HbA1c (Glycosylated Hemoglobin), Estimated Average Glucose (eAG), Fasting Blood Glucose (FBS)",
            "8-10 hours overnight fasting required", 3, "Same Day Reports",
            850.00, 399.00, 53, "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=500&q=80", 1
        ),
        (
            "Lipid Profile Test (Heart Risk Assessment)", "lipid-profile-heart-health",
            "Cardiac", "Crucial panel assessing good and bad cholesterol levels, triglycerides, and heart health risks.",
            "Total Cholesterol, HDL Good Cholesterol, LDL Bad Cholesterol, VLDL, Triglycerides, Total/HDL Ratio",
            "12 hours strict fasting required", 8, "Reports within 18 hours",
            750.00, 349.00, 53, "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=500&q=80", 1
        ),
        (
            "Complete Blood Count (CBC) with ESR", "complete-blood-count-cbc-with-esr",
            "Blood Studies", "Comprehensive snapshot of cellular blood components including hemoglobin, platelets, and infection markers.",
            "Hemoglobin, RBC Count, Platelet Count, Total Leucocyte Count (TLC), DLC (5 tests), PCV, MCV, MCH, MCHC, ESR",
            "No Fasting Required", 24, "Reports within 6 hours",
            400.00, 199.00, 50, "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&q=80", 1
        ),
        (
            "Vitamin D (25-OH) & Vitamin B12 Duo Pack", "vitamin-d-b12-duo-pack",
            "Vitamins", "Identifies underlying deficiencies causing unexplained muscle pain, chronic fatigue, bone weakness, and nerve tingling.",
            "Vitamin D3 25-Hydroxy, Vitamin B12 Cyanocobalamin",
            "No Fasting Required", 2, "Reports within 24 hours",
            1600.00, 699.00, 56, "https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=500&q=80", 1
        ),
        (
            "Liver Function Test (LFT Detailed)", "liver-function-test-lft-detailed",
            "Liver Care", "Evaluates hepatic health, protein metabolism, bilirubin, and enzymes indicating liver inflammation or damage.",
            "Bilirubin Total, Direct & Indirect, SGOT/AST, SGPT/ALT, Alkaline Phosphatase, Total Protein, Albumin, Globulin, A/G Ratio",
            "8 hours fasting recommended", 11, "Reports within 12 hours",
            799.00, 399.00, 50, "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=500&q=80", 1
        ),
        (
            "Kidney Function Test (KFT with Electrolytes)", "kidney-function-test-kft-electrolytes",
            "Kidney Care", "Monitors renal filtering ability, waste clearance, hydration levels, and essential bodily electrolytes.",
            "Blood Urea Nitrogen (BUN), Serum Creatinine, Uric Acid, Calcium, Phosphorus, Sodium, Potassium, Chloride",
            "No Fasting Required", 9, "Reports within 12 hours",
            899.00, 449.00, 50, "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=500&q=80", 1
        )
    ]

    for t in lab_tests_data:
        execute(
            """INSERT INTO lab_tests (
                name, slug, category, description, included_tests, fasting_required,
                test_count, turnaround_time, mrp, price, discount_percent, image_url,
                is_frequently_booked
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            t
        )

    # 6. Coupons
    coupons_data = [
        ("FIRST25", "First Order Special", "Get 25% OFF up to ₹250 on your very first medicine order", "percentage", 25.00, 399.00, 250.00, "Medicines", "2027-12-31"),
        ("PHARMA15", "Flat 15% Savings", "Save 15% on all prescription & OTC wellness orders over ₹499", "percentage", 15.00, 499.00, 150.00, "All", "2027-12-31"),
        ("CARE50", "Flat ₹50 OFF", "Instant ₹50 instant discount on orders exceeding ₹600", "flat", 50.00, 600.00, 50.00, "Healthcare", "2027-12-31"),
        ("LAB100", "Diagnostic Super Save", "Flat ₹100 discount on any lab test package booking", "flat", 100.00, 500.00, 100.00, "Lab Tests", "2027-12-31"),
    ]

    for c in coupons_data:
        execute(
            "INSERT INTO coupons (code, title, description, discount_type, discount_value, min_order_value, max_discount, category, expires_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            c
        )

    # 7. Promotional Banners
    banners_data = [
        (
            "Flat 25% OFF on Medicines", "Upload your prescription or browse medicines to save big with fast delivery.",
            "MEGA HEALTH SALE", "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=1200&q=80",
            "/products?category=medicines", "linear-gradient(135deg, #10847e 0%, #08524e 100%)", 1
        ),
        (
            "Full Body Checkup @ Just ₹899", "63 Vital Tests included. Free home sample collection by certified phlebotomists.",
            "NABL ACCREDITED", "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=1200&q=80",
            "/lab-tests", "linear-gradient(135deg, #0e706b 0%, #043835 100%)", 2
        ),
        (
            "Up to 50% OFF on Top Health Devices", "Monitor BP, blood glucose, and oxygen with certified medical tools at home.",
            "SMART HEALTHCARE", "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1200&q=80",
            "/products?category=healthcare-devices", "linear-gradient(135deg, #149c95 0%, #0d615c 100%)", 3
        ),
        (
            "Ayurvedic Immunity & Wellness Store", "Pure herbal formulas from Himalaya, Dabur, and Baidyanath for whole-family care.",
            "100% NATURAL", "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=1200&q=80",
            "/products?category=ayurvedic-care", "linear-gradient(135deg, #1b8a5d 0%, #0f4f34 100%)", 4
        )
    ]

    for b in banners_data:
        execute(
            "INSERT INTO banners (title, subtitle, tag, image_url, target_url, bg_gradient, display_order) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            b
        )

    # 8. Health Articles
    articles_data = [
        (
            "10 Simple Ways to Keep Your Blood Pressure Healthy Naturally",
            "ways-to-keep-blood-pressure-healthy",
            "Heart Care", "5 min read", "Dr. Rajesh Gupta, MD Cardiology",
            "https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=600&q=80",
            "High blood pressure often develops without any symptoms. Learn evidence-based lifestyle changes to protect your heart.",
            """High blood pressure (hypertension) is often called a silent killer because it rarely shows obvious symptoms until significant cardiovascular strain has occurred. 
            
Here are five proven steps to manage your blood pressure:
1. **Reduce Sodium Intake**: Keep dietary salt under 5 grams (approx 1 teaspoon) per day. Beware of hidden sodium in packaged soups and sauces.
2. **Engage in Aerobic Activity**: Just 30 minutes of brisk walking 5 days a week can lower systolic blood pressure by 5 to 8 mm Hg.
3. **Embrace the DASH Diet**: Increase potassium-rich vegetables, fruits, whole grains, and low-fat dairy while cutting saturated fats.
4. **Manage Stress with Deep Breathing**: Chronic stress increases heart rate and constricts blood vessels. Dedicate 10 minutes to mindfulness daily.
5. **Monitor Regularly**: Keep a certified home digital BP monitor like Omron HEM 7120 to record morning and evening baseline readings."""
        ),
        (
            "Understanding Your HbA1c Report: What Those Percentages Mean",
            "understanding-your-hba1c-report",
            "Diabetes Management", "4 min read", "Dr. Shweta Kulkarni, Diabetologist",
            "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=600&q=80",
            "Why fasting glucose alone isn't enough. Discover why HbA1c is the gold standard in tracking diabetic health.",
            """Unlike a standard capillary blood glucose finger prick that gives a snapshot of your sugar levels at that single moment, the HbA1c test measures the percentage of your hemoglobin that is glycated (coated with sugar) over the 90-120 day lifespan of your red blood cells.

- **Below 5.7%**: Normal healthy range.
- **5.7% to 6.4%**: Prediabetes warning window. Reversible through diet and exercise.
- **6.5% or higher**: Diagnosis of diabetes.
- **Under 7.0%**: General target for most adults managing diabetes effectively."""
        ),
        (
            "Vitamin D Deficiency: Symptoms You Shouldn't Ignore",
            "vitamin-d-deficiency-symptoms-you-shouldnt-ignore",
            "Vitamins & Immunity", "6 min read", "Dr. Ananya Sharma, MBBS, MD",
            "https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=600&q=80",
            "Over 70% of urban Indians have insufficient Vitamin D. Learn the subtle warning signs and how to restore your levels.",
            """Vitamin D is a pro-hormone crucial not only for absorbing calcium and building bone density, but also for modulating cellular immune defenses and mental mood balance.

**Classic Warning Signs:**
- Persistent unexplained fatigue and muscle soreness.
- Frequent respiratory colds and infections.
- Hair loss and slow wound healing.
- Bone pain in lower back, pelvis, or legs.

If your 25-OH Vitamin D blood test shows levels below 20 ng/mL, consult your doctor regarding medical supplementation with Vitamin D3 (such as 60,000 IU weekly doses) alongside sensible midday sun exposure."""
        ),
        (
            "How to Build an Emergency Home Medicine Kit",
            "how-to-build-an-emergency-home-medicine-kit",
            "First Aid & Wellness", "3 min read", "Dr. Vikram Malhotra, Emergency Medicine",
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&q=80",
            "Be prepared for unexpected minor injuries, allergic bouts, and fevers with this pharmacist-curated home medical checklist.",
            """Every household needs a dedicated, accessible medical box stored in a cool, dry place away from children.

**Essential Contents Checklist:**
1. **Fever & Pain**: Paracetamol 650mg tablets for adults and syrup for children.
2. **Digestive Distress**: Antacids (Pantoprazole), ORS hydration salts, and antispasmodic tablets.
3. **Allergies & Insect Stings**: Cetirizine or Fexofenadine tablets, calamine soothing lotion.
4. **Wound Care**: Dettol antiseptic liquid, sterile gauze swabs, adhesive bandages, and povidone-iodine ointment.
5. **Diagnostic Tools**: Digital clinical thermometer, pulse oximeter, and emergency contact numbers clearly listed."""
        )
    ]

    for a in articles_data:
        execute(
            "INSERT INTO articles (title, slug, category, read_time, doctor_reviewed, image_url, excerpt, content) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            a
        )

    # 9. Sample Address for Demo User
    execute(
        """INSERT INTO addresses (user_id, full_name, phone, pincode, address_line1, address_line2, city, state, address_type, is_default)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (demo_user_id, "Rahul Sharma", "9876543211", "110001", "Flat 402, Green Valley Apartments", "Sector 14, Connaught Place", "New Delhi", "Delhi", "Home", 1)
    )

    # 10. Sample Order for Demo User
    first_prod = query("SELECT id, name, price, mrp FROM products WHERE slug = 'dolo-650mg-tablet'", fetchone=True)
    second_prod = query("SELECT id, name, price, mrp FROM products WHERE slug = 'revital-h-daily-health-supplement'", fetchone=True)
    
    if first_prod and second_prod:
        addr = query("SELECT id FROM addresses WHERE user_id = %s", (demo_user_id,), fetchone=True)
        addr_id = addr['id'] if addr else None
        
        tot_mrp = (first_prod['mrp'] * 2) + second_prod['mrp']
        tot_disc = tot_mrp - ((first_prod['price'] * 2) + second_prod['price'])
        net_amount = (first_prod['price'] * 2) + second_prod['price'] + 5.00 # 5 platform fee
        
        order_res = execute(
            """INSERT INTO orders (
                order_number, user_id, address_id, total_mrp, discount,
                delivery_fee, platform_fee, total_amount, payment_method,
                payment_status, order_status, delivery_slot
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            ("PE-ORD-90214", demo_user_id, addr_id, tot_mrp, tot_disc, 0.00, 5.00, net_amount, "UPI", "Paid", "Delivered", "Delivered on Oct 24, 2026")
        )
        ord_id = order_res['lastrowid']
        
        execute(
            "INSERT INTO order_items (order_id, product_id, product_name, price, quantity, subtotal) VALUES (%s, %s, %s, %s, %s, %s)",
            (ord_id, first_prod['id'], first_prod['name'], first_prod['price'], 2, first_prod['price'] * 2)
        )
        execute(
            "INSERT INTO order_items (order_id, product_id, product_name, price, quantity, subtotal) VALUES (%s, %s, %s, %s, %s, %s)",
            (ord_id, second_prod['id'], second_prod['name'], second_prod['price'], 1, second_prod['price'])
        )

    print("Database successfully seeded with realistic pharmacy data!")

if __name__ == '__main__':
    seed_all()

