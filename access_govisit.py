from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import random
import requests
import os

def delete_lock_files(profile_path):
    for filename in os.listdir(profile_path):
        if filename.endswith(".lock") or filename == "parent.lock":
            file_path = os.path.join(profile_path, filename)
            try:
                os.remove(file_path)
                print(f"Deleted lock file: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

def random_sleep(base=1.5, jitter=1.0):
    time.sleep(base + random.uniform(0, jitter))

def get_govisit_token(wait_for_code=60):
    profile_path = r'C:\Users\shake\AppData\Roaming\Mozilla\Firefox\Profiles\ezygy35n.Sele'
    
    # Delete lock files before launching Firefox
    delete_lock_files(profile_path)

    options = Options()
    options.headless = False
    options.profile = profile_path
    # Set language and user-agent (change user-agent to a real one if you want)
    options.set_preference("intl.accept_languages", "en-US, en")
    options.set_preference("general.useragent.override", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0")

    driver = webdriver.Firefox(
        options=options,
        seleniumwire_options={}
    )

    try:
        driver.get("https://govisit.gov.il/he/app/auth/login")
        random_sleep(2, 1)

        # Override navigator.webdriver to undefined
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        driver.find_element(By.ID, "my_visits").click()
        random_sleep(2, 1)

        phone_input = driver.find_element(By.XPATH, "//input[@type='tel']")
        phone_input.send_keys("0533319221")  
        random_sleep(0.5, 0.5)

        driver.find_element(By.ID, "login_button").click()
        print("📱 Phone number submitted")

        time.sleep(wait_for_code)  # Waiting for SMS code as before

        response = requests.get("https://armakizon.pythonanywhere.com/")
        code = response.json().get("code")

        if not code:
            print("❌ No code received from server")
            return None

        print(f"✅ Code received: {code}")
        driver.find_element(By.ID, "pincodeInput").send_keys(code)
        random_sleep(1, 0.5)

        driver.find_element(By.ID, "verify-button").click()
        print("✅ Verification code submitted")

        time.sleep(3)

        for request in driver.requests:
            if request.response and "api/signUp/verify" in request.url and request.method == "POST":
                token = request.response.headers.get("X-GoVisit-Token")
                print(f"✅ X-GoVisit-Token: {token}")
                return token

        print("❌ No matching request with token found")
        return None

    finally:
        random_sleep(1, 0.5)
        driver.quit()
