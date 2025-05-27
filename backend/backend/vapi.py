import os
import json
import logging
import httpx
import time
from typing import Dict, Any, List, Optional, Union
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class VapiIntegration:
    """
    Implements full integration with Vapi.ai for voice conversations
    Uses OpenRouter or other configured LLMs via the agent system
    """
    def __init__(self, public_key: Optional[str] = None, private_key: Optional[str] = None):
        self.public_key = public_key
        self.private_key = private_key
        self.base_url = "https://api.vapi.ai/v1"
        self.headers = {}
        self.update_headers()
    
    def set_api_keys(self, public_key: str, private_key: str):
        """Set the Vapi API keys"""
        self.public_key = public_key
        self.private_key = private_key
        self.update_headers()
        
    def update_headers(self):
        """Update the headers with the current API keys"""
        if self.private_key:
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.private_key}"
            }
    
    def is_configured(self) -> bool:
        """Check if the Vapi integration is configured with valid API keys"""
        return bool(self.public_key and self.private_key)
    
    async def validate_keys(self) -> bool:
        """Validate that the API keys are correct by making a simple API call"""
        if not self.is_configured():
            return False
            
        try:
            # Try to list assistants as a simple validation
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/assistants",
                    headers=self.headers
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error validating Vapi API keys: {e}")
            return False
    
    async def list_assistants(self) -> List[Dict[str, Any]]:
        """List all assistants in the Vapi account"""
        if not self.is_configured():
            logger.error("Vapi API keys not configured")
            raise HTTPException(status_code=400, detail="Vapi API keys not configured")
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/assistants",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json().get("assistants", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while listing assistants: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Vapi API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error listing assistants from Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Vapi: {str(e)}")
    
    async def create_assistant(self, assistant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new assistant in Vapi"""
        if not self.is_configured():
            logger.error("Vapi API keys not configured")
            raise HTTPException(status_code=400, detail="Vapi API keys not configured")
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/assistants",
                    headers=self.headers,
                    json=assistant_data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating assistant: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Vapi API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating assistant in Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Vapi: {str(e)}")
    
    async def get_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """Get details of a specific assistant"""
        if not self.is_configured():
            logger.error("Vapi API keys not configured")
            raise HTTPException(status_code=400, detail="Vapi API keys not configured")
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/assistants/{assistant_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while getting assistant: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Vapi API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error getting assistant from Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Vapi: {str(e)}")
    
    async def create_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new call in Vapi"""
        if not self.is_configured():
            logger.error("Vapi API keys not configured")
            raise HTTPException(status_code=400, detail="Vapi API keys not configured")
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/calls",
                    headers=self.headers,
                    json=call_data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating call: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Vapi API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating call in Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Vapi: {str(e)}")
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """Get details of a specific call"""
        if not self.is_configured():
            logger.error("Vapi API keys not configured")
            raise HTTPException(status_code=400, detail="Vapi API keys not configured")
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/calls/{call_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while getting call: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Vapi API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error getting call from Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Vapi: {str(e)}")
    
    async def create_intelligent_call(
        self, 
        phone_number: str, 
        agent_config: Dict[str, Any],
        lead_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an intelligent call with a lead using a specialized AI agent
        
        Args:
            phone_number: The phone number to call
            agent_config: Configuration for the AI agent
            lead_context: Context about the lead from GHL and Mem0
            
        Returns:
            Dict containing the call details
        """
        if not self.is_configured():
            logger.error("Vapi API keys not configured")
            raise HTTPException(status_code=400, detail="Vapi API keys not configured")
        
        # Build dynamic system prompt with lead context
        system_prompt = self._build_system_prompt(agent_config, lead_context)
        
        # Configure voice based on lead preferences/analysis
        voice_config = self._select_optimal_voice(lead_context)
        
        # Configure agent functions
        functions = self._build_agent_functions(agent_config)
        
        # Prepare call config
        call_config = {
            "to": phone_number,
            "from": agent_config.get("from_number", "+12345678901"),  # Should be configured in settings
            
            # Voice settings
            "voice": voice_config,
            
            # AI model configuration
            "firstMessage": agent_config.get("first_message", "Hello, this is AI Closer calling from ABC Realty. How are you doing today?"),
            "model": {
                "provider": agent_config.get("llm_provider", "openai"),
                "model": agent_config.get("llm_model", "gpt-4o"),
                "temperature": agent_config.get("temperature", 0.7),
                "systemPrompt": system_prompt,
                "functions": functions
            },
            
            # Call options
            "recordingEnabled": True,
            "maxDuration": 900,  # 15 minutes max
            "endCallFunctionEnabled": True,
            "asyncMode": True,  # Process webhooks asynchronously
            
            # Webhook configuration
            "webhook": {
                "url": agent_config.get("webhook_url", ""),
                "headers": {
                    "Authorization": agent_config.get("webhook_auth", "")
                }
            }
        }
        
        try:
            return await self.create_call(call_config)
        except Exception as e:
            logger.error(f"Error creating intelligent call: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating call: {str(e)}")
    
    def _build_system_prompt(self, agent_config: Dict[str, Any], lead_context: Dict[str, Any]) -> str:
        """Build a dynamic system prompt with lead context"""
        agent_type = agent_config.get("type", "initial_contact")
        agent_name = agent_config.get("name", "AI Assistant")
        
        # Extract key lead information
        lead_name = lead_context.get("name", "the customer")
        personality_type = lead_context.get("personality_type", "unknown")
        relationship_stage = lead_context.get("relationship_stage", "initial_contact")
        property_preferences = lead_context.get("property_preferences", {})
        budget = lead_context.get("budget", {})
        
        # Format property preferences for prompt
        property_pref_str = ""
        if property_preferences:
            pref_points = []
            if "bedrooms" in property_preferences:
                pref_points.append(f"{property_preferences['bedrooms']} bedrooms")
            if "bathrooms" in property_preferences:
                pref_points.append(f"{property_preferences['bathrooms']} bathrooms")
            if "location" in property_preferences:
                pref_points.append(f"in {property_preferences['location']}")
            if "property_type" in property_preferences:
                pref_points.append(f"property type: {property_preferences['property_type']}")
                
            if pref_points:
                property_pref_str = f"Property preferences: {', '.join(pref_points)}"
        
        # Format budget for prompt
        budget_str = ""
        if budget:
            if "min" in budget and "max" in budget:
                budget_str = f"Budget range: ${budget['min']:,} - ${budget['max']:,}"
            elif "max" in budget:
                budget_str = f"Maximum budget: ${budget['max']:,}"
        
        # Build prompt based on agent type
        base_prompt = f"""
You are {agent_name}, a specialized AI agent for real estate lead conversion.

LEAD INTELLIGENCE:
- Name: {lead_name}
- Personality Type: {personality_type}
- Relationship Stage: {relationship_stage}
{property_pref_str}
{budget_str}
"""
        
        # Add agent-specific instructions
        if agent_type == "initial_contact":
            base_prompt += """
YOUR OBJECTIVE: Create a positive first impression, build initial rapport, and identify basic lead information.

GUIDELINES:
- Be warm, friendly, and professional
- Ask open-ended questions to encourage engagement
- Listen carefully and acknowledge what you hear
- Avoid being too sales-focused in initial contact
- Identify the best time and method for follow-up

COMMUNICATION STYLE:
- Use the lead's name frequently
- Find common ground quickly
- Show genuine interest in their real estate needs
- Provide immediate value in the conversation
- End with a clear next step
"""
        elif agent_type == "qualifier":
            base_prompt += """
YOUR OBJECTIVE: Assess the lead's needs, determine budget, identify timeline, and understand property preferences.

GUIDELINES:
- Ask direct but conversational questions
- Listen for buying signals and objections
- Avoid making assumptions about needs or budget
- Balance gathering information with providing value

QUALIFICATION CRITERIA:
- Budget: What price range are they considering? Pre-approved?
- Timeline: How soon do they need to buy/sell?
- Motivation: Why are they looking now?
- Authority: Are they the decision-maker?
- Need: What specific property requirements do they have?
"""
        elif agent_type == "nurturer":
            base_prompt += """
YOUR OBJECTIVE: Build meaningful long-term relationship, provide value, educate the lead, and keep your company top-of-mind.

GUIDELINES:
- Personalize all communications based on previous interactions
- Share relevant content and market insights
- Check in regularly without being pushy
- Demonstrate expertise through helpful information

VALUE PROVISION STRATEGIES:
- Share market updates relevant to their search criteria
- Provide educational content about the buying/selling process
- Offer neighborhood insights and local information
- Answer common questions before they ask
"""
        elif agent_type == "objection_handler":
            base_prompt += """
YOUR OBJECTIVE: Identify and address objections, acknowledge concerns with empathy, and move the conversation forward.

GUIDELINES:
- Listen fully before responding
- Never argue or become defensive
- Use the "feel, felt, found" technique when appropriate
- Provide specific examples and evidence

COMMON OBJECTIONS:
- Price: "That's more than we want to spend"
- Timing: "We're not ready to make a decision yet"
- Agent value: "Why should we work with you?"
- Property concerns: "The house needs too much work"
- Area concerns: "We're not sure about the neighborhood"
"""
        elif agent_type == "closer":
            base_prompt += """
YOUR OBJECTIVE: Recognize closing opportunities, create urgency, ask for commitments, and secure next steps.

GUIDELINES:
- Be direct but not pushy
- Summarize value and benefits
- Use assumptive language when appropriate
- Present clear options rather than yes/no questions
- Confirm understanding of terms and next steps

CLOSING TECHNIQUES:
- Assumptive close: "When would you like to schedule the viewing?"
- Alternative close: "Would Tuesday or Thursday work better for the showing?"
- Summary close: "Based on everything we've discussed, it seems like this property meets your needs for [reasons]."
- Urgency close: "This neighborhood has seen properties sell within days recently."
"""
        else:
            # Generic agent instructions
            base_prompt += """
YOUR OBJECTIVE: Build rapport, understand the lead's needs, and guide them through the real estate process.

GUIDELINES:
- Be conversational and natural, not scripted
- Focus on being helpful rather than selling
- Listen carefully and respond to the lead's specific needs
- Provide value in every interaction
"""
        
        # Add memory highlights if available
        if "memories" in lead_context:
            memories = lead_context["memories"]
            if memories:
                base_prompt += "\nKEY MEMORIES FROM PREVIOUS INTERACTIONS:\n"
                for memory in memories[:5]:  # Limit to top 5 memories
                    base_prompt += f"- {memory}\n"
        
        # Add general conversation guidelines
        base_prompt += """
CONVERSATION GUIDELINES:
1. Be natural and conversational, avoiding robotic or overly formal language
2. Use active listening techniques to acknowledge and validate the lead's responses
3. Adapt your communication style based on the lead's personality type
4. Keep responses concise but informative
5. Always be honest and transparent
6. If you don't know something, admit it and offer to find out
7. Never make up information about properties or the market
8. Focus on building a relationship rather than just making a sale
"""
        
        return base_prompt
    
    def _select_optimal_voice(self, lead_context: Dict[str, Any]) -> Dict[str, Any]:
        """Select the optimal voice configuration based on lead context"""
        # Default voice settings
        default_voice = {
            "provider": "elevenlabs",
            "voiceId": "pNInz6obpgDQGcFmaJgB",  # Adam - Male American
            "stability": 0.7,
            "similarityBoost": 0.5
        }
        
        # Adapt voice selection based on lead preferences if available
        if lead_context.get("voice_preference") == "female":
            # Rachel - Female American
            default_voice["voiceId"] = "21m00Tcm4TlvDq8ikWAM"
            
        # You could customize further based on other lead attributes
        personality = lead_context.get("personality_type", "").lower()
        if personality == "analytical":
            # More stable, precise voice
            default_voice["stability"] = 0.8
            default_voice["similarityBoost"] = 0.3
        elif personality == "expressive":
            # More dynamic, expressive voice
            default_voice["stability"] = 0.5
            default_voice["similarityBoost"] = 0.7
            
        return default_voice
    
    def _build_agent_functions(self, agent_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build agent functions configuration based on agent type"""
        agent_type = agent_config.get("type", "initial_contact")
        
        # Common functions for all agents
        common_functions = [
            {
                "name": "schedule_appointment",
                "description": "Schedule a property viewing or consultation appointment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The date for the appointment in YYYY-MM-DD format"
                        },
                        "time": {
                            "type": "string",
                            "description": "The time for the appointment in HH:MM format"
                        },
                        "appointment_type": {
                            "type": "string",
                            "description": "Type of appointment (viewing, consultation, etc.)"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Any additional notes for the appointment"
                        }
                    },
                    "required": ["date", "time", "appointment_type"]
                }
            },
            {
                "name": "send_property_listings",
                "description": "Send property listings matching criteria to the lead",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "property_type": {
                            "type": "string",
                            "description": "Type of property (house, condo, etc.)"
                        },
                        "bedrooms": {
                            "type": "number",
                            "description": "Minimum number of bedrooms"
                        },
                        "bathrooms": {
                            "type": "number",
                            "description": "Minimum number of bathrooms"
                        },
                        "price_min": {
                            "type": "number",
                            "description": "Minimum price"
                        },
                        "price_max": {
                            "type": "number",
                            "description": "Maximum price"
                        },
                        "location": {
                            "type": "string",
                            "description": "Desired location or neighborhood"
                        }
                    }
                }
            }
        ]
        
        # Agent-specific functions
        if agent_type == "qualifier":
            qualifier_functions = [
                {
                    "name": "qualify_budget",
                    "description": "Record the lead's budget information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "min_price": {
                                "type": "number",
                                "description": "Minimum price the lead is considering"
                            },
                            "max_price": {
                                "type": "number",
                                "description": "Maximum price the lead is considering"
                            },
                            "pre_approved": {
                                "type": "boolean",
                                "description": "Whether the lead is pre-approved for financing"
                            },
                            "financing_type": {
                                "type": "string",
                                "description": "Type of financing (cash, conventional, FHA, etc.)"
                            }
                        }
                    }
                },
                {
                    "name": "record_property_preferences",
                    "description": "Record the lead's property preferences",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "property_type": {
                                "type": "string",
                                "description": "Type of property (house, condo, townhouse, etc.)"
                            },
                            "bedrooms": {
                                "type": "number",
                                "description": "Desired number of bedrooms"
                            },
                            "bathrooms": {
                                "type": "number",
                                "description": "Desired number of bathrooms"
                            },
                            "locations": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "Desired locations or neighborhoods"
                            },
                            "must_haves": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "Features that are must-haves"
                            }
                        }
                    }
                }
            ]
            return common_functions + qualifier_functions
        
        elif agent_type == "objection_handler":
            objection_functions = [
                {
                    "name": "record_objection",
                    "description": "Record an objection raised by the lead",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "objection_type": {
                                "type": "string",
                                "description": "Type of objection (price, timing, property, agent, etc.)"
                            },
                            "objection_details": {
                                "type": "string",
                                "description": "Specific details about the objection"
                            },
                            "resolution_status": {
                                "type": "string",
                                "description": "Status of resolution (resolved, pending, escalated)"
                            },
                            "resolution_notes": {
                                "type": "string",
                                "description": "Notes on how the objection was addressed"
                            }
                        },
                        "required": ["objection_type", "objection_details"]
                    }
                }
            ]
            return common_functions + objection_functions
            
        elif agent_type == "closer":
            closer_functions = [
                {
                    "name": "create_opportunity",
                    "description": "Create a sales opportunity in GHL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the opportunity"
                            },
                            "value": {
                                "type": "number",
                                "description": "Monetary value of the opportunity"
                            },
                            "stage": {
                                "type": "string",
                                "description": "Pipeline stage (e.g., 'Interested', 'Viewing Scheduled', 'Offer Made')"
                            },
                            "notes": {
                                "type": "string",
                                "description": "Additional notes about the opportunity"
                            }
                        },
                        "required": ["title", "value"]
                    }
                }
            ]
            return common_functions + closer_functions
            
        # Return common functions for other agent types
        return common_functions
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhooks from Vapi.ai
        
        Args:
            webhook_data: The webhook payload from Vapi
            
        Returns:
            Dict containing the processed result
        """
        webhook_type = webhook_data.get("type")
        call_id = webhook_data.get("call_id")
        
        logger.info(f"Received Vapi webhook: {webhook_type} for call {call_id}")
        
        if webhook_type == "function-call":
            return await self._handle_function_call(webhook_data)
            
        elif webhook_type == "call-started":
            # Just log for now, could update status in GHL/Mem0
            logger.info(f"Call started: {call_id}")
            return {"success": True}
            
        elif webhook_type == "call-ended":
            return await self._handle_call_ended(webhook_data)
            
        elif webhook_type == "transcription-update":
            # Could store in Mem0 or process for real-time insights
            logger.info(f"Transcription update for call {call_id}")
            return {"success": True}
            
        else:
            logger.warning(f"Unknown webhook type: {webhook_type}")
            return {"success": True}
    
    async def _handle_function_call(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle function calls from Vapi"""
        function_call = webhook_data.get("function_call", {})
        function_name = function_call.get("name")
        function_args = function_call.get("arguments", {})
        call_id = webhook_data.get("call_id")
        
        logger.info(f"Function call: {function_name} with args: {function_args}")
        
        # Handle different functions
        if function_name == "schedule_appointment":
            # Implementation would create an appointment in GHL
            # For now, we'll just log and return a mock response
            logger.info(f"Scheduling appointment: {function_args}")
            
            # This response would be sent back to the call
            return {
                "content": f"Great! I've scheduled an appointment for {function_args.get('date')} at {function_args.get('time')}. You'll receive a confirmation shortly.",
                "function_response": {
                    "appointment_id": "app_123456",
                    "status": "confirmed"
                }
            }
            
        elif function_name == "send_property_listings":
            # Implementation would query listings and send to lead
            logger.info(f"Sending property listings: {function_args}")
            
            return {
                "content": f"I've found several properties matching your criteria. I'll send them to you right away. Is there anything specific you're looking for that I should highlight?",
                "function_response": {
                    "listings_sent": 5,
                    "status": "sent"
                }
            }
            
        elif function_name == "qualify_budget":
            # Implementation would update lead profile in GHL and Mem0
            logger.info(f"Qualifying budget: {function_args}")
            
            return {
                "content": f"Thank you for sharing your budget information. This helps us find the right properties for you. Based on what you've shared, properties in the ${function_args.get('min_price', 0):,} to ${function_args.get('max_price', 0):,} range would be appropriate.",
                "function_response": {
                    "status": "recorded"
                }
            }
            
        else:
            logger.warning(f"Unknown function: {function_name}")
            return {
                "content": "I understand. Let me make a note of that and we can continue our conversation.",
                "function_response": {
                    "status": "unknown_function"
                }
            }
    
    async def _handle_call_ended(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle call ended webhook from Vapi"""
        call_id = webhook_data.get("call_id")
        
        # Get full call details including transcript
        call_details = await self.get_call(call_id)
        
        # This would be implemented to:
        # 1. Store call transcript and metadata in Mem0
        # 2. Update GHL with call summary and outcome
        # 3. Trigger post-call analysis with the lead's assigned agent
        
        logger.info(f"Call ended: {call_id}, duration: {call_details.get('duration')}s")
        
        # For now, just return success
        return {"success": True}
    
    async def analyze_call(self, call_id: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a completed call using the assigned agent's LLM
        
        Args:
            call_id: The Vapi call ID
            agent_config: Configuration for the AI agent that will analyze the call
            
        Returns:
            Dict containing the analysis results
        """
        # Get call details including transcript
        call_details = await self.get_call(call_id)
        transcript = call_details.get("transcript", "")
        
        # In a real implementation, this would use the OpenRouter API with the
        # configured LLM to analyze the transcript
        
        # Mock analysis for now
        analysis = {
            "call_id": call_id,
            "duration": call_details.get("duration", 0),
            "sentiment": "positive",
            "intent_classification": {
                "primary_intent": "information_gathering",
                "confidence": 0.85
            },
            "buying_signals": [
                {"signal": "Asked about financing options", "confidence": 0.75},
                {"signal": "Requested additional property photos", "confidence": 0.9}
            ],
            "objections_detected": [
                {"objection": "Concerned about property taxes", "confidence": 0.8}
            ],
            "next_best_action": "Send property listings with tax information",
            "follow_up_recommended": True,
            "follow_up_timeframe": "2 days",
            "key_moments": [
                {"time": 45, "description": "Expressed interest in downtown properties"},
                {"time": 120, "description": "Mentioned budget constraints"},
                {"time": 180, "description": "Asked about school districts"}
            ],
            "summary": "Lead is interested in downtown properties but has concerns about property taxes. They're in the early stages of their search and would like more information about 3-bedroom properties in the $400,000-$500,000 range. Schools are important, and they're planning to buy within 3-4 months."
        }
        
        return analysis