from access_govisit import get_govisit_token

token = get_govisit_token(wait_for_code=60)

if token:
    print("🎉 Token received:")
    print(token)
else:
    print("⚠️ Failed to retrieve token.")
