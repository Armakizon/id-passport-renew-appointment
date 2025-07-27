from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import requests

def get_govisit_token(wait_for_code=60):
    # Your Firefox profile path
    profile_path = r'C:\Users\shake\AppData\Roaming\Mozilla\Firefox\Profiles\Sele.default'

    options = Options()
    options.headless = False

    # Set the profile to use
    options.profile = profile_path

    # Initialize the Firefox driver with Selenium Wire
    driver = webdriver.Firefox(seleniumwire_options={}, options=options)

    try:
        driver.get("https://govisit.gov.il/he/app/auth/login")
        time.sleep(2)

        driver.find_element(By.ID, "my_visits").click()
        time.sleep(2)

        phone_input = driver.find_element(By.XPATH, "//input[@type='tel']")
        phone_input.send_keys("0533319221")  # <-- Hardcoded phone number
        driver.find_element(By.ID, "login_button").click()
        print("📱 Phone number submitted")

        time.sleep(wait_for_code)

        # Get the code from the server
        response = requests.get("https://armakizon.pythonanywhere.com/")
        code = response.json().get("code")

        if not code:
            print("❌ No code received from server")
            return None

        print(f"✅ Code received: {code}")
        driver.find_element(By.ID, "pincodeInput").send_keys(code)
        time.sleep(1)
        driver.find_element(By.ID, "verify-button").click()
        print("✅ Verification code submitted")

        time.sleep(3)

        # Search for the token
        for request in driver.requests:
            if request.response and "api/signUp/verify" in request.url and request.method == "POST":
                token = request.response.headers.get("X-GoVisit-Token")
                print(f"✅ X-GoVisit-Token: {token}")
                return token

        print("❌ No matching request with token found")
        return None

    finally:
        time.sleep(5)
        driver.quit()
