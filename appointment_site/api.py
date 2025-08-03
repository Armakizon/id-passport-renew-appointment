from flask import request, jsonify, redirect, Blueprint
import smtplib
from email.mime.text import MIMEText
import os

api = Blueprint('api', __name__)

@api.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form["email"]
    phone = request.form["phone"]
    
    subject = "Your Appointment Subscription"
    body = f"Thank you! We've received your phone number {phone} and will notify you when an appointment is available."
    send_email(email, subject, body)

    return redirect("/")  # or use render_template to return a confirmation page

def send_email(to_email, subject, body):
    from_email = "your_email@example.com"
    password = "your_app_password"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_email, password)
        smtp.send_message(msg)

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
