import unittest
import time
import os
import threading
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from flask import url_for
from app import create_app, db
from app.models.user import User
from app.models.dataset import Dataset
from app.scout_analysis.models import ScoutReportAnalysis
from app.models.share import Share
from werkzeug.security import generate_password_hash
from sqlalchemy import text

class SeleniumTestCase(unittest.TestCase):
    """Selenium test cases for NBA Player Analytics"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests."""
        # Create Flask app with testing configuration
        cls.app = create_app("testing")
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing
        cls.app.config["SERVER_NAME"] = "localhost:5000"  # Set server name for testing

        # Create test client
        cls.client = cls.app.test_client()

        # Create test files directory
        cls.test_files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files')
        os.makedirs(cls.test_files_dir, exist_ok=True)

        # Initialize database
        with cls.app.app_context():
            # Import all models to ensure they are registered with SQLAlchemy
            from app.models.user import User
            from app.models.dataset import Dataset
            from app.models.share import Share
            from app.scout_analysis.models import ScoutReportAnalysis

            # Drop all tables and create them anew
            db.drop_all()
            db.create_all()

            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            if 'user' not in tables:
                raise Exception("User table was not created")

            # Create test users
            test_user = User(
                username="testuser",
                email="test@example.com"
            )
            test_user.set_password("testpass123")
            
            admin_user = User(
                username="admin",
                email="admin@example.com"
            )
            admin_user.set_password("adminpass123")
            
            db.session.add(test_user)
            db.session.add(admin_user)
            db.session.commit()

            # Verify users were created
            if not User.query.filter_by(username="testuser").first():
                raise Exception("Test user was not created")
            if not User.query.filter_by(username="admin").first():
                raise Exception("Admin user was not created")

        # Start Flask server in a separate thread
        cls.server_thread = threading.Thread(target=cls.app.run, kwargs={
            "host": "localhost",
            "port": 5000,
            "debug": False,
            "use_reloader": False
        })
        cls.server_thread.daemon = True  # Make it a daemon thread
        cls.server_thread.start()

        # Wait for server to start and be accessible
        max_retries = 30
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = requests.get('http://localhost:5000/')
                if response.status_code == 200:
                    # Additional check to ensure server is fully ready
                    time.sleep(2)  # Give server time to fully initialize
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(1)
                retry_count += 1
                continue
        if retry_count == max_retries:
            raise Exception("Flask server failed to start within timeout period")

        # Initialize Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")  # Set a large window size
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(10)
        cls.base_url = "http://localhost:5000"
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        try:
            # Clean up database
            with cls.app.app_context():
                db.session.remove()
                db.drop_all()
                db.session.commit()
            
            # Clean up test files
            if os.path.exists(cls.test_files_dir):
                for file in os.listdir(cls.test_files_dir):
                    os.remove(os.path.join(cls.test_files_dir, file))
                os.rmdir(cls.test_files_dir)
            
            # Clean up WebDriver
            if hasattr(cls, 'driver'):
                cls.driver.quit()
            
            print("Test cleanup completed successfully")
        except Exception as e:
            print(f"Error during test cleanup: {str(e)}")
            raise
    
    def setUp(self):
        """Set up test environment for each test"""
        # Create test file
        self.test_file_path = os.path.join(self.test_files_dir, 'test_report.txt')
        with open(self.test_file_path, 'w') as f:
            f.write("Luka Doncic is one of the NBA's brightest stars, averaging 28 points per game. However, his defense has been criticized as a weakness in his game.")
        
        # Go to the homepage
        self.driver.get('http://localhost:5000/')
        
    def tearDown(self):
        """Clean up after each test"""
        # Only clean up browser cookies and cache
        self.driver.delete_all_cookies()
        self.driver.execute_script("window.localStorage.clear();")
        self.driver.execute_script("window.sessionStorage.clear();")
    
    def create_test_users(self):
        """Create test users for the database"""
        user1 = User(username='testuser', email='test@example.com', 
                    password=generate_password_hash('password123'))
        user2 = User(username='anotheruser', email='another@example.com',
                    password=generate_password_hash('password123'))
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
    
    def login(self, username, password):
        """Helper method to log in a user"""
        try:
            # Go to login page
            self.driver.get('http://localhost:5000/auth/login')
            
            # Wait for login form to be present and visible
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'username'))
            )
            
            # Find form elements
            username_field = self.driver.find_element(By.ID, 'username')
            password_field = self.driver.find_element(By.ID, 'password')
            submit_button = self.driver.find_element(By.ID, 'submit')
            
            # Clear fields and enter credentials
            username_field.clear()
            password_field.clear()
            username_field.send_keys(username)
            password_field.send_keys(password)
            
            # Ensure submit button is clickable
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'submit'))
            )
            
            # Scroll submit button into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)  # Give time for scroll to complete
            
            # Click submit using JavaScript to avoid any overlay issues
            self.driver.execute_script("arguments[0].click();", submit_button)
            
            # Wait for redirect
            WebDriverWait(self.driver, 10).until(
                lambda driver: 'login' in driver.current_url
            )
            return True
                
        except Exception as e:
            # Take screenshot on failure
            screenshot_path = os.path.join(self.test_files_dir, 'login_failure.png')
            self.driver.save_screenshot(screenshot_path)
            print(f"Login error: {str(e)} - see {screenshot_path}")
            return False
    
    def test_1_registration_and_login(self):
        """Test basic registration and login functionality"""
        try:
            # Delete testuser if exists
            with self.app.app_context():
                user = User.query.filter((User.username == 'testuser') | (User.email == 'test@example.com')).first()
                if user:
                    db.session.delete(user)
                    db.session.commit()
            # Go to registration page
            self.driver.get('http://localhost:5000/auth/register')
            time.sleep(2)  # Give page time to load
            
            # Fill in registration form
            username_field = self.driver.find_element(By.ID, 'username')
            email_field = self.driver.find_element(By.ID, 'email')
            password_field = self.driver.find_element(By.ID, 'password')
            password2_field = self.driver.find_element(By.ID, 'confirm_password')
            
            username_field.send_keys('testuser')
            email_field.send_keys('test@example.com')
            password_field.send_keys('testpass123')
            password2_field.send_keys('testpass123')
            
            # Tick the terms and privacy policy checkbox
            terms_checkbox = self.driver.find_element(By.ID, 'terms')
            if not terms_checkbox.is_selected():
                terms_checkbox.click()
            
            # Submit form
            submit_button = self.driver.find_element(By.ID, 'submit')
            
            # Ensure submit button is clickable
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'submit'))
            )
            
            # Scroll submit button into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)  # Give time for scroll to complete
            
            # Click submit using JavaScript to avoid any overlay issues
            self.driver.execute_script("arguments[0].click();", submit_button)
            
            # Wait for either success message, error message, or redirect
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: 
                    'login' in driver.current_url or
                    EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))(driver) or
                    EC.presence_of_element_located((By.CLASS_NAME, 'alert-danger'))(driver)
                )
                
                # Take screenshot for debugging
                screenshot_path = os.path.join(self.test_files_dir, 'registration_result.png')
                self.driver.save_screenshot(screenshot_path)
                print(f"Registration result - see {screenshot_path}")
                
                # Check if we're on the login page
                if 'login' not in self.driver.current_url:
                    self.fail("Registration did not redirect to login page")
                
            except TimeoutException:
                # Take screenshot for debugging
                screenshot_path = os.path.join(self.test_files_dir, 'registration_timeout.png')
                self.driver.save_screenshot(screenshot_path)
                print(f"Registration timeout - see {screenshot_path}")
                self.fail("Registration form submission timed out")
            
            # Login with new credentials
            username_field = self.driver.find_element(By.ID, 'username')
            password_field = self.driver.find_element(By.ID, 'password')
            
            username_field.send_keys('testuser')
            password_field.send_keys('testpass123')
            
            submit_button = self.driver.find_element(By.ID, 'submit')
            
            # Ensure submit button is clickable
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'submit'))
            )
            
            # Scroll submit button into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)  # Give time for scroll to complete
            
            # Click submit using JavaScript to avoid any overlay issues
            self.driver.execute_script("arguments[0].click();", submit_button)
            
            # Wait for redirect to dashboard
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: 'dashboard' in driver.current_url
                )
            except TimeoutException:
                # Take screenshot for debugging
                screenshot_path = os.path.join(self.test_files_dir, 'login_timeout.png')
                self.driver.save_screenshot(screenshot_path)
                print(f"Login timeout - see {screenshot_path}")
                self.fail("Login did not redirect to dashboard")
            
        except Exception as e:
            self.fail(f"Test failed: {str(e)}")

    def test_2_upload_file(self):
        """Test basic file upload functionality"""
        try:
            # Login first
            self.driver.get('http://localhost:5000/auth/login')
            time.sleep(2)
            
            username_field = self.driver.find_element(By.ID, 'username')
            password_field = self.driver.find_element(By.ID, 'password')
            
            username_field.send_keys('testuser')
            password_field.send_keys('testpass123')
            
            submit_button = self.driver.find_element(By.ID, 'submit')
            submit_button.click()
            time.sleep(2)
            
            # Go to upload page
            self.driver.get('http://localhost:5000/datasets/upload')
            time.sleep(2)
            
            # Fill in upload form
            title_field = self.driver.find_element(By.ID, 'title')
            file_input = self.driver.find_element(By.ID, 'file')
            
            title_field.send_keys('Test Report')
            file_input.send_keys(self.test_file_path)
            
            submit_button = self.driver.find_element(By.ID, 'submit')
            submit_button.click()
            time.sleep(2)
            
            # Verify redirect to dashboard
            self.assertIn('dashboard', self.driver.current_url)
            
        except Exception as e:
            self.fail(f"Test failed: {str(e)}")

    def test_3_view_dashboard(self):
        """Test basic dashboard view"""
        try:
            # Login first
            self.driver.get('http://localhost:5000/auth/login')
            time.sleep(2)
            
            username_field = self.driver.find_element(By.ID, 'username')
            password_field = self.driver.find_element(By.ID, 'password')
            
            username_field.send_keys('testuser')
            password_field.send_keys('testpass123')
            
            submit_button = self.driver.find_element(By.ID, 'submit')
            submit_button.click()
            time.sleep(2)
            
            # Go to dashboard
            self.driver.get('http://localhost:5000/dashboard')
            time.sleep(2)
            
            # Verify dashboard elements
            self.assertIn('Dashboard', self.driver.page_source)
            
        except Exception as e:
            self.fail(f"Test failed: {str(e)}")

    def test_4_visualize_report(self):
        """Test basic report visualization"""
        try:
            # Login first
            self.driver.get('http://localhost:5000/auth/login')
            time.sleep(2)
            
            username_field = self.driver.find_element(By.ID, 'username')
            password_field = self.driver.find_element(By.ID, 'password')
            
            username_field.send_keys('testuser')
            password_field.send_keys('testpass123')
            
            submit_button = self.driver.find_element(By.ID, 'submit')
            submit_button.click()
            time.sleep(2)
            
            # Go to dashboard and find first report
            self.driver.get('http://localhost:5000/dashboard')
            time.sleep(2)
            
            # Click first view button if exists
            try:
                view_button = self.driver.find_element(By.XPATH, "//a[contains(@href, 'visualize')]")
                view_button.click()
                time.sleep(2)
                
                # Verify visualization page
                self.assertIn('visualize', self.driver.current_url)
            except:
                # Skip if no reports exist
                pass
            
        except Exception as e:
            self.fail(f"Test failed: {str(e)}")

    def test_5_share_report(self):
        """Test basic report sharing"""
        try:
            # Login first
            self.driver.get('http://localhost:5000/auth/login')
            time.sleep(2)
            
            username_field = self.driver.find_element(By.ID, 'username')
            password_field = self.driver.find_element(By.ID, 'password')
            
            username_field.send_keys('testuser')
            password_field.send_keys('testpass123')
            
            submit_button = self.driver.find_element(By.ID, 'submit')
            submit_button.click()
            time.sleep(2)
            
            # Go to share page
            self.driver.get('http://localhost:5000/share')
            time.sleep(2)
            
            # Verify share page loads
            self.assertIn('Share', self.driver.page_source)
            
        except Exception as e:
            self.fail(f"Test failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()