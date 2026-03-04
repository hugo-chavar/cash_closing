import datetime
from constants import SECONDS_PER_DAY
from date_tests import get_german_date

def format_shortdate(date_time):
    return f"{date_time.strftime('%Y%m%d')}"


class Config:
    def __init__(self, fiskaly_client):
        self.client = fiskaly_client
        self.last_cc_export_id = fiskaly_client.last_cash_point_closing_export_id
        self.base_timestamp = fiskaly_client.base_timestamp
        self.last_receipt_number = fiskaly_client.last_receipt_number
        self.cash_register = fiskaly_client.cash_register
        self.last_processed_tx_number = fiskaly_client.last_processed_tx_number
        self._skipped_days = 0  # Track skipped days separately
    
    def skipped_days_count(self):
        """Returns the number of skipped days (days with no transactions)"""
        return self._skipped_days
    
    def business_day_offset(self):
        """
        Returns the total number of business days to offset from base_timestamp.
        This includes both processed closings AND skipped days.
        """
        return self.last_cc_export_id + self._skipped_days
    
    def timestamp_low(self):
        """Lower bound timestamp for current business day"""
        return self.base_timestamp + SECONDS_PER_DAY * self.business_day_offset()

    def timestamp_high(self):
        """Upper bound timestamp for current business day"""
        return self.timestamp_low() + SECONDS_PER_DAY

    def bussiness_date(self):
        """Get the business date for current day"""
        return get_german_date(self.base_timestamp) + datetime.timedelta(
            days=self.business_day_offset()
        )
    
    def advance_to_next_day_only(self):
        """
        Advance to next business day WITHOUT incrementing the cash closing number.
        Use this for days with no transactions.
        """
        self._skipped_days += 1
        print(f"Advanced to next day (skipped days: {self._skipped_days})")

    def next(self):
        """
        Move to next business day AND increment cash closing number.
        Use this when a cash closing was actually created.
        """
        self.last_cc_export_id = self.last_cc_export_id + 1
        # Reset skipped days counter for the new day
        # Note: We don't reset because skipped days are cumulative from the start
        print(f"Advanced to next closing (closing number: {self.last_cc_export_id})")

    def save_vars(self):
        """Save all variables back to the client"""
        self.client.last_processed_tx_number = self.last_processed_tx_number
        self.client.last_receipt_number = self.last_receipt_number
        self.client.last_cash_point_closing_export_id = self.last_cc_export_id
        # Note: skipped_days doesn't need to be persisted as it's derived
        # from the relationship between base_timestamp and current date
        self.client.save()

    def cc_number(self):
        """Get the next cash closing number"""
        return self.last_cc_export_id + 1

    def reset_skipped_days(self):
        """
        Optional: Reset skipped days counter if you need to recalculate from a specific point
        """
        self._skipped_days = 0
    
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
