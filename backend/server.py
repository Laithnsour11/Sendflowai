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

# Import our services
from persistent_memory import PersistentMemoryManager
from llm_service import LLMService
from agent_orchestrator import AgentOrchestrator
from communication_service import CommunicationService
from knowledge_base import KnowledgeBaseManager

# Initialize services
memory_manager = PersistentMemoryManager()
llm_service = LLMService()
agent_orchestrator = AgentOrchestrator(llm_service=llm_service, memory_manager=memory_manager)
knowledge_manager = KnowledgeBaseManager()
communication_service = CommunicationService(agent_orchestrator=agent_orchestrator, memory_manager=memory_manager)

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
        memory_manager.set_api_key(keys_data["mem0_api_key"])
    
    if "openai_api_key" in keys_data:
        llm_service.set_api_key("openai", keys_data["openai_api_key"])
    
    if "anthropic_api_key" in keys_data:
        llm_service.set_api_key("anthropic", keys_data["anthropic_api_key"])
    
    if "openrouter_api_key" in keys_data:
        llm_service.set_api_key("openrouter", keys_data["openrouter_api_key"])
    
    if "vapi_api_key" in keys_data:
        communication_service.set_vapi_api_key(keys_data["vapi_api_key"])
    
    if "sendblue_api_key" in keys_data:
        communication_service.set_sendblue_api_key(keys_data["sendblue_api_key"])
    
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

# LLM Service endpoints
@app.get("/api/llm/models")
async def get_available_models(provider: Optional[str] = None):
    """Get available models for a provider"""
    models = await llm_service.get_available_models(provider)
    return models

@app.post("/api/llm/completion")
async def generate_completion(
    messages: List[Dict[str, str]] = Body(...),
    model: Optional[str] = Body(None),
    provider: Optional[str] = Body(None),
    temperature: Optional[float] = Body(None),
    max_tokens: Optional[int] = Body(None),
    functions: Optional[List[Dict[str, Any]]] = Body(None)
):
    """Generate a completion using the LLM service"""
    completion = await llm_service.generate_completion(
        messages=messages,
        model=model,
        provider=provider,
        temperature=temperature,
        max_tokens=max_tokens,
        functions=functions
    )
    return completion

@app.post("/api/llm/completion-with-cadence")
async def generate_completion_with_cadence(
    messages: List[Dict[str, str]] = Body(...),
    model: Optional[str] = Body(None),
    provider: Optional[str] = Body(None),
    temperature: Optional[float] = Body(None),
    max_tokens: Optional[int] = Body(None)
):
    """Generate a completion with natural text cadence"""
    completion = await llm_service.generate_text_with_cadence(
        messages=messages,
        model=model,
        provider=provider,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return completion

# Memory System endpoints
@app.post("/api/memory/store")
async def store_memory(
    lead_id: str = Body(...),
    memory_type: str = Body(...),
    memory_content: Dict[str, Any] = Body(...),
    confidence_level: Optional[float] = Body(0.9)
):
    """Store a memory for a lead"""
    result = await memory_manager.store_memory(
        lead_id=lead_id,
        memory_type=memory_type,
        memory_content=memory_content,
        confidence=confidence_level
    )
    return result

@app.get("/api/memory/retrieve")
async def retrieve_memories(
    lead_id: str,
    memory_type: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 10
):
    """Retrieve memories for a lead"""
    memories = await memory_manager.retrieve_memories(
        lead_id=lead_id,
        memory_type=memory_type,
        query=query,
        limit=limit
    )
    return memories

@app.get("/api/memory/context/{lead_id}")
async def get_lead_context(lead_id: str):
    """Get synthesized lead context from memories"""
    context = await memory_manager.synthesize_lead_context(lead_id)
    return context

# Agent System endpoints
@app.post("/api/agents/select")
async def select_agent(context: Dict[str, Any] = Body(...)):
    """Select the most appropriate agent based on context"""
    agent = await agent_orchestrator.select_agent(context)
    return agent

@app.get("/api/agents/config/{agent_type}")
async def get_agent_config(agent_type: str, org_id: str):
    """Get configuration for a specific agent type"""
    config = await agent_orchestrator.get_specialized_agent_config(agent_type, org_id)
    return config

@app.post("/api/agents/generate-response")
async def generate_agent_response(
    agent_type: str = Body(...),
    message: str = Body(...),
    lead_context: Dict[str, Any] = Body(...),
    conversation_history: List[Dict[str, Any]] = Body([]),
    org_id: str = Body(...),
    use_text_cadence: bool = Body(False)
):
    """Generate a response using a specialized agent"""
    response = await agent_orchestrator.generate_agent_response(
        agent_type=agent_type,
        message=message,
        lead_context=lead_context,
        conversation_history=conversation_history,
        org_id=org_id,
        use_text_cadence=use_text_cadence
    )
    return response

@app.post("/api/conversation/process")
async def process_conversation(
    message: str = Body(...),
    lead_id: str = Body(...),
    org_id: str = Body(...),
    conversation_history: Optional[List[Dict[str, Any]]] = Body([]),
    previous_agent: Optional[str] = Body(None),
    channel: str = Body("chat")
):
    """Process a conversation message through the agent orchestrator"""
    result = await agent_orchestrator.orchestrate_conversation(
        message=message,
        lead_id=lead_id,
        org_id=org_id,
        conversation_history=conversation_history,
        previous_agent=previous_agent,
        channel=channel
    )
    
    # Store conversation in database
    convo_data = {
        "_id": str(uuid.uuid4()),
        "lead_id": lead_id,
        "org_id": org_id,
        "message": message,
        "response": result["response"],
        "agent_used": result["agent_used"]["type"],
        "channel": channel,
        "created_at": datetime.now().isoformat()
    }
    
    await db.conversations.insert_one(convo_data)
    
    return result

# Communication Service endpoints
@app.post("/api/communication/sms/send")
async def send_sms(
    phone_number: str = Body(...),
    message: str = Body(...),
    lead_id: str = Body(...),
    org_id: str = Body(...)
):
    """Send an SMS message"""
    result = await communication_service.send_sms(
        phone_number=phone_number,
        message=message,
        lead_id=lead_id,
        org_id=org_id
    )
    return result

@app.post("/api/communication/sms/send-with-cadence")
async def send_sms_with_cadence(
    phone_number: str = Body(...),
    messages: List[Dict[str, Any]] = Body(...),
    lead_id: str = Body(...),
    org_id: str = Body(...)
):
    """Send SMS messages with natural cadence"""
    result = await communication_service.send_sms_with_cadence(
        phone_number=phone_number,
        messages=messages,
        lead_id=lead_id,
        org_id=org_id
    )
    return result

@app.post("/api/communication/sms/webhook")
async def process_sms_webhook(webhook_data: Dict[str, Any] = Body(...)):
    """Process webhook from SendBlue"""
    result = await communication_service.process_sms_webhook(webhook_data)
    return result

@app.post("/api/communication/voice/call")
async def initiate_voice_call(
    phone_number: str = Body(...),
    lead_id: str = Body(...),
    org_id: str = Body(...),
    agent_type: Optional[str] = Body(None)
):
    """Initiate a voice call"""
    result = await communication_service.initiate_voice_call(
        phone_number=phone_number,
        lead_id=lead_id,
        org_id=org_id,
        agent_type=agent_type
    )
    return result

@app.post("/api/communication/voice/webhook")
async def process_vapi_webhook(webhook_data: Dict[str, Any] = Body(...)):
    """Process webhook from Vapi.ai"""
    result = await communication_service.process_vapi_webhook(webhook_data)
    return result

# Knowledge Base endpoints
@app.post("/api/knowledge/documents")
async def add_document(
    org_id: str = Body(...),
    title: str = Body(...),
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
    org_id: str = Body(...),
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

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
