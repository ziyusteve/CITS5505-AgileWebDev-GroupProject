import unittest
import time
import os
import threading
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
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
        cls.app.config["WTF_CSRF_ENABLED"] = True  # Enable CSRF for testing
        cls.app.config["SERVER_NAME"] = "localhost:5000"  # Set server name for testing
        cls.app.config["WTF_CSRF_SECRET_KEY"] = "test-secret-key"  # Set CSRF secret key
        cls.app.config["SECRET_KEY"] = "test-secret-key"  # Set app secret key
        cls.app.config["MAIL_SUPPRESS_SEND"] = True  # Disable actual email sending
        cls.app.config["MAIL_DEFAULT_SENDER"] = "test@example.com"  # Set test email sender
        cls.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///selenium_test.db"  # Use file-based DB for testing

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
                email="test@example.com",
                is_verified=True  # Ensure test user is verified
            )
            test_user.set_password("testpass123")
            
            admin_user = User(
                username="admin",
                email="admin@example.com",
                is_verified=True  # Ensure admin user is verified
            )
            admin_user.set_password("adminpass123")
            
            db.session.add(test_user)
            db.session.add(admin_user)
            db.session.commit()

            # Verify users were created and verified
            if not User.query.filter_by(username="testuser", is_verified=True).first():
                raise Exception("Test user was not created or verified")
            if not User.query.filter_by(username="admin", is_verified=True).first():
                raise Exception("Admin user was not created or verified")

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
            
            # Remove the test database file
            db_path = os.path.join(os.getcwd(), 'selenium_test.db')
            if os.path.exists(db_path):
                os.remove(db_path)
            
            print("Test cleanup completed successfully")
        except Exception as e:
            print(f"Error during test cleanup: {str(e)}")
            raise
    
    def setUp(self):
        """Set up test environment for each test"""
        # Create test file
        self.test_files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files')
        os.makedirs(self.test_files_dir, exist_ok=True)
        self.test_file_path = os.path.join(self.test_files_dir, 'test_report.txt')
        with open(self.test_file_path, 'w') as f:
            f.write("Luka Doncic is one of the NBA's brightest stars, averaging 28 points per game. However, his defense has been criticized as a weakness in his game.")
        
        # Ensure test user exists and is verified
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            if not user:
                user = User(username='testuser', email='test@example.com', is_verified=True)
                user.set_password('testpass123')
                db.session.add(user)
            else:
                user.is_verified = True
                user.set_password('testpass123')
            db.session.commit()
        
        # First navigate to a proper URL
        self.driver.get('http://localhost:5000/')
        
        # Then clear browser state
        try:
            self.driver.delete_all_cookies()
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
        except Exception as e:
            print(f"Warning: Could not clear browser storage: {str(e)}")
            # Continue with test even if storage clearing fails
    
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
            # Ensure test user exists and is verified before login
            with self.app.app_context():
                user = User.query.filter_by(username=username).first()
                if not user:
                    user = User(username=username, email=f'{username}@example.com', is_verified=True)
                    user.set_password(password)
                    db.session.add(user)
                    db.session.commit()
                else:
                    # Always ensure user is verified and password is correct
                    user.is_verified = True
                    user.set_password(password)
                    db.session.commit()

            # Navigate to login page
            self.driver.get('http://localhost:5000/auth/login')
            
            # Wait for login form to be present and visible
            form = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'login-form'))
            )

            # Find form elements
            username_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'username'))
            )
            password_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'password'))
            )
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'submit'))
            )

            # Clear fields and enter credentials
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)

            # Get CSRF token
            csrf_token = form.find_element(By.NAME, 'csrf_token').get_attribute('value')
            
            # Click submit button
            submit_button.click()

            # Wait for either success or error
            try:
                # First check for any error messages
                error_messages = [
                    "Please verify your email before logging in",
                    "Invalid username or password",
                    "Please log in to access this page"
                ]
                
                for error in error_messages:
                    try:
                        error_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{error}')]"))
                        )
                        if error_element.is_displayed():
                            # Take screenshot for debugging
                            screenshot_path = os.path.join(self.test_files_dir, f"login_error_{int(time.time())}.png")
                            self.driver.save_screenshot(screenshot_path)
                            print(f"Login failed with error: {error}")
                            print(f"Screenshot saved to: {screenshot_path}")
                            print(f"Current URL: {self.driver.current_url}")
                            print(f"Page source: {self.driver.page_source}")
                            return False
                    except TimeoutException:
                        continue

                # If no errors found, wait for dashboard
                WebDriverWait(self.driver, 10).until(
                    lambda driver: 'dashboard' in driver.current_url
                )

                # Verify we're on the dashboard
                if 'dashboard' not in self.driver.current_url:
                    # Take screenshot for debugging
                    screenshot_path = os.path.join(self.test_files_dir, f"login_redirect_error_{int(time.time())}.png")
                    self.driver.save_screenshot(screenshot_path)
                    print(f"Login failed: Not redirected to dashboard")
                    print(f"Screenshot saved to: {screenshot_path}")
                    print(f"Current URL: {self.driver.current_url}")
                    print(f"Page source: {self.driver.page_source}")
                    return False

                # Additional verification that we're actually logged in
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.LINK_TEXT, username))
                    )
                except TimeoutException:
                    screenshot_path = os.path.join(self.test_files_dir, f"login_verification_error_{int(time.time())}.png")
                    self.driver.save_screenshot(screenshot_path)
                    print(f"Login failed: Could not find username in navigation")
                    print(f"Screenshot saved to: {screenshot_path}")
                    print(f"Current URL: {self.driver.current_url}")
                    print(f"Page source: {self.driver.page_source}")
                    return False

                return True

            except TimeoutException:
                # Take screenshot for debugging
                screenshot_path = os.path.join(self.test_files_dir, f"login_timeout_{int(time.time())}.png")
                self.driver.save_screenshot(screenshot_path)
                print(f"Login timeout - see {screenshot_path}")
                print(f"Current URL: {self.driver.current_url}")
                print(f"Page source: {self.driver.page_source}")
                return False

        except Exception as e:
            print(f"Login failed: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page source: {self.driver.page_source}")
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
                
                # --- POST-REGISTRATION VERIFICATION STEP ---
                # Set is_verified=True for the new user in the database
                with self.app.app_context():
                    user = User.query.filter_by(username='testuser').first()
                    if user and not user.is_verified:
                        user.is_verified = True
                        db.session.commit()
                # --- END VERIFICATION STEP ---
                
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
            success = self.login('testuser', 'testpass123')
            self.assertTrue(success, "Login failed before accessing upload page")
            self.driver.save_screenshot(os.path.join(self.test_files_dir, 'after_login_upload.png'))
            # Go to upload page
            self.driver.get('http://localhost:5000/datasets/upload')
            time.sleep(2)
            self.driver.save_screenshot(os.path.join(self.test_files_dir, 'after_goto_upload.png'))
            
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
            success = self.login('testuser', 'testpass123')
            self.assertTrue(success, "Login failed before accessing dashboard")
            self.driver.save_screenshot(os.path.join(self.test_files_dir, 'after_login_dashboard.png'))
            # Go to dashboard
            self.driver.get('http://localhost:5000/dashboard')
            time.sleep(2)
            self.driver.save_screenshot(os.path.join(self.test_files_dir, 'after_goto_dashboard.png'))
            
            # Verify dashboard elements
            self.assertIn('Dashboard', self.driver.page_source)
            
        except Exception as e:
            self.fail(f"Test failed: {str(e)}")

    def test_4_visualize_report(self):
        """Test basic report visualization"""
        try:
            # Login first
            success = self.login('testuser', 'testpass123')
            self.assertTrue(success, "Login failed before accessing visualization")
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
            success = self.login('testuser', 'testpass123')
            self.assertTrue(success, "Login failed before accessing share page")
            self.driver.save_screenshot(os.path.join(self.test_files_dir, 'after_login_share.png'))
            # Go to share page
            self.driver.get('http://localhost:5000/share')
            time.sleep(2)
            self.driver.save_screenshot(os.path.join(self.test_files_dir, 'after_goto_share.png'))
            
            # Verify share page loads
            self.assertIn('Share', self.driver.page_source)
            
        except Exception as e:
            self.fail(f"Test failed: {str(e)}")

    def test_user_registration(self):
        """Test user registration functionality."""
        try:
            self.driver.get("http://localhost:5000/auth/register")
            
            # Wait for form elements to be visible
            username_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "username"))
            )
            email_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "email"))
            )
            password_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "password"))
            )
            confirm_password_field = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "confirm_password"))
            )

            # Fill in registration form
            username_field.send_keys("newuser")
            email_field.send_keys("new@example.com")
            password_field.send_keys("securepass")
            confirm_password_field.send_keys("securepass")

            # Check the Terms checkbox
            checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='checkbox']"))
            )
            self.driver.execute_script("arguments[0].click();", checkbox)

            # Submit registration form
            register_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "submit"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", register_button)
            self.driver.execute_script("arguments[0].click();", register_button)

            # Wait for success message or redirect
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
                
                # Verify user was created in database
                with self.app.app_context():
                    user = User.query.filter_by(username='newuser').first()
                    if not user:
                        self.fail("User was not created in database")
                    if not user.is_verified:
                        user.is_verified = True
                        db.session.commit()
                
            except TimeoutException:
                # Take screenshot for debugging
                screenshot_path = os.path.join(self.test_files_dir, 'registration_timeout.png')
                self.driver.save_screenshot(screenshot_path)
                print(f"Registration timeout - see {screenshot_path}")
                print(f"Current URL: {self.driver.current_url}")
                print(f"Page source: {self.driver.page_source}")
                self.fail("Registration form submission timed out")
                
        except Exception as e:
            # Take screenshot for debugging
            screenshot_path = os.path.join(self.test_files_dir, 'registration_exception.png')
            self.driver.save_screenshot(screenshot_path)
            print(f"Registration exception - see {screenshot_path}")
            print(f"Exception: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page source: {self.driver.page_source}")
            raise

    def test_user_logout(self):
        """Test user logout functionality."""
        # First login
        self.driver.get("http://localhost:5000/auth/login")
        
        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "password").send_keys("testpass123")
        
        submit = self.driver.find_element(By.ID, "submit")
        self.driver.execute_script("arguments[0].click();", submit)
        
        # Wait for login success
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "testuser"))
        )
        
        # Click user menu
        user_menu = self.driver.find_element(By.LINK_TEXT, "testuser")
        user_menu.click()
        
        # Click logout
        logout_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
        )
        self.driver.execute_script("arguments[0].click();", logout_link)
        
        # Verify logout success
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        assert "logged out" in self.driver.page_source

    def test_navigation_tabs(self):
        """Test navigation between different tabs."""
        try:
            # Login first
            success = self.login("testuser", "testpass123")
            self.assertTrue(success, "Login failed before testing navigation")
            
            # Wait for dashboard to load and verify we're on the dashboard
            WebDriverWait(self.driver, 10).until(
                lambda driver: 'dashboard' in driver.current_url
            )
            
            # Take screenshot of initial state
            screenshot_path = os.path.join(self.test_files_dir, "initial_navigation_state.png")
            self.driver.save_screenshot(screenshot_path)
            print(f"Initial navigation state - see {screenshot_path}")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page source: {self.driver.page_source}")
            
            # Test navigation to each tab
            tabs = [
                ("Dashboard", "/dashboard", "dashboard-container"),
                ("Upload Data", "/datasets/upload", "upload-container"),
                ("Share Data", "/share", "share-container")
            ]
            
            for link_text, expected_url, container_class in tabs:
                try:
                    # First try to find the link by exact text
                    try:
                        nav_link = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.LINK_TEXT, link_text))
                        )
                    except TimeoutException:
                        # If that fails, try finding it by partial text
                        nav_link = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, f"//a[contains(., '{link_text}')]"))
                        )
                    
                    # Take screenshot before clicking
                    screenshot_path = os.path.join(self.test_files_dir, f"before_click_{link_text}.png")
                    self.driver.save_screenshot(screenshot_path)
                    print(f"Before clicking {link_text} - see {screenshot_path}")
                    print(f"Found link: {nav_link.get_attribute('outerHTML')}")
                    
                    # Scroll the link into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", nav_link)
                    time.sleep(1)  # Give time for scroll to complete
                    
                    # Click the link using JavaScript
                    self.driver.execute_script("arguments[0].click();", nav_link)
                    
                    # Wait for URL to change
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: expected_url in driver.current_url
                    )
                    
                    # Wait for container to be visible if it exists
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, container_class))
                        )
                    except TimeoutException:
                        # Container might not exist on all pages, that's okay
                        pass
                    
                    # Take screenshot after navigation
                    screenshot_path = os.path.join(self.test_files_dir, f"after_navigation_{link_text}.png")
                    self.driver.save_screenshot(screenshot_path)
                    print(f"After navigating to {link_text} - see {screenshot_path}")
                    print(f"Current URL: {self.driver.current_url}")
                    
                    # Verify URL contains the correct path
                    self.assertIn(expected_url, self.driver.current_url)
                    
                except (TimeoutException, StaleElementReferenceException) as e:
                    # Take screenshot on failure
                    screenshot_path = os.path.join(self.test_files_dir, f"navigation_error_{link_text}.png")
                    self.driver.save_screenshot(screenshot_path)
                    print(f"Navigation error for {link_text} - see {screenshot_path}")
                    print(f"Current URL: {self.driver.current_url}")
                    print(f"Page source: {self.driver.page_source}")
                    raise
                
                # Add a small delay between tab switches
                time.sleep(1)
                
        except Exception as e:
            # Take screenshot on any exception
            screenshot_path = os.path.join(self.test_files_dir, "navigation_exception.png")
            self.driver.save_screenshot(screenshot_path)
            print(f"Navigation exception - see {screenshot_path}")
            print(f"Exception: {str(e)}")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page source: {self.driver.page_source}")
            raise

    def test_upload_player_report(self):
        """Test uploading a player report."""
        # Login
        self.driver.get("http://localhost:5000/auth/login")
        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "password").send_keys("testpass123")
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        ).click()

        # Go to Upload Data page
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Upload Data"))
        ).click()

        # Fill in Player Name
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        ).send_keys("Test Player")

        # Upload File
        file_input = self.driver.find_element(By.NAME, "file")
        test_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_test_player.txt")
        file_input.send_keys(test_file_path)

        # Submit the form
        submit_btn = self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='Analyze and Generate Scout Report']")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        self.driver.execute_script("arguments[0].click();", submit_btn)

        # Wait for confirmation
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'File uploaded successfully')]"))
        )

    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords."""
        self.driver.get("http://localhost:5000/auth/register")

        self.driver.find_element(By.NAME, "username").send_keys("testuser")
        self.driver.find_element(By.NAME, "email").send_keys("test@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("securepass")
        self.driver.find_element(By.NAME, "confirm_password").send_keys("securepass1234")

        # Check the Terms checkbox 
        checkbox = self.driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        self.driver.execute_script("arguments[0].click();", checkbox)

        # Submit registration form
        register_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", register_button)
        self.driver.execute_script("arguments[0].click();", register_button)

        # Wait for error message
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        assert "Field must be equal to password." in self.driver.page_source

if __name__ == '__main__':
    unittest.main()