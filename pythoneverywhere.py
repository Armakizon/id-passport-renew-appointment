from flask import Flask, request, jsonify, redirect
import re
import os
import json
import sqlite3
from dotenv import load_dotenv

load_dotenv()

PASSWORD = os.getenv("PASSWORD")

app = Flask(__name__)

# Store last code in memory only (reset on restart)
last_code = None

DB_SUBSCRIPTIONS = "/home/Armakizon/subscriptions.db"  # full path recommended

def initialize_subscriptions_db():
    with sqlite3.connect(DB_SUBSCRIPTIONS) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                locations TEXT,
                fromdate DATETIME,
                todate DATETIME
            )
        """)

def upsert_email(email, locations, fromdate=None, todate=None):
    try:
        loc_list = json.loads(locations)
    except (json.JSONDecodeError, TypeError):
        loc_list = []

    with sqlite3.connect(DB_SUBSCRIPTIONS) as conn:
        cursor = conn.cursor()
        if not loc_list:  # Empty list → remove subscription
            cursor.execute("DELETE FROM subscriptions WHERE email = ?", (email,))
        else:  # Insert or update
            cursor.execute("""
                INSERT INTO subscriptions (email, fromdate, todate, locations)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    fromdate = excluded.fromdate,
                    todate = excluded.todate,
                    locations = excluded.locations
            """, (email, fromdate, todate, locations))
        conn.commit()

@app.route("/", methods=["GET", "POST"])
def receive_sms():
    global last_code
    if request.method == "POST":
        data = request.get_json()
        if not data or "sender" not in data or "message" not in data:
            return jsonify({"error": "Missing sender or message"}), 400

        message = data["message"]
        match = re.search(r"\b(\d{3,4})\b", message)
        last_code = match.group(1) if match else None

        return jsonify({"status": "success", "code": last_code}), 200

    else:
        password = request.args.get("password")
        if password != PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401

        if last_code:
            return jsonify({"code": last_code})
        else:
            return jsonify({"message": "No verification code received yet."}), 404

@app.route("/subscribe", methods=["POST", "GET"])
def subscribe():
    initialize_subscriptions_db()

    if request.method == "POST":
        email = request.form.get("email")
        locations = request.form.get("locations", "[]")
        fromdate = request.form.get("fromdate") or None
        todate = request.form.get("todate") or None

        if not email:
            return jsonify({"error": "Email is required"}), 400

        upsert_email(email, locations, fromdate, todate)
        return jsonify({"status": "subscription updated"}), 200

    else:  # GET
        password = request.args.get("password")
        if password != PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401

        with sqlite3.connect(DB_SUBSCRIPTIONS) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT email, locations, fromdate, todate FROM subscriptions")
            rows = cursor.fetchall()

            subscriptions = []
            for email, locations_json, fromdate, todate in rows:
                try:
                    loc_list = json.loads(locations_json) if locations_json else []
                except json.JSONDecodeError:
                    loc_list = []
                subscriptions.append({
                    "email": email,
                    "locations": loc_list,
                    "fromdate": fromdate,
                    "todate": todate
                })

            return jsonify({"subscriptions": subscriptions})
