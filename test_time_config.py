#!/usr/bin/env python3
"""
Test script for time configuration
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from time_config import (
    get_current_ist_time, format_ist_time, format_relative_time,
    get_date_for_display, get_time_for_display, get_timezone_info,
    is_business_hours, get_available_class_slots, validate_class_time,
    get_class_schedule_time, get_time_difference_hours
)

def test_time_configuration():
    """Test the time configuration functionality"""
    
    print("🕐 Testing Time Configuration (IST)...")
    print("=" * 50)
    
    # Test current time
    current_time = get_current_ist_time()
    print(f"1. Current IST Time: {format_ist_time(current_time)}")
    print(f"   Date Display: {get_date_for_display()}")
    print(f"   Time Display: {get_time_for_display()}")
    
    # Test timezone info
    tz_info = get_timezone_info()
    print(f"\n2. Timezone Information:")
    print(f"   Timezone: {tz_info['timezone']}")
    print(f"   Current Time: {tz_info['current_time']}")
    print(f"   Current Date: {tz_info['current_date']}")
    print(f"   Day of Week: {tz_info['day_of_week']}")
    print(f"   Business Hours: {tz_info['is_business_hours']}")
    
    # Test business hours
    print(f"\n3. Business Hours Check:")
    print(f"   Is Business Hours: {is_business_hours()}")
    
    # Test class schedule time
    print(f"\n4. Class Schedule Time:")
    print(f"   Current Schedule Time: {get_class_schedule_time()}")
    
    # Test available class slots
    print(f"\n5. Available Class Slots for Today:")
    slots = get_available_class_slots()
    if slots:
        for i, slot in enumerate(slots, 1):
            print(f"   {i}. {slot}")
    else:
        print("   No available slots for today")
    
    # Test time validation
    print(f"\n6. Time Validation:")
    test_times = ["09:00", "14:30", "22:00", "08:00"]
    for time_str in test_times:
        is_valid = validate_class_time(time_str)
        print(f"   {time_str}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test relative time formatting
    print(f"\n7. Relative Time Formatting:")
    from datetime import timedelta
    
    # Test different time differences
    now = get_current_ist_time()
    
    # 5 minutes ago
    time_5min_ago = now - timedelta(minutes=5)
    print(f"   5 minutes ago: {format_relative_time(time_5min_ago)}")
    
    # 2 hours ago
    time_2hr_ago = now - timedelta(hours=2)
    print(f"   2 hours ago: {format_relative_time(time_2hr_ago)}")
    
    # 1 day ago
    time_1day_ago = now - timedelta(days=1)
    print(f"   1 day ago: {format_relative_time(time_1day_ago)}")
    
    # 3 days ago
    time_3days_ago = now - timedelta(days=3)
    print(f"   3 days ago: {format_relative_time(time_3days_ago)}")
    
    # Test time difference calculation
    print(f"\n8. Time Difference Calculation:")
    time1 = now
    time2 = now + timedelta(hours=2, minutes=30)
    diff_hours = get_time_difference_hours(time1, time2)
    print(f"   Difference between {format_ist_time(time1)} and {format_ist_time(time2)}: {diff_hours:.2f} hours")
    
    print("\n" + "=" * 50)
    print("✅ Time Configuration Test Complete!")
    print("\nThe website now operates on Indian Standard Time (IST)")
    print("All timestamps, schedules, and time-based features will use IST")

if __name__ == "__main__":
    test_time_configuration() 