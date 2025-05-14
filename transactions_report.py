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
        try:
            with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
                cash_closing = json.load(file)
                cc_id = cash_closing['cash_point_closing_export_id']
                if cc_id < 332:
                    continue
                bussiness_date = str(cash_closing['head']['business_date'])
                
                # Loop through all transactions
                for tx in cash_closing.get('transactions', []):
                    note = ''
                    head = tx.get('head', {})
                    creation_time = str(get_german_date(head['timestamp_end']))[11:19]
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
                    
                    # Determine payment type (Bar or Unbar)
                    tx_payment_type = "Unbar"
                    tx_payment_type_english = "CARD"
                    tx_payment_amount = 0.0
                    for payment in payments:
                        tx_payment_amount += payment['amount']
                        if payment['type'] == "Bar":
                            tx_payment_type = "Bar"
                            tx_payment_type_english = "CASH"
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
                    tx_lines = tx_data.get('lines', [])
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
                                    cash_tx[vat_type] += incl_vat_dec
                                else:
                                    # print(f"Adding {vat_type} {incl_vat}")
                                    incl_vat_dec = Decimal(str(incl_vat))
                                    non_cash_tx[vat_type] += incl_vat_dec
                    
                    if payment['type'] == "Bar":
                        cash_tx_total = float(cash_tx['vat_19'] + cash_tx['vat_7'])
                        if abs(tx_payment_amount - cash_tx_total) > 0.01:
                            note = f"Tx problem {tx['head']['number']} payment_amout {tx_payment_amount} VAT cash total informed to TSE {cash_tx_total}"
                            print(note)
                    else:
                        non_cash_tx_total = float(non_cash_tx['vat_19'] + non_cash_tx['vat_7'])
                        if abs(tx_payment_amount - non_cash_tx_total) > 0.01:
                            note = f"Tx problem {tx['head']['number']} payment_amout {tx_payment_amount} VAT non cash total informed to TSE {non_cash_tx_total}"
                            print(note)
                        
                    data.append([
                        cc_id,
                        bussiness_date,
                        creation_time,
                        head.get('number'),
                        head.get('transaction_export_id'),
                        head.get('tx_id'),
                        head.get('type'),
                        tx_data.get('full_amount_incl_vat'),
                        tx_payment_type_english,
                        bar_total,
                        unbar_total,
                        cash_tx['vat_7'],
                        cash_tx['vat_19'],
                        non_cash_tx['vat_7'],
                        non_cash_tx['vat_19'],
                        note
                    ])
        except Exception as e:
            print(f"Error in file {file_name}.\n{type(e).__name__}: {e}")
            exit(1)
# Write data to CSV file
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    # Write header with separate columns for Bar and Unbar payments
    writer.writerow([
        'cash_closing_id',
        'business_date',
        'creation_time',
        'tx_number',
        'tx_export_id',
        'tx_id',
        'tx_type',
        'full_amount_incl_vat',
        'payment_type',
        'cash_amount',
        'non_cash_amount',
        'cash_7',
        'cash_19',
        'non_cash_7',
        'non_cash_19',
        'note'
    ])
    # Write data rows
    writer.writerows(data)

print(f'Data has been written to {csv_file_path}')
