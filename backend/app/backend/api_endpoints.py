from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, Optional
import logging

from .memory_manager import MemoryManager
from . import database as db

# Configure logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Initialize memory manager
memory_manager = MemoryManager()

@router.post("/api/settings/validate-mem0-key")
async def validate_mem0_api_key(api_key: str = Body(..., embed=True)):
    """
    Validate a Mem0 API key
    
    Args:
        api_key: The Mem0 API key to validate
    
    Returns:
        Dict with validation status
    """
    result = await memory_manager.validate_api_key(api_key)
    return result

@router.post("/api/memory/store")
async def store_memory(
    org_id: str = Body(...),
    lead_id: str = Body(...),
    memory_data: Dict[str, Any] = Body(...),
    memory_type: str = Body("factual"),
    confidence_level: float = Body(0.9)
):
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
    try:
        memory = await memory_manager.store_memory(
            org_id=org_id,
            lead_id=lead_id,
            memory_data=memory_data,
            memory_type=memory_type,
            confidence_level=confidence_level
        )
        return memory
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise HTTPException(status_code=500, detail=f"Error storing memory: {str(e)}")

@router.get("/api/memory/retrieve")
async def retrieve_memories(
    org_id: str,
    lead_id: str,
    query: Optional[str] = None,
    memory_type: Optional[str] = None,
    limit: int = 5
):
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
    try:
        memories = await memory_manager.retrieve_memories(
            org_id=org_id,
            lead_id=lead_id,
            query=query,
            memory_type=memory_type,
            limit=limit
        )
        return memories
    except Exception as e:
        logger.error(f"Error retrieving memories: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving memories: {str(e)}")

@router.get("/api/memory/context/{org_id}/{lead_id}")
async def get_lead_context(org_id: str, lead_id: str):
    """
    Get the synthesized context for a lead
    
    Args:
        org_id: ID of the organization
        lead_id: ID of the lead
        
    Returns:
        Dict containing synthesized lead context
    """
    try:
        context = await memory_manager.synthesize_lead_context(org_id, lead_id)
        return context
    except Exception as e:
        logger.error(f"Error getting lead context: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting lead context: {str(e)}")
