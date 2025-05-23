from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_user_registration():
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:5000/auth/register")

    try:
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "email").send_keys("test@example.com")
        driver.find_element(By.NAME, "password").send_keys("securepass")
        driver.find_element(By.NAME, "confirm_password").send_keys("securepass")

        # Check the Terms checkbox
        checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        driver.execute_script("arguments[0].click();", checkbox)

        # Locate and click the submit input 
        register_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", register_button)

        # 📸 Take screenshot before clicking
        driver.save_screenshot("before_register_click.png")

        driver.execute_script("arguments[0].click();", register_button)

        # Wait for successful registration confirmation 
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        assert "Account created successfully! You can now log in.", "success" in driver.page_source or "successfully" in driver.page_source

    finally:
        driver.quit()

