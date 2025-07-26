import re
import csv
from tabulate import tabulate

def extract_branches_and_hebrew(file_path, output_csv):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all branch ids
    pattern = re.compile(r'id="branch_(\d+)"')
    matches = list(pattern.finditer(content))

    results = []

    for match in matches:
        branch_id = match.group(1)
        start_pos = match.end()

        # Look for the next Hebrew text
        hebrew_pattern = re.compile(r'[\u0590-\u05FF]+(?:[\s\u0590-\u05FF]*)')
        hebrew_match = hebrew_pattern.search(content, pos=start_pos)

        if hebrew_match:
            hebrew_text = hebrew_match.group().strip()
            results.append((branch_id, hebrew_text))

    # Print to console
    if results:
        print(tabulate(results, headers=["Branch ID", "Hebrew Text"], tablefmt="grid"))
    else:
        print("No matches found.")

    # Save to CSV
    with open(output_csv, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Branch ID', 'Hebrew Text'])
        writer.writerows(results)

    print(f"\nExtracted {len(results)} entries to {output_csv}")

# Run the function on your file
extract_branches_and_hebrew("all branch id.txt", "output.csv")
