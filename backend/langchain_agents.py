import os
import json
import logging
import uuid
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime
from enum import Enum

# Placeholder imports for LangChain - you'll need to install these
# pip install langchain langchain-community langchain-openai
try:
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    from langchain.agents import Tool, AgentExecutor
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    
from openrouter_llm import OpenRouterClient
from mem0 import Mem0Integration

logger = logging.getLogger(__name__)

class AgentType(str, Enum):
    INITIAL_CONTACT = "initial_contact"
    QUALIFIER = "qualifier"
    NURTURER = "nurturer"
    OBJECTION_HANDLER = "objection_handler"
    CLOSER = "closer"
    APPOINTMENT_SETTER = "appointment_setter"

class ConversationChannel(str, Enum):
    VOICE = "voice"
    SMS = "sms"
    EMAIL = "email"
    CHAT = "chat"

class RelationshipStage(str, Enum):
    INITIAL_CONTACT = "initial_contact"
    QUALIFICATION = "qualification"
    NURTURING = "nurturing"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    POST_SALE = "post_sale"

class AgentConfig:
    """Configuration for an AI agent"""
    
    def __init__(
        self,
        agent_type: AgentType,
        name: str,
        description: str,
        system_prompt: str,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o",
        temperature: float = 0.7,
        tools: Optional[List[str]] = None
    ):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.temperature = temperature
        self.tools = tools or []

class AgentOrchestrator:
    """Orchestrates the selection and execution of AI agents"""
    
    def __init__(
        self, 
        openrouter_client: Optional[OpenRouterClient] = None,
        mem0_client: Optional[Mem0Integration] = None
    ):
        self.openrouter_client = openrouter_client or OpenRouterClient()
        self.mem0_client = mem0_client or Mem0Integration()
        self.agents = self._initialize_agents()
    
    def _initialize_agents(self) -> Dict[AgentType, AgentConfig]:
        """Initialize the different specialized agents"""
        return {
            AgentType.INITIAL_CONTACT: AgentConfig(
                agent_type=AgentType.INITIAL_CONTACT,
                name="Initial Contact Agent",
                description="Specializes in first impressions and rapport building",
                system_prompt=self._get_initial_contact_prompt(),
                llm_provider="openai",
                llm_model="gpt-4o",
                temperature=0.7,
                tools=["personality_analyzer", "rapport_builder", "interest_detector"]
            ),
            AgentType.QUALIFIER: AgentConfig(
                agent_type=AgentType.QUALIFIER,
                name="Qualification Agent",
                description="Specializes in lead qualification and needs assessment",
                system_prompt=self._get_qualifier_prompt(),
                llm_provider="anthropic",
                llm_model="claude-3-sonnet",
                temperature=0.6,
                tools=["needs_analyzer", "budget_qualifier", "timeline_assessor"]
            ),
            AgentType.NURTURER: AgentConfig(
                agent_type=AgentType.NURTURER,
                name="Nurturing Agent",
                description="Specializes in relationship building and value provision",
                system_prompt=self._get_nurturer_prompt(),
                llm_provider="openai",
                llm_model="gpt-4o",
                temperature=0.7,
                tools=["value_provider", "trust_builder", "education_provider"]
            ),
            AgentType.OBJECTION_HANDLER: AgentConfig(
                agent_type=AgentType.OBJECTION_HANDLER,
                name="Objection Handler Agent",
                description="Specializes in objection resolution and concern addressing",
                system_prompt=self._get_objection_handler_prompt(),
                llm_provider="anthropic",
                llm_model="claude-3-opus",
                temperature=0.5,
                tools=["objection_classifier", "response_generator", "concern_resolver"]
            ),
            AgentType.CLOSER: AgentConfig(
                agent_type=AgentType.CLOSER,
                name="Closer Agent",
                description="Specializes in deal closing and commitment securing",
                system_prompt=self._get_closer_prompt(),
                llm_provider="anthropic",
                llm_model="claude-3-opus",
                temperature=0.6,
                tools=["closing_technique_selector", "urgency_creator", "commitment_securer"]
            ),
            AgentType.APPOINTMENT_SETTER: AgentConfig(
                agent_type=AgentType.APPOINTMENT_SETTER,
                name="Appointment Agent",
                description="Specializes in appointment scheduling and confirmation",
                system_prompt=self._get_appointment_setter_prompt(),
                llm_provider="openai",
                llm_model="gpt-4o",
                temperature=0.6,
                tools=["calendar_manager", "confirmation_sender", "reminder_scheduler"]
            )
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
        agent_info = {
            "type": selected_agent_type,
            "name": agent.name,
            "description": agent.description,
            "system_prompt": agent.system_prompt,
            "llm_provider": agent.llm_provider,
            "llm_model": agent.llm_model,
            "temperature": agent.temperature,
            "tools": agent.tools,
            "selection_reasoning": f"Selected {agent.name} based on relationship stage '{relationship_stage}' and objective '{objective}'."
        }
        
        return agent_info
    
    async def build_agent_prompt(
        self,
        agent: Dict[str, Any],
        lead_context: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Build a comprehensive system prompt for the agent
        
        Args:
            agent: Agent configuration
            lead_context: Lead context data
            conversation_history: Optional conversation history
            
        Returns:
            Complete system prompt for the agent
        """
        base_prompt = agent["system_prompt"]
        
        # Add lead intelligence section
        lead_intelligence = f"""
        LEAD INTELLIGENCE:
        - Name: {lead_context.get('name', 'Unknown')}
        - Personality Type: {lead_context.get('personality_type', 'Unknown')}
        - Communication Style: {lead_context.get('communication_preference', 'Unknown')}
        - Trust Level: {int(lead_context.get('trust_level', 0.5) * 100)}%
        - Relationship Stage: {lead_context.get('relationship_stage', 'initial_contact')}
        """
        
        # Add previous interactions if available
        previous_interactions = ""
        if conversation_history:
            previous_interactions = "PREVIOUS INTERACTIONS:\n"
            for i, interaction in enumerate(conversation_history[-3:]):  # Last 3 interactions
                previous_interactions += f"- Interaction {i+1}: {interaction.get('summary', 'No summary available')}\n"
        
        # Add available tools
        tools_section = "AVAILABLE TOOLS:\n"
        for tool in agent["tools"]:
            tools_section += f"- {tool}\n"
        
        # Combine all sections
        full_prompt = f"""
        {base_prompt}
        
        {lead_intelligence}
        
        {previous_interactions}
        
        {tools_section}
        
        CONVERSATION OBJECTIVE:
        {lead_context.get('current_objective', 'Engage with the lead effectively')}
        
        Remember to adapt your communication style to match the lead's personality and preferences.
        """
        
        return full_prompt
    
    async def generate_response(
        self,
        agent_type: str,
        messages: List[Dict[str, str]],
        lead_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a response using the specified agent
        
        Args:
            agent_type: Type of agent to use
            messages: Conversation messages
            lead_context: Lead context information
            
        Returns:
            Dict containing the generated response and metadata
        """
        agent_config = self.agents.get(agent_type, self.agents[AgentType.INITIAL_CONTACT])
        
        # Build the model identifier based on provider
        model_id = agent_config.llm_model
        if agent_config.llm_provider != "openai":
            model_id = f"{agent_config.llm_provider}/{agent_config.llm_model}"
        
        # Generate response using OpenRouter
        response = await self.openrouter_client.chat_completion(
            messages=messages,
            model=model_id,
            temperature=agent_config.temperature
        )
        
        # Extract the assistant's message
        assistant_message = "I'm not sure how to respond to that."
        if response.get("choices") and len(response["choices"]) > 0:
            assistant_message = response["choices"][0].get("message", {}).get("content", assistant_message)
        
        # Analyze message for multiple parts and pauses
        message_parts = self._analyze_message_for_cadence(assistant_message)
        
        result = {
            "response": assistant_message,
            "message_parts": message_parts,
            "agent_type": agent_type,
            "agent_name": agent_config.name,
            "llm_provider": agent_config.llm_provider,
            "llm_model": agent_config.llm_model,
            "confidence": 0.95,  # Placeholder
            "analysis": {
                "intent_detected": self._detect_intent(assistant_message),
                "sentiment": self._analyze_sentiment(assistant_message),
                "next_best_action": self._determine_next_action(assistant_message, lead_context)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def _analyze_message_for_cadence(self, message: str) -> List[Dict[str, Any]]:
        """
        Analyze the message to determine natural cadence for multi-part delivery
        
        Args:
            message: The full message text
            
        Returns:
            List of message parts with pause durations
        """
        # Simple heuristic implementation for MVP:
        # Split on paragraph breaks with natural pauses
        
        # First, look for explicit pause indicators [pause:X]
        import re
        
        # Check for explicit pause markers
        explicit_parts = []
        pattern = r"(.*?)(?:\[pause:(\d+(?:\.\d+)?)\]|$)"
        matches = re.findall(pattern, message)
        
        if any(m[1] for m in matches):  # If we found explicit pause markers
            for text, pause in matches:
                if text.strip():
                    pause_duration = float(pause) if pause else 0
                    explicit_parts.append({
                        "text": text.strip(),
                        "pause_after": pause_duration
                    })
            return explicit_parts
        
        # If no explicit markers, use heuristics based on structure
        parts = []
        paragraphs = [p for p in message.split("\n\n") if p.strip()]
        
        if not paragraphs:
            # Single paragraph, return as is
            return [{"text": message, "pause_after": 0}]
        
        # Multiple paragraphs
        for i, paragraph in enumerate(paragraphs):
            # Longer pauses between paragraphs, shorter for sentences
            sentences = [s.strip() for s in paragraph.split(". ") if s.strip()]
            
            if len(sentences) <= 2 or len(paragraph) < 100:
                # Short paragraph, keep together
                pause = 1.5 if i < len(paragraphs) - 1 else 0
                parts.append({
                    "text": paragraph,
                    "pause_after": pause
                })
            else:
                # Longer paragraph, split into sentence groups
                current_group = []
                
                for j, sentence in enumerate(sentences):
                    current_group.append(sentence)
                    
                    # Group sentences by 2-3 based on length
                    if len(current_group) >= 2 or len(". ".join(current_group)) > 150:
                        group_text = ". ".join(current_group)
                        if not group_text.endswith("."):
                            group_text += "."
                            
                        # Determine pause based on position
                        pause = 0.8  # Standard pause between sentence groups
                        if j == len(sentences) - 1 and i == len(paragraphs) - 1:
                            pause = 0  # No pause after final text
                        elif j == len(sentences) - 1:
                            pause = 1.5  # Longer pause between paragraphs
                            
                        parts.append({
                            "text": group_text,
                            "pause_after": pause
                        })
                        current_group = []
                
                # Add any remaining sentences
                if current_group:
                    group_text = ". ".join(current_group)
                    if not group_text.endswith("."):
                        group_text += "."
                        
                    pause = 0 if i == len(paragraphs) - 1 else 1.5
                    parts.append({
                        "text": group_text,
                        "pause_after": pause
                    })
        
        return parts
    
    def _detect_intent(self, message: str) -> str:
        """Detect the intent of the message"""
        message_lower = message.lower()
        
        # Simple keyword-based intent detection for MVP
        if any(word in message_lower for word in ["schedule", "appointment", "meet", "available"]):
            return "appointment_scheduling"
        
        if any(word in message_lower for word in ["price", "cost", "budget", "afford"]):
            return "budget_discussion"
        
        if any(word in message_lower for word in ["feature", "bedroom", "bathroom", "square feet", "garage"]):
            return "property_features"
        
        if any(word in message_lower for word in ["neighborhood", "school", "community", "area"]):
            return "location_information"
        
        if any(word in message_lower for word in ["offer", "contract", "paperwork", "submit"]):
            return "transaction_process"
        
        if any(word in message_lower for word in ["when", "timeline", "move", "close"]):
            return "timeline_discussion"
        
        # Default intent
        return "information_gathering"
    
    def _analyze_sentiment(self, message: str) -> str:
        """Analyze the sentiment of the message"""
        message_lower = message.lower()
        
        # Simple keyword-based sentiment analysis for MVP
        positive_words = ["excited", "great", "perfect", "wonderful", "happy", "pleased", "thank", "appreciate"]
        negative_words = ["unfortunately", "sorry", "concern", "issue", "problem", "disappointed", "difficult"]
        neutral_words = ["consider", "option", "alternative", "information", "detail", "understand"]
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        neutral_count = sum(1 for word in neutral_words if word in message_lower)
        
        # Determine sentiment based on counts
        if positive_count > negative_count + neutral_count:
            return "positive"
        elif negative_count > positive_count + neutral_count:
            return "negative"
        elif negative_count > 0 and positive_count > 0:
            return "mixed"
        else:
            return "neutral"
    
    def _determine_next_action(self, message: str, lead_context: Dict[str, Any]) -> str:
        """Determine the next best action based on the message and lead context"""
        message_lower = message.lower()
        relationship_stage = lead_context.get("relationship_stage", "initial_contact")
        
        # Simple rule-based next action determination for MVP
        if "appointment" in message_lower or "schedule" in message_lower:
            return "confirm_appointment"
        
        if "question" in message_lower or "?" in message:
            return "answer_question"
        
        if "price" in message_lower or "budget" in message_lower:
            return "discuss_financing_options"
        
        # Stage-based defaults
        stage_to_action = {
            "initial_contact": "schedule_qualification_call",
            "qualification": "provide_property_recommendations",
            "nurturing": "share_market_insights",
            "objection_handling": "address_specific_concerns",
            "closing": "prepare_offer_documents"
        }
        
        return stage_to_action.get(relationship_stage, "follow_up")

class ConversationManager:
    """Manages conversations across multiple channels"""
    
    def __init__(
        self, 
        agent_orchestrator: AgentOrchestrator,
        mem0_client: Optional[Mem0Integration] = None
    ):
        self.agent_orchestrator = agent_orchestrator
        self.mem0_client = mem0_client or Mem0Integration()
    
    async def process_message(
        self, 
        message: str, 
        lead_context: Dict[str, Any], 
        channel: str = "chat",
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process an incoming message and generate a response
        
        Args:
            message: The user's message
            lead_context: Context about the lead
            channel: The communication channel (chat, sms, email, voice)
            conversation_history: Optional conversation history
            
        Returns:
            Dict containing the response and conversation metadata
        """
        # Determine the appropriate objective based on message content and lead context
        objective = self._determine_objective(message, lead_context)
        
        # Select the appropriate agent
        agent = await self.agent_orchestrator.select_agent({
            "lead_context": lead_context,
            "objective": objective,
            "channel": channel,
            "conversation_history": conversation_history
        })
        
        # Build messages for the model
        messages = []
        
        # Add system message with the agent prompt
        system_prompt = await self.agent_orchestrator.build_agent_prompt(
            agent,
            lead_context,
            conversation_history
        )
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history if available
        if conversation_history:
            # Add a reasonable amount of history (last 5 messages)
            for item in conversation_history[-5:]:
                if "user_message" in item:
                    messages.append({"role": "user", "content": item["user_message"]})
                if "assistant_message" in item:
                    messages.append({"role": "assistant", "content": item["assistant_message"]})
        
        # Add the current user message
        messages.append({"role": "user", "content": message})
        
        # Generate response using the selected agent
        response = await self.agent_orchestrator.generate_response(
            agent_type=agent["type"],
            messages=messages,
            lead_context=lead_context
        )
        
        # Create conversation data for storage
        conversation_data = {
            "id": str(uuid.uuid4()),
            "lead_id": lead_context.get("id"),
            "channel": channel,
            "agent_type": agent["type"],
            "message": message,
            "response": response["response"],
            "analysis": response.get("analysis", {}),
            "message_parts": response.get("message_parts", []),
            "created_at": datetime.now().isoformat()
        }
        
        # Extract key information for memory storage
        memory_data = {
            "user_message": message,
            "ai_response": response["response"],
            "intent": response.get("analysis", {}).get("intent_detected", "unknown"),
            "sentiment": response.get("analysis", {}).get("sentiment", "neutral"),
            "next_action": response.get("analysis", {}).get("next_best_action", "follow_up"),
            "channel": channel,
            "agent_type": agent["type"]
        }
        
        # Store in Mem0 as contextual memory if available
        if self.mem0_client and self.mem0_client.api_key:
            await self.mem0_client.store_memory(
                user_id=lead_context.get("id", "unknown"),
                memory_data=memory_data,
                memory_type="contextual",
                metadata={
                    "conversation_id": conversation_data["id"],
                    "channel": channel,
                    "agent_type": agent["type"],
                    "intent": response.get("analysis", {}).get("intent_detected", "unknown"),
                    "sentiment": response.get("analysis", {}).get("sentiment", "neutral")
                }
            )
        
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
