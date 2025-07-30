from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
import os
import csv
from math import radians, cos, sin, sqrt, atan2

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Load branch data from CSV
BRANCH_MAP = {}
with open("Branch_id.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        BRANCH_MAP[int(row["branch_id"])] = {
            "name": row["branch_name"],
            "address": row["Address"],
            "lat": float(row["latitude"]),
            "lon": float(row["longitude"])
        }

# SQLAlchemy Models
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    branch_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)

class Meta(db.Model):
    key = db.Column(db.String, primary_key=True)
    value = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)

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

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Branch Entries</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            th {
                cursor: pointer;
                user-select: none;
            }
        </style>
    </head>
    <body class="container mt-4">
        <h1 class="mb-3">Branch Entries</h1>

        <p><strong>Last Updated:</strong>
           {{ last_updated if last_updated else 'Never' }}
           ({{ time_since }})
        </p>

        <div class="mb-3">
            <button onclick="getLocation()" class="btn btn-primary">📍 Find My Location</button>
            <button onclick="toggleEarliest()" class="btn btn-outline-secondary">🕐 Show Only Earliest Per Branch</button>
        </div>

        <table id="entry-table" class="table table-striped table-bordered">
            <thead class="table-light">
                <tr>
                    <th onclick="sortTable(0)">Branch <span></span></th>
                    <th onclick="sortTable(1)">Address <span></span></th>
                    <th onclick="sortTable(2)">Date <span></span></th>
                    <th onclick="sortTable(3)">Distance <span></span></th>
                </tr>
            </thead>
            <tbody id="entry-body">
            {% for entry in entries %}
                <tr data-branch="{{ entry.branch_id }}">
                    <td>{{ entry.branch_name }}</td>
                    <td>{{ entry.address }}</td>
                    <td>{{ entry.date }}</td>
                    <td>{% if entry.distance is not none %}{{ entry.distance }}{% else %}-{% endif %}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>

        <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(pos => {
                    const { latitude, longitude } = pos.coords;
                    const url = new URL(window.location.href);
                    url.searchParams.set("lat", latitude);
                    url.searchParams.set("lon", longitude);
                    window.location.href = url;
                }, err => {
                    alert("Location access denied or unavailable.");
                });
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        }

        let sortDirection = [true, true, true, true]; // ASC for each column

        function sortTable(colIndex) {
            const table = document.getElementById("entry-table");
            const tbody = table.tBodies[0];
            const rows = Array.from(tbody.rows);
            const isNumeric = colIndex === 3;
            const isDate = colIndex === 2;

            rows.sort((a, b) => {
                let A = a.cells[colIndex].innerText.trim();
                let B = b.cells[colIndex].innerText.trim();

                if (isNumeric) {
                    A = parseFloat(A) || 0;
                    B = parseFloat(B) || 0;
                } else if (isDate) {
                    A = new Date(A);
                    B = new Date(B);
                }

                if (A < B) return sortDirection[colIndex] ? -1 : 1;
                if (A > B) return sortDirection[colIndex] ? 1 : -1;
                return 0;
            });

            sortDirection[colIndex] = !sortDirection[colIndex];
            tbody.innerHTML = "";
            rows.forEach(row => tbody.appendChild(row));

            updateSortIcons(colIndex);
        }

        function updateSortIcons(colIndex) {
            const headers = document.querySelectorAll("#entry-table thead th");
            headers.forEach((th, i) => {
                th.querySelector("span").textContent = i === colIndex
                    ? (sortDirection[colIndex] ? "▲" : "▼")
                    : "";
            });
        }

        let showEarliestOnly = false;

        function toggleEarliest() {
            showEarliestOnly = !showEarliestOnly;
            const rows = Array.from(document.querySelectorAll("#entry-body tr"));
            const map = {};

            rows.forEach(row => {
                const branch = row.getAttribute("data-branch");
                const date = row.cells[2].innerText;
                if (!map[branch] || new Date(date) < new Date(map[branch].date)) {
                    map[branch] = { row, date };
                }
            });

            rows.forEach(row => row.style.display = "");

            if (showEarliestOnly) {
                const keep = new Set(Object.values(map).map(item => item.row));
                rows.forEach(row => {
                    if (!keep.has(row)) {
                        row.style.display = "none";
                    }
                });
            }
        }
        </script>
    </body>
    </html>
    """, entries=entries_with_distance, last_updated=last_updated, time_since=time_since)

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
