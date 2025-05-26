from fastapi import FastAPI, HTTPException, Depends, Query, Body, Header, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional, Union
import logging
import os
import json
from datetime import datetime
import uuid
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'ai_closer_db')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Import our new components
from knowledge_base import KnowledgeBaseManager
from memory_system import MemorySystem
from multi_agent import AgentOrchestrator, AgentType

# Initialize services
knowledge_manager = KnowledgeBaseManager()
memory_system = MemorySystem()
agent_orchestrator = AgentOrchestrator()

# Create FastAPI app
app = FastAPI(title="AI Closer API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/api")
async def root():
    return {"message": "Welcome to AI Closer API", "version": "1.0.0"}

# Organization endpoints
@app.get("/api/organizations")
async def get_organizations():
    orgs = await db.organizations.find().to_list(length=100)
    for org in orgs:
        org["id"] = str(org["_id"])
    return orgs

# Lead endpoints
@app.get("/api/leads")
async def get_leads(org_id: Optional[str] = None):
    query = {"org_id": org_id} if org_id else {}
    leads = await db.leads.find(query).to_list(length=100)
    for lead in leads:
        lead["id"] = str(lead["_id"])
    return leads

# Conversation endpoints
@app.get("/api/conversations")
async def get_conversations(lead_id: Optional[str] = None):
    query = {"lead_id": lead_id} if lead_id else {}
    conversations = await db.conversations.find(query).to_list(length=100)
    for convo in conversations:
        convo["id"] = str(convo["_id"])
    return conversations

# API Keys management
@app.get("/api/settings/api-keys/{org_id}")
async def get_organization_api_keys(org_id: str):
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    if not api_keys:
        return {}
    
    # Mask sensitive data
    masked_keys = {}
    for key_name, key_value in api_keys.items():
        if key_name.endswith("_api_key") and key_value:
            # Show only last 4 characters
            masked_keys[key_name] = "••••••••" + key_value[-4:] if len(key_value) > 4 else "••••"
        else:
            masked_keys[key_name] = key_value
    
    return masked_keys

@app.put("/api/settings/api-keys/{org_id}")
async def update_organization_api_keys(org_id: str, keys_data: Dict[str, Any]):
    keys_data["org_id"] = org_id
    keys_data["updated_at"] = datetime.now()
    
    # Update API keys in respective services
    if "supabase_url" in keys_data and "supabase_key" in keys_data:
        knowledge_manager.set_api_keys(keys_data["supabase_url"], keys_data["supabase_key"])
    
    if "mem0_api_key" in keys_data:
        memory_system.set_api_key(keys_data["mem0_api_key"])
    
    if "openai_api_key" in keys_data:
        agent_orchestrator.set_api_key(keys_data["openai_api_key"])
    
    result = await db.api_keys.update_one(
        {"org_id": org_id},
        {"$set": keys_data},
        upsert=True
    )
    
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    
    # Mask sensitive data in response
    masked_result = {}
    for key_name, key_value in api_keys.items():
        if key_name.endswith("_api_key") and key_value:
            # Show only last 4 characters
            masked_result[key_name] = "••••••••" + key_value[-4:] if len(key_value) > 4 else "••••"
        else:
            masked_result[key_name] = key_value
    
    return masked_result

# Knowledge Base endpoints
@app.post("/api/knowledge/documents")
async def add_document(
    org_id: str,
    title: str,
    content: str = Body(...),
    document_type: str = Body(...),
    metadata: Optional[Dict[str, Any]] = Body({})
):
    """Add a document to the knowledge base"""
    result = await knowledge_manager.add_document(
        org_id=org_id,
        title=title,
        content=content,
        document_type=document_type,
        metadata=metadata
    )
    return result

@app.get("/api/knowledge/documents")
async def list_documents(
    org_id: str,
    document_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """List documents in the knowledge base"""
    documents = await knowledge_manager.list_documents(
        org_id=org_id,
        document_type=document_type,
        skip=skip,
        limit=limit
    )
    return documents

@app.get("/api/knowledge/documents/{document_id}")
async def get_document(document_id: str):
    """Get a specific document by ID"""
    document = await knowledge_manager.get_document(document_id)
    return document

@app.put("/api/knowledge/documents/{document_id}")
async def update_document(
    document_id: str,
    title: Optional[str] = Body(None),
    content: Optional[str] = Body(None),
    metadata: Optional[Dict[str, Any]] = Body(None)
):
    """Update a document in the knowledge base"""
    result = await knowledge_manager.update_document(
        document_id=document_id,
        title=title,
        content=content,
        metadata=metadata
    )
    return result

@app.delete("/api/knowledge/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the knowledge base"""
    result = await knowledge_manager.delete_document(document_id)
    return {"success": result}

@app.post("/api/knowledge/search")
async def search_knowledge_base(
    org_id: str,
    query: str = Body(...),
    document_type: Optional[str] = Body(None),
    limit: int = Body(5)
):
    """Search the knowledge base"""
    results = await knowledge_manager.search_documents(
        org_id=org_id,
        query=query,
        document_type=document_type,
        limit=limit
    )
    return results

# Memory System endpoints
@app.post("/api/memory")
async def store_memory(
    lead_id: str,
    memory_type: str = Body(...),
    memory_content: Dict[str, Any] = Body(...),
    confidence_level: Optional[float] = Body(0.9)
):
    """Store a memory for a lead"""
    result = await memory_system.store_memory(
        lead_id=lead_id,
        memory_type=memory_type,
        memory_content=memory_content,
        confidence_level=confidence_level
    )
    return result

@app.get("/api/memory")
async def get_memories(
    lead_id: str,
    memory_type: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 5
):
    """Get memories for a lead"""
    memories = await memory_system.retrieve_memories(
        lead_id=lead_id,
        memory_type=memory_type,
        query=query,
        limit=limit
    )
    return memories

@app.get("/api/memory/context/{lead_id}")
async def get_lead_context(lead_id: str):
    """Get synthesized lead context from memories"""
    context = await memory_system.synthesize_lead_context(lead_id)
    return context

# Multi-agent System endpoints
@app.post("/api/agents/select")
async def select_agent(context: Dict[str, Any]):
    """Select the most appropriate agent based on context"""
    agent = await agent_orchestrator.select_agent(context)
    return agent

@app.post("/api/conversation/process")
async def process_conversation(
    message: str = Body(...),
    lead_id: str = Body(...),
    lead_context: Dict[str, Any] = Body(...),
    conversation_history: Optional[List[Dict[str, Any]]] = Body(None),
    channel: str = Body("chat")
):
    """Process a conversation message"""
    result = await agent_orchestrator.orchestrate_conversation(
        message=message,
        lead_context=lead_context,
        conversation_history=conversation_history,
        channel=channel
    )
    
    # Store conversation in database
    convo_data = result["conversation"]
    await db.conversations.insert_one(convo_data)
    
    # Store memory
    await memory_system.store_memory(
        lead_id=lead_id,
        memory_type="contextual",
        memory_content={
            "message": message,
            "response": result["response"]["response"],
            "analysis": result["response"].get("analysis", {})
        }
    )
    
    return result

@app.get("/api/agents/types")
async def get_agent_types():
    """Get all available agent types"""
    return [agent_type.value for agent_type in AgentType]

# Agent Training endpoints
@app.post("/api/agents/training")
async def create_agent_training(
    org_id: str,
    agent_type: str = Body(...),
    name: str = Body(...),
    description: str = Body(None),
    system_prompt: str = Body(...),
    configuration: Dict[str, Any] = Body({})
):
    """Create or update agent training configuration"""
    training_data = {
        "id": str(uuid.uuid4()),
        "org_id": org_id,
        "agent_type": agent_type,
        "name": name,
        "description": description,
        "system_prompt": system_prompt,
        "configuration": configuration,
        "version": 1,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    result = await db.agent_training.insert_one(training_data)
    training_data["_id"] = str(training_data["_id"])
    return training_data

@app.get("/api/agents/training")
async def list_agent_training(org_id: str, agent_type: Optional[str] = None):
    """List agent training configurations"""
    query = {"org_id": org_id}
    if agent_type:
        query["agent_type"] = agent_type
    
    training_configs = await db.agent_training.find(query).to_list(length=100)
    for config in training_configs:
        config["id"] = str(config["_id"])
    
    return training_configs

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
