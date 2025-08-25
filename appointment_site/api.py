from flask import Blueprint, request, redirect, jsonify
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
import json
import requests

load_dotenv()  # Load environment variables from .env file
from_email = os.getenv("EMAIL_ADDRESS")
password = os.getenv("EMAIL_PASSWORD")
api = Blueprint('api', __name__)
db_path="subscriptions.db"

import sqlite3
import os

def initialize_db():
    db_path = "/data/subscriptions.db"
    os.makedirs("/data", exist_ok=True)

    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE "subscriptions" (
                "id" INTEGER NOT NULL,
                "email" TEXT NOT NULL UNIQUE,
                "locations" TEXT,
                "fromdate" DATETIME,
                "todate" DATETIME,
                PRIMARY KEY("id" AUTOINCREMENT)
            )
        """)
        conn.commit()
        conn.close()
        print("Database initialized.")
    else:
        print("Database already exists.")


def register_api_routes(app, db, Entry, set_last_updated):
    @app.route("/add", methods=["POST"])
    def add_entry():
        data = request.get_json()
        if not all(k in data for k in ("date", "branch_id")):
            return {"status": "error", "message": "Missing fields"}, 400

        new_entry = Entry(branch_id=data["branch_id"], date=data["date"])
        db.session.add(new_entry)
        set_last_updated()
        db.session.commit()
        return {"status": "ok", "message": "Entry added", "id": new_entry.id}

    @app.route("/reset", methods=["POST"])
    def reset_db():
        token = request.args.get("token")
        expected = os.environ.get("PASSWORD")
        if token != expected:
            return {"status": "unauthorized", "message": "Invalid token"}, 401

        try:
            db.session.query(Entry).delete()
            set_last_updated()
            db.session.commit()
            return {"status": "ok", "message": "Database reset"}
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

@api.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form["email"]
    locations = request.form.get("locations", "[]")
    fromdate = request.form.get("fromdate") or None
    todate = request.form.get("todate") or None

    # Instead of initialize_db() and upsert_email, send POST request to external API:
    api_url = "https://armakizon.pythonanywhere.com/subscribe"
    payload = {
        "email": email,
        "locations": locations,
        "fromdate": fromdate,
        "todate": todate
    }

    try:
        response = requests.post(api_url, data=payload)
        if response.status_code == 200:
            return redirect("/")  # or return success JSON, depends on your app flow
        else:
            return jsonify({"status": "error", "message": f"API call failed: {response.text}"}), 500
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"Request exception: {str(e)}"}), 500

def send_email(to_email, subject, body):

    if not from_email or not password:
        raise ValueError("Email credentials are not set in environment variables.")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_email, password)
        smtp.send_message(msg)
