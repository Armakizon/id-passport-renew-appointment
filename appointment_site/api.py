from flask import Blueprint, request, redirect, jsonify
import os
import smtplib
from email.mime.text import MIMEText

api = Blueprint('api', __name__)
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

@api.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form["email"]
    
    subject = "Your Appointment Subscription"
    body = f"Thank you! You've been subscribed for appointment updates."
    send_email(email, subject, body)

    return redirect("/")  # or use render_template to return a confirmation page

def send_email(to_email, subject, body):
    from_email = "govappointmentil@gmail.com"
    password = "shaked150150"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_email, password)
        smtp.send_message(msg)
