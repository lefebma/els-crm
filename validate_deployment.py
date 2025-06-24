#!/usr/bin/env python3
"""
Simple validation script for the deployed ELS CRM application
"""

import requests
from datetime import datetime

BASE_URL = "https://appweb-goozh6ngfyubm.azurewebsites.net"

def test_endpoints():
    """Test various application endpoints"""
    endpoints = [
        ("Home page", "/"),
        ("Login page", "/auth/login"),
        ("Opportunities page", "/opportunities"),
        ("Opportunity form", "/opportunities/add"),
        ("Contacts page", "/contacts"),
        ("Accounts page", "/accounts")
    ]
    
    print(f"🚀 Testing ELS CRM deployment at {BASE_URL}")
    print(f"⏰ Test started at {datetime.now()}")
    print("=" * 60)
    
    success_count = 0
    total_count = len(endpoints)
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
            
            if response.status_code in [200, 302]:  # 302 is redirect (expected for protected pages)
                print(f"✅ {name}: {response.status_code}")
                success_count += 1
                
                # Check for specific content
                if endpoint == "/opportunities/add" and response.status_code == 200:
                    if "amount" in response.text.lower():
                        print("   💰 Amount field detected in opportunity form")
                
                if endpoint == "/opportunities" and response.status_code == 200:
                    if "amount" in response.text.lower() or "revenue" in response.text.lower():
                        print("   💰 Amount/Revenue field detected in opportunities list")
                        
            else:
                print(f"❌ {name}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {name}: Connection error - {e}")
    
    print()
    print("=" * 60)
    print(f"📊 Results: {success_count}/{total_count} endpoints accessible")
    
    if success_count == total_count:
        print("🎉 All endpoints are accessible - deployment successful!")
    elif success_count >= total_count * 0.8:
        print("✅ Most endpoints accessible - deployment mostly successful!")
    else:
        print("⚠️  Some endpoints may have issues")
    
    return success_count >= total_count * 0.8

if __name__ == "__main__":
    test_endpoints()
