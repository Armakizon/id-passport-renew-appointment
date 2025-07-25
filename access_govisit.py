from seleniumwire import webdriver  # <<<<< USE seleniumwire
from selenium.webdriver.common.by import By
import time
import requests

options = {
    'headless': False  # Change to True to run headless
}

driver = webdriver.Firefox(seleniumwire_options={}, options=webdriver.FirefoxOptions())

try:
    driver.get("https://govisit.gov.il/he/app/auth/login")
    time.sleep(5)

    driver.find_element(By.ID, "my_visits").click()
    time.sleep(5)

    phone_input = driver.find_element(By.XPATH, "//input[@type='tel']")
    phone_input.send_keys("0533319221")
    driver.find_element(By.ID, "login_button").click()
    print("Submitted phone number successfully")

    time.sleep(60)

    # Grab the code from your server
    response = requests.get("https://armakizon.pythonanywhere.com/")
    code = response.json().get("code")

    if code:
        print(f"Verification code received: {code}")
        driver.find_element(By.ID, "pincodeInput").send_keys(code)
        time.sleep(1)
        driver.find_element(By.ID, "verify-button").click()
        print("Verification code submitted")

        # Wait for verify request to be made
        time.sleep(3)

        # Now search for the request to /api/signUp/verify
        for request in driver.requests:
            if request.response and "api/signUp/verify" in request.url and request.method == "POST":
                token = request.response.headers.get("X-GoVisit-Token")
                print(f"✅ X-GoVisit-Token: {token}")
                break
        else:
            print("❌ No matching request found")
    else:
        print("❌ No code received")

finally:
    time.sleep(2)
    driver.quit()
