#!/usr/bin/env python3
"""
IoT Connection Test Script for Smart Water Meter System

This script simulates an IoT device sending water usage data to test
the API endpoint and database persistence.
"""

import requests
import json
import time
import random
from datetime import datetime, timezone

# Configuration
SERVER_URL = "http://127.0.0.1:8000/api/data/"
DEVICE_ID = "DEVICE_001"
API_KEY = "your-device-api-key-here"  # Replace with actual API key

def test_iot_connection():
    """Test IoT device connection and data submission"""
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        'User-Agent': 'IoT-Test-Script/1.0'
    }
    
    # Generate sample water usage data
    test_data = {
        'device_id': DEVICE_ID,
        'flow_rate': round(random.uniform(0.5, 5.0), 2),  # 0.5-5.0 L/min
        'total_consumption': round(random.uniform(100, 1000), 2),  # 100-1000 L total
        'pulse_count': random.randint(1000, 10000),
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    print("🔄 Testing IoT Connection...")
    print(f"📡 Server URL: {SERVER_URL}")
    print(f"🔑 Device ID: {DEVICE_ID}")
    print(f"📊 Test Data: {json.dumps(test_data, indent=2)}")
    print("-" * 50)
    
    try:
        # Send POST request
        response = requests.post(
            SERVER_URL,
            headers=headers,
            json=test_data,
            timeout=10
        )
        
        print(f"📡 HTTP Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201]:
            print("✅ SUCCESS: Data sent and saved to database!")
            try:
                response_data = response.json()
                print(f"📋 Response Data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📋 Response Text: {response.text}")
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"📋 Response: {response.text}")
            
            # Common error diagnostics
            if response.status_code == 401:
                print("🔧 Fix: Check your API key in Django admin")
            elif response.status_code == 404:
                print("🔧 Fix: Verify server URL and ensure Django is running")
            elif response.status_code == 400:
                print("🔧 Fix: Check data format and device registration")
                
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Cannot reach server")
        print("🔧 Fix: Ensure Django server is running on http://127.0.0.1:8000")
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT ERROR: Server took too long to respond")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")

def test_multiple_readings():
    """Send multiple readings to test continuous data flow"""
    print("\n🔄 Testing Multiple Readings...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
        'User-Agent': 'IoT-Test-Script/1.0'
    }
    
    success_count = 0
    total_consumption = 150.0  # Starting value
    
    for i in range(5):
        # Simulate realistic water usage progression
        flow_rate = round(random.uniform(0.1, 3.0), 2)
        total_consumption += round(flow_rate / 6, 2)  # Add consumption (10-second intervals)
        
        test_data = {
            'device_id': DEVICE_ID,
            'flow_rate': flow_rate,
            'total_consumption': round(total_consumption, 2),
            'pulse_count': int(total_consumption * 450),  # YF-S201 pulse rate
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            response = requests.post(SERVER_URL, headers=headers, json=test_data, timeout=5)
            if response.status_code in [200, 201]:
                success_count += 1
                print(f"✅ Reading {i+1}/5: Flow={flow_rate}L/min, Total={total_consumption}L")
            else:
                print(f"❌ Reading {i+1}/5: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Reading {i+1}/5: {str(e)}")
        
        time.sleep(1)  # Wait 1 second between readings
    
    print(f"\n📊 Results: {success_count}/5 readings successful")
    if success_count == 5:
        print("🎉 All readings sent successfully! IoT integration is working.")
    else:
        print("⚠️  Some readings failed. Check server logs for details.")

def check_server_status():
    """Check if Django server is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Django server is running")
            return True
        else:
            print(f"⚠️  Django server responded with status {response.status_code}")
            return False
    except:
        print("❌ Django server is not accessible")
        return False

if __name__ == "__main__":
    print("🚀 Smart Water Meter IoT Connection Test")
    print("=" * 50)
    
    # Check server status first
    if not check_server_status():
        print("\n🔧 Please start the Django server:")
        print("   cd /home/vincent/Desktop/smartwatermeter")
        print("   source venv/bin/activate")
        print("   python manage.py runserver")
        exit(1)
    
    # Run tests
    test_iot_connection()
    test_multiple_readings()
    
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Check Django admin for new water usage records")
    print("2. Verify data appears in dashboard")
    print("3. Update Arduino code with correct API key")
    print("4. Test with real hardware")
