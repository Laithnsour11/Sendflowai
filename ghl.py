import os
import json
import logging
import httpx
import time
import hmac
import hashlib
from typing import Dict, Any, List, Optional, Union
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class GHLIntegration:
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, shared_secret: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.shared_secret = shared_secret
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = 0
        
        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def set_credentials(self, client_id: str, client_secret: str, shared_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.shared_secret = shared_secret
    
    def set_tokens(self, access_token: str, refresh_token: str, expires_in: int = 3600):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = int(time.time()) + expires_in
        self.headers["Authorization"] = f"Bearer {self.access_token}"
    
    async def get_oauth_url(self, redirect_uri: str) -> str:
        """Get OAuth URL for user authorization"""
        if not self.client_id:
            logger.error("GHL Client ID not set")
            raise HTTPException(status_code=400, detail="GHL Client ID not configured")
        
        return (
            f"{self.base_url}/oauth/chooselocation"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
        )
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if not self.client_id or not self.client_secret:
            logger.error("GHL OAuth credentials not set")
            raise HTTPException(status_code=400, detail="GHL OAuth credentials not configured")
        
        endpoint = f"{self.base_url}/oauth/token"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri
                    }
                )
                response.raise_for_status()
                token_data = response.json()
                
                # Save tokens
                self.set_tokens(
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    expires_in=token_data.get("expires_in", 3600)
                )
                
                return token_data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while exchanging code: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        if not self.client_id or not self.client_secret or not self.refresh_token:
            logger.error("GHL OAuth credentials or refresh token not set")
            raise HTTPException(status_code=400, detail="GHL OAuth credentials or refresh token not configured")
        
        endpoint = f"{self.base_url}/oauth/token"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "refresh_token",
                        "refresh_token": self.refresh_token
                    }
                )
                response.raise_for_status()
                token_data = response.json()
                
                # Save tokens
                self.set_tokens(
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    expires_in=token_data.get("expires_in", 3600)
                )
                
                return token_data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while refreshing token: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if not self.access_token or int(time.time()) >= self.token_expires_at:
            if self.refresh_token:
                await self.refresh_access_token()
            else:
                logger.error("No valid access token or refresh token")
                raise HTTPException(status_code=401, detail="No valid GHL access token")
    
    def verify_webhook_signature(self, signature: str, payload: str) -> bool:
        """Verify the webhook signature from GHL"""
        if not self.shared_secret:
            logger.error("GHL Shared Secret not set")
            return False
        
        calculated_signature = hmac.new(
            self.shared_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(calculated_signature, signature)
    
    # CONTACTS - Rich Data Read/Write Access
    
    async def get_contacts(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get contacts from GHL with pagination support"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/contacts/"
        if not query_params:
            query_params = {}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers, params=query_params)
                response.raise_for_status()
                return response.json().get("contacts", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching contacts: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching contacts from GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get a specific contact from GHL with all details"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/contacts/{contact_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                return response.json().get("contact", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching contact: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching contact from GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact in GHL"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/contacts/"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=self.headers, json=contact_data)
                response.raise_for_status()
                return response.json().get("contact", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating contact: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating contact in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a contact in GHL"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/contacts/{contact_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(endpoint, headers=self.headers, json=contact_data)
                response.raise_for_status()
                return response.json().get("contact", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while updating contact: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error updating contact in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
            
    # CUSTOM FIELDS
    
    async def get_custom_fields(self) -> List[Dict[str, Any]]:
        """Get custom fields from GHL"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/custom-fields"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                return response.json().get("customFields", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching custom fields: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching custom fields from GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def create_custom_field(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom field in GHL"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/custom-fields"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=self.headers, json=field_data)
                response.raise_for_status()
                return response.json().get("customField", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating custom field: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating custom field in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
            
    # PIPELINES
    
    async def get_pipelines(self) -> List[Dict[str, Any]]:
        """Get all pipelines"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/pipelines"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                return response.json().get("pipelines", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching pipelines: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching pipelines from GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
            
    # OPPORTUNITIES
    
    async def get_opportunities(self, contact_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get opportunities, optionally filtered by contact ID"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/opportunities"
        params = {}
        
        if contact_id:
            params["contactId"] = contact_id
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json().get("opportunities", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching opportunities: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching opportunities from GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def create_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new opportunity"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/opportunities"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=self.headers, json=opportunity_data)
                response.raise_for_status()
                return response.json().get("opportunity", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating opportunity: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating opportunity in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def update_opportunity(self, opportunity_id: str, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an opportunity"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/opportunities/{opportunity_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(endpoint, headers=self.headers, json=opportunity_data)
                response.raise_for_status()
                return response.json().get("opportunity", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while updating opportunity: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error updating opportunity in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def move_opportunity_stage(self, opportunity_id: str, stage_id: str) -> Dict[str, Any]:
        """Move an opportunity to a different stage"""
        return await self.update_opportunity(opportunity_id, {"pipelineStageId": stage_id})
        
    # TASKS
    
    async def get_tasks(self, contact_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tasks, optionally filtered by contact ID"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/tasks"
        params = {}
        
        if contact_id:
            params["contactId"] = contact_id
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json().get("tasks", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching tasks: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching tasks from GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/tasks"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=self.headers, json=task_data)
                response.raise_for_status()
                return response.json().get("task", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating task: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating task in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    # NOTES
    
    async def get_contact_notes(self, contact_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get notes for a specific contact"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/contacts/{contact_id}/notes"
        params = {"limit": limit}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json().get("notes", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching notes: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching notes for contact in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def add_note_to_contact(self, contact_id: str, note: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Add a note to a contact"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/contacts/{contact_id}/notes"
        
        note_data = {
            "body": note
        }
        
        if user_id:
            note_data["userId"] = user_id
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=self.headers, json=note_data)
                response.raise_for_status()
                return response.json().get("note", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while adding note: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error adding note to contact in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    # COMPREHENSIVE DATA ACCESS
    
    async def get_comprehensive_lead_data(self, contact_id: str) -> Dict[str, Any]:
        """
        Get comprehensive data about a lead, including:
        - Basic contact details
        - Custom fields
        - Tags
        - Notes
        - Opportunities and pipeline stages
        - Tasks
        """
        await self.ensure_valid_token()
        
        # Get individual pieces of data
        try:
            contact = await self.get_contact(contact_id)
            notes = await self.get_contact_notes(contact_id)
            opportunities = await self.get_opportunities(contact_id=contact_id)
            tasks = await self.get_tasks(contact_id=contact_id)
            
            # Combine all data
            return {
                "contact": contact,
                "notes": notes,
                "opportunities": opportunities,
                "tasks": tasks,
                "fetched_at": time.time()
            }
        except Exception as e:
            logger.error(f"Error fetching comprehensive lead data: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching comprehensive lead data: {str(e)}")
    
    # AI-SPECIFIC OPERATIONS
    
    async def update_ai_insights(self, contact_id: str, ai_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update AI-specific insights in GHL custom fields
        
        Args:
            contact_id: GHL contact ID
            ai_insights: Dict containing AI insights with keys like:
                - personality_type
                - trust_level
                - conversion_probability
                - relationship_stage
                - next_best_action
        """
        # Map our internal insight keys to GHL custom field names
        custom_field_mapping = {
            "personality_type": "AI Personality Type",
            "trust_level": "AI Trust Level",
            "conversion_probability": "AI Conversion Score",
            "relationship_stage": "AI Relationship Stage",
            "next_best_action": "AI Next Best Action"
        }
        
        # Prepare custom field updates
        custom_field_updates = {}
        
        for insight_key, custom_field_name in custom_field_mapping.items():
            if insight_key in ai_insights:
                value = ai_insights[insight_key]
                
                # Format values as needed
                if insight_key in ["trust_level", "conversion_probability"]:
                    # Convert float to percentage integer
                    value = int(float(value) * 100)
                
                custom_field_updates[custom_field_name] = value
        
        # Update custom fields
        if custom_field_updates:
            return await self.update_contact(contact_id, {"customField": custom_field_updates})
        
        return {"message": "No AI insights to update"}
    
    async def add_ai_interaction_note(self, contact_id: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a structured note about an AI interaction
        
        Args:
            contact_id: GHL contact ID
            interaction_data: Dict containing interaction details like:
                - channel: Voice, SMS, Email
                - agent_type: Which specialized agent was used
                - summary: Brief summary of the interaction
                - outcome: What was achieved
                - sentiment: Overall sentiment
                - next_steps: Recommended next steps
        """
        # Format the note in a structured way
        note_content = f"""
        🤖 AI INTERACTION SUMMARY
        
        Channel: {interaction_data.get('channel', 'Unknown')}
        Agent: {interaction_data.get('agent_type', 'General AI')}
        
        Summary: {interaction_data.get('summary', 'No summary provided')}
        
        Outcome: {interaction_data.get('outcome', 'No specific outcome')}
        Sentiment: {interaction_data.get('sentiment', 'Neutral')}
        
        Next Steps: {interaction_data.get('next_steps', 'No specific next steps')}
        
        Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Add the note
        return await self.add_note_to_contact(contact_id, note_content)
    
    async def create_follow_up_task(self, contact_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a follow-up task for a human agent"""
        # Format task data for GHL
        ghl_task_data = {
            "contactId": contact_id,
            "title": task_data.get('title', 'Follow-up required'),
            "description": task_data.get('description', 'AI-suggested follow-up'),
            "dueDate": task_data.get('due_date', None)
        }
        
        if 'assigned_to' in task_data:
            ghl_task_data["assignedTo"] = task_data['assigned_to']
        
        # Create the task
        return await self.create_task(ghl_task_data)
