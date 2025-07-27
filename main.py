# main.py

import time
from access_govisit import get_govisit_token
from govisit_requests import APIcall

while True:
    print("🔁 Running scheduled token fetch...")
    token = get_govisit_token(wait_for_code=60)

    if token:
        print("🎉 Token received:")
        print(token)
        APIcall(token)  # Default CSV is "branch_ids.csv"
    else:
        print("⚠️ Failed to retrieve token.")

    print("⏱️ Sleeping for 1 hour...")
    time.sleep(3600)
