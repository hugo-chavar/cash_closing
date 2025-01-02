import pytz
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# print('Inicia date_tests')

def get_truncated_date(original_date_time):
    truncated_date_time = original_date_time.replace(hour=0, minute=0, second=0, microsecond=0)
    return truncated_date_time

def get_formatted_full_date(date_time):
    return f"{date_time.strftime("%d/%m/%Y, %H:%M:%S")}"


def get_format_shortdate(date_time):
    return f"{date_time.strftime("%Y%m%d")}"

def get_formatted_shortdate(date_time):
    return f"{date_time.strftime("%Y/%m/%d")}"

def date_from_timestamp(timestamp):
    # Convert timestamp to datetime object
    return datetime.fromtimestamp(timestamp)

def truncate_timestamp_to_date(timestamp):
    date_time = date_from_timestamp(timestamp)
    
    # Set time to midnight
    truncated_date_time = get_truncated_date(date_time)

    return truncated_date_time
    
    # # Convert back to timestamp
    # truncated_timestamp = int(truncated_date_time.timestamp())
    
    # return truncated_timestamp


def print_german_date(number, original_timestamp):
    # Example usage
    # original_timestamp = 1719163208  # Example timestamp
    # truncated_timestamp = truncate_timestamp_to_day(original_timestamp)

    # print("Original timestamp:", original_timestamp)
    # print("Truncated timestamp (day only):", truncated_timestamp)

    original_date_time_utc = datetime.fromtimestamp(original_timestamp, tz=datetime.timezone.utc)
    # truncated_date_time_utc = datetime.fromtimestamp(truncated_timestamp, tz=datetime.timezone.utc)

    germany_tz = pytz.timezone('Europe/Berlin')
    original_date_time_germany = original_date_time_utc.astimezone(germany_tz)
    # Set time to midnight
    truncated_date_time_germany = original_date_time_germany.replace(hour=0, minute=0, second=0, microsecond=0)
    # truncated_date_time_germany = truncated_date_time_utc.astimezone(germany_tz)

    # original_date_time = datetime.fromtimestamp(original_timestamp)
    # truncated_date_time = datetime.fromtimestamp(truncated_timestamp)


    print(f"{number}: {original_timestamp} - {original_date_time_germany.strftime("%d/%m/%Y, %H:%M:%S")} - {int(truncated_date_time_germany.timestamp())} {truncated_date_time_germany.strftime("%d/%m/%Y, %H:%M:%S")} ")
# print("Truncated date_time (day only):", truncated_date_time.strftime("%d/%m/%Y, %H:%M:%S"))



def get_german_date_v1(original_timestamp):

    original_date_time_utc = datetime.fromtimestamp(original_timestamp, tz=datetime.timezone.utc)

    germany_tz = pytz.timezone('Europe/Berlin')
    original_date_time_germany = original_date_time_utc.astimezone(germany_tz)
    # Set time to midnight
    truncated_date_time_germany = get_truncated_date(original_date_time_germany)

    return original_date_time_germany
    # return f"{get_formatted_date(original_date_time_germany)}"
    # print(f"{number}: {original_timestamp} - {original_date_time_germany.strftime("%d/%m/%Y, %H:%M:%S")} - {int(truncated_date_time_germany.timestamp())} {truncated_date_time_germany.strftime("%d/%m/%Y, %H:%M:%S")} ")

def get_german_date_v2(original_timestamp):
    """
    Modified version that uses ZoneInfo instead of pytz for better DST handling
    """
    original_date_time_utc = datetime.fromtimestamp(original_timestamp, tz=timezone.utc)
    germany_tz = ZoneInfo('Europe/Berlin')
    original_date_time_germany = original_date_time_utc.astimezone(germany_tz)
    return original_date_time_germany

def get_timestamp_from_german_date_v1(german_datetime):
    """
    Convert a datetime object in German timezone back to UTC timestamp,
    preserving the original UTC offset.
    """
    if isinstance(german_datetime, str):
        # This will preserve the exact offset specified in the string
        dt = datetime.fromisoformat(german_datetime)
    else:
        dt = german_datetime
        
    # Convert to UTC by removing the offset
    utc_datetime = dt.astimezone(timezone.utc)
    return utc_datetime.timestamp()

def get_timestamp_from_german_date_v2(german_datetime):
    """
    Convert a datetime object in German timezone back to UTC timestamp,
    preserving the original UTC offset.
    """
    if isinstance(german_datetime, str):
        # This will preserve the exact offset specified in the string
        dt = datetime.fromisoformat(german_datetime)
    else:
        dt = german_datetime
        
    # Convert to UTC by removing the offset
    utc_datetime = dt.astimezone(timezone.utc)
    return utc_datetime.timestamp()

def get_timestamp_from_german_date_v3(german_datetime):
    """
    Convert a datetime string or object to UTC timestamp while preserving the exact time.
    
    Args:
        german_datetime (str or datetime): Datetime in format "YYYY-MM-DD HH:MM:SS+HH:MM"
    Returns:
        float: UTC timestamp that will convert back to the exact original time
    """
    if isinstance(german_datetime, str):
        dt = datetime.fromisoformat(german_datetime)
    else:
        dt = german_datetime
    
    # Get the offset in hours
    offset = dt.utcoffset().total_seconds() / 3600
    
    # Convert to UTC timestamp while accounting for the offset
    timestamp = dt.timestamp() - (offset * 3600)
    
    return timestamp

def get_german_date_v3(original_timestamp):
    """
    Convert timestamp back to datetime with original offset.
    """
    # Create UTC datetime
    utc_dt = datetime.fromtimestamp(original_timestamp, tz=timezone.utc)
    
    # Add back the +02:00 offset without changing the time
    offset = timedelta(hours=2)
    german_time = utc_dt.replace(tzinfo=timezone(offset))
    
    return german_time


def get_timestamp_from_german_date(german_datetime):
    """
    Convert a datetime string or object to UTC timestamp while preserving the exact time.
    
    Args:
        german_datetime (str or datetime): Datetime in format "YYYY-MM-DD HH:MM:SS+HH:00"
    Returns:
        float: UTC timestamp
    """
    if isinstance(german_datetime, str):
        dt = datetime.fromisoformat(german_datetime)
    else:
        dt = german_datetime
    
    return dt.timestamp()

def get_german_date(original_timestamp):
    """
    Convert timestamp back to datetime with +02:00 offset while preserving the original time.
    """
    # First get UTC time
    utc_dt = datetime.fromtimestamp(original_timestamp, tz=timezone.utc)
    
    # Convert to +02:00 offset while preserving the time
    offset = timedelta(hours=2)
    target_time = utc_dt.astimezone(timezone(offset))
    
    return target_time

german_dt = get_german_date(1719231364)

date = f"{get_formatted_shortdate(german_dt)}"

# original_timestamp = get_timestamp_from_german_date(german_dt)
# back_to_german = get_german_date(original_timestamp)
# print(f"Original: {german_dt}")
# print(f"Converted back: {back_to_german}")

# threshold = "2024-12-16 23:59:59+02:00"
# t_timestamp = get_timestamp_from_german_date(threshold)
# back_to_german = get_german_date(t_timestamp)
# print(f"Threshold timestamp: {t_timestamp}")
# print(f"Threshold Converted back: {back_to_german}")

# print(get_german_date(1720082141))
# print(date_from_timestamp(1720168541))
# print(date)
# print('Fin date_tests')