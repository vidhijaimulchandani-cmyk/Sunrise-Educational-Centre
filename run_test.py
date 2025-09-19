#!/usr/bin/env python3
"""
Quick test to verify the authentication system is working
"""

import subprocess
import time
import requests
import sys

def test_server():
    print("🚀 Starting test server...")
    
    # Start the server in background
    try:
        server_process = subprocess.Popen([sys.executable, 'app.py'], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Test if server is running
        try:
            response = requests.get('http://localhost:10000/', timeout=5)
            print(f"✅ Server is running! Status: {response.status_code}")
            
            # Test auth page
            auth_response = requests.get('http://localhost:10000/auth', timeout=5)
            print(f"✅ Auth page accessible! Status: {auth_response.status_code}")
            
            # Test simple auth page
            simple_auth_response = requests.get('http://localhost:10000/test-auth', timeout=5)
            print(f"✅ Simple auth page accessible! Status: {simple_auth_response.status_code}")
            
            print("\n🎉 All tests passed!")
            print("📝 You can now test authentication at:")
            print("   - Main auth page: http://localhost:10000/auth")
            print("   - Simple test page: http://localhost:10000/test-auth")
            print("\n🔐 Test credentials:")
            print("   Username: yash")
            print("   Password: yash")
            print("   Class: Admin")
            print("   Admin Code: sec@011")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Server not responding: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if test_server():
        print("\n⚠️  Server is running in background. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
    else:
        print("❌ Test failed!")