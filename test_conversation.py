import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:8001/api"

def test_conversation():
    """Test the conversation API"""
    org_id = "test"
    lead_id = "test_lead"
    
    # First create a test organization
    org_response = requests.post(
        f"{BASE_URL}/organizations",
        json={"name": "Test Organization", "subscription_tier": "starter"}
    )
    print("Organization created:", org_response.json() if org_response.status_code == 200 else org_response.text)
    
    if org_response.status_code == 200:
        org_id = org_response.json().get("_id")
    
    # Set up API keys
    api_keys = {
        "vapi_public_key": "d14070eb-c48a-45d5-9a53-6115b8c4d517",
        "vapi_private_key": "c948ca43-806d-4a15-8f7b-a29e019457b1",
        "mem0_api_key": "m0-TTwLd8awIP6aFAixLPn1lgkIUR2DJlDTzApPil8E",
        "ghl_client_id": "681a8d486b267326cb42a4db-mb5qftwj",
        "ghl_client_secret": "12395acc-c70b-4aee-b86f-abb4c7da3b62",
        "ghl_shared_secret": "6a705549-ecb6-48cf-b5e4-8fe59b3bafa9"
    }
    
    keys_response = requests.put(
        f"{BASE_URL}/settings/api-keys/{org_id}",
        json=api_keys
    )
    print("API keys set:", keys_response.json() if keys_response.status_code == 200 else keys_response.text)
    
    # Create a test lead
    lead_data = {
        "org_id": org_id,
        "name": "Test Lead",
        "email": "test@example.com",
        "phone": "+15551234567",
        "personality_type": "analytical",
        "relationship_stage": "initial_contact",
        "property_preferences": {
            "bedrooms": 3,
            "bathrooms": 2,
            "location": "downtown",
            "property_type": "condo"
        },
        "budget_analysis": {
            "min": 300000,
            "max": 450000
        }
    }
    
    lead_response = requests.post(
        f"{BASE_URL}/leads",
        json=lead_data
    )
    print("Lead created:", lead_response.json() if lead_response.status_code == 200 else lead_response.text)
    
    if lead_response.status_code == 200:
        lead_id = lead_response.json().get("_id")
    
    # Test the conversation
    message = "Hi, I'm looking for a 3 bedroom condo in downtown. My budget is around $400k."
    
    conversation_data = {
        "org_id": org_id,
        "lead_id": lead_id,
        "message": message,
        "channel": "chat"
    }
    
    convo_response = requests.post(
        f"{BASE_URL}/conversation/process",
        json=conversation_data
    )
    
    print("\nConversation Result:")
    
    if convo_response.status_code == 200:
        result = convo_response.json()
        print(f"Agent Type: {result.get('agent_type')}")
        print(f"Response: {result.get('response')}")
        
        # Check if Mem0 was used
        if "memories" in result.get("lead_context", {}):
            print("\nMemories retrieved from Mem0:")
            for memory in result["lead_context"]["memories"]:
                print(f"- {memory}")
    else:
        print("Error:", convo_response.text)
    
    # Test Vapi call
    vapi_data = {
        "phone_number": "+15551234567",
        "agent_type": "initial_contact",
        "lead_id": lead_id
    }
    
    vapi_response = requests.post(
        f"{BASE_URL}/vapi/create-call?org_id={org_id}",
        json=vapi_data
    )
    
    print("\nVapi Call Result:")
    if vapi_response.status_code == 200:
        print(vapi_response.json())
    else:
        print("Error:", vapi_response.text)
    
    # Get integration status
    status_response = requests.get(f"{BASE_URL}/settings/integration-status/{org_id}")
    
    print("\nIntegration Status:")
    if status_response.status_code == 200:
        status = status_response.json()
        for service, info in status.items():
            print(f"{service}: {info['status']} ({info['connected']})")
    else:
        print("Error:", status_response.text)

if __name__ == "__main__":
    test_conversation()
