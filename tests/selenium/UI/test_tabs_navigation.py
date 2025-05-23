from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Flask app imports
from app import create_app
from app.models.user import User
from app.extensions import db

def setup_test_user():
    """Ensures testuser exists and is verified before test starts."""
    app = create_app()
    app.app_context().push()

    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username='testuser', email='test@example.com')
        user.set_password('securepass')
        user.is_verified = True
        db.session.add(user)
    else:
        user.is_verified = True

    db.session.commit()

def test_navigation_tabs():
    setup_test_user()
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:5000/auth/login")

    try:
        # Step 1: Login
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("securepass")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        ).click()

        # Step 2: Navigate to Home
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Home"))
        ).click()
        assert "Analyze New Player" in driver.page_source

        # Step 3: Navigate to Dashboard
        WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Dashboard"))
        ).click()
        assert "Upload " in driver.page_source

        # Step 4: Navigate to Upload Data
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Upload Data"))
        ).click()
        assert "Upload Player News/Description" in driver.page_source

        # Step 5: Navigate to Share Data
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Share Data"))
        ).click()
        assert "Create New Share" in driver.page_source
        assert "Current Shares" in driver.page_source

    finally:
        driver.quit()

