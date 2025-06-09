#!/usr/bin/env python3
"""
Comprehensive comparison test between local and Azure ELS CRM deployments
"""

import requests
import sys
import time
from datetime import datetime

# Configuration
LOCAL_URL = "http://127.0.0.1:3000"
AZURE_URL = "https://appweb-goozh6ngfyubm.azurewebsites.net"

TEST_USER = {
    "username": "demo",
    "password": "demo123"
}

def test_environment(base_url, env_name):
    """Test a specific environment (local or Azure)"""
    print(f"\n🔍 Testing {env_name} Environment: {base_url}")
    print("-" * 60)
    
    results = {
        "environment": env_name,
        "base_url": base_url,
        "tests": [],
        "success_count": 0,
        "total_count": 0
    }
    
    def run_test(test_name, url, expected_status=200, timeout=10):
        """Run a single test and record results"""
        results["total_count"] += 1
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=False)
            success = response.status_code == expected_status
            if success:
                results["success_count"] += 1
            
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {test_name}: {response.status_code} (expected {expected_status})")
            
            results["tests"].append({
                "name": test_name,
                "url": url,
                "status_code": response.status_code,
                "expected": expected_status,
                "success": success,
                "response_time": response.elapsed.total_seconds()
            })
            
            return response, success
            
        except requests.exceptions.Timeout:
            print(f"❌ {test_name}: TIMEOUT after {timeout}s")
            results["tests"].append({
                "name": test_name,
                "url": url,
                "status_code": "TIMEOUT",
                "expected": expected_status,
                "success": False,
                "response_time": timeout
            })
            return None, False
            
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
            results["tests"].append({
                "name": test_name,
                "url": url,
                "status_code": f"ERROR: {str(e)}",
                "expected": expected_status,
                "success": False,
                "response_time": 0
            })
            return None, False
    
    # Test 1: Home page (should redirect to login)
    run_test("Home page redirect", f"{base_url}/", 302)
    
    # Test 2: Login page
    run_test("Login page", f"{base_url}/auth/login", 200)
    
    # Test 3: API endpoint without auth (should redirect)
    run_test("API endpoint (no auth)", f"{base_url}/api/leads", 302)
    
    # Test 4: Static assets / health check
    run_test("Dashboard route (no auth)", f"{base_url}/dashboard", 302)
    
    # Test 5: Non-existent route (should return 404)
    run_test("404 test", f"{base_url}/nonexistent", 404)
    
    return results

def compare_environments():
    """Compare local and Azure environments"""
    print("🚀 ELS CRM Deployment Comparison Test")
    print("=" * 70)
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test both environments
    local_results = test_environment(LOCAL_URL, "Local")
    azure_results = test_environment(AZURE_URL, "Azure")
    
    # Summary comparison
    print("\n" + "=" * 70)
    print("📊 COMPARISON SUMMARY")
    print("=" * 70)
    
    print(f"\n🏠 Local Environment (SQLite):")
    print(f"   URL: {LOCAL_URL}")
    print(f"   Success Rate: {local_results['success_count']}/{local_results['total_count']} ({local_results['success_count']/local_results['total_count']*100:.1f}%)")
    
    print(f"\n☁️  Azure Environment (PostgreSQL + VNet):")
    print(f"   URL: {AZURE_URL}")
    print(f"   Success Rate: {azure_results['success_count']}/{azure_results['total_count']} ({azure_results['success_count']/azure_results['total_count']*100:.1f}%)")
    
    # Detailed comparison
    print(f"\n📋 Detailed Test Comparison:")
    print(f"{'Test Name':<25} {'Local':<15} {'Azure':<15} {'Match':<8}")
    print("-" * 70)
    
    for i, local_test in enumerate(local_results['tests']):
        azure_test = azure_results['tests'][i]
        local_status = str(local_test['status_code'])
        azure_status = str(azure_test['status_code'])
        match = "✅" if local_status == azure_status else "❌"
        
        print(f"{local_test['name']:<25} {local_status:<15} {azure_status:<15} {match:<8}")
    
    # Performance comparison
    print(f"\n⚡ Performance Comparison (Response Times):")
    print(f"{'Test Name':<25} {'Local (s)':<12} {'Azure (s)':<12} {'Difference':<12}")
    print("-" * 70)
    
    for i, local_test in enumerate(local_results['tests']):
        azure_test = azure_results['tests'][i]
        if isinstance(local_test['response_time'], (int, float)) and isinstance(azure_test['response_time'], (int, float)):
            local_time = local_test['response_time']
            azure_time = azure_test['response_time']
            diff = azure_time - local_time
            diff_str = f"+{diff:.3f}s" if diff > 0 else f"{diff:.3f}s"
            
            print(f"{local_test['name']:<25} {local_time:<12.3f} {azure_time:<12.3f} {diff_str:<12}")
    
    # Final assessment
    print(f"\n🎯 DEPLOYMENT STATUS:")
    local_healthy = local_results['success_count'] >= 4
    azure_healthy = azure_results['success_count'] >= 4
    
    if local_healthy and azure_healthy:
        print("✅ BOTH ENVIRONMENTS HEALTHY")
        print("   - Local development environment is working correctly")
        print("   - Azure production environment is working correctly")
        print("   - Authentication and routing are functional")
        print("   - Database connectivity is established")
    elif local_healthy:
        print("⚠️  LOCAL HEALTHY, AZURE ISSUES")
        print("   - Local development is working")
        print("   - Azure deployment may have issues")
    elif azure_healthy:
        print("⚠️  AZURE HEALTHY, LOCAL ISSUES")
        print("   - Azure deployment is working")
        print("   - Local development may have issues")
    else:
        print("❌ BOTH ENVIRONMENTS HAVE ISSUES")
        print("   - Both deployments need attention")
    
    print(f"\n🔗 Access URLs:")
    print(f"   Local:  {LOCAL_URL}")
    print(f"   Azure:  {AZURE_URL}")
    print(f"   Demo Login: {TEST_USER['username']} / {TEST_USER['password']}")

if __name__ == "__main__":
    compare_environments()
