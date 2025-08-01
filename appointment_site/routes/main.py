from flask import Blueprint, request, render_template
from models import Entry
from utils.branches import load_branch_map
from utils.distance import calculate_distance
from utils.timestamps import get_last_updated, get_time_since

main_routes = Blueprint("main", __name__)

BRANCH_MAP = load_branch_map()

@main_routes.route("/", methods=["GET"])
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

    return render_template("index.html", entries=entries_with_distance,
                           last_updated=last_updated, time_since=time_since)
