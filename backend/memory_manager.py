import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import os
from fastapi import HTTPException

from mem0_integration import Mem0Integration
import database as db

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages persistent memory storage and retrieval using Mem0.ai"""
    
    def __init__(self):
        self.mem0_integration = Mem0Integration()
    
    async def set_api_key_for_org(self, org_id: str) -> bool:
        """
        Set the Mem0 API key for the organization
        
        Args:
            org_id: ID of the organization
            
        Returns:
            True if API key was set successfully, False otherwise
        """
        try:
            # Get API keys for the organization
            api_keys = await db.get_api_keys(org_id)
            
            if not api_keys or "mem0_api_key" not in api_keys or not api_keys["mem0_api_key"]:
                logger.warning(f"Mem0 API key not configured for organization {org_id}")
                return False
            
            # Set the API key in the Mem0 integration
            self.mem0_integration.set_api_key(api_keys["mem0_api_key"])
            return True
            
        except Exception as e:
            logger.error(f"Error setting Mem0 API key for organization {org_id}: {e}")
            return False
    
    async def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Validate a Mem0 API key
        
        Args:
            api_key: The Mem0 API key to validate
            
        Returns:
            Dict with validation status
        """
        try:
            temp_integration = Mem0Integration(api_key)
            valid = await temp_integration.validate_key()
            
            if valid:
                return {"valid": True, "message": "Mem0 API key is valid"}
            else:
                return {"valid": False, "message": "Invalid Mem0 API key"}
                
        except Exception as e:
            logger.error(f"Error validating Mem0 API key: {e}")
            return {"valid": False, "message": f"Error validating Mem0 API key: {str(e)}"}
    
    async def store_memory(
        self, 
        org_id: str,
        lead_id: str, 
        memory_data: Dict[str, Any], 
        memory_type: str = "factual",
        confidence_level: float = 0.9
    ) -> Dict[str, Any]:
        """
        Store a memory for a lead
        
        Args:
            org_id: ID of the organization
            lead_id: ID of the lead
            memory_data: Data to store in memory
            memory_type: Type of memory (factual, emotional, strategic, contextual)
            confidence_level: Confidence level of the memory (0.0 to 1.0)
            
        Returns:
            Dict containing the stored memory information
        """
        # Ensure we have the API key set
        api_key_set = await self.set_api_key_for_org(org_id)
        
        if not api_key_set:
            logger.warning(f"Mem0 API key not set for organization {org_id}, storing memory locally")
            return await self._store_memory_locally(lead_id, memory_data, memory_type, confidence_level)
        
        try:
            # Store the memory in Mem0
            memory = await self.mem0_integration.store_memory(
                lead_id=lead_id,
                memory_data=memory_data,
                memory_type=memory_type,
                confidence_level=confidence_level
            )
            
            # Store the memory record in our database
            db_memory = await db.create_memory(memory)
            
            return db_memory
            
        except Exception as e:
            logger.error(f"Error storing memory in Mem0: {e}")
            # Fall back to local storage if Mem0 fails
            return await self._store_memory_locally(lead_id, memory_data, memory_type, confidence_level)
    
    async def _store_memory_locally(
        self, 
        lead_id: str, 
        memory_data: Dict[str, Any], 
        memory_type: str,
        confidence_level: float = 0.9
    ) -> Dict[str, Any]:
        """Store memory locally if Mem0 is not available"""
        memory = {
            "_id": str(uuid.uuid4()),
            "lead_id": lead_id,
            "memory_type": memory_type,
            "memory_content": memory_data,
            "confidence_level": confidence_level,
            "retrieval_count": 0,
            "created_at": datetime.now(),
            "last_accessed": datetime.now()
        }
        
        # Store in database
        db_memory = await db.create_memory(memory)
        
        return db_memory
    
    async def retrieve_memories(
        self, 
        org_id: str,
        lead_id: str, 
        query: Optional[str] = None, 
        memory_type: Optional[str] = None, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a lead
        
        Args:
            org_id: ID of the organization
            lead_id: ID of the lead
            query: Optional search query
            memory_type: Optional filter by memory type
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of relevant memories
        """
        # Ensure we have the API key set
        api_key_set = await self.set_api_key_for_org(org_id)
        
        if not api_key_set:
            logger.warning(f"Mem0 API key not set for organization {org_id}, retrieving memories from database")
            return await self._retrieve_memories_from_db(lead_id, memory_type, limit)
        
        try:
            if query:
                # Search for memories using the query
                memories = await self.mem0_integration.search_memories(
                    lead_id=lead_id,
                    query=query,
                    memory_type=memory_type,
                    limit=limit
                )
            else:
                # Get memories by type
                memories = await self.mem0_integration.get_memories_by_type(
                    lead_id=lead_id,
                    memory_type=memory_type or "factual",
                    limit=limit
                )
            
            # Update retrieval count in our database
            for memory in memories:
                if "mem0_memory_id" in memory and memory["mem0_memory_id"]:
                    # Find the memory in our database
                    db_memory = await db.memory_snapshots_collection.find_one({
                        "mem0_memory_id": memory["mem0_memory_id"]
                    })
                    
                    if db_memory:
                        # Update retrieval count and last accessed
                        await db.update_memory(db_memory["_id"], {
                            "retrieval_count": (db_memory.get("retrieval_count", 0) + 1),
                            "last_accessed": datetime.now()
                        })
            
            return memories
            
        except Exception as e:
            logger.error(f"Error retrieving memories from Mem0: {e}")
            # Fall back to database if Mem0 fails
            return await self._retrieve_memories_from_db(lead_id, memory_type, limit)
    
    async def _retrieve_memories_from_db(
        self, 
        lead_id: str, 
        memory_type: Optional[str] = None, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve memories from database if Mem0 is not available"""
        filter_criteria = {"lead_id": lead_id}
        
        if memory_type:
            filter_criteria["memory_type"] = memory_type
        
        memories = await db.list_documents(
            db.memory_snapshots_collection,
            filter_criteria=filter_criteria,
            limit=limit,
            sort_by=[("created_at", -1)]
        )
        
        # Update retrieval count and last accessed
        for memory in memories:
            await db.update_memory(memory["_id"], {
                "retrieval_count": (memory.get("retrieval_count", 0) + 1),
                "last_accessed": datetime.now()
            })
        
        return memories
    
    async def synthesize_lead_context(self, org_id: str, lead_id: str) -> Dict[str, Any]:
        """
        Synthesize a comprehensive lead context from memories
        
        Args:
            org_id: ID of the organization
            lead_id: ID of the lead
            
        Returns:
            Dict containing synthesized lead context
        """
        # Ensure we have the API key set
        api_key_set = await self.set_api_key_for_org(org_id)
        
        if not api_key_set:
            logger.warning(f"Mem0 API key not set for organization {org_id}, synthesizing context from database")
            return await self._synthesize_context_from_db(lead_id)
        
        try:
            # Use Mem0 to synthesize the context
            context = await self.mem0_integration.synthesize_lead_context(lead_id)
            return context
            
        except Exception as e:
            logger.error(f"Error synthesizing context from Mem0: {e}")
            # Fall back to database if Mem0 fails
            return await self._synthesize_context_from_db(lead_id)
    
    async def _synthesize_context_from_db(self, lead_id: str) -> Dict[str, Any]:
        """Synthesize context from database if Mem0 is not available"""
        # Retrieve memories of all types from the database
        factual_memories = await db.list_documents(
            db.memory_snapshots_collection,
            filter_criteria={"lead_id": lead_id, "memory_type": "factual"},
            limit=10,
            sort_by=[("created_at", -1)]
        )
        
        emotional_memories = await db.list_documents(
            db.memory_snapshots_collection,
            filter_criteria={"lead_id": lead_id, "memory_type": "emotional"},
            limit=10,
            sort_by=[("created_at", -1)]
        )
        
        strategic_memories = await db.list_documents(
            db.memory_snapshots_collection,
            filter_criteria={"lead_id": lead_id, "memory_type": "strategic"},
            limit=10,
            sort_by=[("created_at", -1)]
        )
        
        contextual_memories = await db.list_documents(
            db.memory_snapshots_collection,
            filter_criteria={"lead_id": lead_id, "memory_type": "contextual"},
            limit=10,
            sort_by=[("created_at", -1)]
        )
        
        # Synthesize into a single context object
        context = {
            "id": lead_id,
            "factual_information": self._synthesize_memory_type(factual_memories),
            "relationship_insights": self._synthesize_memory_type(emotional_memories),
            "strategic_recommendations": self._synthesize_memory_type(strategic_memories),
            "situational_awareness": self._synthesize_memory_type(contextual_memories),
            "synthesis_timestamp": datetime.now().isoformat()
        }
        
        return context
    
    def _synthesize_memory_type(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize memories of a specific type"""
        if not memories:
            return {}
        
        # For MVP, just use the most recent memory
        latest_memory = max(memories, key=lambda m: m.get("created_at", datetime.min))
        return latest_memory.get("memory_content", {})
