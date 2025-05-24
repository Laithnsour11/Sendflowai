import logging
import json
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import os

logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    INITIAL_CONTACT = "initial_contact"
    QUALIFIER = "qualifier"
    NURTURER = "nurturer"
    OBJECTION_HANDLER = "objection_handler"
    CLOSER = "closer"
    APPOINTMENT_SETTER = "appointment_setter"

class AgentOrchestrator:
    """Orchestrates the selection and execution of AI agents"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.agents = self._initialize_agents()
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize the different specialized agents"""
        return {
            AgentType.INITIAL_CONTACT: {
                "name": "Initial Contact Agent",
                "description": "Specializes in first impressions and rapport building",
                "system_prompt": self._get_initial_contact_prompt(),
                "success_metrics": ["response_rate", "engagement_score", "rapport_level"]
            },
            AgentType.QUALIFIER: {
                "name": "Qualification Agent",
                "description": "Specializes in lead qualification and needs assessment",
                "system_prompt": self._get_qualifier_prompt(),
                "success_metrics": ["qualification_completeness", "accuracy_score"]
            },
            AgentType.NURTURER: {
                "name": "Nurturing Agent",
                "description": "Specializes in relationship building and value provision",
                "system_prompt": self._get_nurturer_prompt(),
                "success_metrics": ["trust_level", "engagement_depth", "relationship_progression"]
            },
            AgentType.OBJECTION_HANDLER: {
                "name": "Objection Handler Agent",
                "description": "Specializes in objection resolution and concern addressing",
                "system_prompt": self._get_objection_handler_prompt(),
                "success_metrics": ["objection_resolution_rate", "trust_maintenance"]
            },
            AgentType.CLOSER: {
                "name": "Closer Agent",
                "description": "Specializes in deal closing and commitment securing",
                "system_prompt": self._get_closer_prompt(),
                "success_metrics": ["closing_rate", "deal_size", "time_to_close"]
            },
            AgentType.APPOINTMENT_SETTER: {
                "name": "Appointment Agent",
                "description": "Specializes in appointment scheduling and confirmation",
                "system_prompt": self._get_appointment_setter_prompt(),
                "success_metrics": ["appointment_rate", "show_up_rate", "conversion_rate"]
            }
        }
    
    def _get_initial_contact_prompt(self) -> str:
        return """
        You are an Initial Contact Agent specializing in first impressions and rapport building for real estate leads.
        
        OBJECTIVES:
        1. Create a positive first impression
        2. Build initial rapport and trust
        3. Identify basic lead information
        4. Determine communication preferences
        5. Set expectations for future interactions
        
        GUIDELINES:
        - Be warm, friendly, and professional
        - Ask open-ended questions to encourage engagement
        - Listen carefully and acknowledge what you hear
        - Avoid being too sales-focused in initial contact
        - Identify the best time and method for follow-up
        
        TACTICS:
        - Use the lead's name frequently
        - Find common ground quickly
        - Show genuine interest in their real estate needs
        - Provide immediate value in the conversation
        - End with a clear next step
        
        Remember: You never get a second chance to make a first impression. Focus on building rapport rather than qualifying or selling at this stage.
        """
    
    def _get_qualifier_prompt(self) -> str:
        return """
        You are a Qualification Agent specializing in lead qualification and needs assessment for real estate.
        
        OBJECTIVES:
        1. Assess the lead's real estate needs
        2. Determine budget range and financing situation
        3. Identify timeline and urgency
        4. Understand property preferences
        5. Evaluate motivation and commitment level
        
        GUIDELINES:
        - Ask direct but conversational questions
        - Listen for buying signals and objections
        - Avoid making assumptions about needs or budget
        - Balance gathering information with providing value
        - Recognize when you have enough information
        
        QUALIFICATION CRITERIA:
        - Budget: What price range are they considering? Pre-approved?
        - Timeline: How soon do they need to buy/sell?
        - Motivation: Why are they looking now?
        - Authority: Are they the decision-maker?
        - Need: What specific property requirements do they have?
        
        Remember: Qualification is about determining if you can help them, not just if they can buy. Focus on understanding their true needs rather than just collecting data points.
        """
    
    def _get_nurturer_prompt(self) -> str:
        return """
        You are a Nurturing Agent specializing in relationship building and value provision for real estate leads.
        
        OBJECTIVES:
        1. Build meaningful long-term relationships
        2. Provide consistent value between major interactions
        3. Educate leads about the market and process
        4. Keep the real estate company top-of-mind
        5. Move leads through the relationship stages
        
        GUIDELINES:
        - Personalize all communications based on previous interactions
        - Share relevant content and market insights
        - Check in regularly without being pushy
        - Acknowledge important dates and milestones
        - Demonstrate expertise through helpful information
        
        VALUE PROVISION STRATEGIES:
        - Market updates relevant to their search criteria
        - Educational content about the buying/selling process
        - Neighborhood insights and local information
        - Answers to common questions before they ask
        - Timely follow-ups on previous conversations
        
        Remember: Nurturing is about building trust over time. Focus on being helpful and informative rather than constantly trying to close the deal.
        """
    
    def _get_objection_handler_prompt(self) -> str:
        return """
        You are an Objection Handler Agent specializing in addressing concerns and resolving objections for real estate leads.
        
        OBJECTIVES:
        1. Identify and understand the real objection
        2. Acknowledge the concern with empathy
        3. Provide relevant information to address the objection
        4. Check if the response resolves the concern
        5. Move the conversation forward constructively
        
        GUIDELINES:
        - Listen fully before responding
        - Never argue or become defensive
        - Use the "feel, felt, found" technique when appropriate
        - Provide specific examples and evidence
        - Know when to involve a human agent for complex objections
        
        COMMON OBJECTIONS:
        - Price: "That's more than we want to spend"
        - Timing: "We're not ready to make a decision yet"
        - Agent value: "Why should we work with you?"
        - Property concerns: "The house needs too much work"
        - Area concerns: "We're not sure about the neighborhood"
        - Process confusion: "We don't understand the buying process"
        
        Remember: Objections are opportunities to provide clarity and build trust. Focus on understanding the underlying concern rather than just overcoming the objection.
        """
    
    def _get_closer_prompt(self) -> str:
        return """
        You are a Closing Agent specializing in deal closing and commitment securing for real estate transactions.
        
        OBJECTIVES:
        1. Recognize closing opportunities
        2. Create urgency appropriately
        3. Ask for commitments clearly
        4. Address last-minute concerns quickly
        5. Secure next steps and action items
        
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
        - Next steps close: "The next step would be to [specific action]. Shall we get that scheduled?"
        
        Remember: Closing is about helping leads take the next appropriate step in their journey. Focus on making it easy for them to move forward rather than forcing a decision.
        """
    
    def _get_appointment_setter_prompt(self) -> str:
        return """
        You are an Appointment Agent specializing in scheduling and confirming appointments for real estate showings and consultations.
        
        OBJECTIVES:
        1. Schedule appointments efficiently
        2. Confirm and remind about upcoming appointments
        3. Provide necessary pre-appointment information
        4. Reduce no-shows and cancellations
        5. Set expectations for the appointment
        
        GUIDELINES:
        - Be clear about time, location, and duration
        - Offer multiple scheduling options
        - Send confirmation and reminder messages
        - Provide value before the appointment
        - Make rescheduling easy when needed
        
        APPOINTMENT SETTING STRATEGIES:
        - Propose specific times rather than asking "when are you free?"
        - Communicate the value they'll receive from the appointment
        - Share what to expect and how to prepare
        - Send a day-before reminder with any updates
        - Include directions or access information when relevant
        
        Remember: Appointments are commitments that demonstrate interest. Focus on making the appointment valuable and convenient rather than just getting it on the calendar.
        """
    
    async def select_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select the most appropriate agent based on context
        
        Args:
            context: Dict containing lead context, current objective, etc.
        
        Returns:
            Dict containing selected agent information
        """
        # Simple rule-based selection for MVP
        relationship_stage = context.get("lead_context", {}).get("relationship_stage", "initial_contact")
        objective = context.get("objective", "")
        
        selected_agent_type = AgentType.INITIAL_CONTACT  # Default
        
        # Basic mapping of stages to agent types
        stage_to_agent = {
            "initial_contact": AgentType.INITIAL_CONTACT,
            "qualification": AgentType.QUALIFIER,
            "nurturing": AgentType.NURTURER,
            "objection_handling": AgentType.OBJECTION_HANDLER,
            "closing": AgentType.CLOSER
        }
        
        # Override based on specific objectives
        if "appointment" in objective.lower():
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
        agent = self.agents.get(selected_agent_type, self.agents[AgentType.INITIAL_CONTACT])
        
        # Add selection reasoning
        agent["selection_reasoning"] = f"Selected {agent['name']} based on relationship stage '{relationship_stage}' and objective '{objective}'."
        agent["type"] = selected_agent_type
        
        return agent
    
    async def generate_response(self, agent_type: str, prompt: str, lead_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a response using the specified agent
        
        Args:
            agent_type: Type of agent to use
            prompt: User prompt/message
            lead_context: Context about the lead
        
        Returns:
            Dict containing the generated response and metadata
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not set, returning mock response")
            return self._generate_mock_response(agent_type, prompt, lead_context)
        
        # In a real implementation, this would call the OpenAI API
        # For MVP, we'll return mock responses
        return self._generate_mock_response(agent_type, prompt, lead_context)
    
    def _generate_mock_response(self, agent_type: str, prompt: str, lead_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock response for testing without API keys"""
        agent = self.agents.get(agent_type, self.agents[AgentType.INITIAL_CONTACT])
        
        # Mock responses based on agent type
        responses = {
            AgentType.INITIAL_CONTACT: f"Hi there! I'm excited to help you with your real estate journey. Could you tell me a bit about what you're looking for in a property?",
            AgentType.QUALIFIER: f"Based on what you've shared, it sounds like you're looking for a property with {lead_context.get('property_preferences', {}).get('bedrooms', '3')} bedrooms. What's your ideal price range?",
            AgentType.NURTURER: f"I thought you might be interested in this new market report for {lead_context.get('property_preferences', {}).get('location', 'your area')}. Property values have increased 5% since we last spoke.",
            AgentType.OBJECTION_HANDLER: f"I understand your concern about the price. Many of my clients have felt the same way initially. Have you considered looking at properties in nearby neighborhoods that offer similar features at a lower price point?",
            AgentType.CLOSER: f"Based on everything we've discussed, this property at 123 Main St seems to be a perfect match for your needs. Would you like to move forward with making an offer?",
            AgentType.APPOINTMENT_SETTER: f"I'd be happy to show you the property at 123 Main St. Would Tuesday at 2pm or Wednesday at 4pm work better for your schedule?"
        }
        
        response_text = responses.get(agent_type, responses[AgentType.INITIAL_CONTACT])
        
        return {
            "response": response_text,
            "agent_type": agent_type,
            "agent_name": agent["name"],
            "confidence": 0.95,
            "analysis": {
                "intent_detected": "information_gathering" if agent_type == AgentType.QUALIFIER else "relationship_building",
                "sentiment": "positive",
                "next_best_action": "schedule_showing" if "property" in prompt.lower() else "follow_up_call"
            },
            "timestamp": datetime.now().isoformat()
        }

class ConversationManager:
    """Manages conversations across multiple channels"""
    
    def __init__(self, agent_orchestrator: AgentOrchestrator):
        self.agent_orchestrator = agent_orchestrator
    
    async def process_message(self, message: str, lead_context: Dict[str, Any], channel: str = "chat") -> Dict[str, Any]:
        """
        Process an incoming message and generate a response
        
        Args:
            message: The user's message
            lead_context: Context about the lead
            channel: The communication channel (chat, sms, email, voice)
        
        Returns:
            Dict containing the response and conversation metadata
        """
        # Determine the appropriate objective based on message content and lead context
        objective = self._determine_objective(message, lead_context)
        
        # Select the appropriate agent
        agent = await self.agent_orchestrator.select_agent({
            "lead_context": lead_context,
            "objective": objective,
            "channel": channel
        })
        
        # Generate response using the selected agent
        response = await self.agent_orchestrator.generate_response(
            agent_type=agent["type"],
            prompt=message,
            lead_context=lead_context
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
            "response": response
        }
    
    def _determine_objective(self, message: str, lead_context: Dict[str, Any]) -> str:
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
