from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
import os
import csv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
        entries_with_coords.append({
            "branch_id": entry.branch_id,
            "branch_name": branch.get("name", entry.branch_id),
            "address": branch.get("address", "-"),
            "date": entry.date,
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

from api import register_api_routes
register_api_routes(app, db, Entry, set_last_updated)
