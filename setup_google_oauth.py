#!/usr/bin/env python3
"""
Google OAuth Setup Helper Script
This script helps you set up Google OAuth credentials for the Sunrise Education Centre application.
"""

import os
import webbrowser
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🌅 Sunrise Education Centre - Google OAuth Setup")
    print("=" * 60)
    print()

def print_steps():
    print("📋 Follow these steps to set up Google OAuth:")
    print()
    print("1. 🌐 Go to Google Cloud Console")
    print("   URL: https://console.cloud.google.com/")
    print()
    print("2. 📁 Create a new project or select existing one")
    print("   - Click on the project dropdown at the top")
    print("   - Click 'New Project' or select existing")
    print()
    print("3. 🔧 Enable APIs")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for and enable:")
    print("     • Google+ API")
    print("     • Google OAuth2 API")
    print()
    print("4. 🔑 Create OAuth 2.0 Credentials")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   - Choose 'Web application' as application type")
    print()
    print("5. 🌍 Configure Authorized Origins")
    print("   - Add your domain: https://sunrise-educational-centre.onrender.com")
    print("   - For local development, also add: http://localhost:10000")
    print()
    print("6. 📋 Copy the Client ID and Client Secret")
    print("   - Save both values securely")
    print()

def check_env_file():
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file found!")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'your_google_client_id_here' in content:
                print("⚠️  Please update the .env file with your actual Google credentials")
                return False
            else:
                print("✅ .env file appears to be configured")
                return True
    else:
        print("❌ .env file not found")
        return False

def create_env_template():
    env_content = """# Google OAuth Configuration
# Replace these with your actual Google OAuth credentials
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Other environment variables
PORT=10000
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Created .env template file")

def open_google_console():
    print("🌐 Opening Google Cloud Console...")
    webbrowser.open('https://console.cloud.google.com/')
    print("   (If browser didn't open, manually visit: https://console.cloud.google.com/)")

def main():
    print_banner()
    
    # Check if .env file exists and is configured
    env_configured = check_env_file()
    
    if not env_configured:
        print("📝 Creating .env template file...")
        create_env_template()
        print()
    
    print_steps()
    
    # Ask if user wants to open Google Console
    response = input("🌐 Would you like to open Google Cloud Console now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        open_google_console()
    
    print()
    print("🎯 Next steps:")
    print("1. Complete the Google Cloud Console setup")
    print("2. Update the .env file with your actual credentials")
    print("3. Restart your application")
    print()
    print("💡 For Render.com deployment:")
    print("   - Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET as environment variables")
    print("   - In your Render dashboard: Environment > Add Environment Variable")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()