import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import os

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages persistent memory storage and retrieval"""
    
    def __init__(self, mem0_api_key: Optional[str] = None):
        self.mem0_api_key = mem0_api_key
    
    async def store_memory(self, lead_id: str, memory_data: Dict[str, Any], memory_type: str = "factual") -> Dict[str, Any]:
        """
        Store a memory for a lead
        
        Args:
            lead_id: ID of the lead
            memory_data: Data to store in memory
            memory_type: Type of memory (factual, emotional, strategic, contextual)
            
        Returns:
            Dict containing the stored memory information
        """
        if not self.mem0_api_key:
            logger.warning("Mem0 API key not set, storing memory locally")
            return self._store_memory_locally(lead_id, memory_data, memory_type)
        
        # In a real implementation, this would call the Mem0 API
        # For MVP, we'll simulate local storage
        return self._store_memory_locally(lead_id, memory_data, memory_type)
    
    def _store_memory_locally(self, lead_id: str, memory_data: Dict[str, Any], memory_type: str) -> Dict[str, Any]:
        """Simulate storing memory locally for testing without API keys"""
        memory_id = str(uuid.uuid4())
        
        memory = {
            "id": memory_id,
            "lead_id": lead_id,
            "memory_type": memory_type,
            "memory_content": memory_data,
            "confidence_level": 0.9,
            "retrieval_count": 0,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        
        # In a real implementation, this would be stored in a database
        # For MVP, we'll log it
        logger.info(f"Stored memory: {json.dumps(memory, default=str)}")
        
        return memory
    
    async def retrieve_memories(self, lead_id: str, query: Optional[str] = None, memory_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a lead
        
        Args:
            lead_id: ID of the lead
            query: Optional search query
            memory_type: Optional filter by memory type
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memories
        """
        if not self.mem0_api_key:
            logger.warning("Mem0 API key not set, retrieving mock memories")
            return self._retrieve_mock_memories(lead_id, query, memory_type, limit)
        
        # In a real implementation, this would call the Mem0 API
        # For MVP, we'll return mock memories
        return self._retrieve_mock_memories(lead_id, query, memory_type, limit)
    
    def _retrieve_mock_memories(self, lead_id: str, query: Optional[str], memory_type: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Generate mock memories for testing without API keys"""
        # Mock memories of different types
        mock_memories = [
            {
                "id": str(uuid.uuid4()),
                "lead_id": lead_id,
                "memory_type": "factual",
                "memory_content": {
                    "property_preferences": {
                        "bedrooms": 3,
                        "bathrooms": 2,
                        "location": "downtown",
                        "property_type": "condo"
                    },
                    "budget": {
                        "min": 300000,
                        "max": 450000
                    }
                },
                "confidence_level": 0.9,
                "created_at": "2023-01-15T10:30:00Z"
            },
            {
                "id": str(uuid.uuid4()),
                "lead_id": lead_id,
                "memory_type": "emotional",
                "memory_content": {
                    "sentiment_progression": [
                        {"date": "2023-01-10", "sentiment": "neutral"},
                        {"date": "2023-01-15", "sentiment": "positive"}
                    ],
                    "rapport_moments": [
                        {"date": "2023-01-15", "description": "Shared interest in local restaurants"}
                    ]
                },
                "confidence_level": 0.8,
                "created_at": "2023-01-15T10:35:00Z"
            },
            {
                "id": str(uuid.uuid4()),
                "lead_id": lead_id,
                "memory_type": "strategic",
                "memory_content": {
                    "buying_signals": [
                        {"date": "2023-01-15", "signal": "Asked about financing options"}
                    ],
                    "objection_patterns": [
                        {"date": "2023-01-10", "objection": "Concerned about property taxes"}
                    ]
                },
                "confidence_level": 0.85,
                "created_at": "2023-01-15T10:40:00Z"
            },
            {
                "id": str(uuid.uuid4()),
                "lead_id": lead_id,
                "memory_type": "contextual",
                "memory_content": {
                    "conversation_context": {
                        "preferred_contact_times": "evenings",
                        "communication_style": "direct and informative"
                    }
                },
                "confidence_level": 0.75,
                "created_at": "2023-01-15T10:45:00Z"
            }
        ]
        
        # Filter by memory type if specified
        if memory_type:
            filtered_memories = [m for m in mock_memories if m["memory_type"] == memory_type]
        else:
            filtered_memories = mock_memories
        
        # If there's a query, simulate semantic search
        if query:
            query_lower = query.lower()
            if "budget" in query_lower or "price" in query_lower:
                return [m for m in filtered_memories if m["memory_type"] == "factual"]
            elif "emotional" in query_lower or "rapport" in query_lower:
                return [m for m in filtered_memories if m["memory_type"] == "emotional"]
            elif "buying" in query_lower or "signal" in query_lower:
                return [m for m in filtered_memories if m["memory_type"] == "strategic"]
            elif "context" in query_lower or "preference" in query_lower:
                return [m for m in filtered_memories if m["memory_type"] == "contextual"]
        
        # Return memories, limited by the specified limit
        return filtered_memories[:limit]
    
    async def synthesize_lead_context(self, lead_id: str) -> Dict[str, Any]:
        """
        Synthesize a comprehensive lead context from memories
        
        Args:
            lead_id: ID of the lead
            
        Returns:
            Dict containing synthesized lead context
        """
        # Retrieve memories of all types
        factual_memories = await self.retrieve_memories(lead_id, memory_type="factual")
        emotional_memories = await self.retrieve_memories(lead_id, memory_type="emotional")
        strategic_memories = await self.retrieve_memories(lead_id, memory_type="strategic")
        contextual_memories = await self.retrieve_memories(lead_id, memory_type="contextual")
        
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
        latest_memory = max(memories, key=lambda m: m["created_at"])
        return latest_memory["memory_content"]
    
    def _synthesize_emotional_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize emotional memories into relationship insights"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m["created_at"])
        return latest_memory["memory_content"]
    
    def _synthesize_strategic_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize strategic memories into recommendations"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m["created_at"])
        return latest_memory["memory_content"]
    
    def _synthesize_contextual_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize contextual memories into situational awareness"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m["created_at"])
        return latest_memory["memory_content"]
