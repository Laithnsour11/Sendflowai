import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
from enum import Enum
from fastapi import HTTPException

from llm_service import LLMService
from persistent_memory import PersistentMemoryManager
from knowledge_base import KnowledgeBaseManager

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
    
    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        memory_manager: Optional[PersistentMemoryManager] = None,
        knowledge_manager: Optional[KnowledgeBaseManager] = None
    ):
        self.llm_service = llm_service or LLMService()
        self.memory_manager = memory_manager or PersistentMemoryManager()
        self.knowledge_manager = knowledge_manager or KnowledgeBaseManager()
    
    async def select_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select the most appropriate agent based on context
        
        Args:
            context: Dictionary containing lead context, conversation history, etc.
        
        Returns:
            Dictionary with selected agent information
        """
        # Extract key context elements
        relationship_stage = context.get("lead_context", {}).get("relationship_stage", "initial_contact")
        message_intent = context.get("message_intent", "")
        lead_personality = context.get("lead_context", {}).get("personality_type")
        previous_agent = context.get("previous_agent")
        conversation_history = context.get("conversation_history", [])
        
        # Create prompt for agent selection
        system_prompt = """
        You are an Agent Orchestrator for a real estate lead conversion system. Your job is to select the most 
        appropriate specialized agent to handle the current conversation with a lead. You will analyze the 
        lead's context, conversation history, and current state to make this decision.
        
        The available specialized agents are:
        
        1. INITIAL_CONTACT: Specializes in first impressions and rapport building
        2. QUALIFIER: Specializes in lead qualification and needs assessment
        3. NURTURER: Specializes in relationship building and value provision
        4. OBJECTION_HANDLER: Specializes in addressing concerns and overcoming objections
        5. CLOSER: Specializes in deal closing and commitment securing
        6. APPOINTMENT_SETTER: Specializes in scheduling appointments and follow-ups
        
        You should analyze multiple factors to select the best agent:
        - The lead's current relationship stage
        - The intent of the lead's most recent message
        - The lead's personality type
        - The previous agent used (for continuity when appropriate)
        - Recent conversation history
        
        Provide your selection along with a detailed explanation of your reasoning.
        """
        
        # Construct prompt with context
        user_prompt = f"""
        Please select the most appropriate agent based on the following context:
        
        RELATIONSHIP STAGE: {relationship_stage}
        MESSAGE INTENT: {message_intent}
        LEAD PERSONALITY: {lead_personality}
        PREVIOUS AGENT: {previous_agent}
        
        RECENT CONVERSATION HISTORY:
        {json.dumps(conversation_history[-3:] if conversation_history else [], indent=2)}
        
        Provide your selection as JSON with the following structure:
        {{
            "selected_agent": "AGENT_TYPE",
            "reasoning": "Detailed explanation of why this agent was selected",
            "confidence": 0.0 to 1.0
        }}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Get completion from LLM
        try:
            completion = await self.llm_service.generate_completion(
                messages=messages,
                model="openai/gpt-4o",  # Use a powerful model for agent selection
                provider="openrouter",
                temperature=0.3  # Low temperature for more deterministic selection
            )
            
            # Parse response
            content = completion.get("content", "")
            
            # Extract JSON from the response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                # Try to find JSON object in the content
                start = content.find("{")
                end = content.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                else:
                    json_str = content
            
            try:
                selection_data = json.loads(json_str)
            except json.JSONDecodeError:
                # Fallback to rule-based selection
                logger.warning("Failed to parse JSON from LLM response, using rule-based selection")
                return await self._rule_based_agent_selection(context)
            
            # Map the selected agent to our enum
            agent_type_str = selection_data.get("selected_agent", "").upper()
            
            try:
                agent_type = AgentType[agent_type_str]
            except (KeyError, ValueError):
                # Try to match with case-insensitive comparison
                for enum_value in AgentType:
                    if enum_value.value.lower() == selection_data.get("selected_agent", "").lower():
                        agent_type = enum_value
                        break
                else:
                    # Fallback to INITIAL_CONTACT if no match
                    agent_type = AgentType.INITIAL_CONTACT
            
            # Get agent details
            agent_details = self._get_agent_details(agent_type)
            
            # Add selection metadata
            agent_details["type"] = agent_type.value
            agent_details["reasoning"] = selection_data.get("reasoning", "No reasoning provided")
            agent_details["confidence"] = selection_data.get("confidence", 0.8)
            
            return agent_details
        except Exception as e:
            logger.error(f"Error in agent selection: {e}")
            # Fallback to rule-based selection
            return await self._rule_based_agent_selection(context)
    
    async def _rule_based_agent_selection(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simple rule-based agent selection as fallback"""
        # Extract key context elements
        relationship_stage = context.get("lead_context", {}).get("relationship_stage", "initial_contact")
        message_intent = context.get("message_intent", "").lower()
        
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
        
        # Override based on specific message intents
        if any(word in message_intent for word in ["appointment", "schedule", "meet", "showing"]):
            selected_agent_type = AgentType.APPOINTMENT_SETTER
        elif any(word in message_intent for word in ["objection", "concern", "expensive", "price", "cost"]):
            selected_agent_type = AgentType.OBJECTION_HANDLER
        elif any(word in message_intent for word in ["qualify", "assessment", "budget", "looking for"]):
            selected_agent_type = AgentType.QUALIFIER
        elif any(word in message_intent for word in ["close", "commit", "offer", "buy", "purchase"]):
            selected_agent_type = AgentType.CLOSER
        elif any(word in message_intent for word in ["nurture", "follow up", "check in"]):
            selected_agent_type = AgentType.NURTURER
        else:
            # Use relationship stage mapping
            selected_agent_type = stage_to_agent.get(relationship_stage, AgentType.INITIAL_CONTACT)
        
        # Get the selected agent's details
        agent_details = self._get_agent_details(selected_agent_type)
        
        # Add selection metadata
        agent_details["type"] = selected_agent_type.value
        agent_details["reasoning"] = f"Rule-based selection based on relationship stage '{relationship_stage}' and message intent '{message_intent}'"
        agent_details["confidence"] = 0.7  # Lower confidence for rule-based selection
        
        return agent_details
    
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
    
    async def get_specialized_agent_config(self, agent_type: str, org_id: str) -> Dict[str, Any]:
        """
        Get specialized agent configuration from database
        
        Args:
            agent_type: Type of agent
            org_id: Organization ID
            
        Returns:
            Dict containing agent configuration
        """
        # TODO: Implement database lookup for agent configuration
        
        # For now, return default configuration
        default_configs = {
            "initial_contact": {
                "name": "Default Initial Contact",
                "provider": "openrouter",
                "model": "openai/gpt-4o",
                "temperature": 0.7,
                "system_prompt": """
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
                """
            },
            "qualifier": {
                "name": "Default Qualifier",
                "provider": "openrouter",
                "model": "anthropic/claude-3-sonnet",
                "temperature": 0.5,
                "system_prompt": """
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
                """
            },
            "nurturer": {
                "name": "Default Nurturer",
                "provider": "openrouter",
                "model": "anthropic/claude-3-haiku",
                "temperature": 0.7,
                "system_prompt": """
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
                """
            },
            "objection_handler": {
                "name": "Default Objection Handler",
                "provider": "openrouter",
                "model": "openai/gpt-4o",
                "temperature": 0.6,
                "system_prompt": """
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
                """
            },
            "closer": {
                "name": "Default Closer",
                "provider": "openrouter",
                "model": "openai/gpt-4o",
                "temperature": 0.6,
                "system_prompt": """
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
                """
            },
            "appointment_setter": {
                "name": "Default Appointment Setter",
                "provider": "openrouter",
                "model": "anthropic/claude-3-haiku",
                "temperature": 0.5,
                "system_prompt": """
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
                """
            }
        }
        
        return default_configs.get(agent_type, default_configs["initial_contact"])
    
    async def _retrieve_relevant_kb_context(self, query: str, lead_context: Dict[str, Any], agent_type: str, org_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge base context using Agentic RAG
        
        Args:
            query: Current message or conversation query
            lead_context: Lead context information
            agent_type: Type of agent making the query
            org_id: Organization ID
            
        Returns:
            List of relevant knowledge base items
        """
        # Create a more specific query based on agent type and lead context
        property_prefs = lead_context.get("property_preferences", {})
        budget = lead_context.get("budget", {})
        relationship_stage = lead_context.get("relationship_stage", "initial_contact")
        
        # Build context-specific query
        enhanced_query = query
        
        if agent_type == "qualifier":
            enhanced_query = f"Qualification information for {query}. Property preferences: {json.dumps(property_prefs)}. Budget: {json.dumps(budget)}"
        elif agent_type == "objection_handler":
            enhanced_query = f"Handling objection: {query}. Relationship stage: {relationship_stage}"
        elif agent_type == "closer":
            enhanced_query = f"Closing techniques for: {query}. Property preferences: {json.dumps(property_prefs)}"
        
        # Retrieve knowledge base items
        kb_items = await self.knowledge_manager.search_documents(
            org_id=org_id,
            query=enhanced_query,
            limit=3  # Limit to most relevant items
        )
        
        return kb_items
    
    async def _build_agent_prompt(self, 
                                agent_config: Dict[str, Any], 
                                lead_context: Dict[str, Any], 
                                conversation_history: List[Dict[str, Any]],
                                kb_context: List[Dict[str, Any]]) -> str:
        """
        Build a comprehensive prompt for the agent
        
        Args:
            agent_config: Agent configuration
            lead_context: Lead context from persistent memory
            conversation_history: Conversation history
            kb_context: Relevant knowledge base items
            
        Returns:
            Complete system prompt for the agent
        """
        base_prompt = agent_config.get("system_prompt", "")
        
        # Add lead context
        lead_context_str = f"""
        LEAD CONTEXT:
        - Name: {lead_context.get("name", "Unknown")}
        - Personality Type: {lead_context.get("personality_type", "Unknown")}
        - Relationship Stage: {lead_context.get("relationship_stage", "initial_contact")}
        - Property Preferences: {json.dumps(lead_context.get("property_preferences", {}), indent=2)}
        - Budget: {json.dumps(lead_context.get("budget", {}), indent=2)}
        """
        
        # Add knowledge base context
        kb_context_str = ""
        if kb_context:
            kb_context_str = "KNOWLEDGE BASE CONTEXT:\n"
            for item in kb_context:
                kb_context_str += f"- {item.get('title', 'Untitled')}: {item.get('content', '')[:300]}...\n\n"
        
        # Compile complete prompt
        complete_prompt = f"""
        {base_prompt}
        
        {lead_context_str}
        
        {kb_context_str}
        
        Remember to adapt your communication style to match the lead's personality type and relationship stage.
        """
        
        return complete_prompt
    
    async def generate_agent_response(self,
                                     agent_type: str,
                                     message: str,
                                     lead_context: Dict[str, Any],
                                     conversation_history: List[Dict[str, Any]],
                                     org_id: str,
                                     use_text_cadence: bool = False) -> Dict[str, Any]:
        """
        Generate a response using a specialized agent
        
        Args:
            agent_type: Type of agent to use
            message: Current message to respond to
            lead_context: Lead context from persistent memory
            conversation_history: Conversation history
            org_id: Organization ID
            use_text_cadence: Whether to use text cadence for messaging
            
        Returns:
            Dict containing the generated response
        """
        # Get agent configuration
        agent_config = await self.get_specialized_agent_config(agent_type, org_id)
        
        # Retrieve relevant knowledge base context
        kb_context = await self._retrieve_relevant_kb_context(message, lead_context, agent_type, org_id)
        
        # Build complete system prompt
        system_prompt = await self._build_agent_prompt(agent_config, lead_context, conversation_history, kb_context)
        
        # Format conversation history for LLM
        formatted_history = []
        for msg in conversation_history[-5:]:  # Use last 5 messages for context
            role = "assistant" if msg.get("is_ai", False) else "user"
            formatted_history.append({
                "role": role,
                "content": msg.get("message", "")
            })
        
        # Add current message
        formatted_history.append({
            "role": "user",
            "content": message
        })
        
        # Add system message at the beginning
        messages = [
            {"role": "system", "content": system_prompt}
        ] + formatted_history
        
        # Generate response
        if use_text_cadence:
            response = await self.llm_service.generate_text_with_cadence(
                messages=messages,
                model=agent_config.get("model"),
                provider=agent_config.get("provider"),
                temperature=agent_config.get("temperature", 0.7)
            )
            
            # Format cadence response
            return {
                "agent_type": agent_type,
                "response_type": "cadence",
                "messages": response.get("messages", []),
                "model": response.get("model"),
                "provider": response.get("provider"),
                "usage": response.get("usage", {})
            }
        else:
            response = await self.llm_service.generate_completion(
                messages=messages,
                model=agent_config.get("model"),
                provider=agent_config.get("provider"),
                temperature=agent_config.get("temperature", 0.7)
            )
            
            # Format standard response
            return {
                "agent_type": agent_type,
                "response_type": "standard",
                "content": response.get("content", ""),
                "model": response.get("model"),
                "provider": response.get("provider"),
                "usage": response.get("usage", {})
            }
    
    async def orchestrate_conversation(self,
                                     message: str,
                                     lead_id: str,
                                     org_id: str,
                                     conversation_history: Optional[List[Dict[str, Any]]] = None,
                                     previous_agent: Optional[str] = None,
                                     channel: str = "chat") -> Dict[str, Any]:
        """
        Orchestrate a complete conversation interaction
        
        Args:
            message: Current message to respond to
            lead_id: ID of the lead
            org_id: Organization ID
            conversation_history: Optional conversation history
            previous_agent: Optional previous agent type
            channel: Communication channel (chat, sms, email, voice)
            
        Returns:
            Dict containing the orchestrated response and metadata
        """
        # Get lead context from persistent memory
        lead_context = await self.memory_manager.synthesize_lead_context(lead_id)
        
        # Determine message intent
        message_intent = await self._determine_message_intent(message, lead_context)
        
        # Select the appropriate agent
        agent_selection = await self.select_agent({
            "lead_context": lead_context,
            "message_intent": message_intent,
            "previous_agent": previous_agent,
            "conversation_history": conversation_history or []
        })
        
        # Use text cadence for SMS/MMS channels
        use_text_cadence = channel in ["sms", "mms"]
        
        # Generate response using selected agent
        response = await self.generate_agent_response(
            agent_type=agent_selection["type"],
            message=message,
            lead_context=lead_context,
            conversation_history=conversation_history or [],
            org_id=org_id,
            use_text_cadence=use_text_cadence
        )
        
        # Store interaction in memory
        if response["response_type"] == "cadence":
            # Join cadence messages for memory storage
            response_text = " ".join([msg["text"] for msg in response.get("messages", [])])
        else:
            response_text = response.get("content", "")
        
        await self.memory_manager.store_contextual_memory(
            lead_id=lead_id,
            memory_content={
                "message": message,
                "response": response_text,
                "agent_type": agent_selection["type"],
                "channel": channel,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Prepare final response
        orchestrated_response = {
            "lead_id": lead_id,
            "agent_used": agent_selection,
            "response": response,
            "message_intent": message_intent,
            "channel": channel,
            "timestamp": datetime.now().isoformat()
        }
        
        return orchestrated_response
    
    async def _determine_message_intent(self, message: str, lead_context: Dict[str, Any]) -> str:
        """
        Determine the intent of a message
        
        Args:
            message: The message to analyze
            lead_context: Lead context information
            
        Returns:
            String describing the message intent
        """
        # Create prompt for intent classification
        system_prompt = """
        You are an Intent Classifier for real estate conversations. Your task is to analyze a message from a lead
        and determine their primary intent or objective. Focus on identifying what the lead is trying to accomplish
        or communicate with this message.
        
        Common intents in real estate conversations include:
        - General inquiry (seeking basic information)
        - Property search (looking for specific properties)
        - Price/budget discussion (talking about affordability)
        - Qualification (providing information about themselves)
        - Objection (expressing concerns or hesitations)
        - Appointment request (wanting to schedule a showing)
        - Follow-up (responding to previous communication)
        - Ready to proceed (showing buying signals)
        
        Respond with a brief phrase (2-5 words) that captures the primary intent.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Message: {message}\n\nWhat is the primary intent of this message?"}
        ]
        
        # Get intent classification from LLM
        try:
            completion = await self.llm_service.generate_completion(
                messages=messages,
                model="anthropic/claude-3-haiku",  # Use a smaller, faster model for intent classification
                provider="openrouter",
                temperature=0.3,
                max_tokens=20  # Short response
            )
            
            intent = completion.get("content", "").strip()
            
            # Clean up the intent (remove quotes, periods, etc.)
            intent = intent.strip('"\'.,;:')
            
            return intent
        except Exception as e:
            logger.error(f"Error determining message intent: {e}")
            # Default to general inquiry if classification fails
            return "general inquiry"
