# PharmEasy Clone - Complete Pharmacy E-Commerce Platform

A responsive pharmacy e-commerce web application inspired by [PharmEasy](https://pharmeasy.in/). Built with **HTML5, CSS3, standard JavaScript, Python Flask, and MySQL** (with zero-configuration automatic fallback to SQLite for immediate demoing).

---

## 🌟 Key Features & Included Pages

### 12 Complete Pages:
1. **Home Page (`/`)**: All 16 visible homepage sections replicated in exact reference order:
   - Sticky header with PharmEasy branding, delivery pincode selector modal, smart search bar with auto-complete suggestions, user profile dropdown, and shopping cart counter.
   - Primary service categories navigation bar (Medicines, Lab Tests, Healthcare, Diabetic Care, Ayurvedic, Offers).
   - Promotional hero banner carousel with auto-rotation, arrow buttons, and dot indicators.
   - Core healthcare service shortcuts (Order Medicines, Book Lab Tests, Healthcare Products, Upload Prescription).
   - Prescription upload call-to-action banner with 3-step guide.
   - Shop by category grid (10 circular categories with hover zoom effect).
   - Deals of the day flash sale with live countdown timer.
   - Trending products carousel with direct "Add to Cart" functionality.
   - Frequently booked diagnostic lab tests with certified lab badges and "Book Now" buttons.
   - Featured brands showcase (Cipla, Abbott, Himalaya, Dabur, Dr. Morepen, Cetaphil, Dettol, Baidyanath, Horlicks, Sebamed).
   - New launches carousel.
   - In-the-spotlight medical devices and essentials.
   - Wellness essentials / Shop by health concern (Diabetes, Heart Care, Joint Pain, Digestion).
   - Medically reviewed health articles and doctor insights.
   - Why choose PharmEasy trust metrics (32M+ users, 100% genuine medicines, 25,000+ pincodes, NABL labs).
   - Popular medicine directory and SEO links cloud.
   - Complete 4-column footer with app download badges, secure payment partners, and legal disclaimers.
2. **Product Listing (`/products`)**: Filter by category, brand, prescription required (Rx), and sort by popularity, discount, price (low/high), or newest.
3. **Product Details (`/product/<slug>`)**: High-res product view, composition, indications, recommended dosage, side effects, stock level, quantity selector, and related products carousel.
4. **Search Results (`/search?q=...`)**: Instant search query match with category filter chips and empty state recommendations.
5. **Authentication (`/login` & `/register`)**: Login and registration with secure password hashing (`Werkzeug`), session persistence, and one-click demo credentials auto-fill buttons.
6. **Shopping Cart (`/cart`)**: Live quantity adjuster (`+` / `-`), item removal, coupon code application, delivery fee calculations (Free above ₹500), platform fee, prescription requirement warning, and order savings summary.
7. **Checkout Demo (`/checkout`)**: Multi-step checkout with address selection, add new address modal, delivery speed slot selection, and payment simulator (UPI, Card, Net Banking, COD).
8. **Prescription Upload (`/prescription`)**: Drag-and-drop file upload zone with validation (JPG, PNG, WEBP, PDF under 16MB), patient information form, pharmacist callback request toggle, and prescription guidelines.
9. **Lab Tests (`/lab-tests`)**: Diagnostic checkup packages catalog, NABL certification badges, fasting requirements, turnaround time, and home sample collection booking modal.
10. **Offers & Coupons (`/offers`)**: Categorized coupon cards with one-click copyable promo codes (`FIRST25`, `PHARMA15`, `CARE50`, `LAB100`).
11. **User Profile & Orders (`/profile`)**: Order history with status tracking stepper (`Placed` -> `Processing` -> `Dispatched` -> `Delivered`), diagnostic lab bookings, uploaded prescription documents, and saved addresses.
12. **Admin Dashboard (`/admin`)**: Revenue and order metrics, complete product inventory management (add, edit, delete products), inline order status updater, prescription review, and lab bookings review.
13. **Health Article Reader (`/article/<slug>`)**: Medically reviewed health guide reading view with doctor details and related topics.

---

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3 (Custom Responsive Grid & Flexbox, no heavy UI frameworks), Standard JavaScript (ES6+ Fetch API, DOM manipulation).
- **Backend**: Python Flask 3.1+, Werkzeug Security, Flask-CORS, python-dotenv.
- **Database**:
  - **MySQL**: Relational schema defined in `database/schema.sql` with foreign keys, indexes, and full constraints.
  - **Auto-Fallback Mode**: Seamlessly operates on SQLite (`database/pharmeasy.db`) out-of-the-box if MySQL is not currently running.

---

## 🚀 Exact Windows Commands to Run Locally

### 1. Requirements:
- Python 3.11 or Python 3.12 (Installed at `%LOCALAPPDATA%\Programs\Python\Python312\python.exe` or available in your system PATH).

### 2. Install Dependencies:
Open **PowerShell** or **Command Prompt** in the project folder `c:\Users\DELL\Desktop\PharmEasy_Project`:
```powershell
pip install -r requirements.txt
```
*(Or run with full path if Python is not in PATH)*:
```powershell
& "$env:LocalAppData\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt
```

### 3. Initialize & Seed Database:
```powershell
.\python.bat database\seed_data.py
```
*(Or if Python is directly on PATH)*:
```powershell
python database\seed_data.py
```

### 4. Run the Application:
Simply double-click either button in `c:\Users\DELL\Desktop\PharmEasy_Project`:
- **`run.bat`**: Starts the Flask server and automatically opens **http://127.0.0.1:5000** in your default web browser after 2 seconds.
- **`Open_Website.bat`**: One-click launcher that checks if the server is already active; if running, it immediately opens your browser, or starts the server and opens the browser.

*(Or run from command line)*:
```powershell
.\run.bat
```

### 5. Open in Your Browser:
Visit: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🗄️ Configuring MySQL (Optional)

If you have MySQL running locally (via **XAMPP**, **WAMP**, **MySQL Workbench**, or the Windows MySQL Service):

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Open `.env` and set your MySQL credentials:
   ```env
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DB=pharmeasy_db
   ```
3. Run the MySQL setup script to create the database and seed the schema:
   ```powershell
   python init_mysql.py
   ```
4. Restart `app.py`. The footer will display `DATABASE CONNECTED: MYSQL`.

---

## 🔑 Demo Login Accounts

| Role | Email | Password | Access |
|---|---|---|---|
| **Customer** | `user@pharmeasy.com` | `user123` | Ordering, Cart, Upload Prescriptions, Profile, Orders |
| **Admin / Pharmacist** | `admin@pharmeasy.com` | `admin123` | Product CRUD, Order Status Manager, Prescription Review, Admin Dashboard |

*Note: On the login page, you can also click the quick **"Demo Customer"** or **"Demo Admin"** buttons to auto-fill these credentials.*

---

## 🎟️ Active Demo Coupons

- **`FIRST25`**: 25% OFF up to ₹250 on first medicine order (Min order ₹399).
- **`PHARMA15`**: 15% OFF up to ₹150 on all orders (Min order ₹499).
- **`CARE50`**: Flat ₹50 OFF on healthcare essentials (Min order ₹600).
- **`LAB100`**: Flat ₹100 OFF on diagnostic lab test bookings.

---

## 🧪 Running Automated Tests

Run the automated test suite covering all APIs, cart logic, orders, lab bookings, and all 12 page routes:
```powershell
python -m unittest tests/test_api.py
```
*(Or with full path)*:
```powershell
& "$env:LocalAppData\Programs\Python\Python312\python.exe" -m unittest tests/test_api.py
```
All 10 test suites pass with **OK**!

