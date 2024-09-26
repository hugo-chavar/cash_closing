import cash_closing
import json
from cash_closing_config import Config
from constants import LAST_CASH_CLOSING_TO_PROCESS
from fiskaly_service import FiskalyService
from models import FiskalyClient
from product_provider import ProductProvider
from transaction_fetcher import TransactionFetcher
from transaction_fixer import TransactionFixer
from types import SimpleNamespace

def parse(d):
    x = SimpleNamespace()
    _ = [setattr(x, k,
                 parse(v) if isinstance(v, dict)
                 else [parse(e) for e in v] if isinstance(v, list)
                 else v) for k, v in d.items()]
    return x


def process_closing(config: Config, transactions):
   options = {
      "last_cash_point_closing_export_id": config.last_cc_export_id,
      "cash_register": config.cash_register,
      "last_receipt_number": config.last_receipt_number,
   }

   print(f"WARNING: check last_cash_point_closing_export_id {options['last_cash_point_closing_export_id']} | last_receipt_number {options['last_receipt_number']} ")

   print('')

   cash_closing_obj = cash_closing.build_cash_closing(transactions, options, ProductProvider())

   with open(config.cash_closing_filename(), encoding='utf-8', mode='w') as res:
      res.write(cash_closing_obj.toJSON())


   config.last_receipt_number = cash_closing_obj.transactions[-1].head.number
   print(f"Transactions: {config.transactions_filename()}")
   print(f"Cash Closing: {config.cash_closing_filename()}")
   # save this value
   print(f"last_receipt_number (update env): {config.last_receipt_number}")
   # save this value
   print(f"last_cash_point_closing_export_id: {config.last_cc_export_id}")


def split_json_files_by_bussiness_date(tx_iterator, config):
    # step 0: setup
    all_transactions = []
    total_count = 0

    # step 1: get all new transactions in batches
    for tx_batch in tx_iterator:
        print("MERGING")
        all_transactions.extend(tx_batch["data"])
        total_count += len(tx_batch["data"])
    
    print(f"Total count: {total_count}")
    # step 2: Sort the merged data by the "number" field
    all_transactions.sort(key=lambda x: x["number"])

    # step 3: complete product data if missing
    product_provider = ProductProvider()
    transaction_fixer = TransactionFixer(product_provider)

    transaction_fixer.complete_transaction_data(all_transactions, config)
    
    print(f"LAST_PROCESSED_TX_NUMBER (update env): {config.last_processed_tx_number}")


    daily_txn_list = [transaction for transaction in all_transactions if transaction["time_start"] >= config.timestamp_low() and transaction["time_start"] <  config.timestamp_high() ]

    daily_txn_count = len(daily_txn_list)
    print(f"filtered_count: {daily_txn_count}. From {config.timestamp_low()} to {config.timestamp_high()}")
    print(f"Date {config.bussiness_date()}")

    while config.last_cc_export_id < LAST_CASH_CLOSING_TO_PROCESS:
    # if 1 == 1:
        if daily_txn_count > 0:
            daily_transactions = {
                "data": daily_txn_list,
                "count": daily_txn_count
            }
            
            # Write the merged dictionary to the output file
            with open(config.transactions_filename(), mode='w', encoding='utf8') as f:
                json.dump(daily_transactions, f, indent=4)

            process_closing(config, parse(daily_transactions))
            
            config.last_processed_tx_number = daily_txn_list[-1]["number"]
            print(f"Saved: {config.transactions_filename()}")

        config.next()
        daily_txn_list = [transaction for transaction in all_transactions if transaction["time_start"] >= config.timestamp_low() and transaction["time_start"] <  config.timestamp_high() ]

        daily_txn_count = len(daily_txn_list)
        
        print(f"filtered_count: {daily_txn_count}. From {config.timestamp_low()} to {config.timestamp_high()}")
        print(f"Date {config.bussiness_date()}")



client = FiskalyClient.objects.get(id=1)
fs = FiskalyService()
fs.credentials = client.get_credentials()
transaction_fetcher = TransactionFetcher(fs, client)
transaction_fetcher.update_last_tx_pending()



transactions_iterator  = iter(transaction_fetcher)
config = Config(client)
split_json_files_by_bussiness_date(transactions_iterator, config)
config.save_vars()