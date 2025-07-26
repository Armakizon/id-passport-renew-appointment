from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

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
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing = Meta.query.filter_by(key="last_updated").first()
    if existing:
        existing.value = now_str
    else:
        db.session.add(Meta(key="last_updated", value=now_str))
    db.session.commit()

def get_last_updated():
    meta = Meta.query.filter_by(key="last_updated").first()
    return meta.value if meta else "Never"

@app.route("/", methods=["GET"])
def index():
    entries = Entry.query.all()
    last_updated = get_last_updated()
    return render_template_string("""
        <h1>Entries</h1>
        <p><strong>Last Updated:</strong> {{ last_updated }}</p>
        <ul>
        {% for entry in entries %}
            <li>ID: {{ entry.id }} — Branch ID: {{ entry.branch_id }} — Date: {{ entry.date }}</li>
        {% endfor %}
        </ul>
    """, entries=entries, last_updated=last_updated)

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
