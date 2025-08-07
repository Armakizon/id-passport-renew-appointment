from flask import Blueprint, request, redirect, jsonify
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
import json

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
        expected = os.environ.get("RESET_TOKEN", "devtoken")
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
    initialize_db()
    upsert_email(email, locations, fromdate, todate)

    return redirect("/")


def upsert_email(email, locations, fromdate=None, todate=None):
    # If 'locations' is a JSON string, parse it
    try:
        loc_list = json.loads(locations)
    except (json.JSONDecodeError, TypeError):
        loc_list = []

    conn = sqlite3.connect("subscriptions.db")
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
    conn.close()

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
