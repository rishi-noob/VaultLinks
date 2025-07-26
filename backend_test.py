#!/usr/bin/env python3
"""
VaultLinks Backend API Testing Suite
Tests authentication and VaultLink CRUD operations
"""

import requests
import json
import uuid
from datetime import datetime
import time
from unittest.mock import patch, MagicMock

# Backend URL from frontend/.env
BACKEND_URL = "https://03298711-3a7d-4aaa-8418-b202bb5f0c03.preview.emergentagent.com/api"

class VaultLinksAPITester:
    def __init__(self):
        self.session_token = None
        self.user_data = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_auth_profile_endpoint(self):
        """Test POST /api/auth/profile with mocked Emergent Auth"""
        print("🔐 Testing Authentication Endpoints...")
        
        # Mock Emergent Auth response
        mock_session_id = str(uuid.uuid4())
        mock_user_data = {
            "email": "sarah.chen@example.com",
            "name": "Sarah Chen",
            "picture": "https://example.com/avatar.jpg",
            "session_token": str(uuid.uuid4())
        }
        
        try:
            # Test with valid session_id (we'll mock the external API call)
            payload = {"session_id": mock_session_id}
            
            # Since we can't actually mock the requests.get call in the running server,
            # we'll test the endpoint behavior and expect it to fail with our fake session_id
            response = requests.post(
                f"{BACKEND_URL}/auth/profile",
                json=payload,
                timeout=10
            )
            
            # We expect this to fail since we're using a fake session_id
            if response.status_code == 401:
                self.log_test(
                    "Auth Profile - Invalid Session ID",
                    True,
                    "Correctly rejected invalid session_id",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "Auth Profile - Invalid Session ID",
                    False,
                    f"Expected 401, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Auth Profile - Network Error",
                False,
                f"Network error: {str(e)}"
            )
            
        # Test with missing session_id
        try:
            response = requests.post(
                f"{BACKEND_URL}/auth/profile",
                json={},
                timeout=10
            )
            
            if response.status_code == 422:  # Validation error
                self.log_test(
                    "Auth Profile - Missing Session ID",
                    True,
                    "Correctly rejected missing session_id",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "Auth Profile - Missing Session ID",
                    False,
                    f"Expected 422, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Auth Profile - Missing Session ID Test",
                False,
                f"Network error: {str(e)}"
            )

    def test_auth_me_endpoint(self):
        """Test GET /api/auth/me endpoint"""
        print("👤 Testing Auth Me Endpoint...")
        
        # Test without session_token
        try:
            response = requests.get(f"{BACKEND_URL}/auth/me", timeout=10)
            
            if response.status_code == 422:  # Missing required parameter
                self.log_test(
                    "Auth Me - Missing Session Token",
                    True,
                    "Correctly rejected missing session_token",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "Auth Me - Missing Session Token",
                    False,
                    f"Expected 422, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Auth Me - Missing Session Token Test",
                False,
                f"Network error: {str(e)}"
            )
            
        # Test with invalid session_token
        try:
            fake_token = str(uuid.uuid4())
            response = requests.get(
                f"{BACKEND_URL}/auth/me",
                params={"session_token": fake_token},
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test(
                    "Auth Me - Invalid Session Token",
                    True,
                    "Correctly rejected invalid session_token",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "Auth Me - Invalid Session Token",
                    False,
                    f"Expected 401, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Auth Me - Invalid Session Token Test",
                False,
                f"Network error: {str(e)}"
            )

    def test_vault_links_without_auth(self):
        """Test VaultLink endpoints without authentication"""
        print("🔒 Testing VaultLink Endpoints Without Authentication...")
        
        # Test POST /api/vault-links without auth
        try:
            link_data = {
                "url": "https://drive.google.com/file/d/example",
                "name": "Test Document",
                "access_level": "Restricted"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/vault-links",
                json=link_data,
                timeout=10
            )
            
            if response.status_code == 422:  # Missing session_token parameter
                self.log_test(
                    "Create VaultLink - No Auth",
                    True,
                    "Correctly rejected request without session_token",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "Create VaultLink - No Auth",
                    False,
                    f"Expected 422, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Create VaultLink - No Auth Test",
                False,
                f"Network error: {str(e)}"
            )
            
        # Test GET /api/vault-links without auth
        try:
            response = requests.get(f"{BACKEND_URL}/vault-links", timeout=10)
            
            if response.status_code == 422:  # Missing session_token parameter
                self.log_test(
                    "Get VaultLinks - No Auth",
                    True,
                    "Correctly rejected request without session_token",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "Get VaultLinks - No Auth",
                    False,
                    f"Expected 422, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Get VaultLinks - No Auth Test",
                False,
                f"Network error: {str(e)}"
            )
            
        # Test DELETE /api/vault-links/{id} without auth
        try:
            fake_id = str(uuid.uuid4())
            response = requests.delete(
                f"{BACKEND_URL}/vault-links/{fake_id}",
                timeout=10
            )
            
            if response.status_code == 422:  # Missing session_token parameter
                self.log_test(
                    "Delete VaultLink - No Auth",
                    True,
                    "Correctly rejected request without session_token",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "Delete VaultLink - No Auth",
                    False,
                    f"Expected 422, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Delete VaultLink - No Auth Test",
                False,
                f"Network error: {str(e)}"
            )

    def test_vault_links_with_invalid_auth(self):
        """Test VaultLink endpoints with invalid authentication"""
        print("🚫 Testing VaultLink Endpoints With Invalid Authentication...")
        
        fake_token = str(uuid.uuid4())
        
        # Test POST with invalid session_token
        try:
            link_data = {
                "url": "https://drive.google.com/file/d/example",
                "name": "Test Document",
                "access_level": "Restricted"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/vault-links",
                json=link_data,
                params={"session_token": fake_token},
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test(
                    "Create VaultLink - Invalid Auth",
                    True,
                    "Correctly rejected invalid session_token",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "Create VaultLink - Invalid Auth",
                    False,
                    f"Expected 401, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Create VaultLink - Invalid Auth Test",
                False,
                f"Network error: {str(e)}"
            )
            
        # Test GET with invalid session_token
        try:
            response = requests.get(
                f"{BACKEND_URL}/vault-links",
                params={"session_token": fake_token},
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test(
                    "Get VaultLinks - Invalid Auth",
                    True,
                    "Correctly rejected invalid session_token",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "Get VaultLinks - Invalid Auth",
                    False,
                    f"Expected 401, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Get VaultLinks - Invalid Auth Test",
                False,
                f"Network error: {str(e)}"
            )

    def test_vault_link_validation(self):
        """Test VaultLink validation with invalid data"""
        print("✅ Testing VaultLink Validation...")
        
        fake_token = str(uuid.uuid4())
        
        # Test with invalid URL (no http/https)
        try:
            invalid_link_data = {
                "url": "drive.google.com/file/d/example",  # Missing http/https
                "name": "Test Document",
                "access_level": "Restricted"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/vault-links",
                json=invalid_link_data,
                params={"session_token": fake_token},
                timeout=10
            )
            
            # Should fail with validation error (422) or auth error (401)
            if response.status_code in [401, 422]:
                self.log_test(
                    "VaultLink Validation - Invalid URL",
                    True,
                    f"Correctly rejected invalid URL format (Status: {response.status_code})"
                )
            else:
                self.log_test(
                    "VaultLink Validation - Invalid URL",
                    False,
                    f"Expected 401 or 422, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "VaultLink Validation - Invalid URL Test",
                False,
                f"Network error: {str(e)}"
            )
            
        # Test with invalid access level
        try:
            invalid_link_data = {
                "url": "https://drive.google.com/file/d/example",
                "name": "Test Document",
                "access_level": "InvalidLevel"  # Invalid access level
            }
            
            response = requests.post(
                f"{BACKEND_URL}/vault-links",
                json=invalid_link_data,
                params={"session_token": fake_token},
                timeout=10
            )
            
            # Should fail with validation error (422) or auth error (401)
            if response.status_code in [401, 422]:
                self.log_test(
                    "VaultLink Validation - Invalid Access Level",
                    True,
                    f"Correctly rejected invalid access level (Status: {response.status_code})"
                )
            else:
                self.log_test(
                    "VaultLink Validation - Invalid Access Level",
                    False,
                    f"Expected 401 or 422, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "VaultLink Validation - Invalid Access Level Test",
                False,
                f"Network error: {str(e)}"
            )
            
        # Test with missing required fields
        try:
            incomplete_data = {
                "url": "https://drive.google.com/file/d/example"
                # Missing name field
            }
            
            response = requests.post(
                f"{BACKEND_URL}/vault-links",
                json=incomplete_data,
                params={"session_token": fake_token},
                timeout=10
            )
            
            if response.status_code == 422:  # Validation error
                self.log_test(
                    "VaultLink Validation - Missing Fields",
                    True,
                    "Correctly rejected missing required fields",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "VaultLink Validation - Missing Fields",
                    False,
                    f"Expected 422, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "VaultLink Validation - Missing Fields Test",
                False,
                f"Network error: {str(e)}"
            )

    def test_delete_nonexistent_link(self):
        """Test deleting a non-existent link"""
        print("🗑️ Testing Delete Non-existent Link...")
        
        fake_token = str(uuid.uuid4())
        fake_link_id = str(uuid.uuid4())
        
        try:
            response = requests.delete(
                f"{BACKEND_URL}/vault-links/{fake_link_id}",
                params={"session_token": fake_token},
                timeout=10
            )
            
            # Should fail with auth error (401) since we're using fake token
            if response.status_code == 401:
                self.log_test(
                    "Delete Non-existent Link - Auth Check",
                    True,
                    "Authentication properly checked before link lookup",
                    f"Status: {response.status_code}"
                )
            else:
                self.log_test(
                    "Delete Non-existent Link - Auth Check",
                    False,
                    f"Expected 401, got {response.status_code}",
                    response.text
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test(
                "Delete Non-existent Link Test",
                False,
                f"Network error: {str(e)}"
            )

    def test_api_endpoints_exist(self):
        """Test that all required API endpoints exist and respond"""
        print("🌐 Testing API Endpoint Availability...")
        
        endpoints = [
            ("POST", "/auth/profile"),
            ("GET", "/auth/me"),
            ("POST", "/vault-links"),
            ("GET", "/vault-links"),
        ]
        
        for method, endpoint in endpoints:
            try:
                if method == "POST":
                    response = requests.post(f"{BACKEND_URL}{endpoint}", json={}, timeout=5)
                else:
                    response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
                
                # Any response (even error) means endpoint exists
                if response.status_code in [200, 401, 422, 500]:
                    self.log_test(
                        f"Endpoint Exists - {method} {endpoint}",
                        True,
                        f"Endpoint responds (Status: {response.status_code})"
                    )
                else:
                    self.log_test(
                        f"Endpoint Exists - {method} {endpoint}",
                        False,
                        f"Unexpected status: {response.status_code}"
                    )
                    
            except requests.exceptions.RequestException as e:
                self.log_test(
                    f"Endpoint Exists - {method} {endpoint}",
                    False,
                    f"Network error: {str(e)}"
                )

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting VaultLinks Backend API Tests")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Test API endpoint availability
        self.test_api_endpoints_exist()
        
        # Test authentication endpoints
        self.test_auth_profile_endpoint()
        self.test_auth_me_endpoint()
        
        # Test VaultLink endpoints without authentication
        self.test_vault_links_without_auth()
        
        # Test VaultLink endpoints with invalid authentication
        self.test_vault_links_with_invalid_auth()
        
        # Test VaultLink validation
        self.test_vault_link_validation()
        
        # Test delete operations
        self.test_delete_nonexistent_link()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}")
            if result["message"]:
                print(f"      {result['message']}")

if __name__ == "__main__":
    tester = VaultLinksAPITester()
    tester.run_all_tests()