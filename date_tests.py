import datetime
import pytz

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
    return datetime.datetime.fromtimestamp(timestamp)

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

    original_date_time_utc = datetime.datetime.fromtimestamp(original_timestamp, tz=datetime.timezone.utc)
    # truncated_date_time_utc = datetime.datetime.fromtimestamp(truncated_timestamp, tz=datetime.timezone.utc)

    germany_tz = pytz.timezone('Europe/Berlin')
    original_date_time_germany = original_date_time_utc.astimezone(germany_tz)
    # Set time to midnight
    truncated_date_time_germany = original_date_time_germany.replace(hour=0, minute=0, second=0, microsecond=0)
    # truncated_date_time_germany = truncated_date_time_utc.astimezone(germany_tz)

    # original_date_time = datetime.datetime.fromtimestamp(original_timestamp)
    # truncated_date_time = datetime.datetime.fromtimestamp(truncated_timestamp)


    print(f"{number}: {original_timestamp} - {original_date_time_germany.strftime("%d/%m/%Y, %H:%M:%S")} - {int(truncated_date_time_germany.timestamp())} {truncated_date_time_germany.strftime("%d/%m/%Y, %H:%M:%S")} ")
# print("Truncated date_time (day only):", truncated_date_time.strftime("%d/%m/%Y, %H:%M:%S"))




def get_german_date(original_timestamp):

    original_date_time_utc = datetime.datetime.fromtimestamp(original_timestamp, tz=datetime.timezone.utc)

    germany_tz = pytz.timezone('Europe/Berlin')
    original_date_time_germany = original_date_time_utc.astimezone(germany_tz)
    # Set time to midnight
    truncated_date_time_germany = get_truncated_date(original_date_time_germany)

    return original_date_time_germany
    # return f"{get_formatted_date(original_date_time_germany)}"
    # print(f"{number}: {original_timestamp} - {original_date_time_germany.strftime("%d/%m/%Y, %H:%M:%S")} - {int(truncated_date_time_germany.timestamp())} {truncated_date_time_germany.strftime("%d/%m/%Y, %H:%M:%S")} ")

date = f"{get_formatted_shortdate(get_german_date(1720082141))}"

# print(get_german_date(1720082141))
# print(date_from_timestamp(1720168541))
# print(date)
# print('Fin date_tests')