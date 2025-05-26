from fastapi import FastAPI, HTTPException, Depends, Query, Body, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
import logging
import os
import json
from datetime import datetime
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
from backend.mem0 import Mem0Integration
from backend.openrouter_llm import OpenRouterClient
from backend.langchain_agents import AgentOrchestrator, ConversationManager
from backend.vapi_integration import VapiIntegration
from backend.sendblue_integration import SendBlueIntegration
from backend.supabase_kb import SupabaseClient, KnowledgeBaseManager

# Initialize services
supabase_client = SupabaseClient()
kb_manager = KnowledgeBaseManager(supabase_client)
openrouter_client = OpenRouterClient()
mem0_client = Mem0Integration()
agent_orchestrator = AgentOrchestrator(openrouter_client, mem0_client)
conversation_manager = ConversationManager(agent_orchestrator, mem0_client)
vapi_integration = VapiIntegration(agent_orchestrator=agent_orchestrator, mem0_client=mem0_client)
sendblue_integration = SendBlueIntegration(agent_orchestrator=agent_orchestrator, mem0_client=mem0_client)

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

# API Key Management
async def get_api_keys(org_id: str):
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    return api_keys or {}

async def update_service_api_keys(org_id: str):
    """Update all service API keys based on stored values"""
    api_keys = await get_api_keys(org_id)
    
    # Update OpenRouter API key
    if "openrouter_api_key" in api_keys:
        openrouter_client.set_api_key(api_keys["openrouter_api_key"])
    
    # Update Mem0 API key
    if "mem0_api_key" in api_keys:
        mem0_client.set_api_key(api_keys["mem0_api_key"])
    
    # Update Vapi API key
    if "vapi_api_key" in api_keys:
        vapi_integration.set_api_key(api_keys["vapi_api_key"])
    
    # Update SendBlue API credentials
    if "sendblue_api_key" in api_keys and "sendblue_api_secret" in api_keys:
        sendblue_integration.set_api_credentials(
            api_keys["sendblue_api_key"],
            api_keys["sendblue_api_secret"]
        )
    
    # Update Supabase credentials
    if "supabase_url" in api_keys and "supabase_key" in api_keys:
        supabase_client.set_credentials(
            api_keys["supabase_url"],
            api_keys["supabase_key"]
        )
    
    # Update OpenAI API key (used for embeddings in KB)
    if "openai_api_key" in api_keys:
        kb_manager.openai_api_key = api_keys["openai_api_key"]

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

@app.post("/api/organizations")
async def create_organization(org_data: Dict[str, Any]):
    result = await db.organizations.insert_one(org_data)
    org_data["_id"] = result.inserted_id
    return org_data

# Lead endpoints
@app.get("/api/leads")
async def get_leads(org_id: Optional[str] = None):
    query = {"org_id": org_id} if org_id else {}
    leads = await db.leads.find(query).to_list(length=100)
    for lead in leads:
        lead["id"] = str(lead["_id"])
    return leads

@app.post("/api/leads")
async def create_lead(lead_data: Dict[str, Any]):
    result = await db.leads.insert_one(lead_data)
    lead_data["_id"] = result.inserted_id
    return lead_data

@app.get("/api/leads/{lead_id}")
async def get_lead(lead_id: str):
    lead = await db.leads.find_one({"_id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead["id"] = str(lead["_id"])
    return lead

@app.get("/api/leads/{lead_id}/context")
async def get_lead_context(lead_id: str):
    lead = await db.leads.find_one({"_id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get context from Mem0
    context = await mem0_client.synthesize_lead_context(lead_id)
    return {**lead, "mem0_context": context}

# Conversation endpoints
@app.get("/api/conversations")
async def get_conversations(lead_id: Optional[str] = None):
    query = {"lead_id": lead_id} if lead_id else {}
    conversations = await db.conversations.find(query).to_list(length=100)
    for convo in conversations:
        convo["id"] = str(convo["_id"])
    return conversations

@app.post("/api/conversations/process")
async def process_message(
    message: str = Body(...),
    lead_id: str = Body(...),
    channel: str = Body(..., description="chat, sms, email, voice"),
    org_id: str = Body(...)
):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Get lead data
    lead = await db.leads.find_one({"_id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Process message
    result = await conversation_manager.process_message(
        message=message,
        lead_context=lead,
        channel=channel
    )
    
    # Store conversation in database
    convo_data = result["conversation"]
    await db.conversations.insert_one(convo_data)
    
    return result

# Memory endpoints
@app.get("/api/memories")
async def get_memories(lead_id: str, memory_type: Optional[str] = None):
    # Update API keys for Mem0
    org_id = None
    lead = await db.leads.find_one({"_id": lead_id})
    if lead:
        org_id = lead.get("org_id")
        if org_id:
            await update_service_api_keys(org_id)
    
    # Get memories from Mem0
    memories = await mem0_client.retrieve_memories(lead_id, memory_type=memory_type)
    return memories

@app.post("/api/memories")
async def store_memory(
    lead_id: str = Body(...),
    memory_data: Dict[str, Any] = Body(...),
    memory_type: str = Body(...),
    org_id: str = Body(...)
):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Store memory in Mem0
    result = await mem0_client.store_memory(
        user_id=lead_id,
        memory_data=memory_data,
        memory_type=memory_type
    )
    
    return result

# Knowledge Base endpoints
@app.get("/api/knowledge")
async def search_knowledge(
    org_id: str,
    query: Optional[str] = None,
    content_type: Optional[str] = None,
    limit: int = 10
):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Search knowledge base
    results = await kb_manager.search_documents(
        org_id=org_id,
        query=query,
        content_type=content_type,
        limit=limit
    )
    
    return results

@app.post("/api/knowledge")
async def add_knowledge_document(
    org_id: str = Body(...),
    title: str = Body(...),
    content: str = Body(...),
    content_type: str = Body(...),
    description: Optional[str] = Body(None),
    tags: Optional[List[str]] = Body(None)
):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Parse content based on content_type
    parsed_content = content
    if content_type in ["script", "faq"]:
        try:
            parsed_content = json.loads(content)
        except:
            parsed_content = content
    
    # Add document to knowledge base
    result = await kb_manager.add_document(
        org_id=org_id,
        title=title,
        content=parsed_content,
        content_type=content_type,
        description=description,
        tags=tags
    )
    
    return result

@app.get("/api/knowledge/{document_id}")
async def get_knowledge_document(document_id: str, org_id: str):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Get document
    document = await kb_manager.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@app.put("/api/knowledge/{document_id}")
async def update_knowledge_document(
    document_id: str,
    org_id: str = Body(...),
    update_data: Dict[str, Any] = Body(...)
):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Update document
    result = await kb_manager.update_document(document_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return result

@app.delete("/api/knowledge/{document_id}")
async def delete_knowledge_document(document_id: str, org_id: str):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Delete document
    result = await kb_manager.delete_document(document_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"status": "success"}

@app.get("/api/knowledge/agent/{agent_type}")
async def get_agent_knowledge(agent_type: str, org_id: str):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Get agent knowledge
    result = await kb_manager.get_agent_knowledge(org_id, agent_type)
    return result

# Voice communication endpoints
@app.post("/api/voice/call")
async def create_voice_call(
    lead_id: str = Body(...),
    phone_number: str = Body(...),
    agent_type: Optional[str] = Body(None),
    objective: Optional[str] = Body(None),
    org_id: str = Body(...)
):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Get lead context
    lead = await db.leads.find_one({"_id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Create call
    result = await vapi_integration.create_call(
        lead_id=lead_id,
        phone_number=phone_number,
        lead_context=lead,
        agent_type=agent_type,
        objective=objective
    )
    
    # Store call information in database
    await db.calls.insert_one({
        "lead_id": lead_id,
        "phone_number": phone_number,
        "call_id": result.get("call_id"),
        "status": result.get("status"),
        "agent_type": agent_type,
        "objective": objective,
        "created_at": datetime.now(),
        "org_id": org_id
    })
    
    return result

@app.post("/api/webhooks/vapi/{lead_id}")
async def vapi_webhook(lead_id: str, request: Request):
    # Get the lead's organization
    lead = await db.leads.find_one({"_id": lead_id})
    if lead:
        org_id = lead.get("org_id")
        if org_id:
            await update_service_api_keys(org_id)
    
    # Process webhook
    event = await request.json()
    result = await vapi_integration.handle_webhook(event)
    return result

# SMS communication endpoints
@app.post("/api/sms/send")
async def send_sms(
    lead_id: str = Body(...),
    to_number: str = Body(...),
    message: str = Body(...),
    from_number: Optional[str] = Body(None),
    media_urls: Optional[List[str]] = Body(None),
    org_id: str = Body(...)
):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Send message
    result = await sendblue_integration.send_message(
        lead_id=lead_id,
        to_number=to_number,
        message=message,
        from_number=from_number,
        media_urls=media_urls
    )
    
    # Store message information in database
    await db.messages.insert_one({
        "lead_id": lead_id,
        "to_number": to_number,
        "from_number": from_number,
        "message": message,
        "media_urls": media_urls,
        "message_id": result.get("id"),
        "status": result.get("status"),
        "created_at": datetime.now(),
        "org_id": org_id,
        "channel": "sms",
        "direction": "outbound"
    })
    
    return result

@app.post("/api/webhooks/sendblue")
async def sendblue_webhook(request: Request):
    # Process webhook
    result = await sendblue_integration.process_webhook(request)
    return result

# LLM provider endpoints
@app.get("/api/llm/models")
async def get_available_models(org_id: str):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Get available models
    models = await openrouter_client.list_models()
    return models

@app.post("/api/llm/chat")
async def create_chat_completion(
    messages: List[Dict[str, str]] = Body(...),
    model: str = Body(...),
    temperature: float = Body(0.7),
    max_tokens: Optional[int] = Body(None),
    org_id: str = Body(...)
):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Create chat completion
    result = await openrouter_client.chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return result

# Agent endpoints
@app.post("/api/agents/select")
async def select_agent(
    lead_context: Dict[str, Any] = Body(...),
    objective: str = Body(...),
    channel: str = Body(...),
    org_id: str = Body(...)
):
    # Update API keys
    await update_service_api_keys(org_id)
    
    # Select agent
    agent = await agent_orchestrator.select_agent({
        "lead_context": lead_context,
        "objective": objective,
        "channel": channel
    })
    
    return agent

@app.get("/api/agents/config")
async def get_agent_configs():
    # Get all agent configurations
    configs = {}
    for agent_type, agent_config in agent_orchestrator.agents.items():
        configs[agent_type] = {
            "name": agent_config.name,
            "description": agent_config.description,
            "llm_provider": agent_config.llm_provider,
            "llm_model": agent_config.llm_model,
            "temperature": agent_config.temperature,
            "tools": agent_config.tools
        }
    
    return configs

@app.put("/api/agents/config/{agent_type}")
async def update_agent_config(
    agent_type: str,
    llm_provider: str = Body(...),
    llm_model: str = Body(...),
    temperature: float = Body(...),
    system_prompt: Optional[str] = Body(None)
):
    # Update agent configuration
    agent = agent_orchestrator.agents.get(agent_type)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    agent.llm_provider = llm_provider
    agent.llm_model = llm_model
    agent.temperature = temperature
    
    if system_prompt:
        agent.system_prompt = system_prompt
    
    return {
        "agent_type": agent_type,
        "name": agent.name,
        "llm_provider": agent.llm_provider,
        "llm_model": agent.llm_model,
        "temperature": agent.temperature
    }

# API Keys management
@app.get("/api/settings/api-keys/{org_id}")
async def get_organization_api_keys(org_id: str):
    api_keys = await get_api_keys(org_id)
    
    # Mask sensitive data
    masked_keys = {}
    for key_name, key_value in api_keys.items():
        if key_name.endswith("_api_key") or key_name.endswith("_api_secret"):
            # Show only last 4 characters
            masked_keys[key_name] = "••••••••" + key_value[-4:] if len(key_value) > 4 else "••••"
        else:
            masked_keys[key_name] = key_value
    
    return masked_keys

@app.put("/api/settings/api-keys/{org_id}")
async def update_organization_api_keys(org_id: str, keys_data: Dict[str, Any]):
    # Filter out None values
    update_data = {k: v for k, v in keys_data.items() if v is not None}
    update_data["org_id"] = org_id
    update_data["updated_at"] = datetime.now()
    
    # Update in database
    result = await db.api_keys.update_one(
        {"org_id": org_id},
        {"$set": update_data},
        upsert=True
    )
    
    # Update service API keys
    await update_service_api_keys(org_id)
    
    # Get updated keys
    api_keys = await get_api_keys(org_id)
    
    # Mask sensitive data in response
    masked_result = {}
    for key_name, key_value in api_keys.items():
        if key_name.endswith("_api_key") or key_name.endswith("_api_secret"):
            # Show only last 4 characters
            masked_result[key_name] = "••••••••" + key_value[-4:] if len(key_value) > 4 else "••••"
        else:
            masked_result[key_name] = key_value
    
    return masked_result

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
