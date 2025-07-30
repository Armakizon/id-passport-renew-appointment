from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
import os
import csv
from math import radians, cos, sin, sqrt, atan2
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Load branch data from CSV
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

# Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)

# Timestamps
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
    selected_branches = request.args.get("branches")
    selected_branch_ids = json.loads(selected_branches) if selected_branches else None
    only_earliest = request.args.get("earliest") == "true"
    sort_by = request.args.get("sort_by", "date")
    sort_dir = request.args.get("sort_dir", "asc")

    entries = Entry.query.all()
    last_updated = get_last_updated()
    time_since = get_time_since(last_updated)

    entry_map = {}
    for entry in entries:
        if selected_branch_ids and entry.branch_id not in selected_branch_ids:
            continue
        if entry.branch_id not in BRANCH_MAP:
            continue
        branch = BRANCH_MAP[entry.branch_id]
        key = entry.branch_id
        if only_earliest:
            if key not in entry_map or entry.date < entry_map[key].date:
                entry_map[key] = entry
        else:
            entry_map.setdefault(key, []).append(entry)

    display_entries = []
    for value in entry_map.values():
        if isinstance(value, list):
            for e in value:
                display_entries.append(e)
        else:
            display_entries.append(value)

    def sort_key(e):
        branch = BRANCH_MAP.get(e.branch_id, {})
        distance = calculate_distance(user_lat, user_lon, branch["lat"], branch["lon"]) if user_lat and user_lon else None
        if sort_by == "branch":
            return branch.get("name", "")
        elif sort_by == "distance":
            return distance if distance is not None else float('inf')
        else:
            return e.date

    reverse = sort_dir == "desc"
    display_entries.sort(key=sort_key, reverse=reverse)

    entries_with_distance = []
    for entry in display_entries:
        branch = BRANCH_MAP[entry.branch_id]
        distance = calculate_distance(user_lat, user_lon, branch["lat"], branch["lon"]) if user_lat and user_lon else None
        entries_with_distance.append({
            "branch_id": entry.branch_id,
            "branch_name": branch["name"],
            "address": branch["address"],
            "date": entry.date,
            "distance": distance
        })

    branch_options = [{
        "id": bid,
        "name": b["name"],
        "address": b["address"]
    } for bid, b in BRANCH_MAP.items()]

    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Appointments</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="p-4">
    <h1 class="mb-4">Appointments</h1>
    <p><strong>Last Updated:</strong> {{ last_updated or 'Never' }} ({{ time_since }})</p>

    <div class="mb-3">
        <button class="btn btn-secondary" onclick="getLocation()">📍 Use My Location</button>
        <label class="form-check-label ms-3">
            <input class="form-check-input" type="checkbox" id="earliestCheckbox" onchange="applyFilters()"> Show Only Earliest per Branch
        </label>
    </div>

    <div class="mb-3">
        <input class="form-control" id="searchInput" placeholder="Search branches..." oninput="filterBranches()">
        <div id="branchResults" class="list-group mt-2"></div>
    </div>

    <div id="selectedBranches" class="mb-3"></div>

    <table class="table table-bordered table-striped">
        <thead>
            <tr>
                <th><a href="#" onclick="sortBy('branch')">Branch Name</a></th>
                <th><a href="#" onclick="sortBy('address')">Address</a></th>
                <th><a href="#" onclick="sortBy('date')">Date</a></th>
                <th><a href="#" onclick="sortBy('distance')">Distance (km)</a></th>
            </tr>
        </thead>
        <tbody>
            {% for entry in entries %}
                <tr>
                    <td>{{ entry.branch_name }}</td>
                    <td>{{ entry.address }}</td>
                    <td>{{ entry.date }}</td>
                    <td>{{ entry.distance if entry.distance is not none else '' }}</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>

    <script>
        const allBranches = {{ branch_options | tojson }};
        let selected = {{ selected_branch_ids | tojson or "[]" }};
        let userLat = {{ user_lat or "null" }};
        let userLon = {{ user_lon or "null" }};
        let sortByField = "{{ sort_by }}";
        let sortDir = "{{ sort_dir }}";

        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(pos => {
                    userLat = pos.coords.latitude;
                    userLon = pos.coords.longitude;
                    applyFilters();
                }, () => alert("Location access denied."));
            } else {
                alert("Geolocation not supported.");
            }
        }

        function filterBranches() {
            const query = document.getElementById("searchInput").value.toLowerCase();
            const container = document.getElementById("branchResults");
            container.innerHTML = "";
            allBranches
                .filter(b => b.name.toLowerCase().includes(query) || b.address.toLowerCase().includes(query))
                .forEach(branch => {
                    const div = document.createElement("div");
                    div.className = "list-group-item list-group-item-action";
                    div.innerText = branch.name + " - " + branch.address;
                    div.onclick = () => {
                        if (!selected.includes(branch.id)) selected.push(branch.id);
                        applyFilters();
                    };
                    container.appendChild(div);
                });
        }

        function applyFilters() {
            const url = new URL(window.location.href.split("?")[0]);
            if (userLat && userLon) {
                url.searchParams.set("lat", userLat);
                url.searchParams.set("lon", userLon);
            }
            if (selected.length) url.searchParams.set("branches", JSON.stringify(selected));
            if (document.getElementById("earliestCheckbox").checked) url.searchParams.set("earliest", "true");
            url.searchParams.set("sort_by", sortByField);
            url.searchParams.set("sort_dir", sortDir);
            window.location.href = url.toString();
        }

        function sortBy(field) {
            if (sortByField === field) {
                sortDir = sortDir === "asc" ? "desc" : "asc";
            } else {
                sortByField = field;
                sortDir = "asc";
            }
            applyFilters();
        }

        window.onload = () => {
            const container = document.getElementById("selectedBranches");
            selected.forEach(id => {
                const branch = allBranches.find(b => b.id === id);
                if (!branch) return;
                const btn = document.createElement("button");
                btn.className = "btn btn-outline-primary btn-sm me-2 mb-2";
                btn.innerText = branch.name;
                btn.onclick = () => {
                    selected = selected.filter(b => b !== id);
                    applyFilters();
                };
                container.appendChild(btn);
            });
        }
    </script>
</body>
</html>
    """, entries=entries_with_distance, last_updated=last_updated,
       time_since=time_since, branch_options=branch_options,
       selected_branch_ids=selected_branch_ids, user_lat=user_lat, user_lon=user_lon,
       sort_by=sort_by, sort_dir=sort_dir)

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
