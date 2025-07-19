from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Launch Firefox with GeckoDriver
driver = webdriver.Firefox()

# Open the login page
driver.get("https://govisit.gov.il/he/home")
time.sleep(2)  # Allow page to load
button = driver.find_element(By.ID, "my_visits")
button.click()
time.sleep(2)

# Find the phone number input field
phone_input = driver.find_element(By.CSS_SELECTOR, 'input[type="tel"]')

# Input your number
phone_input.send_keys("0533319221")

# Optionally: click the next/submit button
# submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
# submit_btn.click()

# Done
