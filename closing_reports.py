import os
import json
import csv

from decimal import Decimal
from date_tests import get_german_date

# Path to the folder containing JSON files
folder_path = 'closings/submitted'
# folder_path = 'closings8/t'
# folder_path = 'closings6'
csv_file_path = 'reports/report18.csv'
# List to hold data for CSV
data = []

# Read and process each JSON file
def extract_cash_closing_totals(cash_closing):
    # initialize
    print(f"CC: {cash_closing['cash_point_closing_export_id']}")
    full_amount = cash_amount = non_cash_amount = Decimal("0")
    incl_vat_1 = excl_vat_1 = vat_1 = Decimal("0")
    incl_vat_2 = excl_vat_2 = vat_2 = Decimal("0")
    cash_totals = {
                'vat_19': Decimal("0"),
                'vat_7': Decimal("0"),
            }

    non_cash_totals = {
                'vat_19': Decimal("0"),
                'vat_7': Decimal("0"),
            }
    time_creation = get_german_date(cash_closing['head']['export_creation_date'])
    
    state = cash_closing.get('state', 'OK')
    
    if state != "DELETED":
        full_amount = cash_closing['cash_statement']['payment']['full_amount']
        cash_amount = next((pt['amount'] for pt in cash_closing['cash_statement']['payment']['payment_types'] if pt['type'] == 'Bar'), 0)
        non_cash_amount = next((pt['amount'] for pt in cash_closing['cash_statement']['payment']['payment_types'] if pt['type'] == 'Unbar'), 0)

        vat_data_1 = next((item for item in cash_closing['cash_statement']['business_cases'][0]['amounts_per_vat_id'] if item['vat_definition_export_id'] == 1), {})
        vat_data_2 = next((item for item in cash_closing['cash_statement']['business_cases'][0]['amounts_per_vat_id'] if item['vat_definition_export_id'] == 2), {})

        incl_vat_1 = vat_data_1.get('incl_vat', 0)
        excl_vat_1 = vat_data_1.get('excl_vat', 0)
        vat_1 = vat_data_1.get('vat', 0)

        incl_vat_2 = vat_data_2.get('incl_vat', 0)
        excl_vat_2 = vat_data_2.get('excl_vat', 0)
        vat_2 = vat_data_2.get('vat', 0)
                
        for tx in cash_closing['transactions']:
            if tx['head']['type'] != "Beleg":
                continue
            # print(f"Processing {item['head']['number']}")
            
            # Processing only problematic tx
            # if tx['head']['number'] != 12423:
            #     continue
            
            tx_payments = tx['data']['payment_types']
            tx_lines = tx['data']['lines']
                    
            # Determine payment type (Bar or Unbar)
            tx_payment_type = "Unbar"  # Default to Unbar
            tx_payment_amount = 0.0
            for payment in tx_payments:
                tx_payment_amount += payment['amount']
                if payment['type'] == "Bar":
                    tx_payment_type = "Bar"
                    # break

            cash_tx = {
                'vat_19': Decimal("0"),
                'vat_7': Decimal("0"),
            }

            non_cash_tx = {
                'vat_19': Decimal("0"),
                'vat_7': Decimal("0"),
            }
            
            # Iterate over lines and accumulate incl_vat based on VAT definition and payment type
            for line in tx_lines:
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
                        if tx_payment_type == "Bar":
                            incl_vat_dec = Decimal(str(incl_vat))
                            cash_totals[vat_type] += incl_vat_dec
                            cash_tx[vat_type] += incl_vat_dec
                        else:
                            # print(f"Adding {vat_type} {incl_vat}")
                            incl_vat_dec = Decimal(str(incl_vat))
                            non_cash_totals[vat_type] += incl_vat_dec
                            non_cash_tx[vat_type] += incl_vat_dec
            
            if payment['type'] == "Bar":
                cash_tx_total = float(cash_tx['vat_19'] + cash_tx['vat_7'])
                if tx_payment_amount != cash_tx_total:
                    print(f"Tx problem {tx['head']['number']} payment_amout {tx_payment_amount} cash total {cash_tx_total}")
            else:
                non_cash_tx_total = float(non_cash_tx['vat_19'] + non_cash_tx['vat_7'])
                if tx_payment_amount != non_cash_tx_total:
                    print(f"Tx problem {tx['head']['number']} payment_amout {tx_payment_amount} cash total {non_cash_tx_total}")
 
    
    return full_amount,cash_amount,non_cash_amount,incl_vat_1,excl_vat_1,vat_1,incl_vat_2,excl_vat_2,vat_2,time_creation,cash_totals,non_cash_totals

for file_name in sorted(os.listdir(folder_path)):
    if file_name.endswith('.json'): # and "_122_" in file_name
        with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
            cash_closing = json.load(file)

            full_amount, cash_amount, non_cash_amount, incl_vat_1, excl_vat_1, vat_1, incl_vat_2, excl_vat_2, vat_2, time_creation, cash_totals, non_cash_totals = extract_cash_closing_totals(cash_closing)
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
