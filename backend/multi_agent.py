import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
from enum import Enum
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    INITIAL_CONTACT = "initial_contact"
    QUALIFIER = "qualifier"
    NURTURER = "nurturer"
    OBJECTION_HANDLER = "objection_handler"
    CLOSER = "closer"
    APPOINTMENT_SETTER = "appointment_setter"
    ORCHESTRATOR = "orchestrator"

class AgentOrchestrator:
    """Advanced agent orchestration system using LangChain patterns"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        self.is_initialized = False
        
        # Initialize if API key is available
        if self.openai_api_key:
            self._initialize()
    
    def _initialize(self):
        """Initialize LangChain components"""
        try:
            # In a real implementation, this would initialize LangChain
            # For MVP, we'll mock the initialization
            self.is_initialized = True
            logger.info("Agent orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing agent orchestrator: {e}")
            raise HTTPException(status_code=500, detail=f"Agent orchestration initialization error: {str(e)}")
    
    def set_api_key(self, openai_api_key: str):
        """Set OpenAI API key and initialize"""
        self.openai_api_key = openai_api_key
        self._initialize()
    
    async def select_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select the most appropriate agent based on context
        
        Args:
            context: Dict containing lead context, current objective, etc.
        
        Returns:
            Dict containing selected agent information
        """
        if not self.is_initialized:
            logger.warning("Agent orchestrator not initialized, using rule-based selection")
            return await self._rule_based_agent_selection(context)
        
        # In a real implementation, this would use LangChain for more sophisticated selection
        # For MVP, we'll use rule-based selection
        return await self._rule_based_agent_selection(context)
    
    async def _rule_based_agent_selection(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simple rule-based agent selection for MVP"""
        # Extract context variables
        relationship_stage = context.get("lead_context", {}).get("relationship_stage", "initial_contact")
        objective = context.get("objective", "")
        channel = context.get("channel", "")
        
        # Default to initial contact agent
        selected_agent_type = AgentType.INITIAL_CONTACT
        
        # Basic mapping of stages to agent types
        stage_to_agent = {
            "initial_contact": AgentType.INITIAL_CONTACT,
            "qualification": AgentType.QUALIFIER,
            "nurturing": AgentType.NURTURER,
            "objection_handling": AgentType.OBJECTION_HANDLER,
            "closing": AgentType.CLOSER
        }
        
        # Override based on specific objectives
        if "appointment" in objective.lower() or "schedule" in objective.lower():
            selected_agent_type = AgentType.APPOINTMENT_SETTER
        elif "objection" in objective.lower() or "concern" in objective.lower():
            selected_agent_type = AgentType.OBJECTION_HANDLER
        elif "qualify" in objective.lower() or "assessment" in objective.lower():
            selected_agent_type = AgentType.QUALIFIER
        elif "close" in objective.lower() or "commit" in objective.lower():
            selected_agent_type = AgentType.CLOSER
        elif "nurture" in objective.lower() or "follow up" in objective.lower():
            selected_agent_type = AgentType.NURTURER
        else:
            # Use relationship stage mapping
            selected_agent_type = stage_to_agent.get(relationship_stage, AgentType.INITIAL_CONTACT)
        
        # Get the selected agent's details
        agent = self._get_agent_details(selected_agent_type)
        
        # Add selection reasoning
        agent["selection_reasoning"] = f"Selected {agent['name']} based on relationship stage '{relationship_stage}' and objective '{objective}'."
        agent["type"] = selected_agent_type
        agent["confidence"] = 0.85  # Mock confidence score
        
        return agent
    
    def _get_agent_details(self, agent_type: AgentType) -> Dict[str, Any]:
        """Get agent details based on type"""
        agents = {
            AgentType.INITIAL_CONTACT: {
                "name": "Initial Contact Agent",
                "description": "Specializes in first impressions and rapport building",
                "key_capabilities": ["personality detection", "rapport building", "interest assessment"],
                "success_metrics": ["response_rate", "engagement_score", "rapport_level"]
            },
            AgentType.QUALIFIER: {
                "name": "Qualification Agent",
                "description": "Specializes in lead qualification and needs assessment",
                "key_capabilities": ["needs analysis", "budget qualification", "timeline assessment"],
                "success_metrics": ["qualification_completeness", "accuracy_score"]
            },
            AgentType.NURTURER: {
                "name": "Nurturing Agent",
                "description": "Specializes in relationship building and value provision",
                "key_capabilities": ["value delivery", "trust building", "education"],
                "success_metrics": ["trust_level", "engagement_depth", "relationship_progression"]
            },
            AgentType.OBJECTION_HANDLER: {
                "name": "Objection Handler Agent",
                "description": "Specializes in objection resolution and concern addressing",
                "key_capabilities": ["objection classification", "response generation", "concern resolution"],
                "success_metrics": ["objection_resolution_rate", "trust_maintenance"]
            },
            AgentType.CLOSER: {
                "name": "Closing Agent",
                "description": "Specializes in deal closing and commitment securing",
                "key_capabilities": ["closing technique selection", "urgency creation", "commitment securing"],
                "success_metrics": ["closing_rate", "deal_size", "time_to_close"]
            },
            AgentType.APPOINTMENT_SETTER: {
                "name": "Appointment Agent",
                "description": "Specializes in appointment scheduling and confirmation",
                "key_capabilities": ["calendar management", "confirmation sending", "reminder scheduling"],
                "success_metrics": ["appointment_rate", "show_up_rate", "conversion_rate"]
            },
            AgentType.ORCHESTRATOR: {
                "name": "Orchestrator Agent",
                "description": "Manages overall conversation flow and agent selection",
                "key_capabilities": ["agent selection", "context management", "conversation planning"],
                "success_metrics": ["context_retention", "appropriate_handoffs", "user_satisfaction"]
            }
        }
        
        return agents.get(agent_type, agents[AgentType.INITIAL_CONTACT])
    
    async def generate_response(self, 
                               agent_type: str, 
                               prompt: str, 
                               lead_context: Dict[str, Any],
                               knowledge_context: Optional[List[Dict[str, Any]]] = None,
                               channel: str = "chat") -> Dict[str, Any]:
        """
        Generate a response using the specified agent
        
        Args:
            agent_type: Type of agent to use
            prompt: User prompt/message
            lead_context: Context about the lead
            knowledge_context: Optional knowledge base context
            channel: The communication channel (chat, sms, email, voice)
            
        Returns:
            Dict containing the generated response and metadata
        """
        if not self.is_initialized:
            logger.warning("Agent orchestrator not initialized, using mock response")
            return self._generate_mock_response(agent_type, prompt, lead_context, channel)
        
        # In a real implementation, this would use LangChain for response generation
        # For MVP, we'll use mock responses
        return self._generate_mock_response(agent_type, prompt, lead_context, channel)
    
    def _generate_mock_response(self, 
                              agent_type: str, 
                              prompt: str, 
                              lead_context: Dict[str, Any],
                              channel: str) -> Dict[str, Any]:
        """Generate a mock response for testing without API keys"""
        personality_type = lead_context.get("personality_type", "analytical")
        property_prefs = lead_context.get("property_preferences", {})
        bedrooms = property_prefs.get("bedrooms", "3")
        location = property_prefs.get("location", "your area")
        
        # Mock responses based on agent type
        responses = {
            AgentType.INITIAL_CONTACT: f"Hi there! I'm excited to help you with your real estate journey. Could you tell me a bit about what you're looking for in a property?",
            AgentType.QUALIFIER: f"Based on what you've shared, it sounds like you're looking for a property with {bedrooms} bedrooms. What's your ideal price range?",
            AgentType.NURTURER: f"I thought you might be interested in this new market report for {location}. Property values have increased 5% since we last spoke.",
            AgentType.OBJECTION_HANDLER: f"I understand your concern about the price. Many of my clients have felt the same way initially. Have you considered looking at properties in nearby neighborhoods that offer similar features at a lower price point?",
            AgentType.CLOSER: f"Based on everything we've discussed, this property at 123 Main St seems to be a perfect match for your needs. Would you like to move forward with making an offer?",
            AgentType.APPOINTMENT_SETTER: f"I'd be happy to show you the property at 123 Main St. Would Tuesday at 2pm or Wednesday at 4pm work better for your schedule?"
        }
        
        agent_type_enum = AgentType(agent_type) if agent_type in [e.value for e in AgentType] else AgentType.INITIAL_CONTACT
        response_text = responses.get(agent_type_enum, responses[AgentType.INITIAL_CONTACT])
        
        # Adjust response based on personality type
        if personality_type == "analytical":
            response_text += " I can provide detailed information and statistics if that would be helpful."
        elif personality_type == "driver":
            response_text += " I respect that you're busy, so I'll keep things direct and focused on results."
        elif personality_type == "expressive":
            response_text += " I'm excited to help you find the perfect property that matches your vision!"
        elif personality_type == "amiable":
            response_text += " I'm here to make this process as smooth and comfortable as possible for you."
        
        agent_details = self._get_agent_details(agent_type_enum)
        
        return {
            "response": response_text,
            "agent_type": agent_type,
            "agent_name": agent_details["name"],
            "confidence": 0.95,
            "analysis": {
                "intent_detected": "information_gathering" if agent_type_enum == AgentType.QUALIFIER else "relationship_building",
                "sentiment": "positive",
                "next_best_action": "schedule_showing" if "property" in prompt.lower() else "follow_up_call",
                "personality_matched": personality_type
            },
            "timestamp": datetime.now().isoformat(),
            "channel": channel
        }
    
    async def orchestrate_conversation(self, 
                                      message: str, 
                                      lead_context: Dict[str, Any],
                                      conversation_history: Optional[List[Dict[str, Any]]] = None,
                                      channel: str = "chat") -> Dict[str, Any]:
        """
        Orchestrate a conversation from start to finish
        
        Args:
            message: The user's message
            lead_context: Context about the lead
            conversation_history: Optional conversation history
            channel: The communication channel
            
        Returns:
            Dict containing the orchestrated response and metadata
        """
        # Determine the appropriate objective based on message content and lead context
        objective = await self._determine_objective(message, lead_context, conversation_history)
        
        # Select the appropriate agent
        agent = await self.select_agent({
            "lead_context": lead_context,
            "objective": objective,
            "channel": channel,
            "conversation_history": conversation_history
        })
        
        # Generate response using the selected agent
        response = await self.generate_response(
            agent_type=agent["type"],
            prompt=message,
            lead_context=lead_context,
            channel=channel
        )
        
        # Update conversation metadata
        conversation_data = {
            "id": str(uuid.uuid4()),
            "lead_id": lead_context.get("id"),
            "channel": channel,
            "agent_type": agent["type"],
            "message": message,
            "response": response["response"],
            "analysis": response.get("analysis", {}),
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "conversation": conversation_data,
            "agent_used": agent,
            "response": response,
            "objective": objective
        }
    
    async def _determine_objective(self, 
                                 message: str, 
                                 lead_context: Dict[str, Any],
                                 conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """Determine the conversation objective based on message content and lead context"""
        
        # Simple keyword-based objective determination for MVP
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["appointment", "schedule", "meet", "showing"]):
            return "schedule_appointment"
        
        if any(word in message_lower for word in ["price", "cost", "expensive", "afford", "budget"]):
            return "address_price_objection"
        
        if any(word in message_lower for word in ["looking", "search", "find", "want", "need"]):
            return "qualify_needs"
        
        # Default objectives based on relationship stage
        stage_to_objective = {
            "initial_contact": "build_rapport",
            "qualification": "qualify_needs",
            "nurturing": "provide_value",
            "objection_handling": "resolve_objections",
            "closing": "secure_commitment"
        }
        
        relationship_stage = lead_context.get("relationship_stage", "initial_contact")
        return stage_to_objective.get(relationship_stage, "build_rapport")
