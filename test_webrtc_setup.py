#!/usr/bin/env python3
"""
Test script to verify WebRTC setup with HTTPS
"""

import requests
import ssl
import socket
from urllib.parse import urlparse

def test_https_connection():
    """Test HTTPS connection to the server"""
    try:
        # Test HTTPS connection
        response = requests.get('https://localhost:10000', verify=False, timeout=5)
        print("✅ HTTPS connection successful")
        print(f"   Status code: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTPS connection failed: {e}")
        return False

def test_ssl_certificate():
    """Test SSL certificate"""
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection(('localhost', 10000)) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as ssock:
                cert = ssock.getpeercert()
                print("✅ SSL certificate is valid")
                print(f"   Subject: {cert.get('subject', 'N/A')}")
                return True
    except Exception as e:
        print(f"❌ SSL certificate test failed: {e}")
        return False

def test_webrtc_requirements():
    """Test WebRTC requirements"""
    print("\n🔍 Testing WebRTC Requirements:")
    
    # Test 1: HTTPS
    https_ok = test_https_connection()
    
    # Test 2: SSL Certificate
    ssl_ok = test_ssl_certificate()
    
    # Test 3: Port accessibility
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

def main():
    print("🚀 WebRTC Setup Test")
    print("=" * 50)
    
    webrtc_ready = test_webrtc_requirements()
    
    print("\n" + "=" * 50)
    if webrtc_ready:
        print("🎉 WebRTC is ready!")
        print("\n📋 Next steps:")
        print("1. Open https://localhost:10000 in your browser")
        print("2. Accept the security warning (click 'Advanced' -> 'Proceed to localhost')")
        print("3. Login to your account")
        print("4. Navigate to Live Class section")
        print("5. Allow camera/microphone permissions when prompted")
        print("\n⚠️  Important: Always use https:// (not http://) for WebRTC features")
    else:
        print("❌ WebRTC setup needs attention")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure the server is running with FLASK_ENV=development")
        print("2. Check that SSL certificates exist (cert.pem, key.pem)")
        print("3. Ensure port 10000 is not blocked by firewall")
        print("4. Try restarting the server")

if __name__ == "__main__":
    main() 