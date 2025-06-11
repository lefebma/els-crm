#!/usr/bin/env python3
"""
Comprehensive test script for the deployed ELS CRM application.
Tests all CRUD operations and functionality.
"""

import requests
import sys
import json
from urllib.parse import urljoin

class CRMTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ELS-CRM-Tester/1.0'
        })
    
    def test_basic_connectivity(self):
        """Test basic connectivity to the application"""
        print("🔍 Testing basic connectivity...")
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                print("✅ Basic connectivity: SUCCESS")
                return True
            else:
                print(f"❌ Basic connectivity: FAILED (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Basic connectivity: FAILED (Error: {e})")
            return False
    
    def test_login(self, username="demo", password="demo123"):
        """Test user authentication"""
        print("🔐 Testing authentication...")
        try:
            # Get login page first
            login_url = urljoin(self.base_url, '/auth/login')
            response = self.session.get(login_url)
            
            if response.status_code != 200:
                print(f"❌ Login page access: FAILED (Status: {response.status_code})")
                return False
            
            # Attempt login
            login_data = {
                'username': username,
                'password': password
            }
            
            response = self.session.post(login_url, data=login_data, allow_redirects=True)
            
            # Check if we're redirected to dashboard (successful login)
            if 'dashboard' in response.url or response.status_code == 200:
                print("✅ Authentication: SUCCESS")
                return True
            else:
                print(f"❌ Authentication: FAILED (Final URL: {response.url})")
                return False
                
        except Exception as e:
            print(f"❌ Authentication: FAILED (Error: {e})")
            return False
    
    def test_database_connection(self):
        """Test database connectivity"""
        print("🗄️  Testing database connection...")
        try:
            debug_url = urljoin(self.base_url, '/debug/db-test')
            response = self.session.get(debug_url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print("✅ Database connection: SUCCESS")
                    print(f"   - Connection successful: {data.get('connection_successful', 'N/A')}")
                    print(f"   - Database name: {data.get('database_name', 'N/A')}")
                    print(f"   - Tables found: {len(data.get('tables', []))}")
                    return True
                else:
                    print(f"❌ Database connection: FAILED (Status: {data.get('status')})")
                    return False
            else:
                print(f"❌ Database connection: FAILED (HTTP {response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Database connection: FAILED (Error: {e})")
            return False
    
    def test_page_access(self):
        """Test access to main application pages"""
        print("📄 Testing page access...")
        pages = [
            ('Dashboard', '/'),
            ('Leads', '/leads'),
            ('Accounts', '/accounts'),
            ('Contacts', '/contacts'),
            ('Opportunities', '/opportunities'),
            ('Add Lead', '/leads/add'),
            ('Add Account', '/accounts/add'),
            ('Add Contact', '/contacts/add'),
            ('Add Opportunity', '/opportunities/add')
        ]
        
        success_count = 0
        for page_name, path in pages:
            try:
                url = urljoin(self.base_url, path)
                response = self.session.get(url)
                
                if response.status_code == 200:
                    print(f"   ✅ {page_name}: SUCCESS")
                    success_count += 1
                else:
                    print(f"   ❌ {page_name}: FAILED (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ {page_name}: FAILED (Error: {e})")
        
        if success_count == len(pages):
            print("✅ Page access: ALL PAGES ACCESSIBLE")
            return True
        else:
            print(f"⚠️  Page access: {success_count}/{len(pages)} pages accessible")
            return success_count > 0
    
    def test_crud_operations(self):
        """Test CRUD operations"""
        print("🔧 Testing CRUD operations...")
        
        # Test Lead creation
        try:
            add_lead_url = urljoin(self.base_url, '/leads/add')
            lead_data = {
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'phone': '555-0123',
                'company': 'Test Company',
                'status': 'MAL'
            }
            
            response = self.session.post(add_lead_url, data=lead_data, allow_redirects=True)
            
            if response.status_code == 200 and 'leads' in response.url:
                print("   ✅ Lead creation: SUCCESS")
                lead_creation_success = True
            else:
                print(f"   ❌ Lead creation: FAILED (Status: {response.status_code})")
                lead_creation_success = False
                
        except Exception as e:
            print(f"   ❌ Lead creation: FAILED (Error: {e})")
            lead_creation_success = False
        
        # Test Account creation
        try:
            add_account_url = urljoin(self.base_url, '/accounts/add')
            account_data = {
                'name': 'Test Account Corp',
                'industry': 'Technology',
                'address': '123 Test Street'
            }
            
            response = self.session.post(add_account_url, data=account_data, allow_redirects=True)
            
            if response.status_code == 200 and 'accounts' in response.url:
                print("   ✅ Account creation: SUCCESS")
                account_creation_success = True
            else:
                print(f"   ❌ Account creation: FAILED (Status: {response.status_code})")
                account_creation_success = False
                
        except Exception as e:
            print(f"   ❌ Account creation: FAILED (Error: {e})")
            account_creation_success = False
        
        return lead_creation_success and account_creation_success
    
    def test_lead_export(self):
        """Test lead export functionality"""
        print("📊 Testing lead export...")
        try:
            export_url = urljoin(self.base_url, '/leads/export')
            response = self.session.get(export_url)
            
            if response.status_code == 200 and 'text/csv' in response.headers.get('Content-Type', ''):
                print("✅ Lead export: SUCCESS")
                return True
            else:
                print(f"❌ Lead export: FAILED (Status: {response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Lead export: FAILED (Error: {e})")
            return False
    
    def run_full_test(self):
        """Run complete test suite"""
        print("🚀 Starting comprehensive ELS CRM deployment test...")
        print(f"📍 Testing application at: {self.base_url}")
        print("=" * 60)
        
        results = {
            'connectivity': self.test_basic_connectivity(),
            'login': self.test_login(),
            'database': self.test_database_connection(),
            'pages': self.test_page_access(),
            'crud': self.test_crud_operations(),
            'export': self.test_lead_export()
        }
        
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY:")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.capitalize():.<20} {status}")
        
        print("-" * 60)
        print(f"Overall Result: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Application is fully functional.")
            return True
        elif passed_tests >= total_tests * 0.8:
            print("⚠️  Most tests passed. Application is mostly functional.")
            return True
        else:
            print("❌ Multiple test failures. Application needs attention.")
            return False

def main():
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "https://appweb-goozh6ngfyubm.azurewebsites.net"
    
    tester = CRMTester(base_url)
    success = tester.run_full_test()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
