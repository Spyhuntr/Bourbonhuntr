import datetime as dt
import time

def now():
    """Get the current timestamp."""
    return dt.datetime.utcnow()

def get_run_dt():
    """Get the run date to flip the dashboard at a certain time"""
    if time.localtime().tm_isdst:
        turnover_time = now().replace(hour=15, minute=0, second=0, microsecond=0)
    else:
        turnover_time = now().replace(hour=16, minute=0, second=0, microsecond=0)
    
    if now().time() < turnover_time.time():
        return now().date() - dt.timedelta(days=1)
    else:
        return now().date()