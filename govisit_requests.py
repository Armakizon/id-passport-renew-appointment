import csv
import requests
import json

def APIcall(token, csv_file_path="Branch_id.csv"):
    govisit_url = "https://govisit.gov.il/API/appointment/api/appointmentScheduling/getDates?authorityId=262"
    your_server_url = "https://govpoitment.onrender.com/add"

    headers = {
        "X-GoVisit-Token": token,
        "Content-Type": "application/json"
    }

    post_headers = {
        "Content-Type": "application/json"
    }

    payload_template = {
        "$type": 2,
        "year": 2025,
        "month": 7,
        "unitId": None,
        "appointmentTypeIds": [343],
        "customer": {
            "personalId": "207081530",
            "customerIdTypeId": 1,
            "additionalParameters": {
                "TelNumber1": "0533319221"
            }
        },
        "appointmentLeadTime": 0,
        "maxAvailableMonth": 6
    }

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
                    print(f"unitId: {unit_id} ➜ No data or bad response")
                    continue

                available_dates = data["data"].get("availableDates", [])
                if not available_dates:
                    print(f"unitId: {unit_id} ➜ No available dates")
                    continue

                # Extract and process each date
                print(f"unitId: {unit_id} ➜ Dates:")
                for entry in available_dates:
                    date_str = entry["date"].split("T")[0]
                    print(f"  - {date_str}")

                    # Send to your server
                    post_payload = {
                        "branch_id": unit_id,
                        "date": date_str
                    }

                    post_resp = requests.post(your_server_url, headers=post_headers, json=post_payload)
                    if post_resp.status_code == 200:
                        print("    ✔ Sent to server")
                    else:
                        print(f"    ⚠ Failed to send: {post_resp.status_code} — {post_resp.text}")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"unitId: {unit_id} ➜ Failed to parse response: {e}")
            except requests.RequestException as e:
                print(f"unitId: {unit_id} ➜ Request failed: {e}")