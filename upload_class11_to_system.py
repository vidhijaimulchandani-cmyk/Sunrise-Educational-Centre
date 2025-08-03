#!/usr/bin/env python3
"""
Upload Class 11 Applied Mathematics resources to bulk upload system
"""

import requests
import json
import os
from datetime import datetime

def upload_to_bulk_system():
    """Upload resources to the bulk upload system"""
    
    # Load resources
    with open('class11_resources_bulk_upload.json', 'r') as f:
        data = json.load(f)
    
    print(f"🚀 Uploading {data['total_resources']} Class 11 Applied Mathematics resources...")
    
    # Upload each resource
    for i, resource in enumerate(data['resources'], 1):
        print(f"\n📤 Uploading {i}/{data['total_resources']}: {resource['description']}")
        
        # Prepare upload data
        upload_data = {
            'file_name': resource['file_name'],
            'category': resource['category'],
            'description': resource['description'],
            'file_path': resource['file_path'],
            'class': resource['class'],
            'type': resource['type'],
            'upload_date': datetime.now().isoformat()
        }
        
        # Here you would integrate with your bulk upload API
        # For now, we'll just print the data
        print(f"   ✅ Prepared: {resource['description']} ({resource['category']})")
    
    print("\n✅ Upload preparation completed!")
    print("\n📋 Next steps:")
    print("   1. Use the Excel file in your bulk upload interface")
    print("   2. Or use the JSON data with your bulk upload API")
    print("   3. Verify all resources are properly categorized")

if __name__ == "__main__":
    upload_to_bulk_system()
