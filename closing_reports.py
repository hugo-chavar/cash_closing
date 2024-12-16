import os
import json
import csv

from date_tests import get_german_date

# Path to the folder containing JSON files
folder_path = 'closings/submitted'
# folder_path = 'closings6'
csv_file_path = 'reports/report10.csv'
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

            # Initialize totals
            cash_totals = {
                'vat_19': 0,
                'vat_7': 0,
            }

            non_cash_totals = {
                'vat_19': 0,
                'vat_7': 0,
            }
            
            for item in json_data['transactions']:
                if item['head']['type'] != "Beleg":
                    continue
                # print(f"Processing {item['head']['number']}")
                payments = item['data']['payment_types']
                lines = item['data']['lines']
                
                # Determine payment type (Bar or Unbar)
                payment_type = "Unbar"  # Default to Unbar
                for payment in payments:
                    if payment['type'] == "Bar":
                        payment_type = "Bar"
                        break

                # Iterate over lines and accumulate incl_vat based on VAT definition and payment type
                for line in lines:
                    for vat_info in line['business_case']['amounts_per_vat_id']:
                        incl_vat = vat_info['incl_vat']
                        vat_type = None

                        # Determine VAT type
                        if vat_info['vat_definition_export_id'] == 1:
                            vat_type = 'vat_19'
                        elif vat_info['vat_definition_export_id'] == 2:
                            vat_type = 'vat_7'

                        # Accumulate incl_vat based on payment type and VAT type
                        if vat_type:
                            if payment_type == "Bar":
                                cash_totals[vat_type] += incl_vat
                            else:
                                # print(f"Adding {vat_type} {incl_vat}")
                                non_cash_totals[vat_type] += incl_vat
            # Append data to the list
            data.append([
                full_amount, incl_vat_1, excl_vat_1, vat_1,
                incl_vat_2, excl_vat_2, vat_2, cash_amount, cash_totals['vat_19'], cash_totals['vat_7'], non_cash_amount, non_cash_totals['vat_19'], non_cash_totals['vat_7'], time_creation
            ])

# Write data to CSV file

with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write header
    writer.writerow([
        'full_amount', 'incl_vat_1', 'excl_vat_1', 'vat_1',
        'incl_vat_2', 'excl_vat_2', 'vat_2', 'total_cash', 'cash_19', 'cash_7', 'total_non_cash', 'non_cash_19', 'non_cash_7', 'creation_date'
    ])
    # Write data
    writer.writerows(data)

print(f'Data has been written to {csv_file_path}')
