from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///local.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    days = db.relationship('Day', backref='location', cascade="all, delete")

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    times = db.relationship('TimeSlot', backref='day', cascade="all, delete")

class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String, nullable=False)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'), nullable=False)

@app.route('/', methods=['GET'])
def index():
    selected_location = request.args.get('location')
    selected_day = request.args.get('day')
    selected_time = request.args.get('time')

    query = TimeSlot.query.join(Day).join(Location)

    if selected_location:
        query = query.filter(Location.name == selected_location)
    if selected_day:
        query = query.filter(Day.date == date.fromisoformat(selected_day))
    if selected_time:
        query = query.filter(TimeSlot.time == selected_time)

    timeslots = query.all()
    locations = Location.query.all()
    return render_template('index.html', timeslots=timeslots, locations=locations)

@app.route('/init')
def init():
    db.create_all()
    return "Database initialized"

if __name__ == '__main__':
    app.run(debug=True)
