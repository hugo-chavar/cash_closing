import os
import json
import csv

from date_tests import get_german_date

# Path to the folder containing JSON files
folder_path = 'closings/submitted'
# folder_path = 'closings6'
csv_file_path = 'reports/report9.csv'
# List to hold data for CSV
data = []

# Read and process each JSON file
for file_name in sorted(os.listdir(folder_path)):
    if file_name.endswith('.json'):
        with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
            json_data = json.load(file)

            # Extract necessary fields
            full_amount = json_data['cash_statement']['payment']['full_amount']
            cash_amount = next((pt['amount'] for pt in json_data['cash_statement']['payment']['payment_types'] if pt['type'] == 'Bar'), 0)
            non_cash_amount = next((pt['amount'] for pt in json_data['cash_statement']['payment']['payment_types'] if pt['type'] == 'Unbar'), 0)

            vat_data_1 = next((item for item in json_data['cash_statement']['business_cases'][0]['amounts_per_vat_id'] if item['vat_definition_export_id'] == 1), {})
            vat_data_2 = next((item for item in json_data['cash_statement']['business_cases'][0]['amounts_per_vat_id'] if item['vat_definition_export_id'] == 2), {})

            incl_vat_1 = vat_data_1.get('incl_vat', 0)
            excl_vat_1 = vat_data_1.get('excl_vat', 0)
            vat_1 = vat_data_1.get('vat', 0)

            incl_vat_2 = vat_data_2.get('incl_vat', 0)
            excl_vat_2 = vat_data_2.get('excl_vat', 0)
            vat_2 = vat_data_2.get('vat', 0)
            time_creation = get_german_date(json_data['head']['export_creation_date'])

            # Append data to the list
            data.append([
                full_amount, incl_vat_1, excl_vat_1, vat_1,
                incl_vat_2, excl_vat_2, vat_2, cash_amount, non_cash_amount, time_creation
            ])

# Write data to CSV file

with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write header
    writer.writerow([
        'full_amount', 'incl_vat_1', 'excl_vat_1', 'vat_1',
        'incl_vat_2', 'excl_vat_2', 'vat_2', 'cash', 'non_cash', 'creation_date'
    ])
    # Write data
    writer.writerows(data)

print(f'Data has been written to {csv_file_path}')
