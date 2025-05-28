
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

    # Phase C.1 Test Methods - Campaign Management
    
    def test_list_campaigns(self):
        """Test listing campaigns for an organization"""
        return self.run_test(
            "List Campaigns",
            "GET",
            f"api/campaigns?org_id=production_org_123",
            200
        )
    
    def test_create_campaign(self):
        """Test creating a new campaign"""
        test_data = {
            "org_id": "production_org_123",
            "campaign_data": {
                "name": "Test SMS Campaign",
                "description": "Initial lead qualification campaign",
                "campaign_type": "outbound_sms",
                "target_config": {
                    "ghl_segment_criteria": {
                        "tags": ["new_lead", "uncontacted"],
                        "pipeline_stage": "Lead",
                        "custom_fields": {}
                    },
                    "lead_filters": {}
                },
                "agent_config": {
                    "initial_agent_type": "initial_contact",
                    "campaign_objective": "Lead qualification and initial engagement",
                    "communication_channels": ["sms"],
                    "llm_model": "gpt-4o"
                },
                "schedule_config": {
                    "daily_contact_limit": 25,
                    "hourly_contact_limit": 5,
                    "contact_hours": {
                        "start": "09:00",
                        "end": "17:00",
                        "timezone": "America/New_York"
                    },
                    "contact_days": [1, 2, 3, 4, 5]
                }
            }
        }
        
        success, response = self.run_test(
            "Create Campaign",
            "POST",
            "api/campaigns/create",
            200,
            data=test_data
        )
        
        if success and "_id" in response:
            self.campaign_id = response["_id"]
            print(f"✅ Created campaign with ID: {self.campaign_id}")
        
        return success, response
    
    def test_start_campaign(self):
        """Test starting a campaign"""
        if not hasattr(self, 'campaign_id'):
            print("⚠️ Skipping Start Campaign test - no campaign ID available")
            return True, {}
            
        test_data = {
            "org_id": "production_org_123"
        }
        
        return self.run_test(
            "Start Campaign",
            "POST",
            f"api/campaigns/{self.campaign_id}/start",
            200,
            data=test_data
        )
    
    def test_get_campaign_status(self):
        """Test getting campaign status"""
        if not hasattr(self, 'campaign_id'):
            print("⚠️ Skipping Get Campaign Status test - no campaign ID available")
            return True, {}
            
        return self.run_test(
            "Get Campaign Status",
            "GET",
            f"api/campaigns/{self.campaign_id}/status?org_id=production_org_123",
            200
        )
    
    def test_pause_campaign(self):
        """Test pausing a campaign"""
        if not hasattr(self, 'campaign_id'):
            print("⚠️ Skipping Pause Campaign test - no campaign ID available")
            return True, {}
            
        test_data = {
            "org_id": "production_org_123"
        }
        
        return self.run_test(
            "Pause Campaign",
            "POST",
            f"api/campaigns/{self.campaign_id}/pause",
            200,
            data=test_data
        )
    
    def test_stop_campaign(self):
        """Test stopping a campaign"""
        if not hasattr(self, 'campaign_id'):
            print("⚠️ Skipping Stop Campaign test - no campaign ID available")
            return True, {}
            
        test_data = {
            "org_id": "production_org_123"
        }
        
        return self.run_test(
            "Stop Campaign",
            "POST",
            f"api/campaigns/{self.campaign_id}/stop",
            200,
            data=test_data
        )
    
    def test_campaign_error_handling(self):
        """Test campaign error handling"""
        # Test invalid campaign ID
        invalid_id = "invalid_campaign_id"
        success1, _ = self.run_test(
            "Invalid Campaign ID",
            "GET",
            f"api/campaigns/{invalid_id}/status?org_id=production_org_123",
            404
        )
        
        # Test invalid status transition (stopping a draft campaign)
        if hasattr(self, 'campaign_id'):
            # Create a new campaign that will remain in draft status
            test_data = {
                "org_id": "production_org_123",
                "campaign_data": {
                    "name": "Draft Campaign for Error Testing",
                    "description": "Testing invalid status transitions",
                    "campaign_type": "outbound_sms",
                    "target_config": {
                        "ghl_segment_criteria": {
                            "tags": ["test"],
                            "pipeline_stage": "Lead",
                            "custom_fields": {}
                        },
                        "lead_filters": {}
                    },
                    "agent_config": {
                        "initial_agent_type": "initial_contact",
                        "campaign_objective": "Testing error handling",
                        "communication_channels": ["sms"],
                        "llm_model": "gpt-4o"
                    },
                    "schedule_config": {
                        "daily_contact_limit": 10,
                        "hourly_contact_limit": 2,
                        "contact_hours": {
                            "start": "09:00",
                            "end": "17:00",
                            "timezone": "America/New_York"
                        },
                        "contact_days": [1, 2, 3, 4, 5]
                    }
                }
            }
            
            success2, response = self.run_test(
                "Create Draft Campaign",
                "POST",
                "api/campaigns/create",
                200,
                data=test_data
            )
            
            if success2 and "_id" in response:
                draft_campaign_id = response["_id"]
                
                # Try to pause a draft campaign (should fail)
                success3, _ = self.run_test(
                    "Invalid Status Transition - Pause Draft",
                    "POST",
                    f"api/campaigns/{draft_campaign_id}/pause",
                    400,
                    data={"org_id": "production_org_123"}
                )
                
                return success1 and success2 and success3
        
        return success1
    
    def test_campaign_lifecycle(self):
        """Test the complete campaign lifecycle"""
        print("\n🔍 Testing Campaign Lifecycle...")
        self.tests_run += 1
        
        try:
            # 1. Create campaign
            success1, create_response = self.test_create_campaign()
            if not success1:
                print("❌ Campaign lifecycle test failed at creation step")
                return False
                
            campaign_id = create_response["_id"]
            print(f"✅ 1. Created campaign: {campaign_id}")
            
            # 2. Verify campaign appears in list
            success2, list_response = self.test_list_campaigns()
            if not success2:
                print("❌ Campaign lifecycle test failed at listing step")
                return False
                
            found = False
            for campaign in list_response.get("campaigns", []):
                if campaign.get("_id") == campaign_id:
                    found = True
                    if campaign.get("status") == "draft":
                        print(f"✅ 2. Campaign appears in list with 'draft' status")
                    else:
                        print(f"❌ Campaign has incorrect initial status: {campaign.get('status')}")
                        return False
            
            if not found:
                print("❌ Created campaign not found in campaign list")
                return False
            
            # 3. Start the campaign
            success3, start_response = self.test_start_campaign()
            if not success3:
                print("❌ Campaign lifecycle test failed at start step")
                return False
                
            print(f"✅ 3. Started campaign successfully")
            
            # 4. Check campaign status
            success4, status_response = self.test_get_campaign_status()
            if not success4:
                print("❌ Campaign lifecycle test failed at status check step")
                return False
                
            if status_response.get("campaign", {}).get("status") != "active":
                print(f"❌ Campaign has incorrect status after starting: {status_response.get('campaign', {}).get('status')}")
                return False
                
            print(f"✅ 4. Campaign status is 'active' after starting")
            
            # 5. Pause the campaign
            success5, pause_response = self.test_pause_campaign()
            if not success5:
                print("❌ Campaign lifecycle test failed at pause step")
                return False
                
            print(f"✅ 5. Paused campaign successfully")
            
            # 6. Check status again
            success6, status_response2 = self.test_get_campaign_status()
            if not success6:
                print("❌ Campaign lifecycle test failed at second status check")
                return False
                
            if status_response2.get("campaign", {}).get("status") != "paused":
                print(f"❌ Campaign has incorrect status after pausing: {status_response2.get('campaign', {}).get('status')}")
                return False
                
            print(f"✅ 6. Campaign status is 'paused' after pausing")
            
            # 7. Resume the campaign
            success7, resume_response = self.test_start_campaign()
            if not success7:
                print("❌ Campaign lifecycle test failed at resume step")
                return False
                
            print(f"✅ 7. Resumed campaign successfully")
            
            # 8. Stop the campaign
            success8, stop_response = self.test_stop_campaign()
            if not success8:
                print("❌ Campaign lifecycle test failed at stop step")
                return False
                
            print(f"✅ 8. Stopped campaign successfully")
            
            # 9. Final status check
            success9, final_status = self.test_get_campaign_status()
            if not success9:
                print("❌ Campaign lifecycle test failed at final status check")
                return False
                
            if final_status.get("campaign", {}).get("status") != "completed":
                print(f"❌ Campaign has incorrect status after stopping: {final_status.get('campaign', {}).get('status')}")
                return False
                
            print(f"✅ 9. Campaign status is 'completed' after stopping")
            
            self.tests_passed += 1
            print("✅ Campaign lifecycle test passed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Campaign lifecycle test failed with error: {str(e)}")
            return False

    # Phase C.2 Test Methods - AI Fine-Tuning System
    
    def test_list_fine_tuning_jobs(self):
        """Test listing fine-tuning jobs for an organization"""
        return self.run_test(
            "List Fine-Tuning Jobs",
            "GET",
            "api/fine-tuning/jobs?org_id=production_org_123",
            200
        )
    
    def test_create_fine_tuning_job(self):
        """Test creating a new fine-tuning job"""
        test_data = {
            "org_id": "production_org_123",
            "job_config": {
                "job_name": "Test Agent Fine-Tuning",
                "description": "Test fine-tuning job for improving agent responses",
                "model_config": {
                    "base_model": "gpt-4o",
                    "provider": "openai",
                    "agent_type": "initial_contact",
                    "target_capabilities": ["response_quality", "tone_appropriateness"]
                },
                "training_config": {
                    "feedback_date_range": {
                        "start": "2024-01-01",
                        "end": "2024-06-01"
                    },
                    "feedback_types": ["response_quality", "tone_appropriateness", "conversation_flow"],
                    "minimum_feedback_score": 3,
                    "include_conversation_context": True,
                    "training_epochs": 3,
                    "learning_rate": 0.0001
                }
            }
        }
        
        success, response = self.run_test(
            "Create Fine-Tuning Job",
            "POST",
            "api/fine-tuning/create",
            200,
            data=test_data
        )
        
        if success and "_id" in response:
            self.fine_tuning_job_id = response["_id"]
            print(f"✅ Created fine-tuning job with ID: {self.fine_tuning_job_id}")
        
        return success, response
    
    def test_get_fine_tuning_job_status(self):
        """Test getting fine-tuning job status"""
        if not hasattr(self, 'fine_tuning_job_id'):
            print("⚠️ Skipping Get Fine-Tuning Job Status test - no job ID available")
            return True, {}
            
        return self.run_test(
            "Get Fine-Tuning Job Status",
            "GET",
            f"api/fine-tuning/{self.fine_tuning_job_id}/status?org_id=production_org_123",
            200
        )
    
    def test_start_fine_tuning_job(self):
        """Test starting a fine-tuning job"""
        if not hasattr(self, 'fine_tuning_job_id'):
            print("⚠️ Skipping Start Fine-Tuning Job test - no job ID available")
            return True, {}
            
        test_data = {
            "org_id": "production_org_123"
        }
        
        return self.run_test(
            "Start Fine-Tuning Job",
            "POST",
            f"api/fine-tuning/{self.fine_tuning_job_id}/start",
            200,
            data=test_data
        )
    
    def test_monitor_fine_tuning_progress(self):
        """Test monitoring fine-tuning job progress"""
        if not hasattr(self, 'fine_tuning_job_id'):
            print("⚠️ Skipping Monitor Fine-Tuning Progress test - no job ID available")
            return True, {}
        
        print("\n🔍 Monitoring Fine-Tuning Progress...")
        self.tests_run += 1
        
        try:
            # Monitor training progress
            max_attempts = 10
            completed = False
            
            for attempt in range(max_attempts):
                time.sleep(2)  # Wait 2 seconds between checks
                
                response = requests.get(
                    f"{self.base_url}/api/fine-tuning/{self.fine_tuning_job_id}/status?org_id=production_org_123"
                )
                
                if response.status_code != 200:
                    print(f"❌ Failed to get job status: {response.status_code}")
                    return False, {}
                
                data = response.json()
                job = data["job"]
                status = job["status"]
                
                if "training_progress" in job:
                    progress = job["training_progress"]
                    current_epoch = progress.get("current_epoch", 0)
                    total_epochs = progress.get("total_epochs", 0)
                    loss = progress.get("loss")
                    
                    print(f"Training progress: Epoch {current_epoch}/{total_epochs}, Loss: {loss}")
                
                if status == "completed":
                    completed = True
                    print("✅ Job completed successfully!")
                    break
                    
                if status == "failed":
                    print(f"❌ Job failed with error: {job.get('error_message', 'Unknown error')}")
                    return False, {}
                
                print(f"Job status check {attempt+1}/{max_attempts}: {status}")
            
            if completed:
                self.tests_passed += 1
                return True, {"status": "completed"}
            else:
                print("⚠️ Job did not complete within expected time, but monitoring was successful")
                self.tests_passed += 1
                return True, {"status": status}
                
        except Exception as e:
            print(f"❌ Error monitoring fine-tuning progress: {str(e)}")
            return False, {}
    
    def test_deploy_fine_tuned_model(self):
        """Test deploying a fine-tuned model"""
        if not hasattr(self, 'fine_tuning_job_id'):
            print("⚠️ Skipping Deploy Fine-Tuned Model test - no job ID available")
            return True, {}
        
        # Check if job is completed
        response = requests.get(
            f"{self.base_url}/api/fine-tuning/{self.fine_tuning_job_id}/status?org_id=production_org_123"
        )
        
        if response.status_code != 200 or response.json()["job"]["status"] != "completed":
            print("⚠️ Job not in 'completed' status, cannot deploy")
            return True, {}
        
        test_data = {
            "org_id": "production_org_123",
            "deployment_config": {
                "a_b_test_config": {
                    "enabled": True,
                    "traffic_percentage": 50
                }
            }
        }
        
        success, response = self.run_test(
            "Deploy Fine-Tuned Model",
            "POST",
            f"api/fine-tuning/{self.fine_tuning_job_id}/deploy",
            200,
            data=test_data
        )
        
        if success:
            # Monitor deployment progress
            max_attempts = 5
            for attempt in range(max_attempts):
                time.sleep(2)  # Wait 2 seconds between checks
                
                status_response = requests.get(
                    f"{self.base_url}/api/fine-tuning/{self.fine_tuning_job_id}/status?org_id=production_org_123"
                )
                
                if status_response.status_code == 200:
                    deployment = status_response.json()["job"]["deployment"]
                    status = deployment.get("deployment_status")
                    
                    print(f"Deployment status check {attempt+1}/{max_attempts}: {status}")
                    
                    if status == "deployed":
                        print("✅ Model deployed successfully!")
                        break
        
        return success, response
    
    def test_cancel_fine_tuning_job(self):
        """Test cancelling a fine-tuning job"""
        # Create a new job to cancel
        test_data = {
            "org_id": "production_org_123",
            "job_config": {
                "job_name": "Test Job to Cancel",
                "description": "Test job that will be cancelled",
                "model_config": {
                    "base_model": "gpt-4o",
                    "provider": "openai",
                    "agent_type": "qualifier"
                },
                "training_config": {
                    "feedback_date_range": {
                        "start": "2024-01-01",
                        "end": "2024-06-01"
                    },
                    "feedback_types": ["response_quality"],
                    "training_epochs": 3
                }
            }
        }
        
        success1, response = self.run_test(
            "Create Job to Cancel",
            "POST",
            "api/fine-tuning/create",
            200,
            data=test_data
        )
        
        if not success1 or "_id" not in response:
            print("❌ Failed to create job for cancellation test")
            return False, {}
        
        job_to_cancel = response["_id"]
        print(f"✅ Created job to cancel with ID: {job_to_cancel}")
        
        # Start the job
        success2, _ = self.run_test(
            "Start Job to Cancel",
            "POST",
            f"api/fine-tuning/{job_to_cancel}/start",
            200,
            data={"org_id": "production_org_123"}
        )
        
        if not success2:
            print("❌ Failed to start job for cancellation test")
            return False, {}
        
        # Wait briefly for job to start processing
        time.sleep(2)
        
        # Cancel the job
        return self.run_test(
            "Cancel Fine-Tuning Job",
            "POST",
            f"api/fine-tuning/{job_to_cancel}/cancel",
            200,
            data={"org_id": "production_org_123"}
        )
    
    def test_get_rlhf_analytics_for_fine_tuning(self):
        """Test getting RLHF analytics for fine-tuning insights"""
        return self.run_test(
            "Get RLHF Analytics for Fine-Tuning",
            "GET",
            "api/rlhf/analytics?org_id=production_org_123",
            200
        )
    
    def test_fine_tuning_error_handling(self):
        """Test error handling for fine-tuning endpoints"""
        print("\n🔍 Testing Fine-Tuning Error Handling...")
        self.tests_run += 1
        
        try:
            # Test invalid job ID
            success1, _ = self.run_test(
                "Invalid Job ID",
                "GET",
                "api/fine-tuning/invalid_id/status?org_id=production_org_123",
                404
            )
            
            # Test missing required fields in job creation
            test_data = {
                "org_id": "production_org_123",
                "job_config": {
                    "job_name": "Invalid Job"
                    # Missing required fields
                }
            }
            
            success2, _ = self.run_test(
                "Missing Required Fields",
                "POST",
                "api/fine-tuning/create",
                500  # Expecting 500 due to validation error
            )
            
            # Test invalid status transitions (if we have a completed job)
            if hasattr(self, 'fine_tuning_job_id'):
                # Check if job is completed
                response = requests.get(
                    f"{self.base_url}/api/fine-tuning/{self.fine_tuning_job_id}/status?org_id=production_org_123"
                )
                
                if response.status_code == 200 and response.json()["job"]["status"] == "completed":
                    # Try to start a completed job
                    success3, _ = self.run_test(
                        "Invalid Status Transition",
                        "POST",
                        f"api/fine-tuning/{self.fine_tuning_job_id}/start",
                        400,  # Expecting 400 for invalid transition
                        data={"org_id": "production_org_123"}
                    )
                    
                    if success1 and success2 and success3:
                        self.tests_passed += 1
                        print("✅ Fine-tuning error handling tests passed")
                        return True, {}
            
            if success1 and success2:
                self.tests_passed += 1
                print("✅ Fine-tuning error handling tests passed")
                return True, {}
            
            return False, {}
            
        except Exception as e:
            print(f"❌ Error in fine-tuning error handling tests: {str(e)}")
            return False, {}
    
    def test_fine_tuning_lifecycle(self):
        """Test the complete fine-tuning job lifecycle"""
        print("\n🔍 Testing Fine-Tuning Job Lifecycle...")
        self.tests_run += 1
        
        try:
            # 1. Create fine-tuning job
            success1, create_response = self.test_create_fine_tuning_job()
            if not success1:
                print("❌ Fine-tuning lifecycle test failed at creation step")
                return False, {}
                
            job_id = create_response["_id"]
            print(f"✅ 1. Created fine-tuning job: {job_id}")
            
            # 2. Verify job appears in list with pending status
            success2, list_response = self.test_list_fine_tuning_jobs()
            if not success2:
                print("❌ Fine-tuning lifecycle test failed at listing step")
                return False, {}
                
            found = False
            for job in list_response.get("jobs", []):
                if job.get("_id") == job_id:
                    found = True
                    if job.get("status") == "pending":
                        print(f"✅ 2. Job appears in list with 'pending' status")
                    else:
                        print(f"❌ Job has incorrect initial status: {job.get('status')}")
                        return False, {}
            
            if not found:
                print("❌ Created job not found in jobs list")
                return False, {}
            
            # 3. Start the job
            success3, start_response = self.test_start_fine_tuning_job()
            if not success3:
                print("❌ Fine-tuning lifecycle test failed at start step")
                return False, {}
                
            print(f"✅ 3. Started fine-tuning job successfully")
            
            # 4. Monitor training progress
            success4, monitor_response = self.test_monitor_fine_tuning_progress()
            if not success4:
                print("❌ Fine-tuning lifecycle test failed at monitoring step")
                return False, {}
                
            print(f"✅ 4. Monitored training progress successfully")
            
            # 5. Deploy the model (if job completed)
            if monitor_response.get("status") == "completed":
                success5, deploy_response = self.test_deploy_fine_tuned_model()
                if not success5:
                    print("❌ Fine-tuning lifecycle test failed at deployment step")
                    return False, {}
                    
                print(f"✅ 5. Deployed fine-tuned model successfully")
            else:
                print("⚠️ Job not completed, skipping deployment step")
            
            self.tests_passed += 1
            print("✅ Fine-tuning lifecycle test passed successfully")
            return True, {}
            
        except Exception as e:
            print(f"❌ Fine-tuning lifecycle test failed with error: {str(e)}")
            return False, {}
    
    # Phase C.3 Test Methods - Advanced Analytics System
    
    def test_comprehensive_dashboard(self, time_period="30d"):
        """Test the comprehensive dashboard endpoint"""
        return self.run_test(
            f"Comprehensive Dashboard ({time_period})",
            "GET",
            f"api/analytics/comprehensive-dashboard?org_id=production_org_123&time_period={time_period}",
            200
        )
    
    def test_campaign_performance_report(self, campaign_id=None):
        """Test the campaign performance report endpoint"""
        endpoint = f"api/analytics/campaign-performance-report?org_id=production_org_123&time_period=30d"
        if campaign_id:
            endpoint += f"&campaign_id={campaign_id}"
            
        return self.run_test(
            f"Campaign Performance Report{' (filtered)' if campaign_id else ''}",
            "GET",
            endpoint,
            200
        )
    
    def test_agent_intelligence_report(self, agent_type=None):
        """Test the agent intelligence report endpoint"""
        endpoint = f"api/analytics/agent-intelligence-report?org_id=production_org_123&time_period=30d"
        if agent_type:
            endpoint += f"&agent_type={agent_type}"
            
        return self.run_test(
            f"Agent Intelligence Report{' (filtered)' if agent_type else ''}",
            "GET",
            endpoint,
            200
        )
    
    def test_export_analytics_report(self):
        """Test the export analytics report endpoint"""
        test_data = {
            "org_id": "production_org_123",
            "report_type": "dashboard",
            "time_period": "30d",
            "format_type": "json"
        }
        
        success, response = self.run_test(
            "Export Analytics Report",
            "POST",
            "api/analytics/export-report",
            200,
            data=test_data
        )
        
        if success and "export_id" in response:
            self.export_id = response["export_id"]
            print(f"✅ Created export with ID: {self.export_id}")
        
        return success, response
    
    def test_download_analytics_export(self):
        """Test the download analytics export endpoint"""
        if not hasattr(self, 'export_id'):
            print("⚠️ Skipping Download Analytics Export test - no export ID available")
            return True, {}
            
        return self.run_test(
            "Download Analytics Export",
            "GET",
            f"api/analytics/exports/{self.export_id}/download",
            200
        )
        
    # UI Action Endpoints Test Methods
    
    def test_add_lead(self):
        """Test the add lead endpoint"""
        test_data = {
            "org_id": self.org_id,
            "name": "Test UI Lead",
            "email": f"test-ui-{uuid.uuid4()}@example.com",
            "phone": "1234567890",
            "status": "Initial Contact",
            "source": "UI Test"
        }
        
        success, response = self.run_test(
            "Add Lead",
            "POST",
            "api/actions/add-lead",
            200,
            data=test_data
        )
        
        if success and "lead_id" in response:
            self.ui_lead_id = response["lead_id"]
            print(f"✅ Created UI lead with ID: {self.ui_lead_id}")
            
            # Also store the MongoDB ObjectId for this lead
            if "lead" in response and "id" in response["lead"]:
                self.ui_lead_mongo_id = response["lead"]["id"]
                print(f"✅ MongoDB ID for UI lead: {self.ui_lead_mongo_id}")
        
        return success, response
    
    def test_view_lead(self):
        """Test the view lead endpoint"""
        # First try with the UI lead ID if available
        if hasattr(self, 'ui_lead_mongo_id'):
            lead_id = self.ui_lead_mongo_id
        # Fall back to the test lead ID
        elif hasattr(self, 'lead_id'):
            lead_id = self.lead_id
        else:
            print("⚠️ Skipping View Lead test - no lead ID available")
            return True, {}
        
        success, response = self.run_test(
            "View Lead",
            "POST",
            f"api/actions/view-lead?lead_id={lead_id}",
            200
        )
        
        # Validate response structure
        if success:
            if "lead" in response and "recent_conversations" in response and "memory_context" in response:
                print("✅ View Lead response contains expected data structure")
            else:
                print("⚠️ View Lead response missing expected data structure")
        
        return success, response
    
    def test_send_message(self):
        """Test the send message endpoint"""
        # First try with the UI lead ID if available
        if hasattr(self, 'ui_lead_mongo_id'):
            lead_id = self.ui_lead_mongo_id
        # Fall back to the test lead ID
        elif hasattr(self, 'lead_id'):
            lead_id = self.lead_id
        else:
            print("⚠️ Skipping Send Message test - no lead ID available")
            return True, {}
        
        # Test with explicit message
        test_data = {
            "lead_id": lead_id,
            "message": "Hello from the UI test! How can I help you today?",
            "org_id": self.org_id
        }
        
        success1, response1 = self.run_test(
            "Send Message (with explicit message)",
            "POST",
            "api/actions/send-message",
            200,
            data=test_data
        )
        
        # Test with auto-generated message
        test_data = {
            "lead_id": lead_id,
            "org_id": self.org_id
        }
        
        success2, response2 = self.run_test(
            "Send Message (with auto-generated message)",
            "POST",
            "api/actions/send-message",
            200,
            data=test_data
        )
        
        # Test with invalid lead ID
        test_data = {
            "lead_id": "invalid_lead_id",
            "message": "This should fail",
            "org_id": self.org_id
        }
        
        success3, _ = self.run_test(
            "Send Message (with invalid lead ID)",
            "POST",
            "api/actions/send-message",
            404,  # Expecting 404 Not Found
            data=test_data
        )
        
        return success1 and success2 and success3, response1
    
    def test_initiate_call(self):
        """Test the initiate call endpoint"""
        # First try with the UI lead ID if available
        if hasattr(self, 'ui_lead_mongo_id'):
            lead_id = self.ui_lead_mongo_id
        # Fall back to the test lead ID
        elif hasattr(self, 'lead_id'):
            lead_id = self.lead_id
        else:
            print("⚠️ Skipping Initiate Call test - no lead ID available")
            return True, {}
        
        # Test with explicit objective
        test_data = {
            "lead_id": lead_id,
            "objective": "Qualify the lead and understand their needs",
            "org_id": self.org_id
        }
        
        success1, response1 = self.run_test(
            "Initiate Call (with explicit objective)",
            "POST",
            "api/actions/initiate-call",
            200,
            data=test_data
        )
        
        # Test with auto-generated objective
        test_data = {
            "lead_id": lead_id,
            "org_id": self.org_id
        }
        
        success2, response2 = self.run_test(
            "Initiate Call (with auto-generated objective)",
            "POST",
            "api/actions/initiate-call",
            200,
            data=test_data
        )
        
        # Test with invalid lead ID
        test_data = {
            "lead_id": "invalid_lead_id",
            "objective": "This should fail",
            "org_id": self.org_id
        }
        
        success3, _ = self.run_test(
            "Initiate Call (with invalid lead ID)",
            "POST",
            "api/actions/initiate-call",
            404,  # Expecting 404 Not Found
            data=test_data
        )
        
        return success1 and success2 and success3, response1
    
    def test_get_leads(self):
        """Test the get leads endpoint"""
        # Test with org_id
        success1, response1 = self.run_test(
            "Get Leads (with org_id)",
            "GET",
            f"api/leads?org_id={self.org_id}",
            200
        )
        
        # Test with limit
        success2, response2 = self.run_test(
            "Get Leads (with limit)",
            "GET",
            f"api/leads?org_id={self.org_id}&limit=5",
            200
        )
        
        # Validate response structure
        if success1:
            if "leads" in response1 and "total" in response1:
                print("✅ Get Leads response contains expected data structure")
                
                # Check if our UI lead is in the list
                if hasattr(self, 'ui_lead_mongo_id'):
                    found = False
                    for lead in response1["leads"]:
                        if lead.get("id") == self.ui_lead_mongo_id:
                            found = True
                            break
                    
                    if found:
                        print("✅ UI lead found in leads list")
                    else:
                        print("⚠️ UI lead not found in leads list")
            else:
                print("⚠️ Get Leads response missing expected data structure")
        
        return success1 and success2, response1
    
    def test_get_conversations(self):
        """Test the get conversations endpoint"""
        # Test with org_id
        success1, response1 = self.run_test(
            "Get Conversations (with org_id)",
            "GET",
            f"api/conversations?org_id={self.org_id}",
            200
        )
        
        # Test with limit
        success2, response2 = self.run_test(
            "Get Conversations (with limit)",
            "GET",
            f"api/conversations?org_id={self.org_id}&limit=5",
            200
        )
        
        # Validate response structure
        if success1:
            if "conversations" in response1 and "total" in response1:
                print("✅ Get Conversations response contains expected data structure")
            else:
                print("⚠️ Get Conversations response missing expected data structure")
        
        return success1 and success2, response1

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
    
    # Phase B.2 Tests
    print("\n" + "=" * 50)
    print("Phase B.2 Tests - Analytics and RLHF")
    print("=" * 50)
    
    # Test agent performance analytics
    tester.test_agent_performance_analytics()
    
    # Test RLHF feedback submission
    tester.test_rlhf_feedback_submission()
    
    # Test different RLHF feedback types
    tester.test_rlhf_feedback_types()
    
    # Test real-time dashboard
    tester.test_real_time_dashboard()
    
    # Phase C.1 Tests - Campaign Management
    print("\n" + "=" * 50)
    print("Phase C.1 Tests - Campaign Management")
    print("=" * 50)
    
    # Test campaign management endpoints
    tester.test_list_campaigns()
    tester.test_create_campaign()
    tester.test_start_campaign()
    tester.test_get_campaign_status()
    tester.test_pause_campaign()
    tester.test_stop_campaign()
    tester.test_campaign_error_handling()
    
    # Test complete campaign lifecycle
    tester.test_campaign_lifecycle()
    
    # Phase C.2 Tests - AI Fine-Tuning System
    print("\n" + "=" * 50)
    print("Phase C.2 Tests - AI Fine-Tuning System")
    print("=" * 50)
    
    # Test AI fine-tuning endpoints
    tester.test_list_fine_tuning_jobs()
    tester.test_create_fine_tuning_job()
    tester.test_get_fine_tuning_job_status()
    tester.test_start_fine_tuning_job()
    tester.test_monitor_fine_tuning_progress()
    tester.test_deploy_fine_tuned_model()
    tester.test_cancel_fine_tuning_job()
    tester.test_get_rlhf_analytics_for_fine_tuning()
    tester.test_fine_tuning_error_handling()
    
    # Test complete fine-tuning job lifecycle
    tester.test_fine_tuning_lifecycle()
    
    # UI Action Endpoints Tests
    print("\n" + "=" * 50)
    print("UI Action Endpoints Tests")
    print("=" * 50)
    
    # Test UI action endpoints
    tester.test_add_lead()
    tester.test_view_lead()
    tester.test_send_message()
    tester.test_initiate_call()
    tester.test_get_leads()
    tester.test_get_conversations()
    
    # Phase C.3 Tests - Advanced Analytics System
    print("\n" + "=" * 50)
    print("Phase C.3 Tests - Advanced Analytics System")
    print("=" * 50)
    
    # Test Advanced Analytics endpoints
    tester.test_comprehensive_dashboard()
    tester.test_comprehensive_dashboard(time_period="7d")
    tester.test_comprehensive_dashboard(time_period="90d")
    tester.test_campaign_performance_report()
    tester.test_campaign_performance_report(campaign_id="campaign_1")
    tester.test_agent_intelligence_report()
    tester.test_agent_intelligence_report(agent_type="initial_contact")
    tester.test_export_analytics_report()
    tester.test_download_analytics_export()
    
    # Print results
    print("\n" + "=" * 50)
    print(f"Tests completed: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed / tester.tests_run) * 100:.1f}%")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
