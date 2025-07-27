from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
import os
import csv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Load branch ID to name mapping
BRANCH_MAP = {}
with open("Branch_id.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        BRANCH_MAP[int(row["branch_id"])] = row["branch_name"]

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

@app.route("/", methods=["GET"])
def index():
    entries = Entry.query.all()
    last_updated = get_last_updated()
    time_since = get_time_since(last_updated)
    return render_template_string("""
        <h1>Entries</h1>
        <p><strong>Last Updated:</strong>
           {{ last_updated if last_updated else 'Never' }}
           ({{ time_since }})
        </p>
        <ul>
        {% for entry in entries %}
            <li>Branch: {{ branch_map.get(entry.branch_id, entry.branch_id) }} — Date: {{ entry.date }}</li>
        {% endfor %}
        </ul>
    """, entries=entries, last_updated=last_updated, time_since=time_since, branch_map=BRANCH_MAP)

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

if __name__ == "__main__":
    app.run()
