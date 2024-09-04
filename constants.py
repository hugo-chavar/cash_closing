import datetime
from date_tests import get_format_shortdate

BASE_DATE_TIME = datetime.datetime(2024, 6, 20, 0, 0)
BASE_TIMESTAMP = 1718938800 # 1718852400 #1718920800
SECONDS_PER_DAY = 86400

LAST_CASH_CLOSING_TO_PROCESS = 76 # procesar de a uno, desaparece esta
LAST_CASH_POINT_CLOSING_EXPORT_ID = 75
LAST_RECEIPT_NUMBER = 7399
# LAST_PROCESSED_TX_NUMBER = 14551 # se usa en merge_json, pero no en la nueva

# TIMESTAMP_LOW = BASE_TIMESTAMP + SECONDS_PER_DAY*LAST_CASH_POINT_CLOSING_EXPORT_ID

# TIMESTAMP_HIGH = TIMESTAMP_LOW + SECONDS_PER_DAY

date_fmt = get_format_shortdate(BASE_DATE_TIME + datetime.timedelta(days=LAST_CASH_POINT_CLOSING_EXPORT_ID + 1))
cc_number = LAST_CASH_POINT_CLOSING_EXPORT_ID + 1
TRANSACTIONS_FILENAME = f'merged7\\merged_file_filter_{date_fmt}.json'
CASH_CLOSING_FILENAME = f'closings\\CASH_CLOSING_{cc_number:03}_{date_fmt}.json'
CASH_CLOSING_UNFORMATTED_FILENAME = 'resultUNF_prod_0.json'

# def get_cc_info(last_cc_export_id):
#     timestamp_low = BASE_TIMESTAMP + SECONDS_PER_DAY*last_cc_export_id

#     timestamp_high = timestamp_low + SECONDS_PER_DAY

#     return timestamp_low, timestamp_high

