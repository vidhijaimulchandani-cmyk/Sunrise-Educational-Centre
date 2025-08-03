"""
Time Configuration for Sunrise Educational Centre
Sets up Indian Standard Time (IST) for the entire website
"""

import os
from datetime import datetime, timezone, timedelta
import pytz

# Set timezone environment variable
os.environ['TZ'] = 'Asia/Kolkata'

# IST timezone object
IST = pytz.timezone('Asia/Kolkata')

def get_current_ist_time():
    """Get current time in IST"""
    return datetime.now(IST)

def get_ist_datetime_from_utc(utc_datetime):
    """Convert UTC datetime to IST"""
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    return utc_datetime.astimezone(IST)

def get_utc_datetime_from_ist(ist_datetime):
    """Convert IST datetime to UTC"""
    if ist_datetime.tzinfo is None:
        ist_datetime = IST.localize(ist_datetime)
    return ist_datetime.astimezone(timezone.utc)

def format_ist_time(datetime_obj, format_str="%Y-%m-%d %H:%M:%S"):
    """Format datetime object to IST string"""
    if datetime_obj.tzinfo is None:
        datetime_obj = IST.localize(datetime_obj)
    elif datetime_obj.tzinfo != IST:
        datetime_obj = datetime_obj.astimezone(IST)
    return datetime_obj.strftime(format_str)

def parse_ist_time(time_str, format_str="%Y-%m-%d %H:%M:%S"):
    """Parse IST time string to datetime object"""
    dt = datetime.strptime(time_str, format_str)
    return IST.localize(dt)

def get_ist_timestamp():
    """Get current IST timestamp"""
    return get_current_ist_time().timestamp()

def get_time_difference_hours(time1, time2):
    """Get difference between two times in hours"""
    if time1.tzinfo is None:
        time1 = IST.localize(time1)
    if time2.tzinfo is None:
        time2 = IST.localize(time2)
    
    diff = abs(time2 - time1)
    return diff.total_seconds() / 3600

def is_business_hours():
    """Check if current time is within business hours (9 AM to 8 PM IST)"""
    current_time = get_current_ist_time()
    start_time = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
    end_time = current_time.replace(hour=20, minute=0, second=0, microsecond=0)
    
    return start_time <= current_time <= end_time

def get_next_business_day():
    """Get next business day (Monday to Friday)"""
    current_time = get_current_ist_time()
    next_day = current_time + timedelta(days=1)
    
    # Skip weekends
    while next_day.weekday() >= 5:  # Saturday = 5, Sunday = 6
        next_day += timedelta(days=1)
    
    return next_day

def format_relative_time(datetime_obj):
    """Format datetime as relative time (e.g., '2 hours ago', 'yesterday')"""
    now = get_current_ist_time()
    
    if datetime_obj.tzinfo is None:
        datetime_obj = IST.localize(datetime_obj)
    elif datetime_obj.tzinfo != IST:
        datetime_obj = datetime_obj.astimezone(IST)
    
    diff = now - datetime_obj
    
    if diff.days > 0:
        if diff.days == 1:
            return "yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        else:
            return format_ist_time(datetime_obj, "%d %b %Y")
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"

def get_class_schedule_time():
    """Get formatted time for class schedules"""
    return get_current_ist_time().strftime("%I:%M %p")

def get_date_for_display():
    """Get current date formatted for display"""
    return get_current_ist_time().strftime("%d %B %Y, %A")

def get_time_for_display():
    """Get current time formatted for display"""
    return get_current_ist_time().strftime("%I:%M:%S %p")

def is_live_class_time(scheduled_time):
    """Check if it's time for a live class (within 15 minutes of scheduled time)"""
    current_time = get_current_ist_time()
    
    if isinstance(scheduled_time, str):
        scheduled_time = parse_ist_time(scheduled_time)
    
    if scheduled_time.tzinfo is None:
        scheduled_time = IST.localize(scheduled_time)
    elif scheduled_time.tzinfo != IST:
        scheduled_time = scheduled_time.astimezone(IST)
    
    time_diff = abs((current_time - scheduled_time).total_seconds() / 60)
    return time_diff <= 15  # Within 15 minutes

def get_timezone_info():
    """Get timezone information for display"""
    current_time = get_current_ist_time()
    return {
        'timezone': 'IST (UTC+5:30)',
        'current_time': format_ist_time(current_time),
        'current_date': current_time.strftime("%d %B %Y"),
        'day_of_week': current_time.strftime("%A"),
        'is_business_hours': is_business_hours()
    }

# Time constants for the application
CLASS_DURATION_MINUTES = 60
BREAK_DURATION_MINUTES = 15
MAX_CLASS_DURATION_HOURS = 2

# Business hours
BUSINESS_START_HOUR = 9
BUSINESS_END_HOUR = 20

# Class timing slots (in 24-hour format)
CLASS_SLOTS = [
    "09:00", "10:00", "11:00", "12:00", "14:00", "15:00", 
    "16:00", "17:00", "18:00", "19:00", "20:00"
]

def get_available_class_slots():
    """Get available class time slots for today"""
    current_time = get_current_ist_time()
    available_slots = []
    
    for slot in CLASS_SLOTS:
        hour, minute = map(int, slot.split(':'))
        slot_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Only show future slots for today
        if slot_time > current_time:
            available_slots.append(slot_time.strftime("%I:%M %p"))
    
    return available_slots

def validate_class_time(class_time_str):
    """Validate if a class time is within business hours"""
    try:
        class_time = datetime.strptime(class_time_str, "%H:%M").time()
        return BUSINESS_START_HOUR <= class_time.hour < BUSINESS_END_HOUR
    except ValueError:
        return False

# Export commonly used functions
__all__ = [
    'get_current_ist_time',
    'get_ist_datetime_from_utc',
    'get_utc_datetime_from_ist',
    'format_ist_time',
    'parse_ist_time',
    'get_ist_timestamp',
    'format_relative_time',
    'get_class_schedule_time',
    'get_date_for_display',
    'get_time_for_display',
    'is_live_class_time',
    'get_timezone_info',
    'get_available_class_slots',
    'validate_class_time',
    'IST'
] 