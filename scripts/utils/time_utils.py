from datetime import datetime, timedelta

STUDY_TIME_RANGES = {
    'Mornings': ('08:00', '12:00'),
    'Afternoons': ('13:00', '17:00'),
    'Evenings': ('18:00', '22:00'),
    'Late Nights': ('22:00', '02:00')
}

WEEKDAY_MAP = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
REVERSE_WEEKDAY_MAP = {v: k for k, v in WEEKDAY_MAP.items()}

def parse_utc_offset(tz_str):
    """
    Extract UTC offset from a string like 'UTC-5'.
    """
    return int(tz_str.replace('UTC', ''))

def shift_to_utc(local_time_str, utc_offset):
    """
    Convert local time (HH:MM) to UTC using the offset.
    """
    local_time = datetime.strptime(local_time_str, "%H:%M")
    utc_time = local_time - timedelta(hours=utc_offset)
    return utc_time.strftime("%H:%M")

def shift_to_local(utc_time_str, utc_offset):
    """
    Convert UTC time (HH:MM) to local using the offset.
    """
    dt = datetime.strptime(utc_time_str, "%H:%M")
    local_dt = dt + timedelta(hours=utc_offset)
    return local_dt.strftime("%H:%M")

def get_utc_day(local_day_str, local_time_str, utc_offset):
    """
    Get the UTC weekday for a local day and time.
    """
    weekday_index = WEEKDAY_MAP[local_day_str]
    ref_date = datetime(2024, 1, 1 + weekday_index)
    local_dt = datetime.combine(ref_date.date(), datetime.strptime(local_time_str, "%H:%M").time())
    utc_dt = local_dt - timedelta(hours=utc_offset)
    return REVERSE_WEEKDAY_MAP[utc_dt.weekday()]