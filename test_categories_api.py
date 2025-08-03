#!/usr/bin/env python3

import requests
import json

def test_categories_api():
    """Test the categories API endpoint"""
    
    # Test URL (assuming server runs on localhost:10000)
    base_url = "http://localhost:10000"
    
    # Test different class IDs
    class_ids = [1, 2, 4, 5, 6, 7]
    
    print("🧪 Testing Categories API Endpoint")
    print("=" * 50)
    
    for class_id in class_ids:
        try:
            url = f"{base_url}/api/categories/{class_id}"
            print(f"\n📚 Testing Class ID: {class_id}")
            print(f"🔗 URL: {url}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Status: {response.status_code}")
                print(f"📊 Response: {json.dumps(data, indent=2)}")
                
                if data.get('success') and data.get('categories'):
                    print(f"📋 Found {len(data['categories'])} categories")
                    for cat in data['categories']:
                        print(f"   • {cat['name']} ({cat['paid_status']})")
                else:
                    print("📭 No categories found for this class")
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: Server not running on {base_url}")
            print("💡 Start the server with: python3 app.py")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Complete!")

if __name__ == "__main__":
    test_categories_api() 