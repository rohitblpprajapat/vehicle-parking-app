from datetime import datetime, timedelta, timezone

def get_ist_now():
    """Get current time in Indian Standard Time (UTC+5:30)"""
    # IST is UTC + 5:30
    ist_offset = timedelta(hours=5, minutes=30)
    ist_tz = timezone(ist_offset)
    return datetime.now(ist_tz)
