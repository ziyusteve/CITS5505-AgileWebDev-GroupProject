from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_user_logout():
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:5000/auth/login")

    try:
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("securepass")

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        driver.execute_script("arguments[0].click();", login_button)

        # Wait for the user dropdown to appear
        user_menu = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "testuser"))
        )
        user_menu.click()

        # Wait for any success alert to disappear
        try:
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "alert-success"))
            )
        except:
            pass  

        # Click logout link
        logout_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Logout"))
        )
        driver.execute_script("arguments[0].click();", logout_link)

        # Wait for logout redirect
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        assert "logged out" in driver.page_source

    finally:
        driver.quit()
