from motor.motor_asyncio import AsyncIOMotorClient
import os
from fastapi import HTTPException
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Database connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'ai_closer_db')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Collections
organizations_collection = db.organizations
leads_collection = db.leads
conversations_collection = db.conversations
agent_interactions_collection = db.agent_interactions
memory_snapshots_collection = db.memory_snapshots
knowledge_base_collection = db.knowledge_base
api_keys_collection = db.api_keys

# Helper functions
async def create_document(collection, document_data):
    if "_id" not in document_data:
        document_data["_id"] = str(uuid.uuid4())
    
    document_data["created_at"] = datetime.now()
    document_data["updated_at"] = datetime.now()
    
    try:
        result = await collection.insert_one(document_data)
        return document_data
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def get_document(collection, document_id):
    try:
        document = await collection.find_one({"_id": document_id})
        if document is None:
            return None
        return document
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def update_document(collection, document_id, update_data):
    update_data["updated_at"] = datetime.now()
    
    try:
        result = await collection.update_one(
            {"_id": document_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await get_document(collection, document_id)
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def delete_document(collection, document_id):
    try:
        result = await collection.delete_one({"_id": document_id})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def list_documents(collection, filter_criteria=None, skip=0, limit=100, sort_by=None):
    try:
        cursor = collection.find(filter_criteria or {})
        
        if sort_by:
            cursor = cursor.sort(sort_by)
        
        cursor = cursor.skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Organization functions
async def create_organization(org_data):
    return await create_document(organizations_collection, org_data)

async def get_organization(org_id):
    return await get_document(organizations_collection, org_id)

async def update_organization(org_id, update_data):
    return await update_document(organizations_collection, org_id, update_data)

async def delete_organization(org_id):
    return await delete_document(organizations_collection, org_id)

async def list_organizations(skip=0, limit=100):
    return await list_documents(organizations_collection, skip=skip, limit=limit, sort_by=[("name", 1)])

# Lead functions
async def create_lead(lead_data):
    return await create_document(leads_collection, lead_data)

async def get_lead(lead_id):
    return await get_document(leads_collection, lead_id)

async def get_lead_by_ghl_id(ghl_contact_id):
    try:
        document = await leads_collection.find_one({"ghl_contact_id": ghl_contact_id})
        return document
    except Exception as e:
        logger.error(f"Error retrieving lead by GHL ID: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def update_lead(lead_id, update_data):
    return await update_document(leads_collection, lead_id, update_data)

async def delete_lead(lead_id):
    return await delete_document(leads_collection, lead_id)

async def list_leads(org_id, skip=0, limit=100):
    filter_criteria = {"org_id": org_id}
    return await list_documents(leads_collection, filter_criteria=filter_criteria, skip=skip, limit=limit, sort_by=[("updated_at", -1)])

# Conversation functions
async def create_conversation(conversation_data):
    return await create_document(conversations_collection, conversation_data)

async def get_conversation(conversation_id):
    return await get_document(conversations_collection, conversation_id)

async def update_conversation(conversation_id, update_data):
    return await update_document(conversations_collection, conversation_id, update_data)

async def delete_conversation(conversation_id):
    return await delete_document(conversations_collection, conversation_id)

async def list_conversations(lead_id=None, skip=0, limit=100):
    filter_criteria = {}
    if lead_id:
        filter_criteria["lead_id"] = lead_id
    
    return await list_documents(conversations_collection, filter_criteria=filter_criteria, skip=skip, limit=limit, sort_by=[("created_at", -1)])

# Memory functions
async def create_memory(memory_data):
    return await create_document(memory_snapshots_collection, memory_data)

async def get_memory(memory_id):
    return await get_document(memory_snapshots_collection, memory_id)

async def update_memory(memory_id, update_data):
    return await update_document(memory_snapshots_collection, memory_id, update_data)

async def delete_memory(memory_id):
    return await delete_document(memory_snapshots_collection, memory_id)

async def list_memories(lead_id, skip=0, limit=100):
    filter_criteria = {"lead_id": lead_id}
    return await list_documents(memory_snapshots_collection, filter_criteria=filter_criteria, skip=skip, limit=limit, sort_by=[("created_at", -1)])

# Knowledge base functions
async def create_knowledge_item(knowledge_data):
    return await create_document(knowledge_base_collection, knowledge_data)

async def get_knowledge_item(item_id):
    return await get_document(knowledge_base_collection, item_id)

async def update_knowledge_item(item_id, update_data):
    return await update_document(knowledge_base_collection, item_id, update_data)

async def delete_knowledge_item(item_id):
    return await delete_document(knowledge_base_collection, item_id)

async def list_knowledge_items(org_id, skip=0, limit=100):
    filter_criteria = {"org_id": org_id}
    return await list_documents(knowledge_base_collection, filter_criteria=filter_criteria, skip=skip, limit=limit, sort_by=[("title", 1)])

# API keys functions
async def get_api_keys(org_id):
    try:
        document = await api_keys_collection.find_one({"org_id": org_id})
        return document
    except Exception as e:
        logger.error(f"Error retrieving API keys: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

async def create_or_update_api_keys(org_id, keys_data):
    try:
        keys_data["updated_at"] = datetime.now()
        
        result = await api_keys_collection.update_one(
            {"org_id": org_id},
            {"$set": keys_data},
            upsert=True
        )
        
        return await get_api_keys(org_id)
    except Exception as e:
        logger.error(f"Error updating API keys: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
