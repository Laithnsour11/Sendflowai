import os
import json
import logging
import httpx
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class PersistentMemoryManager:
    """Manages persistent memory with Mem0 integration for multi-layered lead memory"""
    
    def __init__(self, mem0_api_key: Optional[str] = None):
        self.mem0_api_key = mem0_api_key or os.environ.get('MEM0_API_KEY')
        self.base_url = "https://api.mem0.ai/v1"
    
    def set_api_key(self, mem0_api_key: str):
        """Set Mem0 API key"""
        self.mem0_api_key = mem0_api_key
    
    async def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make API request to Mem0"""
        if not self.mem0_api_key:
            logger.error("Mem0 API key not set")
            raise HTTPException(status_code=400, detail="Mem0 API key not configured")
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.mem0_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                if method.lower() == "get":
                    response = await client.get(url, headers=headers, params=data)
                elif method.lower() == "post":
                    response = await client.post(url, headers=headers, json=data)
                elif method.lower() == "put":
                    response = await client.put(url, headers=headers, json=data)
                elif method.lower() == "delete":
                    response = await client.delete(url, headers=headers, params=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Mem0 API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Mem0: {str(e)}")
    
    async def store_factual_memory(self, lead_id: str, memory_content: Dict[str, Any], confidence: float = 0.9) -> Dict[str, Any]:
        """Store factual memory for a lead"""
        return await self.store_memory(lead_id, "factual", memory_content, confidence)
    
    async def store_emotional_memory(self, lead_id: str, memory_content: Dict[str, Any], confidence: float = 0.9) -> Dict[str, Any]:
        """Store emotional memory for a lead"""
        return await self.store_memory(lead_id, "emotional", memory_content, confidence)
    
    async def store_strategic_memory(self, lead_id: str, memory_content: Dict[str, Any], confidence: float = 0.9) -> Dict[str, Any]:
        """Store strategic memory for a lead"""
        return await self.store_memory(lead_id, "strategic", memory_content, confidence)
    
    async def store_contextual_memory(self, lead_id: str, memory_content: Dict[str, Any], confidence: float = 0.9) -> Dict[str, Any]:
        """Store contextual memory for a lead"""
        return await self.store_memory(lead_id, "contextual", memory_content, confidence)
    
    async def store_memory(self, lead_id: str, memory_type: str, memory_content: Dict[str, Any], confidence: float = 0.9) -> Dict[str, Any]:
        """
        Store memory for a lead with specific memory type
        
        Args:
            lead_id: ID of the lead (corresponds to Mem0 user_id)
            memory_type: Type of memory (factual, emotional, strategic, contextual)
            memory_content: Memory content to store
            confidence: Confidence level (0.0 to 1.0)
            
        Returns:
            Dict containing stored memory information
        """
        endpoint = "memories"
        
        data = {
            "user_id": lead_id,
            "content": memory_content,
            "metadata": {
                "memory_type": memory_type,
                "confidence_level": confidence,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        response = await self._make_api_request("post", endpoint, data)
        
        # Create a memory snapshot record for internal tracking
        memory_snapshot = {
            "id": str(uuid.uuid4()),
            "lead_id": lead_id,
            "mem0_memory_id": response.get("id"),
            "memory_type": memory_type,
            "memory_content": memory_content,
            "confidence_level": confidence,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        
        # In a real implementation, this would be stored in the database
        logger.info(f"Stored memory snapshot: {json.dumps(memory_snapshot, default=str)}")
        
        return memory_snapshot
    
    async def retrieve_memories(self, lead_id: str, memory_type: Optional[str] = None, query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a lead
        
        Args:
            lead_id: ID of the lead
            memory_type: Optional memory type filter
            query: Optional search query
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memories
        """
        endpoint = "search"
        
        data = {
            "user_id": lead_id,
            "limit": limit
        }
        
        if query:
            data["query"] = query
        
        if memory_type:
            data["filter"] = {
                "metadata.memory_type": memory_type
            }
        
        response = await self._make_api_request("post", endpoint, data)
        
        # Extract memories from response
        memories = response.get("memories", [])
        
        # Update last_accessed timestamp for these memories
        memory_ids = [memory.get("id") for memory in memories]
        if memory_ids:
            await self._update_last_accessed(memory_ids)
        
        return memories
    
    async def _update_last_accessed(self, memory_ids: List[str]) -> None:
        """Update last_accessed timestamp for memories"""
        # In a real implementation, this would update the database
        logger.info(f"Updated last_accessed for memories: {memory_ids}")
    
    async def get_memory(self, memory_id: str) -> Dict[str, Any]:
        """Get a specific memory by ID"""
        endpoint = f"memories/{memory_id}"
        
        response = await self._make_api_request("get", endpoint)
        
        # Update last_accessed timestamp
        await self._update_last_accessed([memory_id])
        
        return response
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        endpoint = f"memories/{memory_id}"
        
        await self._make_api_request("delete", endpoint)
        
        return True
    
    async def synthesize_lead_context(self, lead_id: str) -> Dict[str, Any]:
        """
        Synthesize a comprehensive lead context from all memory types
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            Dict containing synthesized lead context
        """
        # Retrieve all memory types
        factual_memories = await self.retrieve_memories(lead_id, memory_type="factual")
        emotional_memories = await self.retrieve_memories(lead_id, memory_type="emotional")
        strategic_memories = await self.retrieve_memories(lead_id, memory_type="strategic")
        contextual_memories = await self.retrieve_memories(lead_id, memory_type="contextual")
        
        # Synthesize into a comprehensive context
        context = {
            "lead_id": lead_id,
            "factual_information": self._synthesize_factual_memories(factual_memories),
            "relationship_insights": self._synthesize_emotional_memories(emotional_memories),
            "strategic_recommendations": self._synthesize_strategic_memories(strategic_memories),
            "situational_awareness": self._synthesize_contextual_memories(contextual_memories),
            "synthesis_timestamp": datetime.now().isoformat()
        }
        
        return context
    
    def _synthesize_factual_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize factual memories into coherent information"""
        if not memories:
            return {}
        
        # Sort memories by timestamp (newest first)
        sorted_memories = sorted(
            memories, 
            key=lambda m: m.get("metadata", {}).get("timestamp", ""), 
            reverse=True
        )
        
        # Extract key factual information
        synthesized = {}
        
        # Property preferences
        property_prefs = {}
        budget_info = {}
        timeline_info = {}
        
        for memory in sorted_memories:
            content = memory.get("content", {})
            
            # Merge property preferences
            if "property_preferences" in content:
                property_prefs.update(content["property_preferences"])
            
            # Merge budget information
            if "budget" in content or "budget_analysis" in content:
                budget_data = content.get("budget", content.get("budget_analysis", {}))
                budget_info.update(budget_data)
            
            # Merge timeline information
            if "timeline" in content:
                timeline_info.update(content["timeline"])
        
        if property_prefs:
            synthesized["property_preferences"] = property_prefs
        
        if budget_info:
            synthesized["budget"] = budget_info
        
        if timeline_info:
            synthesized["timeline"] = timeline_info
        
        return synthesized
    
    def _synthesize_emotional_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize emotional memories into relationship insights"""
        if not memories:
            return {}
        
        # Sort memories by timestamp (newest first)
        sorted_memories = sorted(
            memories, 
            key=lambda m: m.get("metadata", {}).get("timestamp", ""), 
            reverse=True
        )
        
        # Extract emotional insights
        synthesized = {}
        
        # Track sentiment progression
        sentiment_progression = []
        rapport_moments = []
        trust_indicators = []
        
        for memory in sorted_memories:
            content = memory.get("content", {})
            
            # Collect sentiment data
            if "sentiment" in content:
                sentiment_progression.append(content["sentiment"])
            
            # Collect rapport moments
            if "rapport_moments" in content:
                rapport_moments.extend(content["rapport_moments"])
            
            # Collect trust indicators
            if "trust_indicators" in content:
                trust_indicators.extend(content["trust_indicators"])
        
        if sentiment_progression:
            synthesized["sentiment_progression"] = sentiment_progression[:5]  # Last 5 sentiments
        
        if rapport_moments:
            synthesized["rapport_moments"] = rapport_moments[:3]  # Top 3 rapport moments
        
        if trust_indicators:
            synthesized["trust_indicators"] = trust_indicators[:3]  # Top 3 trust indicators
        
        return synthesized
    
    def _synthesize_strategic_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize strategic memories into recommendations"""
        if not memories:
            return {}
        
        # Sort memories by timestamp (newest first)
        sorted_memories = sorted(
            memories, 
            key=lambda m: m.get("metadata", {}).get("timestamp", ""), 
            reverse=True
        )
        
        # Extract strategic insights
        synthesized = {}
        
        # Track buying signals
        buying_signals = []
        objection_patterns = []
        decision_making_style = None
        
        for memory in sorted_memories:
            content = memory.get("content", {})
            
            # Collect buying signals
            if "buying_signals" in content:
                buying_signals.extend(content["buying_signals"])
            
            # Collect objection patterns
            if "objection_patterns" in content:
                objection_patterns.extend(content["objection_patterns"])
            
            # Get decision making style (use most recent)
            if "decision_making_style" in content and decision_making_style is None:
                decision_making_style = content["decision_making_style"]
        
        if buying_signals:
            synthesized["buying_signals"] = buying_signals[:5]  # Top 5 buying signals
        
        if objection_patterns:
            synthesized["objection_patterns"] = objection_patterns[:3]  # Top 3 objection patterns
        
        if decision_making_style:
            synthesized["decision_making_style"] = decision_making_style
        
        return synthesized
    
    def _synthesize_contextual_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize contextual memories into situational awareness"""
        if not memories:
            return {}
        
        # Sort memories by timestamp (newest first)
        sorted_memories = sorted(
            memories, 
            key=lambda m: m.get("metadata", {}).get("timestamp", ""), 
            reverse=True
        )
        
        # Extract contextual information
        synthesized = {}
        
        # Latest conversation context
        conversation_context = None
        communication_preferences = {}
        
        for memory in sorted_memories:
            content = memory.get("content", {})
            
            # Get conversation context (use most recent)
            if "conversation_context" in content and conversation_context is None:
                conversation_context = content["conversation_context"]
            
            # Merge communication preferences
            if "communication_preferences" in content:
                communication_preferences.update(content["communication_preferences"])
        
        if conversation_context:
            synthesized["conversation_context"] = conversation_context
        
        if communication_preferences:
            synthesized["communication_preferences"] = communication_preferences
        
        return synthesized
