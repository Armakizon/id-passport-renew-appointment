import pandas as pd
import json
import re

# === Load CSV ===
csv_file = "Branch_id.csv"
df_csv = pd.read_csv(csv_file)

# === Clean & Normalize Hebrew Names ===
def clean_hebrew(he_name):
    # Remove "לשכת" and strip spaces
    return re.sub(r"^לשכת\s*", "", he_name).strip()

df_csv["name_he_clean"] = df_csv["branch_name"].apply(clean_hebrew)

# === Load JSON ===
with open("response.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)

# Build a lookup dictionary from JSON based on Hebrew name
coord_lookup = {
    entry["name"]["he"].strip(): (
        entry["coordinates"]["latitude"],
        entry["coordinates"]["longitude"]
    )
    for entry in json_data
}

# Add latitude and longitude to DataFrame
df_csv["latitude"] = df_csv["name_he_clean"].apply(lambda name: coord_lookup.get(name, (None, None))[0])
df_csv["longitude"] = df_csv["name_he_clean"].apply(lambda name: coord_lookup.get(name, (None, None))[1])

# Drop helper column (optional)
df_csv.drop(columns=["name_he_clean"], inplace=True)

# === Save new file ===
output_file = "Branch_id_with_coords.csv"
df_csv.to_csv(output_file, index=False)

print(f"✅ Done. File saved: {output_file}")
