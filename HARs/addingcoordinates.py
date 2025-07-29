import json
import csv
import re

def normalize_name(name):
    # Remove the word לשכה and extra spaces, lowercase
    name = re.sub(r'לשכה', '', name)
    name = name.strip()
    name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
    return name.lower()

def add_coordinates_to_csv(csv_path, json_path, output_path):
    # Load JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Build a dict for quick lookup: normalized Hebrew name -> coordinates
    name_to_coords = {}
    for entry in json_data:
        heb_name = entry.get('name', {}).get('he', '')
        norm_name = normalize_name(heb_name)
        coords = entry.get('coordinates', {})
        if 'latitude' in coords and 'longitude' in coords:
            name_to_coords[norm_name] = (coords['latitude'], coords['longitude'])

    # Read CSV and write updated CSV with latitude and longitude
    with open(csv_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['latitude', 'longitude']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            # Choose which column holds the branch name
            # For example, if 'Summary Text' or 'Part 1' - adjust accordingly
            branch_name = row.get('Summary Text') or row.get('Part 1') or ''

            norm_branch_name = normalize_name(branch_name)

            lat, lon = '', ''
            # Try to find a match in the JSON names
            # The exact match or maybe partial match - here exact normalized match
            if norm_branch_name in name_to_coords:
                lat, lon = name_to_coords[norm_branch_name]
            else:
                # Optional: Try partial matching by checking if any JSON name contains branch_name or vice versa
                for name_key in name_to_coords:
                    if norm_branch_name in name_key or name_key in norm_branch_name:
                        lat, lon = name_to_coords[name_key]
                        break

            row['latitude'] = lat
            row['longitude'] = lon
            writer.writerow(row)

    print(f"✅ Saved updated CSV with coordinates to: {output_path}")

# Usage example:
add_coordinates_to_csv('branch_id.csv', 'response.json', 'branch_id_with_coords.csv')
