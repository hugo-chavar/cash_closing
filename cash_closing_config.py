import datetime
from constants import SECONDS_PER_DAY


def format_shortdate(date_time):
    return f"{date_time.strftime("%Y%m%d")}"


def date_from_timestamp(timestamp):
    # Convert timestamp to datetime object
    return datetime.datetime.fromtimestamp(timestamp)


class Config:
    def __init__(self, fiskaly_client):
        self.client = fiskaly_client
        self.last_cc_export_id = fiskaly_client.last_cash_point_closing_export_id
        self.base_timestamp = fiskaly_client.base_timestamp
        self.last_receipt_number = fiskaly_client.last_receipt_number
        self.cash_register = (
            fiskaly_client.cash_register
        )  ## Used in process_closing (generate_all_cc.py)
        self.last_processed_tx_number = fiskaly_client.last_processed_tx_number

    def cc_counter(self):
        deleted_cc = 2 if self.last_cc_export_id > 181 else 0
        return self.last_cc_export_id - deleted_cc
    
    def timestamp_low(self):
        # TODO: do not use self.last_cc_export_id because we have to discount deleted cc
        return self.base_timestamp + SECONDS_PER_DAY * self.cc_counter()

    def timestamp_high(self):
        return self.timestamp_low() + SECONDS_PER_DAY

    def bussiness_date(self):
        # TODO: do not use self.last_cc_export_id because we have to discount deleted cc
        return date_from_timestamp(self.base_timestamp) + datetime.timedelta(
            days=self.cc_counter()
        )

    def cc_number(self):
        return self.last_cc_export_id + 1

    def transactions_filename(self):
        folder = "merged7"
        return f"{folder}\\merged_file_filter_{self.cc_number():03}_{format_shortdate(self.bussiness_date())}.json"

    def cash_closing_filename(self):
        folder = "closings6"
        return f"{folder}\\CASH_CLOSING_{self.cc_number():03}_{format_shortdate(self.bussiness_date())}.json"

    def next(self):
        self.last_cc_export_id = self.cc_number()

    def save_vars(self):
        self.client.last_processed_tx_number = self.last_processed_tx_number
        self.client.last_receipt_number = self.last_receipt_number
        self.client.last_cash_point_closing_export_id = self.last_cc_export_id
        self.client.save()
