import datetime
from constants import SECONDS_PER_DAY
from date_tests import get_german_date

def format_shortdate(date_time):
    return f"{date_time.strftime("%Y%m%d")}"


class Config:
    def __init__(self, fiskaly_client):
        self.client = fiskaly_client
        self.last_cc_export_id = fiskaly_client.last_cash_point_closing_export_id
        self.base_timestamp = fiskaly_client.base_timestamp
        self.last_receipt_number = fiskaly_client.last_receipt_number
        self.cash_register = (
            fiskaly_client.cash_register
        )
        self.last_processed_tx_number = fiskaly_client.last_processed_tx_number

    
    def skipped_days_count(self):
        skipped_days = 0 # initialize this
        return skipped_days
    
    def cc_counter(self):
        return self.last_cc_export_id + self.skipped_days_count()
    
    def timestamp_low(self):
        return self.base_timestamp + SECONDS_PER_DAY * self.cc_counter()

    def timestamp_high(self):
        return self.timestamp_low() + SECONDS_PER_DAY

    def bussiness_date(self):
        return get_german_date(self.base_timestamp) + datetime.timedelta(
            days=self.cc_counter()
        )

    def next(self):
        self.last_cc_export_id = self.cc_number()

    def save_vars(self):
        self.client.last_processed_tx_number = self.last_processed_tx_number
        self.client.last_receipt_number = self.last_receipt_number
        self.client.last_cash_point_closing_export_id = self.last_cc_export_id
        self.client.save()

    def cc_number(self):
        cc_number = self.last_cc_export_id + 1
        return cc_number

    # more unrelated methods ..
    def base_path(self):
        return f"closings\\{self.client.id}"

    def s_path(self):
        return f"{self.base_path()}\\s"
    
    def m_path(self):
        return f"{self.base_path()}\\m"
    
    def r_path(self):
        return f"{self.base_path()}\\r\\cc_report.csv"
    
    def tx_path(self):
        return f"{self.base_path()}\\r\\tx_report.csv"
    
    def cash_closing_options(self):
        return {
            "last_cash_point_closing_export_id": self.last_cc_export_id,
            "cash_register": self.cash_register,
            "last_receipt_number": self.last_receipt_number,
        }

    def file_suffix(self):
        return f"{self.cc_number():03}_{format_shortdate(self.bussiness_date())}"
    
    def transactions_filename(self):
        folder = f"{self.base_path()}\\m"
        return f"{folder}\\merged_{self.file_suffix()}.json"

    def cash_closing_filename(self):
        folder = f"{self.base_path()}\\ns"
        return f"{folder}\\CASH_CLOSING_{self.file_suffix()}.json"
