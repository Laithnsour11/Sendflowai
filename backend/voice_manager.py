import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import os
from fastapi import HTTPException

from vapi_integration import VapiIntegration
import database as db

logger = logging.getLogger(__name__)

class VoiceManager:
    """Manages voice communication using Vapi.ai"""
    
    def __init__(self):
        self.vapi_integration = VapiIntegration()
    
    async def set_api_key_for_org(self, org_id: str) -> bool:
        """
        Set the Vapi API key for the organization
        
        Args:
            org_id: ID of the organization
            
        Returns:
            True if API key was set successfully, False otherwise
        """
        try:
            # Get API keys for the organization
            api_keys = await db.get_api_keys(org_id)
            
            if not api_keys or "vapi_api_key" not in api_keys or not api_keys["vapi_api_key"]:
                logger.warning(f"Vapi API key not configured for organization {org_id}")
                return False
            
            # Set the API key in the Vapi integration
            self.vapi_integration.set_api_key(api_keys["vapi_api_key"])
            return True
            
        except Exception as e:
            logger.error(f"Error setting Vapi API key for organization {org_id}: {e}")
            return False
    
    async def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Validate a Vapi API key
        
        Args:
            api_key: The Vapi API key to validate
            
        Returns:
            Dict with validation status
        """
        try:
            temp_integration = VapiIntegration(api_key)
            valid = await temp_integration.validate_key()
            
            if valid:
                return {"valid": True, "message": "Vapi API key is valid"}
            else:
                return {"valid": False, "message": "Invalid Vapi API key"}
                
        except Exception as e:
            logger.error(f"Error validating Vapi API key: {e}")
            return {"valid": False, "message": f"Error validating Vapi API key: {str(e)}"}
    
    async def make_call(
        self, 
        org_id: str,
        lead_id: str,
        phone_number: str,
        agent_config: Dict[str, Any],
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make a voice call to a lead
        
        Args:
            org_id: ID of the organization
            lead_id: ID of the lead
            phone_number: Phone number to call
            agent_config: Configuration for the AI agent
            webhook_url: Optional webhook URL for call events
            
        Returns:
            Dict containing call information
        """
        # Ensure we have the API key set
        api_key_set = await self.set_api_key_for_org(org_id)
        
        if not api_key_set:
            raise HTTPException(status_code=400, detail="Vapi API key not configured for this organization")
        
        try:
            # Get lead information for context
            lead = await db.get_lead(lead_id)
            if not lead:
                raise HTTPException(status_code=404, detail="Lead not found")
            
            # Prepare assistant configuration with lead context
            assistant_config = self._prepare_assistant_config(lead, agent_config)
            
            # Create call
            call_result = await self.vapi_integration.create_call(
                phone_number=phone_number,
                assistant_config=assistant_config,
                webhook_url=webhook_url
            )
            
            # Store call in database
            call_data = {
                "_id": str(uuid.uuid4()),
                "org_id": org_id,
                "lead_id": lead_id,
                "vapi_call_id": call_result.get("id"),
                "phone_number": phone_number,
                "status": call_result.get("status", "pending"),
                "agent_type": agent_config.get("agent_type", "general"),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Store in database (in a real implementation)
            # call_record = await db.create_conversation(call_data)
            
            return {
                "call_id": call_data["_id"],
                "vapi_call_id": call_result.get("id"),
                "status": call_result.get("status", "pending"),
                "lead_id": lead_id,
                "phone_number": phone_number
            }
            
        except Exception as e:
            logger.error(f"Error making call with Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to make call: {str(e)}")
    
    def _prepare_assistant_config(self, lead: Dict[str, Any], agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare assistant configuration with lead context"""
        # Extract basic lead information
        lead_name = lead.get("name", "there")
        lead_info = {}
        
        # Extract properties from lead if available
        if "property_preferences" in lead:
            lead_info["property_preferences"] = lead["property_preferences"]
        
        if "budget_analysis" in lead:
            lead_info["budget"] = lead["budget_analysis"]
        
        # Default greeting
        first_message = f"Hello {lead_name}, this is AI Closer calling about your real estate inquiry. How are you today?"
        
        # Use provided greeting if available
        if "firstMessage" in agent_config:
            first_message = agent_config["firstMessage"]
        
        # Default system prompt
        system_prompt = f"""
        You are a professional real estate agent assistant.
        
        LEAD INFORMATION:
        - Name: {lead_name}
        - Property Preferences: {json.dumps(lead_info.get('property_preferences', {}))}
        - Budget: {json.dumps(lead_info.get('budget', {}))}
        
        GOALS:
        - Be friendly, helpful, and professional
        - Build rapport with the lead
        - Understand their real estate needs
        - Provide relevant information
        - Move the conversation forward appropriately
        
        GUIDELINES:
        - Keep your responses concise and conversational
        - Ask open-ended questions to encourage discussion
        - Listen actively and acknowledge what the lead says
        - Don't overwhelm with too much information at once
        - End the call politely when appropriate
        """
        
        # Use provided system prompt if available
        if "model" in agent_config and "systemPrompt" in agent_config["model"]:
            system_prompt = agent_config["model"]["systemPrompt"]
        
        # Create assistant configuration
        assistant_config = {
            "firstMessage": first_message,
            "model": {
                "provider": agent_config.get("model", {}).get("provider", "openai"),
                "model": agent_config.get("model", {}).get("model", "gpt-4o"),
                "temperature": agent_config.get("model", {}).get("temperature", 0.7),
                "systemPrompt": system_prompt,
                "functions": agent_config.get("model", {}).get("functions", [])
            },
            "voice": agent_config.get("voice", {
                "provider": "elevenlabs",
                "voiceId": "11labs_amy",
                "stability": 0.7,
                "similarityBoost": 0.7
            }),
            "recordingEnabled": agent_config.get("recordingEnabled", True),
            "transcriptEnabled": agent_config.get("transcriptEnabled", True),
            "endCallFunctionEnabled": agent_config.get("endCallFunctionEnabled", True),
            "maxDurationSeconds": agent_config.get("maxDurationSeconds", 300),
            "responseDelaySeconds": agent_config.get("responseDelaySeconds", 0.5),
            "silenceTimeoutSeconds": agent_config.get("silenceTimeoutSeconds", 10)
        }
        
        return assistant_config
    
    async def handle_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a webhook event from Vapi
        
        Args:
            event: The webhook event data
            
        Returns:
            Dict containing processed event information
        """
        try:
            # Process the event
            processed_event = self.vapi_integration.process_webhook_event(event)
            event_type = processed_event.get("event_type")
            call_id = processed_event.get("call_id")
            
            # In a real implementation, we would store the event in the database
            # and trigger appropriate actions based on the event type
            
            # For end-of-call-report events, perform call analysis
            if event_type == "end-of-call-report":
                # Find the call in our database
                # call_record = await db.get_call_by_vapi_id(call_id)
                
                # Perform call analysis
                # analysis = await self.vapi_integration.analyze_call(call_id)
                
                # Update call record with analysis
                # await db.update_call(call_record["_id"], {
                #     "analysis": analysis,
                #     "status": "completed",
                #     "updated_at": datetime.now()
                # })
                
                # In a real implementation, we would also store a conversation record
                # and update the lead with insights from the call
                
                processed_event["analyzed"] = True
            
            return processed_event
            
        except Exception as e:
            logger.error(f"Error handling webhook event: {e}")
            return {
                "error": str(e),
                "processed": False
            }
    
    async def get_call_details(self, org_id: str, call_id: str) -> Dict[str, Any]:
        """
        Get details about a call
        
        Args:
            org_id: ID of the organization
            call_id: ID of the call
            
        Returns:
            Dict containing call details
        """
        # Ensure we have the API key set
        api_key_set = await self.set_api_key_for_org(org_id)
        
        if not api_key_set:
            raise HTTPException(status_code=400, detail="Vapi API key not configured for this organization")
        
        try:
            # Get call record from database
            # call_record = await db.get_conversation(call_id)
            # if not call_record:
            #     raise HTTPException(status_code=404, detail="Call not found")
            
            # For MVP, return mock data
            call_record = {
                "_id": call_id,
                "org_id": org_id,
                "lead_id": "lead123",
                "vapi_call_id": "call_abc123",
                "phone_number": "+15551234567",
                "status": "completed",
                "agent_type": "qualifier",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Get call details from Vapi
            vapi_call_details = await self.vapi_integration.get_call(call_record["vapi_call_id"])
            
            # Combine with our call record
            call_details = {
                "call_id": call_record["_id"],
                "vapi_call_id": call_record["vapi_call_id"],
                "lead_id": call_record["lead_id"],
                "phone_number": call_record["phone_number"],
                "status": call_record["status"],
                "agent_type": call_record["agent_type"],
                "created_at": call_record["created_at"],
                "updated_at": call_record["updated_at"],
                "vapi_details": vapi_call_details
            }
            
            return call_details
            
        except Exception as e:
            logger.error(f"Error getting call details: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get call details: {str(e)}")
