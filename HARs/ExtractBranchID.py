import csv

def split_summary_text_clean(input_csv, output_csv):
    with open(input_csv, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    new_rows = []
    for row in rows:
        summary = row['Summary Text']
        first_dot = summary.find('.')
        if first_dot == -1:
            col1 = summary.strip()
            col2 = ''
        else:
            second_dot = summary.find('.', first_dot + 1)
            if second_dot == -1:
                col1 = summary[:first_dot].strip()
                col2 = summary[first_dot+1:].strip()
            else:
                col1 = summary[:first_dot].strip()
                # Take text between first and second period
                part = summary[first_dot+1:second_dot].strip()
                # Remove trailing phrase like "התור הפנוי הקרוב:" if present
                trailing_phrases = ['התור הפנוי הקרוב:', 'תור אחרון בתאריך זה']  # add more if needed
                for phrase in trailing_phrases:
                    if part.endswith(phrase):
                        part = part[:-len(phrase)].strip()
                col2 = part

        new_rows.append({
            'Branch ID': row['Branch ID'],
            'Part 1': col1,
            'Part 2': col2
        })

    with open(output_csv, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = ['Branch ID', 'Part 1', 'Part 2']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_rows)

    print(f"✅ Processed {len(new_rows)} rows into {output_csv}")

# Usage
split_summary_text_clean("branch_summaries.csv", "branch_summaries_split_clean.csv")
