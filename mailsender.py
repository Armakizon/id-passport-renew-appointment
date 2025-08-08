import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

PASSWORD = os.getenv("PASSWORD")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(to_email, subject, body_html, body_text=None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    if not body_text:
        body_text = "You have new appointment updates."

    part1 = MIMEText(body_text, "plain")
    part2 = MIMEText(body_html, "html")

    msg.attach(part1)
    msg.attach(part2)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def fetch_subscriptions():
    url = f"https://armakizon.pythonanywhere.com/subscribe"
    params = {"password": PASSWORD}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()["subscriptions"]

def fetch_filtered_entries(branch_ids, fromdate, todate):
    url = f"https://govpoitment.onrender.com/filter_entries"
    params = []
    for branch_id in branch_ids:
        params.append(("branchId", str(branch_id)))
    if fromdate:
        params.append(("startDate", fromdate))
    if todate:
        params.append(("endDate", todate))

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def format_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return date_str  # fallback to original if parse fails

def main():
    subscriptions = fetch_subscriptions()

    for sub in subscriptions:
        email = sub["email"]
        locations = sub.get("locations", [])
        fromdate = sub.get("fromdate")
        todate = sub.get("todate")

        if not locations:
            continue

        entries = fetch_filtered_entries(locations, fromdate, todate)
        if entries:
            rows = ""
            for e in entries:
                formatted_date = format_date(e['date'])
                # Branch Name first column, Date second column
                rows += f"<tr><td>{e['branch_name']}</td><td style='text-align:right'>{formatted_date}</td></tr>"

            unsubscribe_url = f"https://armakizon.pythonanywhere.com/unsubscribe?email={email}"

            body_html = f"""
            <html>
            <body>
                <p>Found {len(entries)} new entries for your subscribed locations:</p>
                <div style="max-width: 600px; margin: auto;">
                  <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
                      <thead>
                          <tr>
                              <th>Branch Name</th>
                              <th style="text-align:right">Date</th>
                          </tr>
                      </thead>
                      <tbody>
                          {rows}
                      </tbody>
                  </table>
                </div>
                <p>If you wish to unsubscribe from these emails, click <a href="{unsubscribe_url}">here</a>.</p>
            </body>
            </html>
            """

            body_text = f"Found {len(entries)} new entries for your subscribed locations.\n" + \
                        "\n".join([f"{e['branch_name']} : {format_date(e['date'])}" for e in entries]) + \
                        f"\n\nTo unsubscribe, visit: {unsubscribe_url}"

            print(f"Sending email to {email} with {len(entries)} entries...")
            send_email(email, "Appointment Updates", body_html, body_text)
        else:
            print(f"No entries for {email}")

if __name__ == "__main__":
    main()
