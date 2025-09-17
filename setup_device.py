#!/usr/bin/env python3
"""
Device Setup Script for Smart Water Meter System

This script helps set up IoT devices in the Django database and generates API keys.
Run this script to prepare devices for IoT communication.
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append('/home/vincent/Desktop/smartwatermeter')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_water_meter.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from water_meter.models import Device
import secrets
import string

def generate_api_key():
    """Generate a secure API key for device authentication"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def setup_device(device_id, name, location, owner_username='admin'):
    """Set up a new IoT device in the database"""
    
    try:
        # Get the owner user
        owner = User.objects.get(username=owner_username)
        
        # Check if device already exists
        device, created = Device.objects.get_or_create(
            device_id=device_id,
            defaults={
                'name': name,
                'location': location,
                'owner': owner,
                'is_active': True,
                'api_key': generate_api_key(),
                'pulse_rate': 450.0  # YF-S201 default
            }
        )
        
        if created:
            print(f"✅ Device created successfully!")
        else:
            print(f"ℹ️  Device already exists, updating details...")
            device.name = name
            device.location = location
            device.is_active = True
            if not device.api_key:
                device.api_key = generate_api_key()
            device.save()
        
        print(f"📱 Device ID: {device.device_id}")
        print(f"📍 Name: {device.name}")
        print(f"🏠 Location: {device.location}")
        print(f"👤 Owner: {device.owner.username}")
        print(f"🔑 API Key: {device.api_key}")
        print(f"⚡ Status: {'Active' if device.is_active else 'Inactive'}")
        
        return device
        
    except User.DoesNotExist:
        print(f"❌ Error: User '{owner_username}' not found")
        print("   Please create a user first or use existing username")
        return None
    except Exception as e:
        print(f"❌ Error setting up device: {str(e)}")
        return None

def list_devices():
    """List all devices in the system"""
    devices = Device.objects.all().select_related('owner')
    
    if not devices:
        print("📱 No devices found in the system")
        return
    
    print(f"📱 Found {devices.count()} device(s):")
    print("-" * 80)
    
    for device in devices:
        status = "🟢 Active" if device.is_active else "🔴 Inactive"
        last_seen = device.last_seen.strftime("%Y-%m-%d %H:%M:%S") if device.last_seen else "Never"
        
        print(f"ID: {device.device_id}")
        print(f"Name: {device.name}")
        print(f"Location: {device.location}")
        print(f"Owner: {device.owner.username}")
        print(f"Status: {status}")
        print(f"Last Seen: {last_seen}")
        print(f"API Key: {device.api_key}")
        print("-" * 40)

def update_arduino_config(device):
    """Generate Arduino configuration snippet"""
    if not device:
        return
    
    print("\n🔧 Arduino Configuration:")
    print("Copy these lines to your Arduino code:")
    print("-" * 40)
    print(f'const char* deviceID = "{device.device_id}";')
    print(f'const char* apiKey = "{device.api_key}";')
    print('const char* serverURL = "http://YOUR_SERVER_IP:8000/api/data/";')
    print("-" * 40)
    print("⚠️  Don't forget to update YOUR_SERVER_IP with your actual server IP!")

def main():
    print("🚀 Smart Water Meter Device Setup")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Set up new device")
        print("2. List all devices")
        print("3. Generate Arduino config for device")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\n📱 Setting up new device...")
            device_id = input("Device ID (e.g., DEVICE_001): ").strip()
            name = input("Device Name (e.g., Kitchen Water Meter): ").strip()
            location = input("Location (e.g., Kitchen): ").strip()
            owner = input("Owner username (default: admin): ").strip() or 'admin'
            
            if device_id and name and location:
                device = setup_device(device_id, name, location, owner)
                if device:
                    update_arduino_config(device)
            else:
                print("❌ Please provide all required information")
        
        elif choice == '2':
            print("\n📱 Listing all devices...")
            list_devices()
        
        elif choice == '3':
            device_id = input("Enter Device ID: ").strip()
            try:
                device = Device.objects.get(device_id=device_id)
                update_arduino_config(device)
            except Device.DoesNotExist:
                print(f"❌ Device '{device_id}' not found")
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
