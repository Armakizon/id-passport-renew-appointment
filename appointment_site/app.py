from flask import Flask, request, render_template, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
import os
import csv
import smtplib
from email.mime.text import MIMEText
from api import register_api_routes, api

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.register_blueprint(api)

db = SQLAlchemy(app)

BRANCH_MAP = {}
with open("Branch_id.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["latitude"] and row["longitude"]:
            BRANCH_MAP[int(row["branch_id"])] = {
                "name": row["branch_name"],
                "address": row["Address"],
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"])
            }

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    branch_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)

class Meta(db.Model):
    key = db.Column(db.String, primary_key=True)
    value = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

def set_last_updated():
    israel_time = datetime.now(timezone("Asia/Jerusalem")).strftime("%Y-%m-%d %H:%M:%S")
    existing = Meta.query.filter_by(key="last_updated").first()
    if existing:
        existing.value = israel_time
    else:
        db.session.add(Meta(key="last_updated", value=israel_time))
    db.session.commit()

def get_last_updated():
    meta = Meta.query.filter_by(key="last_updated").first()
    return meta.value if meta else None

def get_time_since(updated_str):
    if not updated_str:
        return "Never"
    updated_time = datetime.strptime(updated_str, "%Y-%m-%d %H:%M:%S")
    updated_time = timezone("Asia/Jerusalem").localize(updated_time)
    delta = datetime.now(timezone("Asia/Jerusalem")) - updated_time
    days = delta.days
    seconds = delta.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m ago"

@app.route("/")
def index():
    entries = Entry.query.all()
    last_updated = get_last_updated()
    time_since = get_time_since(last_updated)

    entries_with_coords = []
    for entry in entries:
        branch = BRANCH_MAP.get(entry.branch_id, {})
        # Convert entry.date string to datetime and format as DD/MM/YYYY
        try:
            formatted_date = datetime.strptime(entry.date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            formatted_date = entry.date  # fallback if parsing fails

        entries_with_coords.append({
            "branch_id": entry.branch_id,
            "branch_name": branch.get("name", entry.branch_id),
            "address": branch.get("address", "-"),
            "date": formatted_date,
            "lat": branch.get("lat"),
            "lon": branch.get("lon")
        })

    return render_template(
        "index.html",
        entries=entries_with_coords,
        last_updated=last_updated,
        time_since=time_since,
        branch_map=BRANCH_MAP
    )

@app.route("/all_branches")
def all_branches():
    return jsonify([
        {
            "id": branch_id,
            "name": info["name"],
            "address": info["address"],
            "lat": info["lat"],
            "lon": info["lon"]
        }
        for branch_id, info in BRANCH_MAP.items()
    ])

register_api_routes(app, db, Entry, set_last_updated)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route("/filter_entries", methods=["GET"])
def filter_entries():
    start_date = request.args.get("startDate")  # e.g. "2025-01-01"
    end_date = request.args.get("endDate")      # e.g. "2025-02-01"
    active_branch_ids = request.args.getlist("branchId")  # e.g. ?branchId=135&branchId=137

    query = Entry.query

    # Filter by branch IDs if provided
    if active_branch_ids:
        try:
            branch_ids_int = list(map(int, active_branch_ids))
            query = query.filter(Entry.branch_id.in_(branch_ids_int))
        except ValueError:
            return jsonify({"error": "Invalid branchId"}), 400

    # Filter by start date
    if start_date:
        query = query.filter(Entry.date >= start_date)

    # Filter by end date
    if end_date:
        query = query.filter(Entry.date <= end_date)

    results = []
    for entry in query.all():
        branch = BRANCH_MAP.get(entry.branch_id, {})
        try:
            formatted_date = datetime.strptime(entry.date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            formatted_date = entry.date

        results.append({
            "branch_id": entry.branch_id,
            "branch_name": branch.get("name", entry.branch_id),
            "address": branch.get("address", "-"),
            "date": formatted_date,
            "lat": branch.get("lat"),
            "lon": branch.get("lon")
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
