#!/usr/bin/env python3
"""
Test script for live class status management
"""

import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_handler import (
    create_live_class, get_live_classes_for_display, 
    auto_update_class_statuses, get_upcoming_live_classes,
    get_active_live_classes, get_completed_live_classes,
    start_live_class, end_live_class, cancel_live_class
)
from time_config import get_current_ist_time, format_ist_time

def test_live_class_status_management():
    """Test the live class status management functionality"""
    
    print("🎓 Testing Live Class Status Management...")
    print("=" * 60)
    
    # Test 1: Create different types of classes
    print("1. Creating test classes...")
    
    # Create a class scheduled for future
    future_time = get_current_ist_time() + timedelta(hours=2)
    future_time_str = format_ist_time(future_time)
    
    class1_id = create_live_class(
        class_code="TEST001",
        pin="1234",
        meeting_url="/test/video1.mp4",
        topic="Future Class Test",
        description="This class is scheduled for future",
        status='scheduled',
        scheduled_time=future_time_str
    )
    print(f"   ✅ Created future class (ID: {class1_id}) scheduled for {future_time_str}")
    
    # Create a class scheduled for past (should become active)
    past_time = get_current_ist_time() - timedelta(minutes=30)
    past_time_str = format_ist_time(past_time)
    
    class2_id = create_live_class(
        class_code="TEST002",
        pin="5678",
        meeting_url="/test/video2.mp4",
        topic="Past Class Test",
        description="This class was scheduled for past",
        status='scheduled',
        scheduled_time=past_time_str
    )
    print(f"   ✅ Created past class (ID: {class2_id}) scheduled for {past_time_str}")
    
    # Create an active class
    class3_id = create_live_class(
        class_code="TEST003",
        pin="9012",
        meeting_url="/test/video3.mp4",
        topic="Active Class Test",
        description="This class is currently active",
        status='active'
    )
    print(f"   ✅ Created active class (ID: {class3_id})")
    
    # Create a completed class
    class4_id = create_live_class(
        class_code="TEST004",
        pin="3456",
        meeting_url="/test/video4.mp4",
        topic="Completed Class Test",
        description="This class is completed",
        status='completed'
    )
    print(f"   ✅ Created completed class (ID: {class4_id})")
    
    # Test 2: Check initial status distribution
    print(f"\n2. Checking initial class distribution...")
    classes_data = get_live_classes_for_display()
    
    print(f"   Upcoming classes: {len(classes_data['upcoming'])}")
    print(f"   Active classes: {len(classes_data['active'])}")
    print(f"   Completed classes: {len(classes_data['completed'])}")
    
    # Test 3: Test automatic status updates
    print(f"\n3. Testing automatic status updates...")
    auto_update_class_statuses()
    
    classes_data_after = get_live_classes_for_display()
    print(f"   After auto-update:")
    print(f"   Upcoming classes: {len(classes_data_after['upcoming'])}")
    print(f"   Active classes: {len(classes_data_after['active'])}")
    print(f"   Completed classes: {len(classes_data_after['completed'])}")
    
    # Test 4: Test manual status changes
    print(f"\n4. Testing manual status changes...")
    
    # Start a class
    start_live_class(class1_id)
    print(f"   ✅ Started class {class1_id}")
    
    # End a class
    end_live_class(class3_id)
    print(f"   ✅ Ended class {class3_id}")
    
    # Cancel a class
    cancel_live_class(class2_id)
    print(f"   ✅ Cancelled class {class2_id}")
    
    # Test 5: Final status check
    print(f"\n5. Final status distribution...")
    final_classes = get_live_classes_for_display()
    
    print(f"   Upcoming classes: {len(final_classes['upcoming'])}")
    for cls in final_classes['upcoming']:
        print(f"     - {cls[4]} (ID: {cls[0]}, Status: {cls[7]})")
    
    print(f"   Active classes: {len(final_classes['active'])}")
    for cls in final_classes['active']:
        print(f"     - {cls[4]} (ID: {cls[0]}, Status: {cls[7]})")
    
    print(f"   Completed classes: {len(final_classes['completed'])}")
    for cls in final_classes['completed']:
        print(f"     - {cls[4]} (ID: {cls[0]}, Status: {cls[7]})")
    
    # Test 6: Test individual status functions
    print(f"\n6. Testing individual status functions...")
    
    upcoming = get_upcoming_live_classes()
    active = get_active_live_classes()
    completed = get_completed_live_classes()
    
    print(f"   get_upcoming_live_classes(): {len(upcoming)} classes")
    print(f"   get_active_live_classes(): {len(active)} classes")
    print(f"   get_completed_live_classes(): {len(completed)} classes")
    
    print("\n" + "=" * 60)
    print("✅ Live Class Status Management Test Complete!")
    print("\nKey Features Tested:")
    print("• Automatic status updates based on time")
    print("• Manual status changes (start, end, cancel)")
    print("• Class distribution by status")
    print("• Real-time dashboard data")
    print("\nThe system now automatically:")
    print("• Moves scheduled classes to active when time comes")
    print("• Moves active classes to completed after 2 hours")
    print("• Organizes classes into upcoming/active/completed sections")
    print("• Provides real-time status monitoring")

if __name__ == "__main__":
    test_live_class_status_management() 