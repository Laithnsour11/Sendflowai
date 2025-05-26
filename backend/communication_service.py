import os
import json
import logging
import httpx
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
from fastapi import HTTPException

from agent_orchestrator import AgentOrchestrator
from persistent_memory import PersistentMemoryManager

logger = logging.getLogger(__name__)

class CommunicationService:
    """
    Service for handling omnichannel communications:
    - SMS/MMS via SendBlue
    - Voice via Vapi.ai
    """
    
    def __init__(
        self,
        agent_orchestrator: Optional[AgentOrchestrator] = None,
        memory_manager: Optional[PersistentMemoryManager] = None
    ):
        self.agent_orchestrator = agent_orchestrator or AgentOrchestrator()
        self.memory_manager = memory_manager or PersistentMemoryManager()
        self.vapi_api_key = os.environ.get('VAPI_API_KEY')
        self.sendblue_api_key = os.environ.get('SENDBLUE_API_KEY')
    
    def set_vapi_api_key(self, api_key: str):
        """Set Vapi API key"""
        self.vapi_api_key = api_key
    
    def set_sendblue_api_key(self, api_key: str):
        """Set SendBlue API key"""
        self.sendblue_api_key = api_key
    
    # SMS/MMS via SendBlue
    async def send_sms(self, 
                      phone_number: str, 
                      message: str,
                      lead_id: str,
                      org_id: str) -> Dict[str, Any]:
        """
        Send a single SMS message via SendBlue
        
        Args:
            phone_number: Recipient phone number
            message: Message content
            lead_id: Lead ID
            org_id: Organization ID
            
        Returns:
            Dict containing the send result
        """
        if not self.sendblue_api_key:
            logger.error("SendBlue API key not set")
            raise HTTPException(status_code=400, detail="SendBlue API key not configured")
        
        url = "https://api.sendblue.co/api/send-message"
        headers = {
            "Authorization": f"Bearer {self.sendblue_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "phone_number": phone_number,
            "message": message
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Log the message to persistent memory
                await self.memory_manager.store_contextual_memory(
                    lead_id=lead_id,
                    memory_content={
                        "message_sent": message,
                        "phone_number": phone_number,
                        "channel": "sms",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                return {
                    "id": result.get("id"),
                    "status": result.get("status"),
                    "message": message,
                    "phone_number": phone_number,
                    "timestamp": datetime.now().isoformat()
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while sending SMS: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"SendBlue API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            raise HTTPException(status_code=500, detail=f"Error sending SMS: {str(e)}")
    
    async def send_sms_with_cadence(self,
                                  phone_number: str,
                                  messages: List[Dict[str, Any]],
                                  lead_id: str,
                                  org_id: str) -> List[Dict[str, Any]]:
        """
        Send multiple SMS messages with natural cadence
        
        Args:
            phone_number: Recipient phone number
            messages: List of messages with delay information
            lead_id: Lead ID
            org_id: Organization ID
            
        Returns:
            List of send results
        """
        results = []
        
        for message_info in messages:
            message = message_info.get("text", "")
            delay = message_info.get("delay", 0)
            
            # Apply delay if specified
            if delay > 0:
                await asyncio.sleep(delay)
            
            # Send the message
            result = await self.send_sms(phone_number, message, lead_id, org_id)
            results.append(result)
        
        return results
    
    async def process_sms_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming SMS webhook from SendBlue
        
        Args:
            webhook_data: Webhook data from SendBlue
            
        Returns:
            Dict containing the processing result
        """
        # Extract key information
        phone_number = webhook_data.get("from", "")
        message = webhook_data.get("body", "")
        timestamp = webhook_data.get("timestamp", datetime.now().isoformat())
        
        # TODO: Map phone number to lead_id and org_id
        # For now, use placeholders
        lead_id = "placeholder_lead_id"
        org_id = "placeholder_org_id"
        
        # Log the incoming message to persistent memory
        await self.memory_manager.store_contextual_memory(
            lead_id=lead_id,
            memory_content={
                "message_received": message,
                "phone_number": phone_number,
                "channel": "sms",
                "timestamp": timestamp
            }
        )
        
        # Get conversation history
        # TODO: Implement conversation history retrieval
        conversation_history = []
        
        # Orchestrate response through AI agent
        response = await self.agent_orchestrator.orchestrate_conversation(
            message=message,
            lead_id=lead_id,
            org_id=org_id,
            conversation_history=conversation_history,
            channel="sms"
        )
        
        # Send response with cadence if applicable
        if response["response"]["response_type"] == "cadence":
            await self.send_sms_with_cadence(
                phone_number=phone_number,
                messages=response["response"]["messages"],
                lead_id=lead_id,
                org_id=org_id
            )
        else:
            await self.send_sms(
                phone_number=phone_number,
                message=response["response"]["content"],
                lead_id=lead_id,
                org_id=org_id
            )
        
        return {
            "status": "processed",
            "phone_number": phone_number,
            "agent_used": response["agent_used"]["type"],
            "timestamp": datetime.now().isoformat()
        }
    
    # Voice via Vapi.ai
    async def initiate_voice_call(self,
                                phone_number: str,
                                lead_id: str,
                                org_id: str,
                                agent_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Initiate a voice call via Vapi.ai
        
        Args:
            phone_number: Recipient phone number
            lead_id: Lead ID
            org_id: Organization ID
            agent_type: Optional specific agent type to use
            
        Returns:
            Dict containing the call information
        """
        if not self.vapi_api_key:
            logger.error("Vapi API key not set")
            raise HTTPException(status_code=400, detail="Vapi API key not configured")
        
        # Get lead context
        lead_context = await self.memory_manager.synthesize_lead_context(lead_id)
        
        # Select agent if not specified
        if not agent_type:
            agent_selection = await self.agent_orchestrator.select_agent({
                "lead_context": lead_context,
                "message_intent": "outbound_call",
                "conversation_history": []
            })
            agent_type = agent_selection["type"]
        
        # Get agent configuration
        agent_config = await self.agent_orchestrator.get_specialized_agent_config(agent_type, org_id)
        
        # Create Vapi call
        url = "https://api.vapi.ai/call/phone"
        headers = {
            "Authorization": f"Bearer {self.vapi_api_key}",
            "Content-Type": "application/json"
        }
        
        # Compile agent prompt
        system_prompt = f"""
        {agent_config.get('system_prompt', '')}
        
        LEAD CONTEXT:
        - Name: {lead_context.get('name', 'Unknown')}
        - Personality Type: {lead_context.get('personality_type', 'Unknown')}
        - Relationship Stage: {lead_context.get('relationship_stage', 'initial_contact')}
        - Property Preferences: {json.dumps(lead_context.get('property_preferences', {}), indent=2)}
        - Budget: {json.dumps(lead_context.get('budget', {}), indent=2)}
        
        Remember to adapt your communication style to match the lead's personality type and relationship stage.
        This is a voice conversation, so be natural, conversational, and engaging.
        """
        
        # Configure the model based on agent configuration
        model_config = {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": agent_config.get("temperature", 0.7),
            "systemPrompt": system_prompt
        }
        
        # Map OpenRouter model to Vapi supported model if needed
        if agent_config.get("provider") == "openrouter":
            or_model = agent_config.get("model", "")
            if "openai" in or_model:
                model_config["model"] = or_model.split("/")[1]  # Extract model name after "openai/"
                model_config["provider"] = "openai"
            elif "anthropic" in or_model:
                model_config["model"] = or_model.split("/")[1]  # Extract model name after "anthropic/"
                model_config["provider"] = "anthropic"
        elif agent_config.get("provider") == "anthropic":
            model_config["provider"] = "anthropic"
            model_config["model"] = agent_config.get("model")
        
        payload = {
            "phoneNumber": phone_number,
            "model": model_config,
            "firstMessage": f"Hello, this is {agent_config.get('name', 'AI Closer')} from ABC Realty. Do you have a moment to talk about your real estate needs?",
            "recordingEnabled": True,
            "transcriptEnabled": True,
            "serverUrl": "https://your-server.com/api/vapi/webhook",  # Replace with your actual webhook URL
            "serverUrlSecret": "your-webhook-secret"  # Replace with your actual webhook secret
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Store call initiation in memory
                await self.memory_manager.store_contextual_memory(
                    lead_id=lead_id,
                    memory_content={
                        "call_initiated": True,
                        "phone_number": phone_number,
                        "agent_type": agent_type,
                        "channel": "voice",
                        "call_id": result.get("callId"),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                return {
                    "call_id": result.get("callId"),
                    "status": result.get("status"),
                    "phone_number": phone_number,
                    "agent_type": agent_type,
                    "timestamp": datetime.now().isoformat()
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while initiating voice call: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Vapi API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error initiating voice call: {e}")
            raise HTTPException(status_code=500, detail=f"Error initiating voice call: {str(e)}")
    
    async def process_vapi_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook from Vapi.ai
        
        Args:
            webhook_data: Webhook data from Vapi
            
        Returns:
            Dict containing the processing result
        """
        event_type = webhook_data.get("event")
        call_id = webhook_data.get("callId")
        
        # TODO: Map call_id to lead_id and org_id
        # For now, use placeholders
        lead_id = "placeholder_lead_id"
        org_id = "placeholder_org_id"
        
        if event_type == "call-ended":
            # Process call completion
            transcript = webhook_data.get("transcript", "")
            recording_url = webhook_data.get("recordingUrl", "")
            duration = webhook_data.get("duration", 0)
            
            # Store call details in memory
            await self.memory_manager.store_contextual_memory(
                lead_id=lead_id,
                memory_content={
                    "call_completed": True,
                    "call_id": call_id,
                    "transcript": transcript,
                    "recording_url": recording_url,
                    "duration": duration,
                    "channel": "voice",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # TODO: Generate call summary and analysis
            # TODO: Update GHL with call details
            
            return {
                "status": "processed",
                "event_type": event_type,
                "call_id": call_id,
                "timestamp": datetime.now().isoformat()
            }
        
        elif event_type == "function-call":
            # Handle function call from Vapi
            function_name = webhook_data.get("functionCall", {}).get("name")
            function_args = webhook_data.get("functionCall", {}).get("arguments", {})
            
            # TODO: Implement function call handling based on function name
            # For example: update_lead_info, schedule_appointment, etc.
            
            return {
                "status": "processed",
                "event_type": event_type,
                "function_name": function_name,
                "call_id": call_id,
                "timestamp": datetime.now().isoformat()
            }
        
        # Default response for other event types
        return {
            "status": "received",
            "event_type": event_type,
            "call_id": call_id,
            "timestamp": datetime.now().isoformat()
        }
