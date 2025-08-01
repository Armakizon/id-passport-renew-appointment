import csv

def load_branch_map(csv_path="Branch_id.csv"):
    BRANCH_MAP = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["latitude"] and row["longitude"]:
                BRANCH_MAP[int(row["branch_id"])] = {
                    "name": row["branch_name"],
                    "address": row["Address"],
                    "lat": float(row["latitude"]),
                    "lon": float(row["longitude"]),
                }
    return BRANCH_MAP
