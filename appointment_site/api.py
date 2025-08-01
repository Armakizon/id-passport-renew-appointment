from flask import request, jsonify
import os

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
