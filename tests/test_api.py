import unittest
import json
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from services.db import query, execute, init_tables
from database.seed_data import seed_all

class PharmEasyTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        init_tables()
        seed_all()

    def test_01_homepage_renders(self):
        """Test homepage renders with HTTP 200 and key PharmEasy brand elements"""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'PharmEasy', res.data)
        self.assertIn(b'Order Medicines', res.data)
        self.assertIn(b'Book Lab Tests', res.data)
        self.assertIn(b'Deals of the Day', res.data)
        self.assertIn(b'Trending Products', res.data)
        self.assertIn(b'Frequently Booked Lab Tests', res.data)

    def test_02_products_listing(self):
        """Test product listing and category filtering"""
        res = self.client.get('/products')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'All Medicines &amp; Health Products', res.data)

        # Test filtering by category
        res_cat = self.client.get('/products?category=medicines')
        self.assertEqual(res_cat.status_code, 200)
        self.assertIn(b'Dolo 650mg', res_cat.data)

    def test_03_product_detail(self):
        """Test product detail page loads with specifications and composition"""
        res = self.client.get('/product/dolo-650mg-tablet')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Dolo 650mg Tablet', res.data)
        self.assertIn(b'Paracetamol (650mg)', res.data)
        self.assertIn(b'Add to Cart', res.data)

    def test_04_search_suggestions_api(self):
        """Test instant search suggestions API"""
        res = self.client.get('/api/search/suggestions?q=dolo')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(len(data) > 0)
        self.assertIn('Dolo', data[0]['name'])

    def test_05_auth_flow(self):
        """Test customer registration and login"""
        # Register new user
        reg_res = self.client.post('/register', data={
            'name': 'Test User',
            'email': 'testuser_pytest@pharmeasy.com',
            'phone': '9811223344',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(reg_res.status_code, 200)

        # Logout
        self.client.get('/logout')

        # Login with newly created user
        login_res = self.client.post('/login', data={
            'email': 'testuser_pytest@pharmeasy.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Test', login_res.data)

    def test_06_cart_operations(self):
        """Test Add to Cart, Quantity Adjust, Coupon Apply, and Cart Summary"""
        # Get a product ID
        prod = query("SELECT id FROM products WHERE slug = 'dolo-650mg-tablet'", fetchone=True)
        self.assertIsNotNone(prod)

        # Add to cart
        add_res = self.client.post('/api/cart/add', json={
            'product_id': prod['id'],
            'quantity': 2
        })
        self.assertEqual(add_res.status_code, 200)
        add_data = json.loads(add_res.data)
        self.assertTrue(add_data['success'])
        self.assertEqual(add_data['cart_count'], 2)

        # Apply valid coupon FIRST25
        coupon_res = self.client.post('/api/coupons/apply', json={'code': 'FIRST25'})
        coupon_data = json.loads(coupon_res.data)
        # Check cart summary
        cart_res = self.client.get('/api/cart')
        cart_data = json.loads(cart_res.data)
        self.assertTrue(cart_data['success'])
        self.assertEqual(cart_data['cart']['items_count'], 2)

    def test_07_order_creation_and_tracking(self):
        """Test end-to-end checkout order creation"""
        # Add item to cart first
        prod = query("SELECT id FROM products LIMIT 1", fetchone=True)
        self.client.post('/api/cart/add', json={'product_id': prod['id'], 'quantity': 1})

        # Create Order
        order_res = self.client.post('/api/orders/create', json={
            'customer_name': 'Aakash Verma',
            'customer_email': 'aakash@example.com',
            'customer_phone': '9876541230',
            'payment_method': 'UPI',
            'address_data': {
                'full_name': 'Aakash Verma',
                'phone': '9876541230',
                'pincode': '110001',
                'address_line1': '12 Connaught Circus',
                'city': 'New Delhi',
                'state': 'Delhi'
            }
        })
        self.assertEqual(order_res.status_code, 200)
        order_data = json.loads(order_res.data)
        self.assertTrue(order_data['success'])
        self.assertIn('PE-', order_data['order_number'])

        # Check tracking page
        tracking_res = self.client.get(f"/order/{order_data['order_number']}")
        self.assertEqual(tracking_res.status_code, 200)
        self.assertIn(b'Order Placed Successfully', tracking_res.data)

    def test_08_lab_booking(self):
        """Test diagnostic lab test booking"""
        test = query("SELECT id FROM lab_tests LIMIT 1", fetchone=True)
        res = self.client.post('/api/lab-tests/book', json={
            'test_id': test['id'],
            'patient_name': 'Meera Joshi',
            'phone': '9822334455',
            'patient_age': 28,
            'patient_gender': 'Female',
            'booking_date': '2026-11-01',
            'time_slot': '07:30 AM - 08:30 AM',
            'address': 'Flat 101, Lakeview',
            'pincode': '110001'
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('LAB-', data['booking_number'])

    def test_09_admin_dashboard_and_product_crud(self):
        """Test admin login and product creation"""
        # Login as admin
        self.client.post('/login', data={'email': 'admin@pharmeasy.com', 'password': 'admin123'})

        # Access dashboard
        dash_res = self.client.get('/admin')
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b'Admin Dashboard', dash_res.data)

        # Create new product via admin API
        cat = query("SELECT id FROM categories LIMIT 1", fetchone=True)
        create_res = self.client.post('/api/admin/products/create', json={
            'name': 'Cipla Vitamin B12 1000mcg',
            'category_id': cat['id'],
            'mrp': 150.00,
            'discount_percent': 20,
            'stock': 100,
            'packaging': 'Strip of 10 Tablets',
            'composition': 'Cyanocobalamin 1000mcg',
            'description': 'Essential vitamin B12 supplement for nerve and RBC support.',
            'prescription_required': False,
            'is_trending': True
        })
        self.assertEqual(create_res.status_code, 200)
        create_data = json.loads(create_res.data)
        self.assertTrue(create_data['success'])

    def test_10_all_twelve_pages_return_200(self):
        """Verify all 12 requested pages render with HTTP 200 OK"""
        # Ensure user logged in for protected views
        self.client.post('/login', data={'email': 'admin@pharmeasy.com', 'password': 'admin123'})

        # Add an item to cart so checkout page renders without redirecting
        prod = query("SELECT id FROM products LIMIT 1", fetchone=True)
        self.client.post('/api/cart/add', json={'product_id': prod['id'], 'quantity': 1})

        pages = [
            ('/', b'PharmEasy'),                                                  # 1. Home page
            ('/products', b'Healthcare Store'),                                  # 2. Product listing
            ('/product/dolo-650mg-tablet', b'Dolo 650mg Tablet'),                 # 3. Product details
            ('/search?q=vitamin', b'Search Results'),                            # 4. Search results
            ('/login', b'Sign In'),                                              # 5. Login
            ('/register', b'Register'),                                          # 5b. Registration
            ('/cart', b'Shopping Cart'),                                         # 6. Cart
            ('/checkout', b'Secure Checkout'),                                   # 7. Checkout demo
            ('/prescription', b'Upload Doctor\'s Prescription'),                 # 8. Prescription upload
            ('/lab-tests', b'Diagnostic Lab Tests'),                             # 9. Lab tests
            ('/offers', b'Wallet Offers'),                                       # 10. Offers
            ('/profile?tab=orders', b'My Account'),                              # 11. User profile
            ('/admin', b'Admin Dashboard'),                                      # 12. Admin dashboard
            ('/article/ways-to-keep-blood-pressure-healthy', b'Blood Pressure') # Health article
        ]

        for path, expected_text in pages:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Page {path} failed with status {res.status_code}")
            self.assertIn(expected_text, res.data, f"Page {path} missing expected content")

if __name__ == '__main__':
    unittest.main()
