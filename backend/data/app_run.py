import json
import csv

# Load data from input JSON file
input_filename = 'data/processed_data.json'
with open(input_filename, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Prepare data for CSV
csv_data = []

for entry in data:
    name = entry['name']
    projects = entry['projects']
    hash_dict = entry['hash']

    # If projects are empty, skip this person
    if not projects:
        continue
    
    # Process each project and its corresponding hash
    for i, project in enumerate(projects, start=1):
        cred_id = hash_dict.get(f'hash_{i}')
        if cred_id:  # Ensure there's a corresponding hash
            csv_data.append([name, project, cred_id])

# Write to CSV file
output_filename = 'data/processed_data.csv'
with open(output_filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # Write header
    writer.writerow(['name', 'project_id', 'cred_id'])
    # Write rows
    writer.writerows(csv_data)

print(f"Processed data saved to {output_filename}")
