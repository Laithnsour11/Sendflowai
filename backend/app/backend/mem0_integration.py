import logging
import json
import httpx
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import os
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class Mem0Integration:
    """Integration with Mem0.ai for persistent memory management"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.mem0.ai/v1"
        self.headers = {}
        
        if self.api_key:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def set_api_key(self, api_key: str):
        """Set the Mem0 API key and update headers"""
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def validate_key(self) -> bool:
        """Validate the API key by making a test request"""
        if not self.api_key:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/account",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to validate Mem0 API key: {e}")
            return False
    
    async def store_memory(
        self, 
        lead_id: str, 
        memory_data: Dict[str, Any], 
        memory_type: str = "factual", 
        confidence_level: float = 0.9
    ) -> Dict[str, Any]:
        """
        Store a memory for a lead in Mem0
        
        Args:
            lead_id: ID of the lead (used as Mem0 user_id)
            memory_data: Data to store in memory
            memory_type: Type of memory (factual, emotional, strategic, contextual)
            confidence_level: Confidence level of the memory (0.0 to 1.0)
            
        Returns:
            Dict containing the stored memory information with Mem0 memory_id
        """
        if not self.api_key:
            logger.warning("Mem0 API key not set, cannot store memory")
            raise ValueError("Mem0 API key not configured")
        
        # Format the memory content based on the memory type
        memory_content = self._format_memory_content(memory_data, memory_type)
        
        # Create memory payload for Mem0
        payload = {
            "user_id": lead_id,
            "messages": [
                {
                    "role": "assistant" if memory_type in ["strategic", "emotional"] else "system",
                    "content": json.dumps(memory_content)
                }
            ],
            "metadata": {
                "memory_type": memory_type,
                "confidence_level": confidence_level,
                "source": "ai_closer",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/memories",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                mem0_response = response.json()
                
                # Create memory record with Mem0 memory_id
                memory = {
                    "id": str(uuid.uuid4()),
                    "lead_id": lead_id,
                    "mem0_memory_id": mem0_response.get("memory_id"),
                    "memory_type": memory_type,
                    "memory_content": memory_content,
                    "confidence_level": confidence_level,
                    "retrieval_count": 0,
                    "created_at": datetime.now().isoformat(),
                    "last_accessed": datetime.now().isoformat()
                }
                
                # Return the memory record
                return memory
                
        except Exception as e:
            logger.error(f"Error storing memory in Mem0: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to store memory in Mem0: {str(e)}")
    
    def _format_memory_content(self, memory_data: Dict[str, Any], memory_type: str) -> Dict[str, Any]:
        """Format memory content based on the memory type"""
        
        if memory_type == "factual":
            # Structure for factual memories (preferences, facts, constraints)
            return {
                "factual_data": memory_data,
                "memory_description": "Factual information about the lead"
            }
        
        elif memory_type == "emotional":
            # Structure for emotional memories (sentiment, rapport, trust)
            return {
                "emotional_data": memory_data,
                "memory_description": "Emotional insights and relationship building"
            }
        
        elif memory_type == "strategic":
            # Structure for strategic memories (buying signals, objections, strategies)
            return {
                "strategic_data": memory_data,
                "memory_description": "Strategic insights for lead conversion"
            }
        
        elif memory_type == "contextual":
            # Structure for contextual memories (conversation context, timing, preferences)
            return {
                "contextual_data": memory_data,
                "memory_description": "Contextual awareness about the lead"
            }
        
        else:
            # Default structure for unknown memory types
            return {
                "data": memory_data,
                "memory_description": f"Memory of type {memory_type}"
            }
    
    async def search_memories(
        self, 
        lead_id: str, 
        query: str, 
        memory_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant memories for a lead
        
        Args:
            lead_id: ID of the lead (used as Mem0 user_id)
            query: Search query
            memory_type: Optional filter by memory type
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memories
        """
        if not self.api_key:
            logger.warning("Mem0 API key not set, cannot search memories")
            raise ValueError("Mem0 API key not configured")
        
        # Create search payload
        payload = {
            "user_id": lead_id,
            "query": query,
            "limit": limit
        }
        
        # Add filter for memory_type if specified
        if memory_type:
            payload["filters"] = {
                "metadata.memory_type": memory_type
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                search_results = response.json()
                
                # Process and format the search results
                memories = []
                for result in search_results.get("memories", []):
                    # Parse the memory content
                    content = result.get("messages", [])[0].get("content", "{}")
                    try:
                        memory_content = json.loads(content)
                    except:
                        memory_content = {"raw_content": content}
                    
                    # Get metadata
                    metadata = result.get("metadata", {})
                    
                    # Create formatted memory object
                    memory = {
                        "id": str(uuid.uuid4()),
                        "lead_id": lead_id,
                        "mem0_memory_id": result.get("memory_id"),
                        "memory_type": metadata.get("memory_type", "unknown"),
                        "memory_content": memory_content,
                        "confidence_level": metadata.get("confidence_level", 0.5),
                        "relevance_score": result.get("score", 0.0),
                        "created_at": metadata.get("timestamp", result.get("created_at", "")),
                        "last_accessed": datetime.now().isoformat()
                    }
                    
                    memories.append(memory)
                
                return memories
                
        except Exception as e:
            logger.error(f"Error searching memories in Mem0: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to search memories in Mem0: {str(e)}")
    
    async def get_memories_by_type(
        self, 
        lead_id: str, 
        memory_type: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get memories for a lead filtered by memory type
        
        Args:
            lead_id: ID of the lead (used as Mem0 user_id)
            memory_type: Type of memory to retrieve
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of memories of the specified type
        """
        # For this function, we'll search with a general query but filter by memory_type
        general_query = f"memories of type {memory_type}"
        return await self.search_memories(lead_id, general_query, memory_type, limit)
    
    async def delete_memory(self, mem0_memory_id: str) -> bool:
        """
        Delete a memory from Mem0
        
        Args:
            mem0_memory_id: ID of the memory in Mem0
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if not self.api_key:
            logger.warning("Mem0 API key not set, cannot delete memory")
            raise ValueError("Mem0 API key not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/memories/{mem0_memory_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error deleting memory from Mem0: {e}")
            return False
    
    async def synthesize_lead_context(self, lead_id: str) -> Dict[str, Any]:
        """
        Synthesize a comprehensive lead context from memories in Mem0
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            Dict containing synthesized lead context
        """
        # Retrieve memories of all types
        factual_memories = await self.get_memories_by_type(lead_id, "factual")
        emotional_memories = await self.get_memories_by_type(lead_id, "emotional")
        strategic_memories = await self.get_memories_by_type(lead_id, "strategic")
        contextual_memories = await self.get_memories_by_type(lead_id, "contextual")
        
        # Synthesize into a single context object
        context = {
            "id": lead_id,
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
        
        # For MVP, just use the most recent memory
        # In a more advanced implementation, this would merge information from multiple memories
        latest_memory = max(memories, key=lambda m: m["created_at"])
        return latest_memory["memory_content"].get("factual_data", {})
    
    def _synthesize_emotional_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize emotional memories into relationship insights"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m["created_at"])
        return latest_memory["memory_content"].get("emotional_data", {})
    
    def _synthesize_strategic_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize strategic memories into recommendations"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m["created_at"])
        return latest_memory["memory_content"].get("strategic_data", {})
    
    def _synthesize_contextual_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize contextual memories into situational awareness"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m["created_at"])
        return latest_memory["memory_content"].get("contextual_data", {})
