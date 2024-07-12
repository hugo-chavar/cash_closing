import datetime
from date_tests import get_format_shortdate

BASE_DATE_TIME = datetime.datetime(2024, 6, 20, 0, 0)

LAST_CASH_POINT_CLOSING_EXPORT_ID = 16
LAST_RECEIPT_NUMBER = 1616

date_fmt = get_format_shortdate(BASE_DATE_TIME + datetime.timedelta(days=LAST_CASH_POINT_CLOSING_EXPORT_ID + 1))
cc_number = LAST_CASH_POINT_CLOSING_EXPORT_ID + 1
TRANSACTIONS_FILENAME = f'merged_json\\merged_file_filter_{date_fmt}.json'
CASH_CLOSING_FILENAME = f'closings\\CASH_CLOSING_{cc_number:03}_{date_fmt}.json'
CASH_CLOSING_UNFORMATTED_FILENAME = 'resultUNF_prod_0.json'

