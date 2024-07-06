import json
import time
from constants import CASH_CLOSING_FILENAME, CASH_CLOSING_UNFORMATTED_FILENAME, TRANSACTIONS_FILENAME, LAST_CASH_POINT_CLOSING_EXPORT_ID, LAST_RECEIPT_NUMBER
from types import SimpleNamespace
from product_provider import ProductProvider
import cash_closing

options = {
   "last_cash_point_closing_export_id": LAST_CASH_POINT_CLOSING_EXPORT_ID,
   "cash_register": "e2bc3f5a-1130-4d08-ac54-0fb6730d3963",
   "last_receipt_number": LAST_RECEIPT_NUMBER,
}

print(f"WARNING: check last_cash_point_closing_export_id {options['last_cash_point_closing_export_id']} | last_receipt_number {options['last_receipt_number']} ")

with open(TRANSACTIONS_FILENAME, encoding='utf-8', mode='r') as f:
   j = json.load(f, object_hook=lambda d: SimpleNamespace(**d))

   # print(str(j))
   print('')

   cash_closing_obj = cash_closing.build_cash_closing(j, options, ProductProvider())
   # print(cash_closing_obj.client_id)

   # # print(json.dumps(cash_closing_obj.__dict__))
   with open(CASH_CLOSING_FILENAME, encoding='utf-8', mode='w') as res:
      res.write(cash_closing_obj.toJSON())

   # print(cash_closing_obj.toJSON())
   # jo = cash_closing_obj.toJSON()
   # print(type(cash_closing_obj.get_dict()))
   # print('')
   # print(json.dumps(cash_closing_obj.get_dict()))
   # with open(CASH_CLOSING_UNFORMATTED_FILENAME, encoding='utf-8', mode='w') as unf:
   #    unf.write(json.dumps(cash_closing_obj.get_dict()))


   print(f"Transactions: {TRANSACTIONS_FILENAME}")
   print(f"Cash Closing: {CASH_CLOSING_FILENAME}")
   print(f"last_receipt_number: {cash_closing_obj.transactions[-1]["head"]["number"]}")
   print(f"last_cash_point_closing_export_id: {LAST_CASH_POINT_CLOSING_EXPORT_ID + 1}")

