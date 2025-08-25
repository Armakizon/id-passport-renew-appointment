import csv
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

def APIcall(token, csv_file_path="appointment_site/Branch_id.csv"):
    govisit_url = "https://govisit.gov.il/API/appointment/api/appointmentScheduling/getDates?authorityId=262"
    your_server_url = "https://bookgov.onrender.com/add"
    reset_url = "https://bookgov.onrender.com/reset"

    headers = {
        "X-GoVisit-Token": token,
        "Content-Type": "application/json"
    }

    post_headers = {
        "Content-Type": "application/json"
    }

    now = datetime.now()
    current_year = now.year
    current_month = now.month
    phone_number = os.getenv("PHONE_NUMBER")
    id_number = os.getenv("ID_NUMBER")
    reset_token = os.getenv("PASSWORD")  # get password from .env

    # --- Reset the database first ---
    if reset_token:
        try:
            requests.post(reset_url, params={"token": reset_token})
        except requests.RequestException:
            pass

    payload_template = {
        "$type": 2,
        "year": current_year,
        "month": current_month,
        "unitId": None,
        "appointmentTypeIds": [343],
        "customer": {
            "personalId": id_number,
            "customerIdTypeId": 1,
            "additionalParameters": {
                "TelNumber1": phone_number
            }
        },
        "appointmentLeadTime": 0,
        "maxAvailableMonth": 6
    }

    # --- Loop through branch IDs and add data ---
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row or not row[0].isdigit():
                continue

            unit_id = int(row[0])
            payload = payload_template.copy()
            payload["unitId"] = unit_id

            try:
                response = requests.post(govisit_url, headers=headers, json=payload)
                data = response.json()

                if response.status_code != 200 or "data" not in data or not data["data"]:
                    continue

                available_dates = data["data"].get("availableDates", [])
                if not available_dates:
                    continue

                for entry in available_dates:
                    date_str = entry["date"].split("T")[0]

                    post_payload = {
                        "branch_id": unit_id,
                        "date": date_str
                    }

                    requests.post(your_server_url, headers=post_headers, json=post_payload)

            except (json.JSONDecodeError, KeyError):
                pass
            except requests.RequestException:
                pass
