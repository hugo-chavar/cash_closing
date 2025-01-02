import json
from constants import LAST_CASH_CLOSING_TO_PROCESS
from types import SimpleNamespace
from product_provider import ProductProvider
from cash_closing_config import Config
import cash_closing
from models import FiskalyClient


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

   # print(f"WARNING: check last_cash_point_closing_export_id {options['last_cash_point_closing_export_id']} | last_receipt_number {options['last_receipt_number']} ")

   print('')

   cash_closing_obj = cash_closing.build_cash_closing(transactions, options, ProductProvider())

   with open(config.cash_closing_filename(), encoding='utf-8', mode='w') as res:
      res.write(cash_closing_obj.toJSON())


   config.last_receipt_number = cash_closing_obj.transactions[-1].head.number
   print(f"Transactions: {config.transactions_filename()}")
   print(f"Cash Closing: {config.cash_closing_filename()}")
   # save this value
   # print(f"last_receipt_number (update env): {config.last_receipt_number}")
   # save this value
   # print(f"last_cash_point_closing_export_id: {config.last_cc_export_id}")


client = FiskalyClient.objects.get(id=1)
# fs = FiskalyService()
# fs.credentials = client.get_credentials()

config = Config(client)
config.last_cc_export_id = 181  # Error from this 183

while config.last_cc_export_id < LAST_CASH_CLOSING_TO_PROCESS:
   # if 1 == 1:
   # except the problematic cc
   # if config.last_cc_export_id in [16, 20, 21, 22, 28, 29, 179, 180]:
   # if config.last_cc_export_id in [16, 22, 29, 179, 180]:
   #    config.next()
   #    continue
   # process only the problematic cc
   # if config.last_cc_export_id not in [16, 22, 29]:
   #    config.next()
   #    continue
   print(f"Date {config.bussiness_date()}")
   with open(config.transactions_filename(), encoding='utf-8', mode='r') as f:
      # transactions = json.load(f, object_hook=lambda d: SimpleNamespace(**d))
      transactions_dict = json.load(f)
      transactions = parse(transactions_dict)
      try:
         process_closing(config, transactions)
      except cash_closing.CashClosingException:
         print(f"CC {config.last_cc_export_id + 1} ended with errors")
   config.next()

# config.save_vars()    