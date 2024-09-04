import json
from constants import LAST_CASH_POINT_CLOSING_EXPORT_ID, LAST_RECEIPT_NUMBER, BASE_TIMESTAMP, LAST_CASH_CLOSING_TO_PROCESS
from types import SimpleNamespace
from product_provider import ProductProvider
from cash_closing_config import Config
import cash_closing


def parse(d):
    x = SimpleNamespace()
    _ = [setattr(x, k,
                 parse(v) if isinstance(v, dict)
                 else [parse(e) for e in v] if isinstance(v, list)
                 else v) for k, v in d.items()]
    return x


def process_closing(config: Config):
   options = {
      "last_cash_point_closing_export_id": config.last_cc_export_id,
      "cash_register": config.cash_register,
      "last_receipt_number": config.last_receipt_number,
   }

   print(f"WARNING: check last_cash_point_closing_export_id {options['last_cash_point_closing_export_id']} | last_receipt_number {options['last_receipt_number']} ")

   with open(config.transactions_filename(), encoding='utf-8', mode='r') as f:
      j = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

   # https://stackoverflow.com/questions/16877422/whats-the-best-way-to-parse-a-json-response-from-the-requests-library
   # https://medium.com/snowflake/json-methods-load-vs-loads-and-dump-vs-dumps-21434a520b17



      # print(str(j))
      print('')

      cash_closing_obj = cash_closing.build_cash_closing(j, options, ProductProvider())
      # print(cash_closing_obj.client_id)

      # # print(json.dumps(cash_closing_obj.__dict__))
      with open(config.cash_closing_filename(), encoding='utf-8', mode='w') as res:
         res.write(cash_closing_obj.toJSON())

      # print(cash_closing_obj.toJSON())
      # jo = cash_closing_obj.toJSON()
      # print(type(cash_closing_obj.get_dict()))
      # print('')
      # print(json.dumps(cash_closing_obj.get_dict()))
      # with open(CASH_CLOSING_UNFORMATTED_FILENAME, encoding='utf-8', mode='w') as unf:
      #    unf.write(json.dumps(cash_closing_obj.get_dict()))


      config.last_receipt_number = cash_closing_obj.transactions[-1].head.number
      print(f"Transactions: {config.transactions_filename()}")
      print(f"Cash Closing: {config.cash_closing_filename()}")
      # save this value
      print(f"last_receipt_number: {config.last_receipt_number}")
      # save this value
      print(f"last_cash_point_closing_export_id: {config.cc_number()}")

config = Config(BASE_TIMESTAMP, last_cc_export_id=LAST_CASH_POINT_CLOSING_EXPORT_ID, last_receipt_number=LAST_RECEIPT_NUMBER)
config.cash_register = "e2bc3f5a-1130-4d08-ac54-0fb6730d3963"

while config.last_cc_export_id < LAST_CASH_CLOSING_TO_PROCESS:

   print(f"Date {config.bussiness_date()}")
   process_closing(config)
   config.next()

    