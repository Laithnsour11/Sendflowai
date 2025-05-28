import requests
import json
import time
import uuid
from bson import ObjectId

# Get the backend URL from the frontend .env file
import os
from dotenv import load_dotenv

# Load environment variables from frontend .env
load_dotenv('/app/frontend/.env')

# Get the backend URL
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    raise ValueError("REACT_APP_BACKEND_URL not found in frontend/.env")

print(f"Using backend URL: {BACKEND_URL}")

# Test class for UI action endpoints
class TestUIActionEndpoints:
    def __init__(self):
        self.base_url = f"{BACKEND_URL}/api"
        self.lead_id = None
        self.org_id = "production_org_123"  # Default org ID
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n=== Running UI Action Endpoint Tests ===\n")
        
        # Test add lead
        print("\n--- Testing POST /api/actions/add-lead ---")
        lead_result = self.test_add_lead()
        if not lead_result:
            print("❌ Failed to add lead, cannot continue with other tests")
            return False
            
        # Test get leads
        print("\n--- Testing GET /api/leads ---")
        leads_result = self.test_get_leads()
        if not leads_result:
            print("❌ Failed to get leads")
        
        # Test view lead
        print("\n--- Testing POST /api/actions/view-lead ---")
        view_result = self.test_view_lead()
        if not view_result:
            print("❌ Failed to view lead")
        
        # Test send message
        print("\n--- Testing POST /api/actions/send-message ---")
        message_result = self.test_send_message()
        if not message_result:
            print("❌ Failed to send message")
        
        # Test initiate call
        print("\n--- Testing POST /api/actions/initiate-call ---")
        call_result = self.test_initiate_call()
        if not call_result:
            print("❌ Failed to initiate call")
        
        # Test error handling with invalid lead ID
        print("\n--- Testing Error Handling with Invalid Lead ID ---")
        self.test_error_handling()
        
        print("\n=== UI Action Endpoint Tests Complete ===\n")
        return True
        
    def test_add_lead(self):
        """Test adding a new lead"""
        try:
            # Generate unique email to avoid duplicates
            unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
            
            # Prepare data
            data = {
                "org_id": self.org_id,
                "name": "Test Lead",
                "email": unique_email,
                "phone": "+15551234567",
                "status": "Initial Contact",
                "source": "API Test"
            }
            
            # Make request
            response = requests.post(f"{self.base_url}/actions/add-lead", json=data)
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                self.lead_id = result.get("lead_id")
                print(f"✅ Successfully added lead with ID: {self.lead_id}")
                print(f"   Response: {json.dumps(result, indent=2)}")
                return True
            else:
                print(f"❌ Failed to add lead: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception in test_add_lead: {str(e)}")
            return False
    
    def test_get_leads(self):
        """Test getting leads list"""
        try:
            # Make request
            response = requests.get(f"{self.base_url}/leads?org_id={self.org_id}")
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                leads = result.get("leads", [])
                
                # Check if our lead is in the list
                found = False
                for lead in leads:
                    if lead.get("id") == self.lead_id:
                        found = True
                        break
                
                if found:
                    print(f"✅ Successfully retrieved leads list containing our test lead")
                    print(f"   Total leads: {len(leads)}")
                    return True
                else:
                    print(f"❌ Our test lead (ID: {self.lead_id}) was not found in the leads list")
                    return False
            else:
                print(f"❌ Failed to get leads: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception in test_get_leads: {str(e)}")
            return False
    
    def test_view_lead(self):
        """Test viewing a lead"""
        if not self.lead_id:
            print("❌ No lead ID available for testing")
            return False
            
        try:
            # Make request
            response = requests.post(f"{self.base_url}/actions/view-lead?lead_id={self.lead_id}")
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                lead = result.get("lead", {})
                
                if lead.get("id"):
                    print(f"✅ Successfully viewed lead details")
                    print(f"   Lead name: {lead.get('name')}")
                    print(f"   Lead email: {lead.get('email')}")
                    return True
                else:
                    print(f"❌ Lead details not found in response")
                    return False
            else:
                print(f"❌ Failed to view lead: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception in test_view_lead: {str(e)}")
            return False
    
    def test_send_message(self):
        """Test sending a message to a lead"""
        if not self.lead_id:
            print("❌ No lead ID available for testing")
            return False
            
        try:
            # Prepare data
            data = {
                "lead_id": self.lead_id,
                "message": "This is a test message from the API test",
                "org_id": self.org_id
            }
            
            # Make request
            response = requests.post(f"{self.base_url}/actions/send-message", json=data)
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    print(f"✅ Successfully sent message to lead")
                    print(f"   Conversation ID: {result.get('conversation_id')}")
                    print(f"   Agent type: {result.get('agent_type')}")
                    return True
                else:
                    print(f"❌ Message sending reported failure")
                    return False
            else:
                print(f"❌ Failed to send message: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception in test_send_message: {str(e)}")
            return False
    
    def test_initiate_call(self):
        """Test initiating a call to a lead"""
        if not self.lead_id:
            print("❌ No lead ID available for testing")
            return False
            
        try:
            # Prepare data
            data = {
                "lead_id": self.lead_id,
                "objective": "Test call from API test",
                "org_id": self.org_id
            }
            
            # Make request
            response = requests.post(f"{self.base_url}/actions/initiate-call", json=data)
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    print(f"✅ Successfully initiated call to lead")
                    print(f"   Call ID: {result.get('call_id')}")
                    print(f"   Conversation ID: {result.get('conversation_id')}")
                    print(f"   Agent type: {result.get('agent_type')}")
                    return True
                else:
                    print(f"❌ Call initiation reported failure")
                    return False
            else:
                print(f"❌ Failed to initiate call: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception in test_initiate_call: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid lead ID"""
        try:
            # Generate invalid lead ID
            invalid_id = str(uuid.uuid4())
            
            # Test view lead with invalid ID
            print("\n--- Testing view-lead with invalid ID ---")
            response = requests.post(f"{self.base_url}/actions/view-lead?lead_id={invalid_id}")
            if response.status_code == 404:
                print(f"✅ Correctly returned 404 for invalid lead ID in view-lead")
            else:
                print(f"❌ Unexpected response for invalid lead ID in view-lead: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test send message with invalid ID
            print("\n--- Testing send-message with invalid ID ---")
            data = {
                "lead_id": invalid_id,
                "message": "Test message with invalid ID",
                "org_id": self.org_id
            }
            response = requests.post(f"{self.base_url}/actions/send-message", json=data)
            if response.status_code == 404:
                print(f"✅ Correctly returned 404 for invalid lead ID in send-message")
            else:
                print(f"❌ Unexpected response for invalid lead ID in send-message: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test initiate call with invalid ID
            print("\n--- Testing initiate-call with invalid ID ---")
            data = {
                "lead_id": invalid_id,
                "objective": "Test call with invalid ID",
                "org_id": self.org_id
            }
            response = requests.post(f"{self.base_url}/actions/initiate-call", json=data)
            if response.status_code == 404:
                print(f"✅ Correctly returned 404 for invalid lead ID in initiate-call")
            else:
                print(f"❌ Unexpected response for invalid lead ID in initiate-call: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test with malformed ObjectId
            print("\n--- Testing with malformed ObjectId ---")
            malformed_id = "not-a-valid-objectid"
            response = requests.post(f"{self.base_url}/actions/view-lead?lead_id={malformed_id}")
            if response.status_code == 404:
                print(f"✅ Correctly handled malformed ObjectId")
            else:
                print(f"❌ Unexpected response for malformed ObjectId: {response.status_code}")
                print(f"   Response: {response.text}")
            
            return True
                
        except Exception as e:
            print(f"❌ Exception in test_error_handling: {str(e)}")
            return False

# Run the tests
if __name__ == "__main__":
    tester = TestUIActionEndpoints()
    tester.run_all_tests()
