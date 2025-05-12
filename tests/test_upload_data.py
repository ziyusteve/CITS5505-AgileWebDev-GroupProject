import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_upload_player_report():
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:5000/auth/login")

    try:
        # Login
        driver.find_element(By.NAME, "username").send_keys("testuser")
        driver.find_element(By.NAME, "password").send_keys("securepass")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        ).click()

        # Go to Upload Data page
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Upload Data"))
        ).click()

        # Fill in Player Name
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        ).send_keys("Test Player")

        # Upload File
        file_input = driver.find_element(By.NAME, "file")
        test_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data_test_player.txt"))
        file_input.send_keys(test_file_path)

        # Submit the form
        submit_btn = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Analyze and Generate Scout Report']")

        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        driver.execute_script("arguments[0].click();", submit_btn)

        # Wait for confirmation
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'File uploaded successfully')]"))
        )

    finally:
        driver.quit()
