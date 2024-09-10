import json
from fiskaly_service import FiskalyService
from product_provider import ProductProvider
from transaction_fetcher import TransactionFetcher
from cash_closing_config import Config
from constants import LAST_CASH_CLOSING_TO_PROCESS
from models import FiskalyClient

# merge_json.py
def split_json_files_by_bussiness_date(iter, config):
    # step 0
    merged_data = []
    total_count = 0

    # step 1: get all new transactions
    for batch in iter:
        print("MERGING")
        merged_data.extend(batch["data"])
        total_count += len(batch["data"])
    
    print(f"Total count: {total_count}")
    # step 2: Sort the merged data by the "number" field
    merged_data.sort(key=lambda x: x["number"])

    # step 3: complete product data if missing
    p_tx_n = config.last_processed_tx_number
    pp = ProductProvider()
    for transaction in merged_data:
        if p_tx_n != (transaction['number'] - 1):
            print(f"{p_tx_n} => {(transaction['number'] - 1)} falta el siguiente ************ ERROR split\n\n")
            print(f"Set LAST_PROCESSED_TX_NUMBER to {(transaction['number'] - 1)} \n\n")

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

    # get last transaction to process
    last_transaction_to_process = merged_data[-1]["number"]
    print(f"last_transaction_to_process: {last_transaction_to_process}")
    # step 4: save file
    # Write the merged dictionary to the output file
    # with open("json_files/E8.json", mode='w', encoding='utf8') as f:
    #     json.dump(merged_data, f, indent=4)


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

    # save here the value of last_transaction_to_process


client = FiskalyClient.objects.get(id=1)
# last_tx_ok=LAST_PROCESSED_TX_NUMBER
fs = FiskalyService()
fs.credentials = client.get_credentials()
tf = TransactionFetcher(fs, client)
tf.update_last_tx_pending()



myiter  = iter(tf)
# config = Config(BASE_TIMESTAMP, LAST_CASH_POINT_CLOSING_EXPORT_ID, LAST_RECEIPT_NUMBER)
config = Config(client)
split_json_files_by_bussiness_date(myiter, config)
# print(str(next(myiter)))
# print(next(myiter))