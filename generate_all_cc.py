import json
from constants import LAST_CASH_CLOSING_TO_PROCESS
from product_provider import ProductProvider
from cash_closing_config import Config
import cash_closing
from restaurant_picker import get_config
from simple_ns_parser import parse


def process_closing(config: Config, transactions):

    print(f"Transactions: {config.transactions_filename()}")
    cash_closing_obj = cash_closing.build_cash_closing(
        transactions, config.cash_closing_options(), ProductProvider()
    )

    with open(config.cash_closing_filename(), encoding="utf-8", mode="w") as res:
        res.write(cash_closing_obj.toJSON())

    config.last_receipt_number = cash_closing_obj.transactions[-1].head.number
    
    print(f"Cash Closing: {config.cash_closing_filename()}")
    # print(f"last_receipt_number (update env): {config.last_receipt_number}")
    # print(f"last_cash_point_closing_export_id: {config.last_cc_export_id}")


config = get_config()
client = config.client
# fs = FiskalyService()
# fs.credentials = client.get_credentials()

# config.last_cc_export_id = 1

# while config.last_cc_export_id < LAST_CASH_CLOSING_TO_PROCESS:
if 1 == 1:
    # except the problematic cc
    # if config.last_cc_export_id in [16, 20, 21, 22, 28, 29, 179, 180]:
    # if config.last_cc_export_id in [16, 22, 29, 179, 180]:
    #    config.next()
    #    continue
    # process only the problematic cc
    # if config.last_cc_export_id not in [16, 22, 29]:
    #    config.next()
    #    continue
    print("")
    print("="*50)
    print(f"Date {config.bussiness_date()}")
    print(f"Opening {config.transactions_filename()}")
    
    with open(config.transactions_filename(), encoding="utf-8", mode="r") as f:
        # transactions = json.load(f, object_hook=lambda d: SimpleNamespace(**d))
        transactions_dict = json.load(f)
        transactions = parse(transactions_dict)
        try:
            process_closing(config, transactions)
        except cash_closing.CashClosingException:
            print(f"CC {config.last_cc_export_id + 1} ended with errors")
    config.next()

# config.save_vars()
