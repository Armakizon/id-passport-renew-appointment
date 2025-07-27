from flask import Flask, request, jsonify
import re

app = Flask(__name__)

last_message = None
last_sender = None
last_code = None  # Store extracted verification code

@app.route("/", methods=["GET", "POST"])
def receive_sms():
    global last_message, last_sender, last_code
    if request.method == "POST":
        data = request.get_json()
        if not data or "sender" not in data or "message" not in data:
            return jsonify({"error": "Missing sender or message"}), 400

        last_sender = data["sender"]
        last_message = data["message"]

        # Extract 3–4 digit code using regex
        match = re.search(r"\b(\d{3,4})\b", last_message)
        last_code = match.group(1) if match else None

        print(f"Received SMS from {last_sender}: {last_message}")
        if last_code:
            print(f"Extracted code: {last_code}")
        else:
            print("No code found in message.")

        return jsonify({
            "status": "success",
            "sender": last_sender,
            "message": last_message,
            "code": last_code
        }), 200

    else:  # GET request
        if last_code:
            return jsonify({"code": last_code})
        else:
            return jsonify({"message": "No verification code received yet."}), 404
