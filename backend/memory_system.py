import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class MemorySystem:
    """Manages persistent memory storage and retrieval with Mem0 integration"""
    
    def __init__(self, mem0_api_key: Optional[str] = None):
        self.mem0_api_key = mem0_api_key or os.environ.get('MEM0_API_KEY')
        self.mem0_api_url = "https://api.mem0.ai/v1"  # Example API URL
    
    def set_api_key(self, mem0_api_key: str):
        """Set Mem0 API key"""
        self.mem0_api_key = mem0_api_key
    
    async def _make_mem0_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Mem0 API"""
        if not self.mem0_api_key:
            logger.warning("Mem0 API key not set, using mock data")
            return await self._generate_mock_response(method, endpoint, data)
        
        url = f"{self.mem0_api_url}/{endpoint}"
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
            logger.error(f"HTTP error occurred while making Mem0 request: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Mem0 API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error making Mem0 request: {e}")
            return await self._generate_mock_response(method, endpoint, data)
    
    async def _generate_mock_response(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate mock response for local testing without API key"""
        if endpoint.startswith("users") and endpoint.endswith("memories") and method.lower() == "post":
            # Mock creating a memory
            return {
                "memory_id": str(uuid.uuid4()),
                "user_id": data.get("user_id"),
                "memory_type": data.get("memory_type", "factual"),
                "content": data.get("content", {}),
                "created_at": datetime.now().isoformat()
            }
        elif endpoint.startswith("users") and endpoint.endswith("memories") and method.lower() == "get":
            # Mock retrieving memories
            return {
                "memories": [
                    {
                        "memory_id": str(uuid.uuid4()),
                        "user_id": data.get("user_id"),
                        "memory_type": "factual",
                        "content": {
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
                        "created_at": (datetime.now().replace(day=datetime.now().day-5)).isoformat()
                    },
                    {
                        "memory_id": str(uuid.uuid4()),
                        "user_id": data.get("user_id"),
                        "memory_type": "emotional",
                        "content": {
                            "sentiment_progression": [
                                {"date": (datetime.now().replace(day=datetime.now().day-10)).isoformat(), "sentiment": "neutral"},
                                {"date": (datetime.now().replace(day=datetime.now().day-5)).isoformat(), "sentiment": "positive"}
                            ],
                            "rapport_moments": [
                                {"date": (datetime.now().replace(day=datetime.now().day-5)).isoformat(), "description": "Shared interest in local restaurants"}
                            ]
                        },
                        "created_at": (datetime.now().replace(day=datetime.now().day-5)).isoformat()
                    },
                    {
                        "memory_id": str(uuid.uuid4()),
                        "user_id": data.get("user_id"),
                        "memory_type": "strategic",
                        "content": {
                            "buying_signals": [
                                {"date": (datetime.now().replace(day=datetime.now().day-5)).isoformat(), "signal": "Asked about financing options"}
                            ],
                            "objection_patterns": [
                                {"date": (datetime.now().replace(day=datetime.now().day-10)).isoformat(), "objection": "Concerned about property taxes"}
                            ]
                        },
                        "created_at": (datetime.now().replace(day=datetime.now().day-5)).isoformat()
                    },
                    {
                        "memory_id": str(uuid.uuid4()),
                        "user_id": data.get("user_id"),
                        "memory_type": "contextual",
                        "content": {
                            "conversation_context": {
                                "preferred_contact_times": "evenings",
                                "communication_style": "direct and informative"
                            }
                        },
                        "created_at": (datetime.now().replace(day=datetime.now().day-5)).isoformat()
                    }
                ]
            }
        
        # Default mock response
        return {
            "success": True,
            "mock": True,
            "endpoint": endpoint,
            "method": method,
            "data": data
        }
    
    async def store_memory(self, 
                         lead_id: str, 
                         memory_type: str, 
                         memory_content: Dict[str, Any],
                         confidence_level: Optional[float] = 0.9) -> Dict[str, Any]:
        """
        Store a memory for a lead
        
        Args:
            lead_id: ID of the lead (corresponds to Mem0 user_id)
            memory_type: Type of memory (factual, emotional, strategic, contextual)
            memory_content: Data to store in memory
            confidence_level: Confidence level for the memory
            
        Returns:
            Dict containing the stored memory information
        """
        endpoint = f"users/{lead_id}/memories"
        data = {
            "user_id": lead_id,
            "memory_type": memory_type,
            "content": memory_content,
            "confidence_level": confidence_level
        }
        
        response = await self._make_mem0_request("post", endpoint, data)
        
        # Store in local database for tracking
        memory_snapshot = {
            "id": str(uuid.uuid4()),
            "lead_id": lead_id,
            "mem0_memory_id": response.get("memory_id"),
            "memory_type": memory_type,
            "memory_content": memory_content,
            "confidence_level": confidence_level,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        
        # In a real implementation, this would be stored in a database
        logger.info(f"Stored memory snapshot: {json.dumps(memory_snapshot, default=str)}")
        
        return memory_snapshot
    
    async def retrieve_memories(self, 
                              lead_id: str, 
                              memory_type: Optional[str] = None,
                              query: Optional[str] = None,
                              limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a lead
        
        Args:
            lead_id: ID of the lead
            memory_type: Optional filter by memory type
            query: Optional search query
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memories
        """
        endpoint = f"users/{lead_id}/memories"
        params = {
            "user_id": lead_id,
            "limit": limit
        }
        
        if memory_type:
            params["memory_type"] = memory_type
            
        if query:
            params["query"] = query
        
        response = await self._make_mem0_request("get", endpoint, params)
        
        # Update last accessed timestamp for these memories
        memories = response.get("memories", [])
        for memory in memories:
            memory["last_accessed"] = datetime.now().isoformat()
        
        return memories
    
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
        
        # For MVP, just use the content from the most recent memory
        sorted_memories = sorted(memories, key=lambda m: m.get("created_at", ""), reverse=True)
        if sorted_memories:
            return sorted_memories[0].get("content", {})
        
        return {}
    
    def _synthesize_emotional_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize emotional memories into relationship insights"""
        if not memories:
            return {}
        
        # For MVP, just use the content from the most recent memory
        sorted_memories = sorted(memories, key=lambda m: m.get("created_at", ""), reverse=True)
        if sorted_memories:
            return sorted_memories[0].get("content", {})
        
        return {}
    
    def _synthesize_strategic_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize strategic memories into recommendations"""
        if not memories:
            return {}
        
        # For MVP, just use the content from the most recent memory
        sorted_memories = sorted(memories, key=lambda m: m.get("created_at", ""), reverse=True)
        if sorted_memories:
            return sorted_memories[0].get("content", {})
        
        return {}
    
    def _synthesize_contextual_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize contextual memories into situational awareness"""
        if not memories:
            return {}
        
        # For MVP, just use the content from the most recent memory
        sorted_memories = sorted(memories, key=lambda m: m.get("created_at", ""), reverse=True)
        if sorted_memories:
            return sorted_memories[0].get("content", {})
        
        return {}
