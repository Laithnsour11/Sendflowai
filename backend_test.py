
import requests
import json
import sys
import time
import uuid
from datetime import datetime

class AICloserAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.org_id = "test_org_" + str(uuid.uuid4())[:8]  # Generate a unique test org ID
        self.lead_id = "test_lead_" + str(uuid.uuid4())[:8]  # Generate a unique test lead ID

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if not headers:
            headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            
            status_match = response.status_code == expected_status
            
            if status_match:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {"status": "success", "no_json_response": True}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_details = response.json()
                    print(f"Error details: {json.dumps(error_details, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "api",
            200
        )

    def test_get_api_keys(self):
        """Test getting API keys for an organization"""
        return self.run_test(
            "Get API Keys",
            "GET",
            f"api/settings/api-keys/{self.org_id}",
            200
        )

    def test_update_api_keys(self):
        """Test updating API keys for an organization"""
        test_data = {
            "ghl_client_id": "test-client-id",
            "ghl_client_secret": "test-client-secret",
            "ghl_shared_secret": "test-shared-secret",
            "openai_api_key": "test-openai-key",
            "vapi_api_key": "test-vapi-key",
            "mem0_api_key": "test-mem0-key"
        }
        return self.run_test(
            "Update API Keys",
            "PUT",
            f"api/settings/api-keys/{self.org_id}",
            200,
            data=test_data
        )

    def test_integration_status(self):
        """Test getting integration status for an organization"""
        return self.run_test(
            "Get Integration Status",
            "GET",
            f"api/settings/integration-status/{self.org_id}",
            200
        )

    def test_ghl_webhook(self):
        """Test the GHL webhook endpoint"""
        test_data = {
            "event": "ContactCreate",
            "companyId": self.org_id,
            "contact": {
                "id": "test-contact-id",
                "firstName": "Test",
                "lastName": "User",
                "email": "test@example.com",
                "phone": "1234567890"
            }
        }
        return self.run_test(
            "GHL Webhook",
            "POST",
            "api/webhooks/ghl",
            200,
            data=test_data
        )

    def test_ghl_sync_leads(self):
        """Test the GHL sync leads endpoint"""
        return self.run_test(
            "GHL Sync Leads",
            "POST",
            f"api/ghl/sync-leads?org_id={self.org_id}",
            400  # Expecting 400 because we don't have valid GHL credentials
        )

    def test_agent_selection(self):
        """Test the agent selection endpoint"""
        return self.run_test(
            "Agent Selection",
            "GET",
            f"api/agents/select?lead_id={self.lead_id}&objective=initial_contact&channel=chat&conversation_history=true",
            404  # Expecting 404 because the lead doesn't exist
        )

    def test_process_message(self):
        """Test the message processing endpoint"""
        return self.run_test(
            "Process Message",
            "GET",
            f"api/agents/process-message?lead_id={self.lead_id}&message=Hello&channel=chat",
            404  # Expecting 404 because the lead doesn't exist
        )

def main():
    print("=" * 50)
    print("AI Closer API Test Suite")
    print("=" * 50)
    
    tester = AICloserAPITester()
    
    # Test basic API endpoints
    tester.test_root_endpoint()
    
    # Test settings endpoints
    tester.test_get_api_keys()
    tester.test_update_api_keys()
    tester.test_integration_status()
    
    # Test GHL integration endpoints
    tester.test_ghl_webhook()
    tester.test_ghl_sync_leads()
    
    # Test agent orchestration endpoints
    tester.test_agent_selection()
    tester.test_process_message()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"Tests completed: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed / tester.tests_run) * 100:.1f}%")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
