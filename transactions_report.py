import os
import json
import csv
from decimal import Decimal
from date_tests import get_german_date

# Path to the folder containing JSON files
folder_path = 'closings/submitted'
csv_file_path = 'reports/transactions.csv'
data = []

# Process each JSON file
for file_name in sorted(os.listdir(folder_path)):
    if file_name.endswith('.json'):
        with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
            cash_closing = json.load(file)
            cc_id = cash_closing['cash_point_closing_export_id']
            creation_date = get_german_date(cash_closing['head']['export_creation_date'])
            # Loop through all transactions
            for tx in cash_closing.get('transactions', []):
                head = tx.get('head', {})
                tx_data = tx.get('data', {})
                # Split payment types into two columns "Bar" and "Unbar"
                payments = tx_data.get('payment_types', [])
                bar_total = 0.0
                unbar_total = 0.0
                for p in payments:
                    if p.get('type') == "Bar":
                        bar_total += p.get('amount', 0)
                    elif p.get('type') == "Unbar":
                        unbar_total += p.get('amount', 0)
                
                data.append([
                    cc_id,
                    creation_date,
                    head.get('number'),
                    head.get('transaction_export_id'),
                    head.get('tx_id'),
                    head.get('type'),
                    tx_data.get('full_amount_incl_vat'),
                    bar_total,
                    unbar_total
                ])

# Write data to CSV file
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write header with separate columns for Bar and Unbar payments
    writer.writerow([
        'cash_closing_export_id',
        'creation_date',
        'transaction_number',
        'transaction_export_id',
        'tx_id',
        'transaction_type',
        'full_amount_incl_vat',
        'Bar',
        'Unbar'
    ])
    # Write data rows
    writer.writerows(data)

print(f'Data has been written to {csv_file_path}')
