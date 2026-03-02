import datetime
from constants import SECONDS_PER_DAY
from date_tests import get_german_date

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
        # self.deleted_cc = dict([(180, True), (181, True), (183, True), (184, True), (185, True), (186, True), (187, True), (188, True), (204, True), (205, True), (224, True)])
        self.deleted_cc = {}

    def deleted_count(self):
        deleted_cc = 0
        # deleted_cc += 1 if self.last_cc_export_id > 179 else 0
        # print(f"Deleted count: {deleted_cc}")
        return deleted_cc
    
    def skipped_days_count(self):
        skipped_days = 0
        # 30-06-2025 has 0 tx
        # skipped_days += 1 if self.last_cc_export_id > 384 else 0
        # print(f"Skipped count: {skipped_days}")
        return skipped_days
    
    def cc_counter(self):
        return self.last_cc_export_id - self.deleted_count()  + self.skipped_days_count()
    
    def timestamp_low(self):
        # TODO: do not use self.last_cc_export_id because we have to discount deleted cc
        return self.base_timestamp + SECONDS_PER_DAY * self.cc_counter()

    def timestamp_high(self):
        return self.timestamp_low() + SECONDS_PER_DAY

    def bussiness_date(self):
        # TODO: do not use self.last_cc_export_id because we have to discount deleted cc
        return get_german_date(self.base_timestamp) + datetime.timedelta(
            days=self.cc_counter()
        )

    def cc_number(self):
        cc_number = self.last_cc_export_id + 1
        while self.deleted_cc.get(cc_number, False):
            cc_number += 1
        return cc_number

    def file_suffix(self):
        return f"{self.cc_number():03}_{format_shortdate(self.bussiness_date())}"
    
    def transactions_filename(self):
        folder = f"{self.base_path()}\\m"
        return f"{folder}\\merged_{self.file_suffix()}.json"

    def cash_closing_filename(self):
        folder = f"{self.base_path()}\\ns"
        return f"{folder}\\CASH_CLOSING_{self.file_suffix()}.json"

    def next(self):
        self.last_cc_export_id = self.cc_number()

    def save_vars(self):
        self.client.last_processed_tx_number = self.last_processed_tx_number
        self.client.last_receipt_number = self.last_receipt_number
        self.client.last_cash_point_closing_export_id = self.last_cc_export_id
        self.client.save()

    def base_path(self):
        return f"closings\\{self.client.id}"

    def s_path(self):
        return f"{self.base_path()}\\s"
    
    def m_path(self):
        return f"{self.base_path()}\\m"