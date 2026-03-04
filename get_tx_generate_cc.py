import json
from datetime import datetime
from cash_closing import CashClosingException, build_cash_closing
from cash_closing_config import Config
from fiskaly_service import FiskalyService
from product_provider import ProductProvider
from transaction_fetcher import TransactionFetcher
from transaction_fixer import TransactionFixer
from types import SimpleNamespace
from constants import SECONDS_PER_DAY

from date_tests import get_timestamp_from_german_date, get_yesterday_end_timestamp, get_midnight_timestamp
from restaurant_picker import get_config

# The written date will be taken, including the time 23:59:59
TIMESTAMP_THRESHOLD = get_midnight_timestamp(datetime(2025, 12, 23)) + (SECONDS_PER_DAY - 1)
NUMBER_OF_CASH_CLOSINGS_TO_PROCESS = 1
fiskaly_service = FiskalyService()


def parse(d):
    x = SimpleNamespace()
    _ = [
        setattr(
            x,
            k,
            (
                parse(v)
                if isinstance(v, dict)
                else [parse(e) for e in v] if isinstance(v, list) else v
            ),
        )
        for k, v in d.items()
    ]
    return x


def process_closing(config: Config, transactions):
    options = {
        "last_cash_point_closing_export_id": config.last_cc_export_id,
        "cash_register": config.cash_register,
        "last_receipt_number": config.last_receipt_number,
    }

    print(
        f"WARNING: check last_cash_point_closing_export_id {options['last_cash_point_closing_export_id']} | last_receipt_number {options['last_receipt_number']} "
    )

    print("")

    cash_closing_obj = build_cash_closing(transactions, options, ProductProvider())
    config.last_receipt_number = cash_closing_obj.transactions[-1].head.number

    with open(config.cash_closing_filename(), encoding="utf-8", mode="w") as res:
        res.write(cash_closing_obj.toJSON())

    cc_uuid = fiskaly_service.new_guid()
    fiskaly_service.create_cash_closing(cc_uuid, cash_closing_obj.get_dict())

    print(f"Transactions: {config.transactions_filename()}")
    print(f"Cash Closing: {config.cash_closing_filename()}")
    print(f"last_receipt_number (update env): {config.last_receipt_number}")
    print(f"last_cash_point_closing_export_id: {config.last_cc_export_id}")


def split_json_files_by_bussiness_date(tx_iterator, config):
    # step 0: setup
    all_transactions = []
    total_count = 0

    # step 1: get all new transactions in batches
    threshold = TIMESTAMP_THRESHOLD

    for tx_batch in tx_iterator:
        print("MERGING")
        threshold_exceeded = False
        for tx in tx_batch["data"]:
            tx.pop("qr_code_data", None)
            tx.pop("tss_serial_number", None)
            tx.pop("tss_id", None)
            if not threshold_exceeded:
                threshold_exceeded = (tx["time_start"] >= threshold)
        all_transactions.extend(tx_batch["data"])
        total_count += len(tx_batch["data"])
        if threshold_exceeded:
            print("BREAK")
            break

    print(f"Total count: {total_count}")

    # step 2: Sort the merged data by the "number" field
    all_transactions.sort(key=lambda x: x["number"])

    # step 3: complete product data if missing
    product_provider = ProductProvider()
    transaction_fixer = TransactionFixer(product_provider, fiskaly_service, config)

    transaction_fixer.complete_transaction_data(all_transactions)

    limit_timestamp = get_yesterday_end_timestamp()
    transaction_fixer.cancel_active_txn(all_transactions, limit_timestamp)

    print(f"LAST_PROCESSED_TX_NUMBER (update env): {config.last_processed_tx_number}")

    config_timestamp_low = config.timestamp_low()
    config_timestamp_high = config.timestamp_high()
    
    print(f"config_timestamp_low: {config_timestamp_low}")
    print(f"config_timestamp_high: {config_timestamp_high}")
    
    daily_txn_list = [
        transaction
        for transaction in all_transactions
        if transaction["time_start"] >= config.timestamp_low()
        and transaction["time_start"] < config.timestamp_high()
    ]

    daily_txn_count = len(daily_txn_list)
    print(
        f"filtered_count: {daily_txn_count}. From {config.timestamp_low()} to {config.timestamp_high()}"
    )
    print(f"Date {config.bussiness_date()}")

    LAST_CASH_CLOSING_TO_PROCESS = (
        config.last_cc_export_id + NUMBER_OF_CASH_CLOSINGS_TO_PROCESS
    )

    try:
        while config.last_cc_export_id < LAST_CASH_CLOSING_TO_PROCESS:
            if daily_txn_count > 0:

                daily_transactions = {"data": daily_txn_list, "count": daily_txn_count}

                # Write the merged dictionary to the output file
                with open(
                    config.transactions_filename(), mode="w", encoding="utf8"
                ) as f:
                    json.dump(daily_transactions, f, indent=4)

                process_closing(config, parse(daily_transactions))

                config.last_processed_tx_number = daily_txn_list[-1]["number"]
                print(f"Saved: {config.transactions_filename()}")

            config.next()
            daily_txn_list = [
                transaction
                for transaction in all_transactions
                if transaction["time_start"] >= config.timestamp_low()
                and transaction["time_start"] < config.timestamp_high()
            ]

            daily_txn_count = len(daily_txn_list)
            if daily_txn_count == 0:
                # la unica manera de que de 0 es que se ejecute al dia
                break

            print(
                f"filtered_count: {daily_txn_count}. From {config.timestamp_low()} to {config.timestamp_high()}"
            )
            print(f"Date {config.bussiness_date()}")
    except CashClosingException as e:
        print(f"Process cancelled due to error: {str(e)}")

config = get_config()
client = config.client

fiskaly_service.credentials = client.get_credentials()
fiskaly_service.token = client.get_token()
transaction_fetcher = TransactionFetcher(fiskaly_service, client)
transaction_fetcher.update_last_tx_pending()


transactions_iterator = iter(transaction_fetcher)
client.access_token = fiskaly_service.token
split_json_files_by_bussiness_date(transactions_iterator, config)
config.save_vars()
