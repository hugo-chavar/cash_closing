import json
import os
from product_provider import ProductProvider
from date_tests import get_format_shortdate, get_german_date
from cash_closing_config import Config
from constants import LAST_CASH_POINT_CLOSING_EXPORT_ID, BASE_TIMESTAMP, LAST_RECEIPT_NUMBER, LAST_CASH_CLOSING_TO_PROCESS

# # 20240711 - 1720648800
# # Next START_TIME: 20240712 - 1720735200
# START_TIME = 1720735200
# END_TIME = START_TIME + 86400

# Output file name
# output_json_file = f"merged_json/merged_file_filter_{get_format_shortdate(get_german_date(START_TIME))}.json"

# Input folder containing JSON files
input_folder = "json_files"

def split_json_files_by_bussiness_date(input_folder, config):
    merged_data = []
    total_count = 0

    # List all JSON files in the input folder
    file_list = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    
    for file_name in file_list:
        file_path = os.path.join(input_folder, file_name)
        print(f"Processing {file_name}")
        with open(file_path, mode='r', encoding='utf8') as f:
            data = json.load(f)
            merged_data.extend(data["data"])

            total_count += len(data["data"]) #data["count"]
    
    print(f"Total count: {total_count}")
    # Sort the merged data by the "number" field
    merged_data.sort(key=lambda x: x["number"])

    # Check for specific conditions
    p_tx_n = 0
    pp = ProductProvider()
    for transaction in merged_data:
        if p_tx_n != (transaction['number'] - 1):
            print(f"{p_tx_n} falta el siguiente ************ ERROR ERROR\n\n")
        p_tx_n = transaction['number']
        if "schema" in transaction and "standard_v1" in transaction["schema"]:
            standard_v1 = transaction["schema"]["standard_v1"]
            is_ok = True
            if "order" in standard_v1 and "line_items" in standard_v1["order"]:
                for line_item in standard_v1["order"]["line_items"]:
                    if line_item["text"].startswith("null"):

                        try:
                            product = line_item["text"].split(' - ')[1]
                            # print("Result:", line_item["text"])

                            try:
                                # pp.get_by_title(product)
                                # print("Replaced by:", str(pp.get_by_title(product)))
                                line_item["text"] = str(pp.get_by_title(product))
                                # pass
                            except KeyError:
                                print(f"{transaction['number']} Result:", product, "   ========> NOT FOUND")

                            
                        except AttributeError as e:
                            print("AttributeError: The variable 'x' is not a string-like object or is None.")
                            print(e)
                        except IndexError as e:
                            print("IndexError: The result of 'x.split()' does not have enough elements.")
                            print(e)
                        except TypeError as e:
                            print("TypeError: The variable 'x' has an incorrect type or cannot be split.")
                            print(e)


    
    filtered_data = [transaction for transaction in merged_data if transaction["time_start"] >= config.timestamp_low() and transaction["time_start"] <  config.timestamp_high() ]

    filtered_count = len(filtered_data)
    print(f"filtered_count: {filtered_count}. From {config.timestamp_low()} to {config.timestamp_high()}")
    print(f"Date {config.bussiness_date()}")

    while config.last_cc_export_id < LAST_CASH_CLOSING_TO_PROCESS:
        if filtered_count > 0:
            merged_dict = {
                "data": filtered_data,
                "count": filtered_count
            }
            
            # Write the merged dictionary to the output file
            with open(config.transactions_filename(), mode='w', encoding='utf8') as f:
                json.dump(merged_dict, f, indent=4)

            print(f"Saved: {config.transactions_filename()}")

        config.next()
        filtered_data = [transaction for transaction in merged_data if transaction["time_start"] >= config.timestamp_low() and transaction["time_start"] <  config.timestamp_high() ]

        filtered_count = len(filtered_data)
        print(f"filtered_count: {filtered_count}. From {config.timestamp_low()} to {config.timestamp_high()}")
        print(f"Date {config.bussiness_date()}")


def merge_json_files(input_folder, config):
    merged_data = []
    total_count = 0

    # List all JSON files in the input folder
    file_list = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    
    for file_name in file_list:
        file_path = os.path.join(input_folder, file_name)
        print(f"Processing {file_name}")
        with open(file_path, mode='r', encoding='utf8') as f:
            data = json.load(f)
            merged_data.extend(data["data"])

            total_count += len(data["data"]) #data["count"]
    
    print(f"Total count: {total_count}")
    # Sort the merged data by the "number" field
    merged_data.sort(key=lambda x: x["number"])

    # Check for specific conditions
    p_tx_n = 0
    pp = ProductProvider()
    for transaction in merged_data:
        if p_tx_n != (transaction['number'] - 1):
            print(f"{p_tx_n} falta el siguiente ************ ERROR ERROR\n\n")
        p_tx_n = transaction['number']
        if "schema" in transaction and "standard_v1" in transaction["schema"]:
            standard_v1 = transaction["schema"]["standard_v1"]
            is_ok = True
            if "order" in standard_v1 and "line_items" in standard_v1["order"]:
                for line_item in standard_v1["order"]["line_items"]:
                    if line_item["text"].startswith("null"):

                        try:
                            product = line_item["text"].split(' - ')[1]
                            # print("Result:", line_item["text"])

                            try:
                                # pp.get_by_title(product)
                                # print("Replaced by:", str(pp.get_by_title(product)))
                                line_item["text"] = str(pp.get_by_title(product))
                                # pass
                            except KeyError:
                                print(f"{transaction['number']} Result:", product, "   ========> NOT FOUND")

                            
                        except AttributeError as e:
                            print("AttributeError: The variable 'x' is not a string-like object or is None.")
                            print(e)
                        except IndexError as e:
                            print("IndexError: The result of 'x.split()' does not have enough elements.")
                            print(e)
                        except TypeError as e:
                            print("TypeError: The variable 'x' has an incorrect type or cannot be split.")
                            print(e)

                        # is_ok = False
                        # print(line_item["text"])

                        # print(f"Transaction number with 'null' line item: {transaction['number']}")
                        # break
            # if is_ok:
            #     print(f"{transaction['number']} OK")
            # else:
            #     print(f"{transaction['number']} ***** has null")

    # Filter transactions based on time_start value 1719317830
    filtered_data = [transaction for transaction in merged_data if transaction["time_start"] >= config.timestamp_low() and transaction["time_start"] <  config.timestamp_high() ]

    # Update the total count after filtering
    filtered_count = len(filtered_data)
    # Create the merged dictionary
    merged_dict = {
        "data": filtered_data,
        "count": filtered_count
    }
    
    # Write the merged dictionary to the output file
    with open(config.transactions_filename(), mode='w', encoding='utf8') as f:
        json.dump(merged_dict, f, indent=4)

    print(f"Saved: {config.transactions_filename()}")

# # Merge the JSON files
# config = Config(BASE_TIMESTAMP, LAST_CASH_POINT_CLOSING_EXPORT_ID, LAST_RECEIPT_NUMBER)
# merge_json_files(input_folder, config)

# split_json_files_by_bussiness_date
# config = Config(BASE_TIMESTAMP)
config = Config(BASE_TIMESTAMP, LAST_CASH_POINT_CLOSING_EXPORT_ID, LAST_RECEIPT_NUMBER)
split_json_files_by_bussiness_date(input_folder, config)

print(f"Next START_TIME: {config.timestamp_high()}")
