from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import time
import random
import requests
from dotenv import load_dotenv
import os
import tempfile
import shutil

load_dotenv()
password=os.getenv("PASSWORD")

def create_temporary_profile():
    """Create a temporary Firefox profile that won't interfere with main profile"""
    temp_dir = tempfile.mkdtemp(prefix="firefox_temp_")
    print(f"🔧 Created temporary profile: {temp_dir}")
    return temp_dir

def cleanup_temporary_profile(profile_path):
    """Clean up temporary profile directory"""
    try:
        if os.path.exists(profile_path):
            shutil.rmtree(profile_path)
            print(f"🧹 Cleaned up temporary profile: {profile_path}")
    except Exception as e:
        print(f"⚠️ Warning: Could not clean up profile {profile_path}: {e}")

def random_sleep(base=2.5, jitter=1.0):
    time.sleep(base + random.uniform(0, jitter))

def get_govisit_token(wait_for_code=60):
    # Create a temporary profile instead of using existing one
    temp_profile_path = create_temporary_profile()
    
    try:
        options = Options()
        options.profile = temp_profile_path
        
        # Set language and user-agent - using profile-specific preferences to avoid global interference
        # These preferences are now isolated to the temporary profile only
        options.set_preference("intl.accept_languages", "en-US, en")
        options.set_preference("general.useragent.override", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0")
        
        # Enhanced profile isolation settings
        options.set_preference("profile.default_helpers", "")
        options.set_preference("profile.managed_default_content_settings.images", 1)
        options.set_preference("profile.default_content_setting_values.notifications", 2)
        
        # Firefox compatibility and security settings
        options.set_preference("security.fileuri.strict_origin_policy", False)
        options.set_preference("dom.disable_beforeunload", True)
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        
        # Additional settings for newer Firefox versions to prevent SecurityError
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)
        options.set_preference("marionette", True)
        options.set_preference("marionette.port", 0)  # Use random port
        options.set_preference("marionette.log.level", "Warn")
        
        # Remove duplicate user-agent override (was duplicated in original code)
        # options.set_preference("general.useragent.override", 
        #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0")

        try:
            print("🚀 Initializing Firefox driver with temporary profile...")
            driver = webdriver.Firefox(
                options=options,
                seleniumwire_options={}
            )
            print("✅ Firefox driver initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Firefox driver: {e}")
            print("🔧 This might be due to Firefox version compatibility or Selenium version issues")
            
            # Try fallback options for older Firefox versions
            print("🔄 Trying fallback Firefox options...")
            try:
                # Remove problematic preferences for older Firefox versions
                options.set_preference("marionette", False)
                options.set_preference("marionette.port", None)
                options.set_preference("marionette.log.level", None)
                
                driver = webdriver.Firefox(
                    options=options,
                    seleniumwire_options={}
                )
                print("✅ Firefox driver initialized with fallback options")
            except Exception as fallback_error:
                print(f"❌ Fallback options also failed: {fallback_error}")
                print("🔧 Please check your Firefox version and Selenium compatibility")
                raise fallback_error

        # Note: Temporary profile isolation is handled by Selenium's profile system
        # No additional JavaScript isolation needed - the profile separation is sufficient

        try:
            driver.get("https://govisit.gov.il/he/app/auth/login")
            random_sleep(2, 1)

            # Override navigator.webdriver to undefined
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            driver.find_element(By.ID, "my_visits").click()
            random_sleep(3, 1)

            phone_input = driver.find_element(By.XPATH, "//input[@type='tel']")
            phone_number = os.getenv("PHONE_NUMBER")
            phone_input.send_keys(phone_number)  
            random_sleep(2, 0.5)

            driver.find_element(By.ID, "login_button").click()
            print("📱 Phone number submitted")

            time.sleep(wait_for_code)  # Waiting for SMS code as before

            url = "https://armakizon.pythonanywhere.com/"
            params = {"password": password}

            response = requests.get(url, params=params)
            code = response.json().get("code")

            if not code:
                print("❌ No code received from server")
                return None

            print(f"✅ Code received: {code}")
            driver.find_element(By.ID, "pincodeInput").send_keys(code)
            random_sleep(2, 0.5)

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
            
    finally:
        # Always clean up the temporary profile
        cleanup_temporary_profile(temp_profile_path)
