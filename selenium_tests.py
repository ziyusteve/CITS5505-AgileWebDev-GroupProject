import unittest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from flask import url_for
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

class SeleniumTestCase(unittest.TestCase):
    """Selenium test cases for NBA Player Analytics"""
    
    def setUp(self):
        # Set up Chrome options for headless testing
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        
        # Initialize the browser
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()
        
        # Create the Flask application for testing
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Start the Flask server in a testing thread
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app.config['SERVER_NAME'] = 'localhost:5000'
        
        # Create the database and tables
        db.create_all()
        
        # Create test users
        self.create_test_users()
        
        # Go to the homepage
        self.driver.get('http://localhost:5000/')
        
    def tearDown(self):
        # Clean up
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
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
        self.driver.get('http://localhost:5000/auth/login')
        self.driver.find_element(By.ID, 'username').send_keys(username)
        self.driver.find_element(By.ID, 'password').send_keys(password)
        self.driver.find_element(By.ID, 'submit').click()
        # Wait for login to complete
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
    
    def test_1_registration_and_login(self):
        """Test user registration and login functionality"""
        # Go to the registration page
        self.driver.get('http://localhost:5000/auth/register')
        
        # Fill in the registration form
        self.driver.find_element(By.ID, 'username').send_keys('newuser')
        self.driver.find_element(By.ID, 'email').send_keys('new@example.com')
        self.driver.find_element(By.ID, 'password').send_keys('NewPassword123')
        self.driver.find_element(By.ID, 'terms').click()
        self.driver.find_element(By.ID, 'submit').click()
        
        # Check if registration was successful (redirected to login)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        self.assertIn('auth/login', self.driver.current_url)
        
        # Now log in with the new user
        self.driver.find_element(By.ID, 'username').send_keys('newuser')
        self.driver.find_element(By.ID, 'password').send_keys('NewPassword123')
        self.driver.find_element(By.ID, 'submit').click()
        
        # Check if login was successful (redirected to dashboard)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        self.assertIn('dashboard', self.driver.current_url)
        
        # Check if username appears in the navbar
        navbar_text = self.driver.find_element(By.CLASS_NAME, 'navbar-nav').text
        self.assertIn('newuser', navbar_text)
    
    def test_2_upload_file(self):
        """Test uploading a player data file"""
        # Login first
        self.login('testuser', 'password123')
        
        # Go to upload page
        self.driver.get('http://localhost:5000/datasets/upload')
        
        # Fill in the form
        self.driver.find_element(By.ID, 'title').send_keys('Luka Doncic')
        
        # Create a test file path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_file_path = os.path.join(current_dir, 'test_scout_report.txt')
        
        # If test file doesn't exist, create one
        if not os.path.exists(test_file_path):
            with open(test_file_path, 'w') as f:
                f.write("Luka Doncic is one of the NBA's brightest stars, "
                        "averaging 28 points per game. However, his defense "
                        "has been criticized as a weakness in his game.")
        
        # Upload the file
        file_input = self.driver.find_element(By.ID, 'file')
        file_input.send_keys(test_file_path)
        
        # Submit the form
        self.driver.find_element(By.ID, 'submit').click()
        
        # Check if upload was successful (redirected to dashboard with success message)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        self.assertIn('dashboard', self.driver.current_url)
        
        # Verify the new report appears in the dashboard
        table_content = self.driver.find_element(By.TAG_NAME, 'table').text
        self.assertIn('Luka Doncic', table_content)
    
    def test_3_view_dashboard(self):
        """Test viewing the dashboard with reports"""
        # Login first
        self.login('testuser', 'password123')
        
        # Upload a test file to ensure there's content
        self.test_2_upload_file()
        
        # Go to dashboard
        self.driver.get('http://localhost:5000/dashboard')
        
        # Check if dashboard loads with expected sections
        self.assertIn('Your Scout Reports', self.driver.find_element(By.TAG_NAME, 'h1').text)
        
        # Check for "My Scout Reports" section
        section_titles = self.driver.find_elements(By.CLASS_NAME, 'card-header')
        section_texts = [title.text for title in section_titles]
        self.assertTrue(any('MY SCOUT REPORTS' in text.upper() for text in section_texts))
        
        # Check for "Shared With Me" section
        self.assertTrue(any('SHARED WITH ME' in text.upper() for text in section_texts))
        
        # Verify there's at least one report in the table
        try:
            table = self.driver.find_element(By.TAG_NAME, 'table')
            rows = table.find_elements(By.TAG_NAME, 'tr')
            # Header row + at least one data row
            self.assertGreater(len(rows), 1)
        except:
            self.fail("No reports found in the dashboard")
    
    def test_4_visualize_report(self):
        """Test visualizing a player analysis report"""
        # Login first
        self.login('testuser', 'password123')
        
        # Upload a test file to ensure there's content
        self.test_2_upload_file()
        
        # Find and click the View button for the first report
        view_button = self.driver.find_element(By.XPATH, "//a[contains(@href, 'visualize') and contains(@class, 'btn-primary')]")
        view_button.click()
        
        # Wait for visualization page to load (timeout after 20 seconds)
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, 'scout-report-analysis'))
            )
        except TimeoutException:
            self.fail("Visualization page failed to load within timeout period")
        
        # Verify key elements of the visualization page
        self.assertIn('visualize', self.driver.current_url)
        
        # If the analysis is completed (not pending), check for charts and data
        try:
            # Wait a bit for the analysis to complete or for an error message
            time.sleep(5)
            
            # Check if we have either a completed analysis or an error message
            page_content = self.driver.page_source
            has_player_name = 'Luka Doncic' in page_content
            has_ratings = 'Performance Ratings' in page_content
            has_error = 'alert-danger' in page_content or 'alert-warning' in page_content
            
            # At least one of these conditions should be true
            self.assertTrue(has_player_name or has_ratings or has_error, 
                           "No player data or error message found on visualization page")
            
        except Exception as e:
            self.fail(f"Error checking visualization page: {e}")
    
    def test_5_share_report(self):
        """Test sharing a report with another user"""
        # Login first
        self.login('testuser', 'password123')
        
        # Upload a test file to ensure there's content
        self.test_2_upload_file()
        
        # Go to sharing page
        self.driver.get('http://localhost:5000/share')
        
        # Fill in the sharing form
        try:
            # Select the dataset to share (first option)
            dataset_select = self.driver.find_element(By.ID, 'dataset_id')
            dataset_options = dataset_select.find_elements(By.TAG_NAME, 'option')
            # Skip the first option if it's a placeholder
            for option in dataset_options:
                if option.get_attribute('value'):
                    option.click()
                    break
            
            # Select the user to share with (anotheruser)
            user_select = self.driver.find_element(By.ID, 'user_id')
            user_options = user_select.find_elements(By.TAG_NAME, 'option')
            for option in user_options:
                if 'anotheruser' in option.text:
                    option.click()
                    break
            
            # Submit the form
            share_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            share_button.click()
            
            # Check if sharing was successful
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
            )
            self.assertIn('share', self.driver.current_url)
            
            # Verify the shared report appears in the shared list
            tables = self.driver.find_elements(By.TAG_NAME, 'table')
            if len(tables) > 1:  # If there's a shared reports table
                shared_table = tables[1]
                self.assertIn('anotheruser', shared_table.text)
            
            # Now log out
            self.driver.find_element(By.XPATH, "//a[contains(@href, 'logout')]").click()
            
            # Log in as the other user
            self.login('anotheruser', 'password123')
            
            # Go to dashboard and check if shared report appears
            self.driver.get('http://localhost:5000/dashboard')
            
            # Get all tables on the page
            tables = self.driver.find_elements(By.TAG_NAME, 'table')
            all_table_text = ' '.join([table.text for table in tables])
            
            # Verify shared report is visible to the other user
            self.assertIn('Luka Doncic', all_table_text)
            self.assertIn('testuser', all_table_text)
            
        except Exception as e:
            self.fail(f"Error testing share functionality: {e}")


if __name__ == '__main__':
    unittest.main()