from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time

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
    #time.sleep(4)


    # Step 2: Click the send SMS button
    button = driver.find_element(By.ID, "login_button")
    button.click()

    print("Submitted phone number successfully")

    # Wait to receive the SMS
    time.sleep(10)

finally:
    driver.quit()
