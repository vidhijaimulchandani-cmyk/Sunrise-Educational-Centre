#!/usr/bin/env python3
"""
Test Google OAuth Configuration
This script tests if the Google OAuth credentials are properly configured.
"""

import os

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ python-dotenv loaded successfully")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables")

def test_google_config():
    print("🔍 Testing Google OAuth Configuration...")
    print()
    
    # Check if environment variables are set
    client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    
    print(f"GOOGLE_CLIENT_ID: {'✅ Set' if client_id else '❌ Not set'}")
    if client_id:
        if client_id == 'your_google_client_id_here':
            print("   ⚠️  Still using placeholder value")
        else:
            print(f"   ✅ Value: {client_id[:20]}...")
    
    print(f"GOOGLE_CLIENT_SECRET: {'✅ Set' if client_secret else '❌ Not set'}")
    if client_secret:
        if client_secret == 'your_google_client_secret_here':
            print("   ⚠️  Still using placeholder value")
        else:
            print(f"   ✅ Value: {client_secret[:20]}...")
    
    print()
    
    # Test Flask app configuration
    try:
        from app import app
        flask_client_id = app.config.get('GOOGLE_CLIENT_ID', '')
        print(f"Flask App GOOGLE_CLIENT_ID: {'✅ Set' if flask_client_id else '❌ Not set'}")
        
        if flask_client_id:
            print("✅ Google Sign-In should work in the web application")
        else:
            print("❌ Google Sign-In will show configuration error")
            
    except Exception as e:
        print(f"❌ Error testing Flask app: {e}")
    
    print()
    print("📋 Summary:")
    if client_id and client_id != 'your_google_client_id_here':
        print("✅ Google OAuth is properly configured!")
        print("   You can now use Google Sign-In in your application.")
    else:
        print("❌ Google OAuth is not configured.")
        print("   Please run: python3 setup_google_oauth.py")
        print("   Then update the .env file with your actual credentials.")

if __name__ == "__main__":
    test_google_config()