import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional, Union
from fastapi import HTTPException
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class Mem0Integration:
    """
    Implements full integration with Mem0 for persistent, multi-layered memory
    Provides structured storage and retrieval of lead interactions and insights
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.mem0.ai/v1"
        self.headers = {}
        self.update_headers()
    
    def set_api_key(self, api_key: str):
        """Set the Mem0 API key"""
        self.api_key = api_key
        self.update_headers()
        
    def update_headers(self):
        """Update the headers with the current API key"""
        if self.api_key:
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
    
    def is_configured(self) -> bool:
        """Check if the Mem0 integration is configured with a valid API key"""
        return bool(self.api_key)
    
    async def validate_key(self) -> bool:
        """Validate that the API key is correct by making a simple API call"""
        if not self.is_configured():
            return False
            
        try:
            # Try to list memories as a simple validation
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/memories",
                    headers=self.headers,
                    params={"limit": 1}
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error validating Mem0 API key: {e}")
            return False
    
    async def store_multi_layered_memory(
        self,
        user_id: str,
        memory_data: Dict[str, Any],
        memory_type: str = "contextual"
    ) -> Dict[str, Any]:
        """
        Store a multi-layered memory for a lead
        
        Args:
            user_id: ID of the lead
            memory_data: The memory data to store
            memory_type: Type of memory (factual, emotional, strategic, contextual)
            
        Returns:
            Dict containing the stored memory information
        """
        if not self.is_configured():
            logger.error("Mem0 API key not configured")
            raise HTTPException(status_code=400, detail="Mem0 API key not configured")
        
        # Structure the memory with layers
        memory_content = {
            "memory_type": memory_type,
            "content": memory_data,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            # Add memory to Mem0
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/memories",
                    headers=self.headers,
                    json={
                        "user_id": user_id,
                        "content": json.dumps(memory_content),
                        "metadata": {
                            "memory_type": memory_type,
                            "source": "ai_closer_bot",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while storing memory: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Mem0 API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error storing memory in Mem0: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Mem0: {str(e)}")
    
    async def store_factual_memory(
        self, 
        user_id: str, 
        factual_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store factual information about a lead (preferences, constraints, etc.)"""
        return await self.store_multi_layered_memory(
            user_id=user_id,
            memory_data=factual_data,
            memory_type="factual"
        )
    
    async def store_emotional_memory(
        self, 
        user_id: str, 
        emotional_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store emotional insights about a lead (sentiment, rapport, etc.)"""
        return await self.store_multi_layered_memory(
            user_id=user_id,
            memory_data=emotional_data,
            memory_type="emotional"
        )
    
    async def store_strategic_memory(
        self, 
        user_id: str, 
        strategic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store strategic insights about a lead (buying signals, objections, etc.)"""
        return await self.store_multi_layered_memory(
            user_id=user_id,
            memory_data=strategic_data,
            memory_type="strategic"
        )
    
    async def store_contextual_memory(
        self, 
        user_id: str, 
        contextual_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store contextual information about interactions (time, channel, etc.)"""
        return await self.store_multi_layered_memory(
            user_id=user_id,
            memory_data=contextual_data,
            memory_type="contextual"
        )
    
    async def store_conversation_memory(
        self,
        user_id: str,
        conversation: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store a complete conversation with analysis across all memory layers
        
        Args:
            user_id: ID of the lead
            conversation: The conversation data
            analysis: AI analysis of the conversation
            
        Returns:
            Dict containing the stored memory information
        """
        if not self.is_configured():
            logger.error("Mem0 API key not configured")
            raise HTTPException(status_code=400, detail="Mem0 API key not configured")
        
        # Extract factual information
        factual_data = {
            "statements": analysis.get("factual_statements", []),
            "preferences": analysis.get("expressed_preferences", {}),
            "constraints": analysis.get("mentioned_constraints", {}),
            "property_criteria": analysis.get("property_requirements", {}),
            "budget_information": analysis.get("budget_details", {}),
            "timeline": analysis.get("timeline_indicators", {})
        }
        
        # Extract emotional insights
        emotional_data = {
            "sentiment_progression": analysis.get("sentiment_trajectory", []),
            "trust_indicators": analysis.get("trust_building_moments", []),
            "rapport_moments": analysis.get("positive_interactions", []),
            "emotional_triggers": analysis.get("emotional_triggers", []),
            "communication_style_preferences": analysis.get("communication_preferences", {})
        }
        
        # Extract strategic insights
        strategic_data = {
            "buying_signals": analysis.get("buying_indicators", []),
            "objection_patterns": analysis.get("objection_history", []),
            "decision_making_style": analysis.get("decision_patterns", {}),
            "influence_receptivity": analysis.get("influence_analysis", {}),
            "closing_readiness": analysis.get("closing_indicators", {})
        }
        
        # Contextual information
        contextual_data = {
            "conversation_id": conversation.get("id"),
            "agent_type": conversation.get("agent_type"),
            "channel": conversation.get("channel"),
            "timestamp": conversation.get("created_at") or datetime.now().isoformat(),
            "duration": conversation.get("duration_seconds"),
            "outcome": conversation.get("outcome"),
            "next_best_action": analysis.get("next_best_action")
        }
        
        # Store all memory layers
        try:
            factual_result = await self.store_factual_memory(user_id, factual_data)
            emotional_result = await self.store_emotional_memory(user_id, emotional_data)
            strategic_result = await self.store_strategic_memory(user_id, strategic_data)
            contextual_result = await self.store_contextual_memory(user_id, contextual_data)
            
            # Return a combined result
            return {
                "user_id": user_id,
                "memories_stored": {
                    "factual": factual_result.get("id"),
                    "emotional": emotional_result.get("id"),
                    "strategic": strategic_result.get("id"),
                    "contextual": contextual_result.get("id")
                },
                "storage_success": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error storing conversation memory: {e}")
            raise HTTPException(status_code=500, detail=f"Error storing memory: {str(e)}")
    
    async def retrieve_memories(
        self, 
        user_id: str, 
        memory_type: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a user
        
        Args:
            user_id: ID of the user/lead
            memory_type: Optional filter by memory type (factual, emotional, strategic, contextual)
            query: Optional search query
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memories
        """
        if not self.is_configured():
            logger.error("Mem0 API key not configured")
            raise HTTPException(status_code=400, detail="Mem0 API key not configured")
        
        try:
            # Build query parameters
            params = {
                "user_id": user_id,
                "limit": limit
            }
            
            # Add metadata filter for memory type if specified
            if memory_type:
                params["metadata.memory_type"] = memory_type
                
            # Add search query if specified
            if query:
                params["query"] = query
            
            # Retrieve memories from Mem0
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/memories/search",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                results = response.json().get("memories", [])
                
                # Parse memory content
                parsed_memories = []
                for memory in results:
                    try:
                        content = json.loads(memory.get("content", "{}"))
                        memory["parsed_content"] = content
                        parsed_memories.append(memory)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse memory content: {memory.get('content')}")
                        # Still include the memory but without parsed content
                        memory["parsed_content"] = {}
                        parsed_memories.append(memory)
                
                return parsed_memories
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while retrieving memories: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Mem0 API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error retrieving memories from Mem0: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Mem0: {str(e)}")
    
    async def synthesize_lead_context(self, user_id: str) -> Dict[str, Any]:
        """
        Synthesize a comprehensive lead context from memories
        
        Args:
            user_id: ID of the lead
            
        Returns:
            Dict containing synthesized lead context
        """
        if not self.is_configured():
            logger.warning("Mem0 API key not configured, returning empty context")
            return {}
        
        try:
            # Retrieve memories of all types
            factual_memories = await self.retrieve_memories(user_id, memory_type="factual", limit=5)
            emotional_memories = await self.retrieve_memories(user_id, memory_type="emotional", limit=5)
            strategic_memories = await self.retrieve_memories(user_id, memory_type="strategic", limit=5)
            contextual_memories = await self.retrieve_memories(user_id, memory_type="contextual", limit=5)
            
            # Synthesize into a single context object
            context = {
                "user_id": user_id,
                "factual_information": self._synthesize_factual_memories(factual_memories),
                "relationship_insights": self._synthesize_emotional_memories(emotional_memories),
                "strategic_recommendations": self._synthesize_strategic_memories(strategic_memories),
                "situational_awareness": self._synthesize_contextual_memories(contextual_memories),
                "memory_confidence": self._calculate_memory_confidence(factual_memories),
                "synthesis_timestamp": datetime.now().isoformat()
            }
            
            # Extract key data points for easier access
            context.update(self._extract_key_data_points(context))
            
            # Add key memory highlights for agent prompts
            context["memories"] = self._extract_memory_highlights(
                factual_memories, emotional_memories, strategic_memories, contextual_memories
            )
            
            return context
        except Exception as e:
            logger.error(f"Error synthesizing lead context: {e}")
            return {
                "user_id": user_id,
                "error": f"Failed to synthesize context: {str(e)}",
                "synthesis_timestamp": datetime.now().isoformat()
            }
    
    def _synthesize_factual_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize factual memories into coherent information"""
        if not memories:
            return {}
        
        # Combine all factual memories
        combined = {
            "property_preferences": {},
            "budget": {},
            "timeline": {},
            "constraints": {},
            "preferences": {}
        }
        
        for memory in memories:
            content = memory.get("parsed_content", {}).get("content", {})
            
            # Merge property criteria
            if "property_criteria" in content:
                combined["property_preferences"].update(content["property_criteria"])
                
            # Merge budget information
            if "budget_information" in content:
                combined["budget"].update(content["budget_information"])
                
            # Merge timeline
            if "timeline" in content:
                combined["timeline"].update(content["timeline"])
                
            # Merge constraints
            if "constraints" in content:
                combined["constraints"].update(content["constraints"])
                
            # Merge preferences
            if "preferences" in content:
                combined["preferences"].update(content["preferences"])
        
        return combined
    
    def _synthesize_emotional_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize emotional memories into relationship insights"""
        if not memories:
            return {}
        
        # Combine all emotional memories
        combined = {
            "sentiment_history": [],
            "trust_indicators": [],
            "rapport_moments": [],
            "emotional_triggers": [],
            "communication_preferences": {}
        }
        
        for memory in memories:
            content = memory.get("parsed_content", {}).get("content", {})
            
            # Add sentiment progression with timestamps
            if "sentiment_progression" in content:
                for sentiment in content["sentiment_progression"]:
                    if sentiment not in combined["sentiment_history"]:
                        combined["sentiment_history"].append(sentiment)
            
            # Add trust indicators
            if "trust_indicators" in content:
                for indicator in content["trust_indicators"]:
                    if indicator not in combined["trust_indicators"]:
                        combined["trust_indicators"].append(indicator)
            
            # Add rapport moments
            if "rapport_moments" in content:
                for moment in content["rapport_moments"]:
                    if moment not in combined["rapport_moments"]:
                        combined["rapport_moments"].append(moment)
            
            # Add emotional triggers
            if "emotional_triggers" in content:
                for trigger in content["emotional_triggers"]:
                    if trigger not in combined["emotional_triggers"]:
                        combined["emotional_triggers"].append(trigger)
            
            # Merge communication preferences
            if "communication_style_preferences" in content:
                combined["communication_preferences"].update(
                    content["communication_style_preferences"]
                )
        
        return combined
    
    def _synthesize_strategic_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize strategic memories into recommendations"""
        if not memories:
            return {}
        
        # Combine all strategic memories
        combined = {
            "buying_signals": [],
            "objection_patterns": [],
            "decision_making": {},
            "influence_factors": {},
            "closing_readiness": {}
        }
        
        for memory in memories:
            content = memory.get("parsed_content", {}).get("content", {})
            
            # Add buying signals
            if "buying_signals" in content:
                for signal in content["buying_signals"]:
                    if signal not in combined["buying_signals"]:
                        combined["buying_signals"].append(signal)
            
            # Add objection patterns
            if "objection_patterns" in content:
                for objection in content["objection_patterns"]:
                    if objection not in combined["objection_patterns"]:
                        combined["objection_patterns"].append(objection)
            
            # Merge decision making style
            if "decision_making_style" in content:
                combined["decision_making"].update(content["decision_making_style"])
            
            # Merge influence receptivity
            if "influence_receptivity" in content:
                combined["influence_factors"].update(content["influence_receptivity"])
            
            # Merge closing readiness
            if "closing_readiness" in content:
                combined["closing_readiness"].update(content["closing_readiness"])
        
        return combined
    
    def _synthesize_contextual_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize contextual memories into situational awareness"""
        if not memories:
            return {}
        
        # Get the most recent contextual memory
        sorted_memories = sorted(
            memories, 
            key=lambda m: m.get("parsed_content", {}).get("content", {}).get("timestamp", ""),
            reverse=True
        )
        
        if not sorted_memories:
            return {}
        
        latest_memory = sorted_memories[0]
        latest_content = latest_memory.get("parsed_content", {}).get("content", {})
        
        # Extract key contextual information
        context = {
            "last_interaction": {
                "timestamp": latest_content.get("timestamp"),
                "channel": latest_content.get("channel"),
                "agent_type": latest_content.get("agent_type"),
                "outcome": latest_content.get("outcome"),
                "next_best_action": latest_content.get("next_best_action")
            },
            "preferred_contact_times": {},
            "communication_preferences": {}
        }
        
        # Combine information about contact preferences from all memories
        for memory in memories:
            content = memory.get("parsed_content", {}).get("content", {})
            
            # Extract contact preferences
            if "conversation_context" in content:
                conversation_context = content["conversation_context"]
                
                if "preferred_contact_times" in conversation_context:
                    context["preferred_contact_times"].update(
                        conversation_context["preferred_contact_times"]
                    )
                
                if "channel_preferences" in conversation_context:
                    context["communication_preferences"].update(
                        conversation_context["channel_preferences"]
                    )
        
        return context
    
    def _calculate_memory_confidence(self, factual_memories: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in the memory based on recency, frequency and confidence scores"""
        if not factual_memories:
            return 0.0
        
        # For simplicity, use an average of available confidence levels
        confidence_levels = []
        
        for memory in factual_memories:
            content = memory.get("parsed_content", {})
            if "confidence_level" in content:
                confidence_levels.append(content["confidence_level"])
        
        if not confidence_levels:
            return 0.5  # Default mid-range confidence
            
        return sum(confidence_levels) / len(confidence_levels)
    
    def _extract_key_data_points(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key data points from synthesized context for easier access"""
        key_data = {}
        
        # Extract personality type from relationship insights
        relationship = context.get("relationship_insights", {})
        if "communication_preferences" in relationship:
            comm_prefs = relationship["communication_preferences"]
            if "personality_type" in comm_prefs:
                key_data["personality_type"] = comm_prefs["personality_type"]
        
        # Extract budget from factual information
        factual = context.get("factual_information", {})
        if "budget" in factual:
            key_data["budget"] = factual["budget"]
        
        # Extract property preferences from factual information
        if "property_preferences" in factual:
            key_data["property_preferences"] = factual["property_preferences"]
        
        # Extract relationship stage from strategic recommendations
        strategic = context.get("strategic_recommendations", {})
        if "closing_readiness" in strategic and "relationship_stage" in strategic["closing_readiness"]:
            key_data["relationship_stage"] = strategic["closing_readiness"]["relationship_stage"]
        
        # Extract trust level
        if "trust_indicators" in relationship:
            # Calculate a simple trust level based on number of positive indicators
            trust_indicators = relationship["trust_indicators"]
            if trust_indicators:
                # Simple average of trust indicator scores if available
                trust_scores = [
                    indicator.get("score", 0.5) 
                    for indicator in trust_indicators 
                    if isinstance(indicator, dict) and "score" in indicator
                ]
                
                if trust_scores:
                    key_data["trust_level"] = sum(trust_scores) / len(trust_scores)
        
        return key_data
    
    def _extract_memory_highlights(
        self,
        factual_memories: List[Dict[str, Any]],
        emotional_memories: List[Dict[str, Any]],
        strategic_memories: List[Dict[str, Any]],
        contextual_memories: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract key memory highlights for agent prompts"""
        highlights = []
        
        # Add property preferences
        for memory in factual_memories:
            content = memory.get("parsed_content", {}).get("content", {})
            if "property_criteria" in content:
                criteria = content["property_criteria"]
                if criteria:
                    highlight = "Looking for "
                    details = []
                    
                    if "bedrooms" in criteria:
                        details.append(f"{criteria['bedrooms']} bedroom")
                    
                    if "property_type" in criteria:
                        details.append(criteria["property_type"])
                    
                    if "location" in criteria:
                        details.append(f"in {criteria['location']}")
                    
                    if details:
                        highlight += ", ".join(details)
                        highlights.append(highlight)
        
        # Add budget
        for memory in factual_memories:
            content = memory.get("parsed_content", {}).get("content", {})
            if "budget_information" in content:
                budget = content["budget_information"]
                if budget and "max" in budget:
                    highlight = f"Budget up to ${budget['max']:,}"
                    highlights.append(highlight)
        
        # Add timeline
        for memory in factual_memories:
            content = memory.get("parsed_content", {}).get("content", {})
            if "timeline" in content:
                timeline = content["timeline"]
                if timeline and "timeframe" in timeline:
                    highlight = f"Timeline: {timeline['timeframe']}"
                    highlights.append(highlight)
        
        # Add objections
        for memory in strategic_memories:
            content = memory.get("parsed_content", {}).get("content", {})
            if "objection_patterns" in content:
                objections = content["objection_patterns"]
                for objection in objections[:2]:  # Limit to top 2
                    if isinstance(objection, dict) and "objection" in objection:
                        highlight = f"Previously expressed concern: {objection['objection']}"
                        highlights.append(highlight)
        
        # Add buying signals
        for memory in strategic_memories:
            content = memory.get("parsed_content", {}).get("content", {})
            if "buying_signals" in content:
                signals = content["buying_signals"]
                for signal in signals[:2]:  # Limit to top 2
                    if isinstance(signal, dict) and "signal" in signal:
                        highlight = f"Showed interest: {signal['signal']}"
                        highlights.append(highlight)
        
        # Add communication preferences
        for memory in emotional_memories:
            content = memory.get("parsed_content", {}).get("content", {})
            if "communication_style_preferences" in content:
                prefs = content["communication_style_preferences"]
                if prefs and "style" in prefs:
                    highlight = f"Prefers {prefs['style']} communication style"
                    highlights.append(highlight)
        
        # Limit to top 10 highlights
        return highlights[:10]