import json
import os
from date_tests import truncate_timestamp_to_date, get_formatted_shortdate


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

            print(f"{file_name}: {get_formatted_shortdate(cdate)} first {first_tx:04} last {last_tx:04}")

            if first_tx > last_tx_number + 1:
                ok = False
                print(f"ERROR: first {first_tx:04} last {last_tx_number:04}")

            last_tx_number = last_tx
if ok:
    print('Todo OK')
else:
    print('Hay problemas')




