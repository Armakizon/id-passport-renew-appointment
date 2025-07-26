from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-generated
    date = db.Column(db.String, nullable=False)
    branch_id = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET"])
def index():
    entries = Entry.query.all()
    return render_template_string("""
        <h1>Entries</h1>
        <ul>
        {% for entry in entries %}
            <li>ID: {{ entry.id }} — Date: {{ entry.date }} — Branch ID: {{ entry.branch_id }}</li>
        {% endfor %}
        </ul>
    """, entries=entries)

@app.route("/add", methods=["POST"])
def add_entry():
    data = request.get_json()
    if not all(k in data for k in ("date", "branch_id")):
        return {"status": "error", "message": "Missing fields"}, 400

    new_entry = Entry(date=data["date"], branch_id=data["branch_id"])
    db.session.add(new_entry)
    db.session.commit()
    return {"status": "ok", "message": "Entry added", "id": new_entry.id}

if __name__ == "__main__":
    app.run()
