import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import re

# ─── Load environment variables ───────────────────────────────────────────────
load_dotenv()
PASSWORD = os.getenv("PASSWORD")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ─── Jinja2 setup ─────────────────────────────────────────────
env = Environment(loader=FileSystemLoader("email_templates"))

def render_template(template_name, **kwargs):
    template = env.get_template(template_name)
    return template.render(**kwargs)

# ─── Mobile detection function ───────────────────────────────────────────────
def is_mobile_email(email):
    """
    Detect if the email is likely from a mobile device based on email patterns.
    This is a heuristic approach since we can't directly detect the device.
    """
    # Common mobile email patterns
    mobile_patterns = [
        r'@.*\.mobile',  # .mobile domains
        r'@.*\.mobi',    # .mobi domains
        r'@.*mobile',    # mobile in domain
        r'@.*\.app',     # .app domains
        r'@.*\.ios',     # iOS specific
        r'@.*\.android', # Android specific
    ]
    
    # Check if email matches any mobile pattern
    for pattern in mobile_patterns:
        if re.search(pattern, email.lower()):
            return True
    
    # Default to mobile for better mobile experience
    # You can change this to False if you want to default to desktop
    return True

# ─── Email sending function ───────────────────────────────────────────────
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

# ─── API functions ───────────────────────────────────────────────
def fetch_subscriptions():
    url = f"https://armakizon.pythonanywhere.com/subscribe"
    params = {"password": PASSWORD}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()["subscriptions"]

def fetch_filtered_entries(branch_ids, fromdate, todate):
    url = f"https://bookgov.onrender.com/filter_entries"
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

# ─── Date formatting ─────────────────────────────────────────────
def format_date(date_str):
    try:
        # Handle both YYYY-MM-DD and DD/MM/YYYY formats
        if "/" in date_str:
            # Already in DD/MM/YYYY format
            return date_str
        else:
            # Convert from YYYY-MM-DD to DD/MM/YYYY
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
    except Exception:
        return date_str

# ─── Main logic ───────────────────────────────────────────────
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
            # Ensure formatted_date is available for templates
            for e in entries:
                # Only format if not already formatted (backend now returns DD/MM/YYYY)
                if not e.get("formatted_date"):
                    e["formatted_date"] = format_date(e["date"])
            
            # Reorganize entries: first show earliest for each branch, then sort remaining by date
            reorganized_entries = []
            branch_earliest = {}
            
            # First pass: find the earliest appointment for each branch
            for entry in entries:
                branch_id = entry['branch_id']
                if branch_id not in branch_earliest:
                    branch_earliest[branch_id] = entry
                else:
                    # Compare dates to find the earliest for this branch
                    current_earliest = branch_earliest[branch_id]
                    if entry['date'] < current_earliest['date']:
                        branch_earliest[branch_id] = entry
            
            # Add earliest appointments for each branch first
            earliest_entries = list(branch_earliest.values())
            earliest_entries.sort(key=lambda x: x['date'])  # Sort by date
            reorganized_entries.extend(earliest_entries)
            
            # Add remaining appointments, sorted by date
            remaining_entries = []
            for entry in entries:
                if entry not in earliest_entries:
                    remaining_entries.append(entry)
            
            remaining_entries.sort(key=lambda x: x['date'])  # Sort by date
            reorganized_entries.extend(remaining_entries)
            
            # Replace the original entries with reorganized ones
            entries = reorganized_entries

            unsubscribe_url = f"https://armakizon.pythonanywhere.com/unsubscribe?email={email}"

            # Choose template based on mobile detection
            is_mobile = is_mobile_email(email)
            
            if is_mobile:
                html_template = "appointment_update_mobile.html"
                text_template = "appointment_update_mobile.txt"
                print(f"Using mobile template for {email}")
            else:
                html_template = "appointment_update.html"
                text_template = "appointment_update.txt"
                print(f"Using desktop template for {email}")

            body_html = render_template(
                html_template,
                count=len(entries),
                entries=entries,
                unsubscribe_url=unsubscribe_url
            )

            body_text = render_template(
                text_template,
                count=len(entries),
                entries=entries,
                unsubscribe_url=unsubscribe_url
            )

            # Get the earliest date for the email subject
            earliest_date = None
            if entries:
                # Find the earliest date among all entries
                earliest_entry = min(entries, key=lambda e: e.get('date', ''))
                earliest_date = earliest_entry.get('date', '')
                
                # Convert DD/MM/YYYY to DD/MM for subject
                try:
                    if '/' in earliest_date:
                        day_month = '/'.join(earliest_date.split('/')[:2])  # Extract DD/MM
                    else:
                        # Fallback if date format is unexpected
                        day_month = earliest_date
                except:
                    day_month = earliest_date
            
            # Create dynamic subject with earliest date
            subject = f"תורים זמינים - {day_month}" if day_month else "תורים זמינים"
            
            print(f"Sending email to {email} with {len(entries)} entries, earliest date: {earliest_date}")
            send_email(email, subject, body_html, body_text)
        else:
            print(f"No entries for {email}")

if __name__ == "__main__":
    main()
