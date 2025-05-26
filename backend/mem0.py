import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional, Union
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class Mem0Integration:
    """Handles integration with Mem0 for persistent memory storage and retrieval"""
    
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
        """Set the Mem0 API key"""
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def store_memory(
        self, 
        user_id: str, 
        memory_data: Dict[str, Any], 
        memory_type: str = "factual",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a memory for a user/lead
        
        Args:
            user_id: ID of the user/lead
            memory_data: Data to store in memory
            memory_type: Type of memory (factual, emotional, strategic, contextual)
            metadata: Additional metadata for the memory
            
        Returns:
            Dict containing the stored memory information
        """
        if not self.api_key:
            logger.warning("Mem0 API key not set, storing memory locally")
            return self._store_memory_locally(user_id, memory_data, memory_type, metadata)
        
        # Prepare metadata with memory type
        if metadata is None:
            metadata = {}
        
        metadata["memory_type"] = memory_type
        
        # Convert memory data to messages format for Mem0
        if isinstance(memory_data, dict) and "messages" in memory_data:
            messages = memory_data["messages"]
        else:
            # Create a single message with the memory content
            messages = [{
                "role": "system",
                "content": json.dumps(memory_data) if isinstance(memory_data, dict) else str(memory_data)
            }]
        
        try:
            payload = {
                "user_id": user_id,
                "messages": messages,
                "metadata": metadata
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/memories",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Memory stored in Mem0 for user {user_id} with ID {result.get('memory_id')}")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while storing memory: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Mem0 API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error storing memory in Mem0: {e}")
            return self._store_memory_locally(user_id, memory_data, memory_type, metadata)
    
    async def retrieve_memories(
        self, 
        user_id: str, 
        query: Optional[str] = None, 
        memory_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a user/lead
        
        Args:
            user_id: ID of the user/lead
            query: Optional search query
            memory_type: Optional filter by memory type
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memories
        """
        if not self.api_key:
            logger.warning("Mem0 API key not set, retrieving mock memories")
            return self._retrieve_mock_memories(user_id, query, memory_type, limit)
        
        try:
            params = {
                "user_id": user_id,
                "limit": limit
            }
            
            if query:
                params["query"] = query
            
            filters = {}
            if memory_type:
                filters["memory_type"] = memory_type
            
            if filters:
                params["filters"] = json.dumps(filters)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                return result.get("memories", [])
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while retrieving memories: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Mem0 API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error retrieving memories from Mem0: {e}")
            return self._retrieve_mock_memories(user_id, query, memory_type, limit)
    
    async def store_multi_layered_memory(
        self,
        lead_id: str,
        interaction: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store a multi-layered memory for a lead
        
        Args:
            lead_id: ID of the lead
            interaction: Interaction data
            analysis: Conversation analysis data
            
        Returns:
            Dict containing the stored memory information
        """
        if not self.api_key:
            logger.warning("Mem0 API key not set, storing multi-layered memory locally")
            return self._store_memory_locally(lead_id, {
                "interaction": interaction,
                "analysis": analysis
            }, "multi_layered")
        
        # Create multi-layered memory structure
        memory_layers = {
            # Factual layer - concrete information
            "factual": {
                "statements": interaction.get("factual_statements", []),
                "preferences": interaction.get("expressed_preferences", {}),
                "constraints": interaction.get("mentioned_constraints", {}),
                "property_criteria": interaction.get("property_requirements", {}),
                "budget_information": interaction.get("budget_details", {}),
                "timeline": interaction.get("timeline_indicators", {})
            },
            
            # Emotional layer - relationship building
            "emotional": {
                "sentiment_progression": analysis.get("sentiment_trajectory", []),
                "trust_indicators": analysis.get("trust_building_moments", []),
                "rapport_moments": interaction.get("positive_interactions", []),
                "emotional_triggers": analysis.get("emotional_triggers", []),
                "communication_style_preferences": analysis.get("communication_preferences", {})
            },
            
            # Strategic layer - sales intelligence
            "strategic": {
                "buying_signals": analysis.get("buying_indicators", []),
                "objection_patterns": analysis.get("objection_history", []),
                "decision_making_style": analysis.get("decision_patterns", {}),
                "influence_receptivity": analysis.get("influence_analysis", {}),
                "closing_readiness": analysis.get("closing_indicators", {})
            },
            
            # Contextual layer - situational awareness
            "contextual": {
                "conversation_context": interaction.get("situational_factors", {}),
                "timing_preferences": interaction.get("optimal_contact_times", []),
                "channel_preferences": analysis.get("channel_effectiveness", {}),
                "environmental_factors": interaction.get("background_context", {})
            }
        }
        
        # Store each layer separately
        results = {}
        
        for layer_name, layer_content in memory_layers.items():
            # Skip empty layers
            if not any(layer_content.values()):
                continue
                
            metadata = {
                "memory_type": layer_name,
                "interaction_type": interaction.get("type", "conversation"),
                "channel": interaction.get("channel", "unknown"),
                "agent_type": interaction.get("agent_used", "unknown"),
                "effectiveness_score": interaction.get("outcome_score", 0.0),
                "timestamp": interaction.get("timestamp", None)
            }
            
            # Store as a single message with the layer content
            message = {
                "role": "system",
                "content": json.dumps(layer_content)
            }
            
            try:
                result = await self.store_memory(
                    user_id=lead_id,
                    memory_data={"messages": [message]},
                    memory_type=layer_name,
                    metadata=metadata
                )
                
                results[layer_name] = result
                
            except Exception as e:
                logger.error(f"Error storing {layer_name} memory layer: {e}")
        
        return {
            "lead_id": lead_id,
            "layers_stored": list(results.keys()),
            "memory_ids": {layer: result.get("memory_id") for layer, result in results.items()},
            "storage_success": len(results) > 0
        }
    
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
            "synthesis_timestamp": "now"
        }
        
        return context
    
    def _store_memory_locally(
        self, 
        user_id: str, 
        memory_data: Dict[str, Any], 
        memory_type: str = "factual",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Simulate storing memory locally for testing without API keys"""
        import uuid
        from datetime import datetime
        
        memory_id = str(uuid.uuid4())
        
        if metadata is None:
            metadata = {}
            
        metadata["memory_type"] = memory_type
        
        memory = {
            "memory_id": memory_id,
            "user_id": user_id,
            "content": memory_data,
            "metadata": metadata,
            "created_at": datetime.now().isoformat()
        }
        
        # In a real implementation, this would be stored in a database
        # For MVP, we'll log it
        logger.info(f"Stored memory locally: {json.dumps(memory, default=str)}")
        
        return memory
    
    def _retrieve_mock_memories(
        self, 
        user_id: str, 
        query: Optional[str], 
        memory_type: Optional[str], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Generate mock memories for testing without API keys"""
        import uuid
        
        # Mock memories of different types
        mock_memories = [
            {
                "memory_id": str(uuid.uuid4()),
                "user_id": user_id,
                "metadata": {"memory_type": "factual"},
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
                "confidence_level": 0.9,
                "created_at": "2023-01-15T10:30:00Z"
            },
            {
                "memory_id": str(uuid.uuid4()),
                "user_id": user_id,
                "metadata": {"memory_type": "emotional"},
                "content": {
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
                "memory_id": str(uuid.uuid4()),
                "user_id": user_id,
                "metadata": {"memory_type": "strategic"},
                "content": {
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
                "memory_id": str(uuid.uuid4()),
                "user_id": user_id,
                "metadata": {"memory_type": "contextual"},
                "content": {
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
            filtered_memories = [m for m in mock_memories if m.get("metadata", {}).get("memory_type") == memory_type]
        else:
            filtered_memories = mock_memories
        
        # If there's a query, simulate semantic search
        if query:
            query_lower = query.lower()
            if "budget" in query_lower or "price" in query_lower:
                return [m for m in filtered_memories if m.get("metadata", {}).get("memory_type") == "factual"]
            elif "emotional" in query_lower or "rapport" in query_lower:
                return [m for m in filtered_memories if m.get("metadata", {}).get("memory_type") == "emotional"]
            elif "buying" in query_lower or "signal" in query_lower:
                return [m for m in filtered_memories if m.get("metadata", {}).get("memory_type") == "strategic"]
            elif "context" in query_lower or "preference" in query_lower:
                return [m for m in filtered_memories if m.get("metadata", {}).get("memory_type") == "contextual"]
        
        # Return memories, limited by the specified limit
        return filtered_memories[:limit]
    
    def _synthesize_factual_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize factual memories into coherent information"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m.get("created_at", ""))
        
        # Try to extract content from Mem0 format
        content = latest_memory.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                pass
        
        return content
    
    def _synthesize_emotional_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize emotional memories into relationship insights"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m.get("created_at", ""))
        
        # Try to extract content from Mem0 format
        content = latest_memory.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                pass
        
        return content
    
    def _synthesize_strategic_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize strategic memories into recommendations"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m.get("created_at", ""))
        
        # Try to extract content from Mem0 format
        content = latest_memory.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                pass
        
        return content
    
    def _synthesize_contextual_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize contextual memories into situational awareness"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m.get("created_at", ""))
        
        # Try to extract content from Mem0 format
        content = latest_memory.get("content", {})
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                pass
        
        return content
