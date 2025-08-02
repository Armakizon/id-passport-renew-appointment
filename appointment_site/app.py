from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
from math import radians, cos, sin, sqrt, atan2
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
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 1)
@app.route("/")
def index():
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)

    entries = Entry.query.all()
    last_updated = get_last_updated()
    time_since = get_time_since(last_updated)

    entries_with_distance = []
    for entry in entries:
        branch = BRANCH_MAP.get(entry.branch_id, {})
        distance = None
        if user_lat is not None and user_lon is not None and branch:
            distance = calculate_distance(user_lat, user_lon, branch["lat"], branch["lon"])
        entries_with_distance.append({
            "branch_id": entry.branch_id,
            "branch_name": branch.get("name", entry.branch_id),
            "address": branch.get("address", "-"),
            "date": entry.date,
            "distance": distance
        })

    return render_template(
        "index.html",
        entries=entries_with_distance,
        last_updated=last_updated,
        time_since=time_since
    )


from api import register_api_routes
register_api_routes(app, db, Entry, set_last_updated)
