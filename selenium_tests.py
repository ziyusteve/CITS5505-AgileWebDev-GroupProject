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
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

class SeleniumTestCase(unittest.TestCase):
    """Selenium test cases for NBA Player Analytics"""
    
    def setUp(self):
        # Set up Firefox options for headless testing
        self.options = FirefoxOptions()
        self.options.add_argument('--headless')
        
        # Initialize the Firefox browser
        self.driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=self.options
        )
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
        submit_button = self.driver.find_element(By.ID, 'submit')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        # Add a small wait to ensure the page has responded to the scroll
        import time
        time.sleep(0.5)
        # Now try clicking
        submit_button.click()
        
        # Check if login was successful (redirected to dashboard)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        self.assertIn('dashboard', self.driver.current_url)
        
        # Check if username appears in the navbar
        navbar_text = self.driver.find_element(By.CLASS_NAME, 'navbar-nav').text
        self.assertIn('newuser', navbar_text)
    
    # Rest of the test methods remain unchanged
    # ...

if __name__ == '__main__':
    unittest.main()