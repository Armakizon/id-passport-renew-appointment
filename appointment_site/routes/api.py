from flask import Blueprint, request, jsonify
from models import Entry
from utils.timestamps import set_last_updated
from app import db
from config import RESET_TOKEN

api_routes = Blueprint("api", __name__)

@api_routes.route("/add", methods=["POST"])
def add_entry():
    data = request.get_json()
    if not all(k in data for k in ("date", "branch_id")):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    new_entry = Entry(branch_id=data["branch_id"], date=data["date"])
    db.session.add(new_entry)
    set_last_updated()
    db.session.commit()
    return jsonify({"status": "ok", "message": "Entry added", "id": new_entry.id})

@api_routes.route("/reset", methods=["POST"])
def reset_db():
    token = request.args.get("token")
    if token != RESET_TOKEN:
        return jsonify({"status": "unauthorized", "message": "Invalid token"}), 401

    try:
        db.session.query(Entry).delete()
        set_last_updated()
        db.session.commit()
        return jsonify({"status": "ok", "message": "Database reset"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
