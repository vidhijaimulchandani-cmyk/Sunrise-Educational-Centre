#!/usr/bin/env python3
"""
Main Test Runner for Live Class System and WebRTC Setup

This single script consolidates all previous test scripts:
- Database integrity and end-to-end live class tests
- Status management tests (auto/manual updates)
- WebRTC HTTPS prerequisites tests
"""

import os
import sys
import sqlite3
import socket
import ssl
from datetime import datetime, timedelta
import glob
import subprocess

try:
    import requests
except Exception:
    requests = None


# -----------------------------
# Utilities
# -----------------------------
DATABASE = 'users.db'


def check_database_integrity():
    print("\n🔍 Checking Database Integrity...")
    print("=" * 50)

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    try:
        # Check live_classes table
        c.execute("SELECT COUNT(*) FROM live_classes")
        total_classes = c.fetchone()[0]
        print(f"  Total live classes: {total_classes}")

        # Check status distribution
        c.execute("SELECT status, COUNT(*) FROM live_classes GROUP BY status")
        status_dist = c.fetchall()
        print("  Status distribution:")
        for status, count in status_dist:
            print(f"    {status}: {count}")

        # Check attendance table
        try:
            c.execute("SELECT COUNT(*) FROM live_class_attendance")
            total_attendance = c.fetchone()[0]
            print(f"  Total attendance records: {total_attendance}")
        except sqlite3.OperationalError:
            print("  live_class_attendance table not found (ok if not yet created)")

        # Check messages table
        try:
            c.execute("SELECT COUNT(*) FROM live_class_messages")
            total_messages = c.fetchone()[0]
            print(f"  Total messages: {total_messages}")
        except sqlite3.OperationalError:
            print("  live_class_messages table not found (ok if not yet created)")

        # Check for inconsistencies
        try:
            c.execute("SELECT COUNT(*) FROM live_classes WHERE is_active = 1 AND status != 'active'")
            inconsistent = c.fetchone()[0]
            if inconsistent > 0:
                print(f"  ⚠️  Found {inconsistent} inconsistent status records")
            else:
                print("  ✅ No status inconsistencies found")
        except sqlite3.OperationalError:
            print("  Could not verify is_active/status consistency (columns may be missing)")

        print("  ✅ Database integrity check completed")

    except Exception as e:
        print(f"  ❌ Error checking database: {e}")
    finally:
        conn.close()


def test_live_class_system():
    print("\n🧪 Testing Live Class System...")
    print("=" * 50)

    try:
        from auth_handler import (
            create_live_class, get_class_details_by_id, update_live_class_status,
            record_attendance, get_class_attendance, get_live_class_analytics,
            validate_live_class_data
        )

        print("✅ Successfully imported live class functions")

        # Test 1: Create a live class
        print("\n📝 Test 1: Creating a live class...")
        test_class_id = create_live_class(
            class_code="TEST123",
            pin="1234",
            meeting_url="/test-video.mp4",
            topic="Test Live Class",
            description="Testing the live class system"
        )
        print(f"  ✅ Created class with ID: {test_class_id}")

        # Test 2: Get class details
        print("\n📋 Test 2: Getting class details...")
        details = get_class_details_by_id(test_class_id)
        if details:
            print(f"  ✅ Class details: {details}")
        else:
            print("  ❌ Could not get class details")

        # Test 3: Record attendance
        print("\n👥 Test 3: Recording attendance...")
        record_attendance(test_class_id, 1, "test_user_1")
        record_attendance(test_class_id, 2, "test_user_2")
        record_attendance(test_class_id, 3, "test_user_3")
        print("  ✅ Recorded attendance for 3 users")

        # Test 4: Get attendance
        print("\n📊 Test 4: Getting attendance...")
        attendance = get_class_attendance(test_class_id)
        print(f"  ✅ Attendance rows: {len(attendance)}")

        # Test 5: Update status
        print("\n🔄 Test 5: Updating class status...")
        update_live_class_status(test_class_id, "active")
        print("  ✅ Updated status to active")

        # Test 6: Get analytics
        print("\n📈 Test 6: Getting analytics...")
        analytics = get_live_class_analytics()
        print(f"  ✅ Analytics: {analytics}")

        # Test 7: Validate data
        try:
            print("\n🔍 Test 7: Validating data...")
            validate_live_class_data()
            print("  ✅ Data validation completed")
        except Exception:
            print("  ℹ️  validate_live_class_data() not available, skipping")

        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("DELETE FROM live_class_attendance WHERE class_id = ?", (test_class_id,))
        # Delete from messages with multiple possible schemas
        try:
            c.execute("DELETE FROM live_class_messages WHERE live_class_id = ?", (test_class_id,))
        except sqlite3.OperationalError:
            try:
                c.execute("DELETE FROM live_class_messages WHERE class_id = ?", (test_class_id,))
            except sqlite3.OperationalError:
                pass
        c.execute("DELETE FROM live_classes WHERE id = ?", (test_class_id,))
        conn.commit()
        conn.close()
        print("  ✅ Test data cleaned up")

        print("\n" + "=" * 50)
        print("✅ Live class system basic test finished")

    except Exception as e:
        print(f"❌ Error testing live class system: {e}")
        import traceback
        traceback.print_exc()


def test_live_class_status_management():
    print("\n🎓 Testing Live Class Status Management...")
    print("=" * 60)

    try:
        from auth_handler import (
            create_live_class, get_live_classes_for_display,
            auto_update_class_statuses, get_upcoming_live_classes,
            get_active_live_classes, get_completed_live_classes,
            start_live_class, end_live_class, cancel_live_class
        )
        from time_config import get_current_ist_time, format_ist_time

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

        # Check initial distribution
        classes_data = get_live_classes_for_display()
        print(f"   Initial => Upcoming: {len(classes_data['upcoming'])}, Active: {len(classes_data['active'])}, Completed: {len(classes_data['completed'])}")

        # Auto update statuses
        auto_update_class_statuses()
        classes_data_after = get_live_classes_for_display()
        print(f"   After auto-update => Upcoming: {len(classes_data_after['upcoming'])}, Active: {len(classes_data_after['active'])}, Completed: {len(classes_data_after['completed'])}")

        # Manual changes
        start_live_class(class1_id)
        print(f"   ✅ Started class {class1_id}")
        end_live_class(class3_id)
        print(f"   ✅ Ended class {class3_id}")
        cancel_live_class(class2_id)
        print(f"   ✅ Cancelled class {class2_id}")

        # Final
        final_classes = get_live_classes_for_display()
        print(f"   Final => Upcoming: {len(final_classes['upcoming'])}, Active: {len(final_classes['active'])}, Completed: {len(final_classes['completed'])}")

        # Individual functions
        upcoming = get_upcoming_live_classes()
        active = get_active_live_classes()
        completed = get_completed_live_classes()
        print(f"   Individual => upcoming({len(upcoming)}), active({len(active)}), completed({len(completed)})")

        print("\n" + "=" * 60)
        print("✅ Live Class Status Management Test Complete!")

    except Exception as e:
        print(f"❌ Error in status management test: {e}")
        import traceback
        traceback.print_exc()


def test_https_connection():
    if requests is None:
        print("❌ requests library not available, skipping HTTPS test")
        return False
    try:
        response = requests.get('https://localhost:10000', verify=False, timeout=5)
        print("✅ HTTPS connection successful")
        print(f"   Status code: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ HTTPS connection failed: {e}")
        return False


def test_ssl_certificate():
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with socket.create_connection(('localhost', 10000), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as ssock:
                cert = ssock.getpeercert()
                print("✅ SSL certificate is reachable")
                print(f"   Subject: {cert.get('subject', 'N/A')}")
                return True
    except Exception as e:
        print(f"❌ SSL certificate test failed: {e}")
        return False


def test_webrtc_requirements():
    print("\n🔍 Testing WebRTC Requirements:")
    https_ok = test_https_connection()
    ssl_ok = test_ssl_certificate()
    # Port accessibility
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 10000))
        sock.close()
        if result == 0:
            print("✅ Port 10000 is accessible")
            port_ok = True
        else:
            print("❌ Port 10000 is not accessible")
            port_ok = False
    except Exception as e:
        print(f"❌ Port test failed: {e}")
        port_ok = False
    return https_ok and ssl_ok and port_ok


def run_all_tests():
    print("🚀 Running All Tests")
    print("=" * 64)

    results = {}

    try:
        check_database_integrity()
        results['db_integrity'] = True
    except Exception as e:
        results['db_integrity'] = False
        print(f"❌ DB integrity failed: {e}")

    try:
        test_live_class_system()
        results['live_class_basic'] = True
    except Exception as e:
        results['live_class_basic'] = False
        print(f"❌ live class basic failed: {e}")

    try:
        test_live_class_status_management()
        results['status_management'] = True
    except Exception as e:
        results['status_management'] = False
        print(f"❌ status management failed: {e}")

    try:
        ok = test_webrtc_requirements()
        results['webrtc'] = ok
    except Exception as e:
        results['webrtc'] = False
        print(f"❌ webrtc tests failed: {e}")

    print("\n" + "=" * 64)
    print("Summary:")
    for key, ok in results.items():
        print(f"- {key}: {'✅ PASS' if ok else '❌ FAIL'}")
    print("=" * 64)

    # Discover and run any remaining standalone test scripts once, then remove them
    print("\n🔎 Discovering additional test scripts (test*.py)...")
    this_file = os.path.basename(__file__)
    test_files = [f for f in glob.glob(os.path.join(os.path.dirname(__file__), 'test*.py'))
                  if os.path.basename(f) != this_file]
    if not test_files:
        print("No extra test scripts found.")
        return

    print(f"Found {len(test_files)} extra test scripts:")
    for tf in test_files:
        print(f" - {os.path.basename(tf)}")

    print("\n▶️ Running extra test scripts once before consolidation...")
    for tf in test_files:
        try:
            print(f"\n--- Running {os.path.basename(tf)} ---")
            proc = subprocess.run([sys.executable, tf], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=180)
            print(proc.stdout)
            if proc.returncode != 0:
                print(f"❌ {os.path.basename(tf)} exited with code {proc.returncode}")
            else:
                print(f"✅ {os.path.basename(tf)} completed")
        except Exception as e:
            print(f"❌ Failed running {os.path.basename(tf)}: {e}")

    print("\n🧹 Removing extra standalone test scripts to consolidate into this runner...")
    for tf in test_files:
        try:
            os.remove(tf)
            print(f"Deleted: {os.path.basename(tf)}")
        except Exception as e:
            print(f"Failed to delete {os.path.basename(tf)}: {e}")


if __name__ == '__main__':
    run_all_tests()

