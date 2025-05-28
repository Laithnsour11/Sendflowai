import requests
import json
import time
import uuid
import re
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

# Test class for API key validation endpoints
class TestAPIKeyValidation:
    def __init__(self):
        self.base_url = f"{BACKEND_URL}/api"
        
    def run_all_tests(self):
        """Run all API key validation endpoint tests"""
        print("\n=== Running API Key Validation Endpoint Tests ===\n")
        
        # Test Mem0 API key validation
        print("\n--- Testing POST /api/settings/validate-mem0-key ---")
        self.test_mem0_key_validation()
        
        # Test Vapi API key validation
        print("\n--- Testing POST /api/settings/validate-vapi-key ---")
        self.test_vapi_key_validation()
        
        # Test SendBlue API key validation
        print("\n--- Testing POST /api/settings/validate-sendblue-key ---")
        self.test_sendblue_key_validation()
        
        # Test OpenAI API key validation
        print("\n--- Testing POST /api/settings/validate-openai-key ---")
        self.test_openai_key_validation()
        
        # Test OpenRouter API key validation
        print("\n--- Testing POST /api/settings/validate-openrouter-key ---")
        self.test_openrouter_key_validation()
        
        print("\n=== API Key Validation Endpoint Tests Complete ===\n")
        return True
    
    def test_mem0_key_validation(self):
        """Test Mem0 API key validation endpoint"""
        try:
            # Test with valid key
            valid_key = "m0-1234567890abcdefghijklmnop"
            response = requests.post(
                f"{self.base_url}/settings/validate-mem0-key",
                json={"api_key": valid_key},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("valid"):
                    print(f"✅ Successfully validated valid Mem0 API key")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Valid Mem0 API key was incorrectly rejected")
                    print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed to validate Mem0 API key: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test with invalid key
            invalid_key = "invalid-key"
            response = requests.post(
                f"{self.base_url}/settings/validate-mem0-key",
                json={"api_key": invalid_key},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get("valid"):
                    print(f"✅ Successfully rejected invalid Mem0 API key")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Invalid Mem0 API key was incorrectly accepted")
                    print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed to validate Mem0 API key: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception in test_mem0_key_validation: {str(e)}")
    
    def test_vapi_key_validation(self):
        """Test Vapi API key validation endpoint"""
        try:
            # Test with valid key (UUID format)
            valid_key = "d14070eb-c48a-45d5-9a53-6115b8c4d517"
            response = requests.post(
                f"{self.base_url}/settings/validate-vapi-key",
                json={"api_key": valid_key},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("valid"):
                    print(f"✅ Successfully validated valid Vapi API key")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Valid Vapi API key was incorrectly rejected")
                    print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed to validate Vapi API key: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test with invalid key
            invalid_key = "not-a-uuid"
            response = requests.post(
                f"{self.base_url}/settings/validate-vapi-key",
                json={"api_key": invalid_key},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get("valid"):
                    print(f"✅ Successfully rejected invalid Vapi API key")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Invalid Vapi API key was incorrectly accepted")
                    print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed to validate Vapi API key: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception in test_vapi_key_validation: {str(e)}")
    
    def test_sendblue_key_validation(self):
        """Test SendBlue API key validation endpoint"""
        try:
            # Test with valid key (length > 10)
            valid_key = "sendblue123456"
            response = requests.post(
                f"{self.base_url}/settings/validate-sendblue-key",
                json={"api_key": valid_key},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("valid"):
                    print(f"✅ Successfully validated valid SendBlue API key")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Valid SendBlue API key was incorrectly rejected")
                    print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed to validate SendBlue API key: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test with invalid key (too short)
            invalid_key = "short"
            response = requests.post(
                f"{self.base_url}/settings/validate-sendblue-key",
                json={"api_key": invalid_key},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get("valid"):
                    print(f"✅ Successfully rejected invalid SendBlue API key")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Invalid SendBlue API key was incorrectly accepted")
                    print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed to validate SendBlue API key: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception in test_sendblue_key_validation: {str(e)}")
    
    def test_openai_key_validation(self):
        """Test OpenAI API key validation endpoint"""
        try:
            # Test with valid key (starts with sk-, length > 20)
            valid_key = "sk-1234567890abcdefghijklmnop"
            response = requests.post(
                f"{self.base_url}/settings/validate-openai-key",
                json={"api_key": valid_key},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("valid"):
                    print(f"✅ Successfully validated valid OpenAI API key")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Valid OpenAI API key was incorrectly rejected")
                    print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed to validate OpenAI API key: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test with invalid key
            invalid_key = "invalid-openai-key"
            response = requests.post(
                f"{self.base_url}/settings/validate-openai-key",
                json={"api_key": invalid_key},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get("valid"):
                    print(f"✅ Successfully rejected invalid OpenAI API key")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Invalid OpenAI API key was incorrectly accepted")
                    print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed to validate OpenAI API key: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception in test_openai_key_validation: {str(e)}")
    
    def test_openrouter_key_validation(self):
        """Test OpenRouter API key validation endpoint"""
        try:
            # Test with valid key (starts with sk-or-v1-, length > 25)
            valid_key = "sk-or-v1-1234567890abcdefghijklmnop"
            response = requests.post(
                f"{self.base_url}/settings/validate-openrouter-key",
                json={"api_key": valid_key},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("valid"):
                    print(f"✅ Successfully validated valid OpenRouter API key")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Valid OpenRouter API key was incorrectly rejected")
                    print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed to validate OpenRouter API key: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test with invalid key
            invalid_key = "sk-invalid-key"
            response = requests.post(
                f"{self.base_url}/settings/validate-openrouter-key",
                json={"api_key": invalid_key},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get("valid"):
                    print(f"✅ Successfully rejected invalid OpenRouter API key")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"❌ Invalid OpenRouter API key was incorrectly accepted")
                    print(f"   Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ Failed to validate OpenRouter API key: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception in test_openrouter_key_validation: {str(e)}")

# Test class for UI action endpoints with Pydantic models
class TestUIActionEndpoints:
    def __init__(self):
        self.base_url = f"{BACKEND_URL}/api"
        self.lead_id = None
        self.org_id = "production_org_123"  # Default org ID
        
    def run_all_tests(self):
        """Run all tests in sequence to verify Pydantic model implementations"""
        print("\n=== Running UI Action Endpoint Tests with Pydantic Models ===\n")
        
        # Test add lead
        print("\n--- Testing POST /api/actions/add-lead with JSON body ---")
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
        print("\n--- Testing POST /api/actions/view-lead with JSON body ---")
        view_result = self.test_view_lead()
        if not view_result:
            print("❌ Failed to view lead")
        
        # Test send message with JSON body
        print("\n--- Testing POST /api/actions/send-message with JSON body ---")
        message_result = self.test_send_message()
        if not message_result:
            print("❌ Failed to send message")
        
        # Test initiate call with JSON body
        print("\n--- Testing POST /api/actions/initiate-call with JSON body ---")
        call_result = self.test_initiate_call()
        if not call_result:
            print("❌ Failed to initiate call")
        
        # Test error handling with invalid lead ID
        print("\n--- Testing Error Handling with Invalid Lead ID ---")
        self.test_error_handling()
        
        print("\n=== UI Action Endpoint Tests Complete ===\n")
        return True
        
    def test_add_lead(self):
        """Test adding a new lead with JSON body"""
        try:
            # Generate unique email to avoid duplicates
            unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
            
            # Prepare data as JSON body
            data = {
                "org_id": self.org_id,
                "name": "Test Lead",
                "email": unique_email,
                "phone": "+15551234567",
                "status": "Initial Contact",
                "source": "API Test"
            }
            
            # Make request with JSON body
            response = requests.post(
                f"{self.base_url}/actions/add-lead", 
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
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
        """Test viewing a lead with JSON body"""
        if not self.lead_id:
            print("❌ No lead ID available for testing")
            return False
            
        try:
            # Prepare data as JSON body
            data = {
                "lead_id": self.lead_id
            }
            
            # Make request with JSON body
            response = requests.post(
                f"{self.base_url}/actions/view-lead", 
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
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
        """Test sending a message to a lead with JSON body"""
        if not self.lead_id:
            print("❌ No lead ID available for testing")
            return False
            
        try:
            # Prepare data as JSON body
            data = {
                "lead_id": self.lead_id,
                "message": "This is a test message from the API test",
                "org_id": self.org_id
            }
            
            # Make request with JSON body
            response = requests.post(
                f"{self.base_url}/actions/send-message", 
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    print(f"✅ Successfully sent message to lead using JSON body")
                    print(f"   Conversation ID: {result.get('conversation_id')}")
                    print(f"   Agent type: {result.get('agent_type')}")
                    
                    # Verify that a conversation record was created
                    time.sleep(1)  # Give the server a moment to process
                    view_response = requests.post(
                        f"{self.base_url}/actions/view-lead", 
                        json={"lead_id": self.lead_id},
                        headers={"Content-Type": "application/json"}
                    )
                    if view_response.status_code == 200:
                        view_result = view_response.json()
                        conversations = view_result.get("recent_conversations", [])
                        if conversations:
                            print(f"✅ Verified conversation record was created")
                        else:
                            print(f"⚠️ Could not verify conversation record creation")
                    
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
        """Test initiating a call to a lead with JSON body"""
        if not self.lead_id:
            print("❌ No lead ID available for testing")
            return False
            
        try:
            # Prepare data as JSON body
            data = {
                "lead_id": self.lead_id,
                "objective": "Test call from API test",
                "org_id": self.org_id
            }
            
            # Make request with JSON body
            response = requests.post(
                f"{self.base_url}/actions/initiate-call", 
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                
                if result.get("success"):
                    print(f"✅ Successfully initiated call to lead using JSON body")
                    print(f"   Call ID: {result.get('call_id')}")
                    print(f"   Conversation ID: {result.get('conversation_id')}")
                    print(f"   Agent type: {result.get('agent_type')}")
                    
                    # Verify that a conversation record was created
                    time.sleep(1)  # Give the server a moment to process
                    view_response = requests.post(
                        f"{self.base_url}/actions/view-lead", 
                        json={"lead_id": self.lead_id},
                        headers={"Content-Type": "application/json"}
                    )
                    if view_response.status_code == 200:
                        view_result = view_response.json()
                        conversations = view_result.get("recent_conversations", [])
                        interactions = view_result.get("recent_interactions", [])
                        
                        if conversations:
                            print(f"✅ Verified conversation record was created")
                        else:
                            print(f"⚠️ Could not verify conversation record creation")
                            
                        if interactions:
                            print(f"✅ Verified interaction record was created")
                        else:
                            print(f"⚠️ Could not verify interaction record creation")
                    
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
        """Test error handling with invalid lead ID using JSON body"""
        try:
            # Generate invalid lead ID
            invalid_id = str(uuid.uuid4())
            
            # Test view lead with invalid ID
            print("\n--- Testing view-lead with invalid ID ---")
            response = requests.post(
                f"{self.base_url}/actions/view-lead", 
                json={"lead_id": invalid_id},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 404:
                print(f"✅ Correctly returned 404 for invalid lead ID in view-lead")
            elif response.status_code == 500:
                print(f"⚠️ Server returned 500 instead of 404 for invalid lead ID in view-lead")
                print(f"   This is a minor issue that could be improved")
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
            response = requests.post(
                f"{self.base_url}/actions/send-message", 
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 404:
                print(f"✅ Correctly returned 404 for invalid lead ID in send-message")
            elif response.status_code == 500:
                print(f"⚠️ Server returned 500 instead of 404 for invalid lead ID in send-message")
                print(f"   This is a minor issue that could be improved")
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
            response = requests.post(
                f"{self.base_url}/actions/initiate-call", 
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 404:
                print(f"✅ Correctly returned 404 for invalid lead ID in initiate-call")
            elif response.status_code == 500:
                print(f"⚠️ Server returned 500 instead of 404 for invalid lead ID in initiate-call")
                print(f"   This is a minor issue that could be improved")
            else:
                print(f"❌ Unexpected response for invalid lead ID in initiate-call: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test with malformed ObjectId
            print("\n--- Testing with malformed ObjectId ---")
            malformed_id = "not-a-valid-objectid"
            response = requests.post(
                f"{self.base_url}/actions/view-lead", 
                json={"lead_id": malformed_id},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 404:
                print(f"✅ Correctly handled malformed ObjectId")
            elif response.status_code == 500:
                print(f"⚠️ Server returned 500 instead of 404 for malformed ObjectId")
                print(f"   This is a minor issue that could be improved")
            else:
                print(f"❌ Unexpected response for malformed ObjectId: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Test with missing required fields
            print("\n--- Testing with missing required fields ---")
            response = requests.post(
                f"{self.base_url}/actions/view-lead", 
                json={},  # Missing lead_id
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 422:
                print(f"✅ Correctly returned 422 for missing required fields")
            else:
                print(f"❌ Unexpected response for missing required fields: {response.status_code}")
                print(f"   Response: {response.text}")
            
            return True
                
        except Exception as e:
            print(f"❌ Exception in test_error_handling: {str(e)}")
            return False

# Run the tests
# Test class for API key saving endpoints
class TestAPIKeySaving:
    def __init__(self):
        self.base_url = f"{BACKEND_URL}/api"
        self.org_id = "test_org_" + str(uuid.uuid4())[:8]
        
    def run_all_tests(self):
        """Run all API key saving endpoint tests"""
        print("\n=== Running API Key Saving Endpoint Tests ===\n")
        
        # Test saving API keys
        print("\n--- Testing PUT /api/settings/api-keys/{org_id} ---")
        save_result = self.test_save_api_keys()
        if not save_result:
            print("❌ Failed to save API keys, cannot continue with retrieval test")
            return False
            
        # Test retrieving API keys
        print("\n--- Testing GET /api/settings/api-keys/{org_id} ---")
        retrieve_result = self.test_retrieve_api_keys()
        if not retrieve_result:
            print("❌ Failed to retrieve API keys")
            
        print("\n=== API Key Saving Endpoint Tests Complete ===\n")
        return True
    
    def test_save_api_keys(self):
        """Test saving API keys for an organization"""
        try:
            # Prepare API keys data
            api_keys = {
                "mem0_api_key": "m0-1234567890abcdefghijklmnop",
                "vapi_api_key": "d14070eb-c48a-45d5-9a53-6115b8c4d517",
                "sendblue_api_key": "sendblue123456",
                "openai_api_key": "sk-1234567890abcdefghijklmnop",
                "openrouter_api_key": "sk-or-v1-1234567890abcdefghijklmnop"
            }
            
            # Make request to save API keys
            response = requests.put(
                f"{self.base_url}/settings/api-keys/{self.org_id}",
                json=api_keys,
                headers={"Content-Type": "application/json"}
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    print(f"✅ Successfully saved API keys for organization: {self.org_id}")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                    return True
                else:
                    print(f"❌ API key saving reported failure")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                    return False
            else:
                print(f"❌ Failed to save API keys: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception in test_save_api_keys: {str(e)}")
            return False
    
    def test_retrieve_api_keys(self):
        """Test retrieving API keys for an organization"""
        try:
            # Make request to retrieve API keys
            response = requests.get(
                f"{self.base_url}/settings/api-keys/{self.org_id}",
                headers={"Content-Type": "application/json"}
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                
                # Check if all API keys are present
                expected_keys = ["mem0_api_key", "vapi_api_key", "sendblue_api_key", "openai_api_key", "openrouter_api_key"]
                missing_keys = [key for key in expected_keys if key not in result]
                
                if not missing_keys:
                    print(f"✅ Successfully retrieved API keys for organization: {self.org_id}")
                    print(f"   Retrieved keys: {', '.join(expected_keys)}")
                    
                    # Check if values are masked (for security)
                    masked_values = True
                    for key in expected_keys:
                        value = result.get(key, "")
                        if not value.startswith("••••••••"):
                            masked_values = False
                            print(f"⚠️ API key {key} is not properly masked: {value}")
                    
                    if masked_values:
                        print(f"✅ All API key values are properly masked for security")
                    
                    return True
                else:
                    print(f"❌ Some API keys are missing from the response: {', '.join(missing_keys)}")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                    return False
            else:
                print(f"❌ Failed to retrieve API keys: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception in test_retrieve_api_keys: {str(e)}")
            return False

if __name__ == "__main__":
    # Run API key validation tests
    print("\n=== TESTING API KEY VALIDATION ENDPOINTS ===\n")
    api_key_tester = TestAPIKeyValidation()
    api_key_tester.run_all_tests()
    
    # Run API key saving tests
    print("\n=== TESTING API KEY SAVING ENDPOINTS ===\n")
    api_key_saving_tester = TestAPIKeySaving()
    api_key_saving_tester.run_all_tests()
    
    # Run UI action endpoint tests
    print("\n=== TESTING UI ACTION ENDPOINTS ===\n")
    ui_tester = TestUIActionEndpoints()
    ui_tester.run_all_tests()
