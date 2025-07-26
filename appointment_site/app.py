from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

@app.route("/", methods=["GET"])
def index():
    entries = Entry.query.all()
    return render_template_string("""
        <h1>Entries</h1>
        <ul>
        {% for entry in entries %}
            <li>ID: {{ entry.id }} — Date: {{ entry.date }}</li>
        {% endfor %}
        </ul>
    """, entries=entries)

@app.route("/add", methods=["POST"])
def add_entry():
    data = request.get_json()
    new_entry = Entry(id=data["id"], date=data["date"])
    db.session.add(new_entry)
    db.session.commit()
    return {"status": "ok", "message": "Entry added"}

if __name__ == "__main__":
    app.run()
