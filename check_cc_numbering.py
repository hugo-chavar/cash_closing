import json
import os
from date_tests import truncate_timestamp_to_date, get_formatted_shortdate
from cash_closing_config import Config
from models import FiskalyClient

# Path to the folder containing JSON files
folder_path = 'closings/submitted'
# folder_path = 'closings6'


# last_tx_number = 0
last_tx_number = 98
ok = True



file_list = sorted(os.listdir(folder_path))

# print(str(file_list))
# Read and process each JSON file
for file_name in file_list:
    if file_name.endswith('.json'):
        with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as file:
            json_data = json.load(file)

            transactions = json_data['transactions']
            first_tx = transactions[0]["head"]["number"]
            last_tx = transactions[-1]["head"]["number"]
            cdate = truncate_timestamp_to_date(transactions[-1]["head"]["timestamp_start"])

            print(f"{file_name}: {get_formatted_shortdate(cdate)} first {first_tx:06} last {last_tx:06}")

            if first_tx > last_tx_number + 1:
                ok = False
                print(f"ERROR: first {first_tx:06} last {last_tx_number:06}")

            last_tx_number = last_tx
if ok:
    print('Todo OK')
else:
    print('Hay problemas')


client = FiskalyClient.objects.get(id=1)

config = Config(client)

last_cc_file_name=file_list[-1]
print(f"Last: {last_cc_file_name}")

with open(os.path.join(folder_path, last_cc_file_name), 'r', encoding='utf-8') as file:
    json_data = json.load(file)

    last_cc_export_id = int(json_data["cash_point_closing_export_id"])

    transactions = json_data['transactions']
    # first_tx = transactions[0]["head"]["number"]
    last_receipt_number = int(transactions[-1]["head"]["number"])
    # cdate = truncate_timestamp_to_date(transactions[-1]["head"]["timestamp_start"])

    print(f"{file_name}: {get_formatted_shortdate(cdate)} first {first_tx:06} last {last_tx:06}")

folder_path = 'merged6'
file_list = sorted(os.listdir(folder_path))
last_merged_file = file_list[-1]

with open(os.path.join(folder_path, last_merged_file), encoding='utf-8', mode='r') as mf:
    json_data = json.load(mf)
    last_processed_tx_number = int(json_data["data"][-1]["number"])

if config.last_cc_export_id == last_cc_export_id:
    print("last_cc_export_id OK.")

if config.last_receipt_number == last_receipt_number:
    print("last_receipt_number OK.")

if config.last_processed_tx_number == last_processed_tx_number:
    print("last_processed_tx_number OK.")

