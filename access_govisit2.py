from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import requests

# Setup Firefox in headless mode (can turn off for debugging)
options = Options()
options.headless = False  # Set to True later for headless mode

driver = webdriver.Firefox(options=options)

try:
    driver.get("https://govisit.gov.il/he/app/auth/login")
    time.sleep(5)  # Wait for Angular to load the page
    button = driver.find_element(By.ID, "my_visits")
    button.click()
    time.sleep(5)

    # Step 1: Find the phone number input
    phone_input = driver.find_element(By.XPATH, "//input[@type='tel']")
    phone_input.send_keys("0533319221")  # Replace with your phone number

    # Step 2: Click the send SMS button
    button = driver.find_element(By.ID, "login_button")
    button.click()

    print("Submitted phone number successfully")

    # Wait to receive the SMS
    time.sleep(10)
    
    response = requests.get("https://armakizon.pythonanywhere.com/")
    data = response.json()
    code = data.get("code")
    if code:
        print(f"Verification code received: {code}")
        # Fill the code in the pincodeInput field
        pincode_input = driver.find_element(By.ID, "pincodeInput")
        pincode_input.send_keys(code)
        time.sleep(1)  # small delay before clicking verify
        
        # Click the verify button
        verify_button = driver.find_element(By.ID, "verify-button")
        verify_button.click()
        print("Verification code submitted")
    else:
        print("No code received yet")

finally:
#    driver.quit()
