import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional, Union
from fastapi import HTTPException
from datetime import datetime
import uuid

from langchain_agents import AgentOrchestrator, ConversationManager
from mem0 import Mem0Integration

logger = logging.getLogger(__name__)

class VapiIntegration:
    """Handles integration with Vapi.ai for voice communication"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        agent_orchestrator: Optional[AgentOrchestrator] = None,
        mem0_client: Optional[Mem0Integration] = None
    ):
        self.api_key = api_key
        self.base_url = "https://api.vapi.ai"
        self.headers = {}
        self.agent_orchestrator = agent_orchestrator
        self.mem0_client = mem0_client
        
        if self.api_key:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def set_api_key(self, api_key: str):
        """Set the Vapi API key"""
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_call(
        self,
        lead_id: str,
        phone_number: str,
        lead_context: Dict[str, Any],
        agent_type: Optional[str] = None,
        objective: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate a call to a lead using Vapi.ai
        
        Args:
            lead_id: ID of the lead
            phone_number: Phone number to call
            lead_context: Context about the lead
            agent_type: Optional agent type to use
            objective: Optional call objective
            
        Returns:
            Dict containing call information
        """
        if not self.api_key:
            logger.warning("Vapi API key not set")
            return self._get_mock_call(lead_id, phone_number)
        
        if not self.agent_orchestrator:
            logger.warning("Agent orchestrator not set")
            return self._get_mock_call(lead_id, phone_number)
        
        # Set default objective if not provided
        if not objective:
            objective = self._get_default_objective(lead_context)
        
        # Select the appropriate agent if not specified
        agent = None
        if agent_type:
            agent = self.agent_orchestrator.agents.get(agent_type)
        
        if not agent:
            agent_info = await self.agent_orchestrator.select_agent({
                "lead_context": lead_context,
                "objective": objective,
                "channel": "voice"
            })
            agent_type = agent_info["type"]
        
        # Build the system prompt
        system_prompt = await self.agent_orchestrator.build_agent_prompt(
            {"type": agent_type} if agent_type else {},
            lead_context,
            []  # No conversation history for initial call
        )
        
        # Get agent configuration for the selected agent
        agent_config = self.agent_orchestrator.agents.get(agent_type)
        
        # Determine which provider/model to use
        model_provider = "openai"
        model_name = "gpt-4o"
        
        if agent_config:
            model_provider = agent_config.llm_provider
            model_name = agent_config.llm_model
        
        # Configure the voice based on lead context
        voice_config = self._select_voice_for_lead(lead_context)
        
        # Configure Vapi call
        call_config = {
            "phone_number": phone_number,
            
            # Voice configuration
            "voice": voice_config,
            
            # Model configuration
            "model": {
                "provider": model_provider,
                "model": model_name,
                "system_prompt": system_prompt,
                "temperature": 0.7,
                "functions": self._get_vapi_functions()
            },
            
            # Webhook for real-time processing
            "server_url": f"https://yourdomain.com/api/webhooks/vapi/{lead_id}",
            "server_url_secret": "your_webhook_secret",
            
            # Call settings
            "first_message": self._get_greeting_for_lead(lead_context),
            "end_call_function_enabled": True,
            "recording_enabled": True,
            "transcription_enabled": True,
            "reduce_latency": True,
            "response_delay_seconds": 0.5,
            "max_duration_seconds": 1200,  # 20 minutes
            "amd_enabled": True,  # Answering machine detection
            
            # Optional metadata
            "metadata": {
                "lead_id": lead_id,
                "agent_type": agent_type,
                "objective": objective
            },
            
            # Webhook events to receive
            "webhook_events": ["call-initiated", "call-completed", "transcription-update", "function-call"]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/call",
                    headers=self.headers,
                    json=call_config,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating call: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Vapi API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating call with Vapi: {e}")
            return self._get_mock_call(lead_id, phone_number)
    
    async def handle_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Vapi webhook events
        
        Args:
            event: Webhook event data
            
        Returns:
            Response to the webhook
        """
        event_type = event.get("event")
        call_id = event.get("call_id")
        metadata = event.get("metadata", {})
        lead_id = metadata.get("lead_id")
        
        logger.info(f"Received Vapi webhook event: {event_type} for call {call_id}")
        
        if event_type == "call-initiated":
            # Call was initiated
            await self._handle_call_initiated(event)
            return {"success": True}
        
        elif event_type == "call-completed":
            # Call has ended
            await self._handle_call_completed(event)
            return {"success": True}
        
        elif event_type == "transcription-update":
            # Real-time transcription update
            await self._handle_transcription_update(event)
            return {"success": True}
        
        elif event_type == "function-call":
            # Function call from the AI
            return await self._handle_function_call(event)
        
        return {"success": True}
    
    async def _handle_call_initiated(self, event: Dict[str, Any]):
        """Handle call-initiated event"""
        call_id = event.get("call_id")
        metadata = event.get("metadata", {})
        lead_id = metadata.get("lead_id")
        
        # Store call initiation in memory
        if self.mem0_client and lead_id:
            await self.mem0_client.store_memory(
                user_id=lead_id,
                memory_data={
                    "event": "call_initiated",
                    "call_id": call_id,
                    "timestamp": datetime.now().isoformat()
                },
                memory_type="contextual",
                metadata={
                    "event_type": "call_initiated",
                    "call_id": call_id
                }
            )
    
    async def _handle_call_completed(self, event: Dict[str, Any]):
        """Handle call-completed event"""
        call_id = event.get("call_id")
        metadata = event.get("metadata", {})
        lead_id = metadata.get("lead_id")
        call_summary = event.get("summary", {})
        transcript = event.get("transcript", "")
        
        # Store call summary in memory
        if self.mem0_client and lead_id:
            # Store full transcript
            await self.mem0_client.store_memory(
                user_id=lead_id,
                memory_data={
                    "event": "call_completed",
                    "call_id": call_id,
                    "transcript": transcript,
                    "summary": call_summary,
                    "timestamp": datetime.now().isoformat()
                },
                memory_type="factual",
                metadata={
                    "event_type": "call_completed",
                    "call_id": call_id
                }
            )
            
            # Extract insights and store as multi-layered memory
            await self._extract_and_store_call_insights(lead_id, call_id, transcript, call_summary)
    
    async def _handle_transcription_update(self, event: Dict[str, Any]):
        """Handle transcription-update event"""
        call_id = event.get("call_id")
        metadata = event.get("metadata", {})
        lead_id = metadata.get("lead_id")
        transcript = event.get("transcript", "")
        
        # For real-time processing, we could analyze the transcript
        # and take actions, but for MVP we'll just log it
        logger.info(f"Transcription update for call {call_id}: {transcript[:100]}...")
    
    async def _handle_function_call(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle function-call event
        
        Args:
            event: Function call event data
            
        Returns:
            Response to the function call
        """
        call_id = event.get("call_id")
        metadata = event.get("metadata", {})
        lead_id = metadata.get("lead_id")
        function_name = event.get("function", {}).get("name")
        function_args = event.get("function", {}).get("arguments", {})
        
        logger.info(f"Function call {function_name} for call {call_id}")
        
        # Handle different functions
        if function_name == "schedule_appointment":
            return await self._handle_schedule_appointment(lead_id, function_args)
        
        elif function_name == "get_property_details":
            return await self._handle_get_property_details(lead_id, function_args)
        
        elif function_name == "log_lead_information":
            return await self._handle_log_lead_information(lead_id, function_args)
        
        elif function_name == "end_call":
            return await self._handle_end_call(lead_id, function_args)
        
        # Default response for unknown functions
        return {
            "content": "I'm unable to process that request at the moment."
        }
    
    async def _handle_schedule_appointment(
        self, 
        lead_id: str, 
        args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle schedule_appointment function call"""
        # In a real implementation, this would integrate with a calendar system
        date = args.get("date")
        time = args.get("time")
        property_address = args.get("property_address")
        
        # For MVP, just store the appointment request
        if self.mem0_client and lead_id:
            await self.mem0_client.store_memory(
                user_id=lead_id,
                memory_data={
                    "event": "appointment_requested",
                    "date": date,
                    "time": time,
                    "property_address": property_address,
                    "timestamp": datetime.now().isoformat()
                },
                memory_type="factual",
                metadata={
                    "event_type": "appointment_requested"
                }
            )
        
        return {
            "content": f"I've scheduled a showing for {date} at {time} for the property at {property_address}. You'll receive a confirmation email shortly."
        }
    
    async def _handle_get_property_details(
        self, 
        lead_id: str, 
        args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get_property_details function call"""
        property_id = args.get("property_id")
        property_address = args.get("property_address")
        
        # In a real implementation, this would query a property database
        # For MVP, return mock data
        property_details = {
            "address": property_address or "123 Main St",
            "price": "$450,000",
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1800,
            "year_built": 2010,
            "description": "Beautiful modern home with updated kitchen, hardwood floors, and large backyard."
        }
        
        return {
            "content": f"Here are the details for the property at {property_details['address']}: It's priced at {property_details['price']}, has {property_details['bedrooms']} bedrooms and {property_details['bathrooms']} bathrooms, with {property_details['square_feet']} square feet. It was built in {property_details['year_built']}. {property_details['description']}"
        }
    
    async def _handle_log_lead_information(
        self, 
        lead_id: str, 
        args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle log_lead_information function call"""
        # Store lead information in memory
        if self.mem0_client and lead_id:
            await self.mem0_client.store_memory(
                user_id=lead_id,
                memory_data=args,
                memory_type="factual",
                metadata={
                    "event_type": "lead_information_update"
                }
            )
        
        return {
            "content": "I've updated your information in our system."
        }
    
    async def _handle_end_call(
        self, 
        lead_id: str, 
        args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle end_call function call"""
        reason = args.get("reason", "Conversation completed")
        
        # For MVP, just acknowledge the end call request
        return {
            "content": "Thank you for your time today. I'll follow up with more information via email. Have a great day!",
            "end_call": True
        }
    
    async def _extract_and_store_call_insights(
        self,
        lead_id: str,
        call_id: str,
        transcript: str,
        call_summary: Dict[str, Any]
    ):
        """Extract insights from call and store in multi-layered memory"""
        # This would typically use an AI model to analyze the call
        # For MVP, we'll use a simplified approach with mock data
        
        # Mock interaction and analysis data
        interaction = {
            "type": "voice_call",
            "channel": "voice",
            "agent_used": call_summary.get("agent_type", "unknown"),
            "factual_statements": call_summary.get("key_points", []),
            "expressed_preferences": call_summary.get("preferences", {}),
            "mentioned_constraints": call_summary.get("constraints", {}),
            "property_requirements": call_summary.get("property_requirements", {}),
            "budget_details": call_summary.get("budget", {}),
            "timeline_indicators": call_summary.get("timeline", {}),
            "positive_interactions": call_summary.get("positive_moments", []),
            "situational_factors": call_summary.get("context", {}),
            "optimal_contact_times": call_summary.get("contact_preferences", []),
            "background_context": call_summary.get("background", {})
        }
        
        analysis = {
            "sentiment_trajectory": call_summary.get("sentiment_trajectory", []),
            "trust_building_moments": call_summary.get("trust_indicators", []),
            "emotional_triggers": call_summary.get("emotional_triggers", []),
            "communication_preferences": call_summary.get("communication_style", {}),
            "buying_indicators": call_summary.get("buying_signals", []),
            "objection_history": call_summary.get("objections", []),
            "decision_patterns": call_summary.get("decision_making", {}),
            "influence_analysis": call_summary.get("influence_factors", {}),
            "closing_indicators": call_summary.get("closing_readiness", {}),
            "channel_effectiveness": {"voice": call_summary.get("effectiveness_score", 0.7)}
        }
        
        # Store multi-layered memory
        if self.mem0_client:
            await self.mem0_client.store_multi_layered_memory(
                lead_id=lead_id,
                interaction=interaction,
                analysis=analysis
            )
    
    def _get_vapi_functions(self) -> List[Dict[str, Any]]:
        """Get the function definitions for Vapi"""
        return [
            {
                "name": "schedule_appointment",
                "description": "Schedule a property showing appointment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The date for the appointment (YYYY-MM-DD)"
                        },
                        "time": {
                            "type": "string",
                            "description": "The time for the appointment (HH:MM AM/PM)"
                        },
                        "property_address": {
                            "type": "string",
                            "description": "The address of the property to show"
                        }
                    },
                    "required": ["date", "time"]
                }
            },
            {
                "name": "get_property_details",
                "description": "Get details about a specific property",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "property_id": {
                            "type": "string",
                            "description": "The ID of the property"
                        },
                        "property_address": {
                            "type": "string",
                            "description": "The address of the property"
                        }
                    }
                }
            },
            {
                "name": "log_lead_information",
                "description": "Log information about the lead",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "budget_min": {
                            "type": "number",
                            "description": "The minimum budget"
                        },
                        "budget_max": {
                            "type": "number",
                            "description": "The maximum budget"
                        },
                        "bedrooms": {
                            "type": "number",
                            "description": "The number of bedrooms required"
                        },
                        "bathrooms": {
                            "type": "number",
                            "description": "The number of bathrooms required"
                        },
                        "property_type": {
                            "type": "string",
                            "description": "The type of property (house, condo, etc.)"
                        },
                        "timeline": {
                            "type": "string",
                            "description": "The timeline for buying/selling"
                        },
                        "areas_of_interest": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Areas or neighborhoods of interest"
                        }
                    }
                }
            },
            {
                "name": "end_call",
                "description": "End the call when appropriate",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "The reason for ending the call"
                        }
                    }
                }
            }
        ]
    
    def _select_voice_for_lead(self, lead_context: Dict[str, Any]) -> Dict[str, Any]:
        """Select the appropriate voice for the lead based on context"""
        # Default voice configuration
        voice_config = {
            "provider": "elevenlabs",
            "voice_id": "Antoni",  # Default to a professional male voice
            "stability": 0.7,
            "similarity_boost": 0.8
        }
        
        # Adjust based on lead preferences if available
        personality_type = lead_context.get("personality_type")
        if personality_type == "analytical":
            # More measured, professional voice
            voice_config["voice_id"] = "Antoni"
            voice_config["stability"] = 0.8
            voice_config["similarity_boost"] = 0.7
        elif personality_type == "driver":
            # More direct, confident voice
            voice_config["voice_id"] = "Adam"
            voice_config["stability"] = 0.6
            voice_config["similarity_boost"] = 0.7
        elif personality_type == "expressive":
            # More dynamic, engaging voice
            voice_config["voice_id"] = "Bella"
            voice_config["stability"] = 0.5
            voice_config["similarity_boost"] = 0.8
        elif personality_type == "amiable":
            # Warmer, friendlier voice
            voice_config["voice_id"] = "Elli"
            voice_config["stability"] = 0.7
            voice_config["similarity_boost"] = 0.9
        
        return voice_config
    
    def _get_default_objective(self, lead_context: Dict[str, Any]) -> str:
        """Get the default objective based on lead context"""
        # Determine objective based on relationship stage
        relationship_stage = lead_context.get("relationship_stage", "initial_contact")
        
        stage_to_objective = {
            "initial_contact": "Introduce and build rapport",
            "qualification": "Qualify needs and assess requirements",
            "nurturing": "Provide value and nurture relationship",
            "objection_handling": "Address concerns and overcome objections",
            "closing": "Secure commitment and move forward"
        }
        
        return stage_to_objective.get(relationship_stage, "Engage effectively and gather information")
    
    def _get_greeting_for_lead(self, lead_context: Dict[str, Any]) -> str:
        """Get the appropriate greeting for the lead"""
        # Basic personalization
        name = lead_context.get("name", "there")
        
        # Personalized greeting based on relationship stage
        relationship_stage = lead_context.get("relationship_stage", "initial_contact")
        
        if relationship_stage == "initial_contact":
            return f"Hello {name}, this is AI Closer calling from ABC Realty. Do you have a moment to chat about your real estate needs?"
        
        if relationship_stage == "qualification":
            return f"Hi {name}, it's AI Closer from ABC Realty following up on our previous conversation. I wanted to learn more about what you're looking for in your next property. Is now a good time to talk?"
        
        if relationship_stage == "nurturing":
            return f"Hello {name}, it's AI Closer from ABC Realty. I wanted to share some new properties that match your criteria and see how your home search is progressing. Do you have a few minutes?"
        
        if relationship_stage == "closing":
            return f"Hi {name}, it's AI Closer from ABC Realty. I'm calling about the property you expressed interest in. I have some updates I'd like to share. Is this a good time?"
        
        # Default greeting
        return f"Hello {name}, this is AI Closer from ABC Realty. How are you today?"
    
    def _get_mock_call(self, lead_id: str, phone_number: str) -> Dict[str, Any]:
        """Generate a mock call response for testing without API key"""
        call_id = str(uuid.uuid4())
        
        return {
            "call_id": call_id,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "phone_number": phone_number,
            "metadata": {
                "lead_id": lead_id
            },
            "message": "Call queued successfully (mock)"
        }
