import time
import random
from access_govisit import get_govisit_token
from govisit_requests import APIcall
from mailsender import main
from captchaenjoyer import apply_anti_captcha_strategies

while True:
    try:
        # Apply enhanced anti-captcha strategies
        apply_anti_captcha_strategies()
        
        token = get_govisit_token(wait_for_code=60)
        # token = 'your-manual-token-here'

        if token:
            print("🎉 Token received:")
            print(token)
            APIcall(token)
            main()  # Only run main() if token is valid
        else:
            print("⚠️ Failed to retrieve token.")
            # Don't run main()

    except Exception as e:
        print("❌ An error occurred during token retrieval:")
        print(e)
        # Don't run main() on exceptions either

    # Randomize sleep time to avoid predictable patterns
    base_sleep = 3751  # ~1 hour
    random_variation = random.uniform(0.8, 1.2)  # ±20% variation
    actual_sleep = int(base_sleep * random_variation)
    
    print(f"⏳ Sleeping for {actual_sleep} seconds ({actual_sleep/3600:.1f} hours) before next attempt...\n")
    time.sleep(actual_sleep)
