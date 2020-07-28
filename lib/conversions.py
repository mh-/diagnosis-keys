import datetime

interval_length_minutes = 10  # 10 minutes per interval
tek_rolling_period = 144  # 24*60//10 - 24 hours per day, 60 minutes per hour, 10 minutes per interval


def get_timestamp_from_interval(interval_number):
    return interval_number * interval_length_minutes * 60  # 60 seconds per minute


def get_interval_from_utc_timestamp(utc_time_stamp):
    return utc_time_stamp // (interval_length_minutes * 60)  # 60 seconds per minute


def get_datetime_from_utc_timestamp(utc_timestamp):
    return datetime.datetime.utcfromtimestamp(utc_timestamp).replace(tzinfo=datetime.timezone.utc)


def get_timestamp_from_utc_datetime(utc_datetime):
    return int(datetime.datetime.timestamp(utc_datetime))


def get_local_datetime(date_time):
    return date_time.astimezone(datetime.datetime.utcnow().astimezone().tzinfo)


def get_string_from_datetime(date_time):
    return date_time.strftime('%Y-%m-%d %H:%M:%S %Z')
