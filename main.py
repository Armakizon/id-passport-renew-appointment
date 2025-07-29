import time
from access_govisit import get_govisit_token
from govisit_requests import APIcall

while True:
    try:
        token = get_govisit_token(wait_for_code=60)
        # token = 'your-manual-token-here'

        if token:
            print("🎉 Token received:")
            print(token)
            APIcall(token)
        else:
            print("⚠️ Failed to retrieve token.")

    except Exception as e:
        print("❌ An error occurred during token retrieval:")
        print(e)

    print("⏳ Sleeping for 1 hour before next attempt...\n")
    time.sleep(3751)
