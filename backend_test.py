
import requests
import json
import sys
import time
import uuid
import os
from datetime import datetime
from bson import ObjectId

class AICloserAPITester:
    def __init__(self, base_url=None):
        # Use the REACT_APP_BACKEND_URL from frontend/.env if available
        if not base_url:
            try:
                with open('/app/frontend/.env', 'r') as f:
                    for line in f:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            base_url = line.strip().split('=')[1].strip('"\'')
                            break
            except Exception as e:
                print(f"Error reading frontend/.env: {e}")
                base_url = "http://localhost:8001"
        
        self.base_url = base_url
        print(f"Using backend URL: {self.base_url}")
        self.tests_run = 0
        self.tests_passed = 0
        self.org_id = "test_org_" + str(uuid.uuid4())[:8]  # Generate a unique test org ID
        self.lead_id = str(ObjectId())  # Generate a valid MongoDB ObjectId
        self.contact_id = None  # Will be set after creating a lead via webhook

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
        # Skip if no contact_id is available
        if not self.contact_id:
            print("⚠️ Skipping Agent Selection test - no contact ID available")
            return True
            
        # We need to get the MongoDB _id for the lead
        response = requests.get(f"{self.base_url}/api/leads?org_id={self.org_id}")
        if response.status_code != 200:
            print(f"❌ Failed to get leads - Status: {response.status_code}")
            return False
            
        leads = response.json()
        lead_id = None
        for lead in leads:
            if lead.get("ghl_contact_id") == self.contact_id:
                lead_id = lead.get("id")
                break
                
        if not lead_id:
            print("❌ Failed to find lead with matching contact ID")
            return False
            
        print(f"✅ Found lead with ID: {lead_id}")
        self.lead_id = lead_id
            
        return self.run_test(
            "Agent Selection",
            "POST",
            f"api/agents/select?lead_id={self.lead_id}&objective=initial_contact&channel=chat&conversation_history=true",
            200
        )
        
    def test_process_message(self):
        """Test the message processing endpoint"""
        # Skip if no lead_id is available
        if not hasattr(self, 'lead_id') or not self.lead_id:
            print("⚠️ Skipping Process Message test - no lead ID available")
            return True
            
        return self.run_test(
            "Process Message",
            "POST",
            f"api/agents/process-message?lead_id={self.lead_id}&message=Hello&channel=chat",
            200
        )

    def test_create_lead_via_webhook(self):
        """Test creating a lead via GHL webhook"""
        contact_id = str(uuid.uuid4())
        test_data = {
            "event": "ContactCreate",
            "companyId": self.org_id,
            "contact": {
                "id": contact_id,
                "firstName": "Test",
                "lastName": "Lead",
                "email": "test@example.com",
                "phone": "1234567890",
                "source": "API Test",
                "tags": ["test", "api"]
            }
        }
        result = self.run_test(
            "Create Lead via Webhook",
            "POST",
            "api/webhooks/ghl",
            200,
            data=test_data
        )
        
        # If successful, update the lead_id to use the contact_id
        if result:
            self.contact_id = contact_id
            print(f"✅ Created lead with contact ID: {contact_id}")
        
        return result
        
    # Phase B.2 Test Methods
    
    def test_agent_performance_analytics(self):
        """Test the agent performance analytics endpoint"""
        return self.run_test(
            "Agent Performance Analytics",
            "GET",
            f"api/analytics/agent-performance?org_id={self.org_id}&time_period=30_days",
            200
        )
    
    def test_rlhf_feedback_submission(self):
        """Test the RLHF feedback submission endpoint"""
        # Create test feedback data
        test_data = {
            "conversation_id": str(uuid.uuid4()),
            "feedback_type": "agent_selection",
            "rating": 4,
            "feedback_text": "The agent was very helpful but could have been more specific about pricing options."
        }
        
        return self.run_test(
            "RLHF Feedback Submission",
            "POST",
            "api/rlhf/feedback",
            200,
            data=test_data
        )
    
    def test_real_time_dashboard(self):
        """Test the real-time dashboard endpoint"""
        return self.run_test(
            "Real-time Dashboard",
            "GET",
            f"api/dashboard/real-time?org_id={self.org_id}",
            200
        )
        
    def test_rlhf_feedback_types(self):
        """Test different types of RLHF feedback submissions"""
        feedback_types = [
            {
                "conversation_id": str(uuid.uuid4()),
                "feedback_type": "response_effectiveness",
                "rating": 5,
                "feedback_text": "The response was very effective at addressing my concerns."
            },
            {
                "conversation_id": str(uuid.uuid4()),
                "feedback_type": "learning_opportunity",
                "rating": 3,
                "feedback_text": "The agent could learn more about our specific product features."
            },
            {
                "conversation_id": str(uuid.uuid4()),
                "feedback_type": "conversation_rating",
                "rating": 4,
                "feedback_text": "Good conversation flow but took a bit too long to get to the point."
            }
        ]
        
        all_passed = True
        for i, feedback in enumerate(feedback_types):
            print(f"\nTesting RLHF feedback type {i+1}: {feedback['feedback_type']}")
            result, _ = self.run_test(
                f"RLHF Feedback - {feedback['feedback_type']}",
                "POST",
                "api/rlhf/feedback",
                200,
                data=feedback
            )
            if not result:
                all_passed = False
                
        return all_passed

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
    
    # Test lead creation
    tester.test_create_lead_via_webhook()
    
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
