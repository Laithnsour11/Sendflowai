from fastapi import FastAPI, HTTPException, Depends, Query, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
import logging
import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Local imports
from .models import (
    Organization, OrganizationCreate, OrganizationUpdate,
    LeadProfile, LeadProfileCreate, LeadProfileUpdate,
    Conversation, ConversationCreate,
    AgentInteraction, MemorySnapshot, KnowledgeBase, ApiKeys, ApiKeysUpdate
)
import backend.database as db
from backend.ghl import GHLIntegration
from backend.agents import AgentOrchestrator, ConversationManager
from backend.memory import MemoryManager
from backend.knowledge import KnowledgeBaseManager

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
db_instance = client[db_name]

# Initialize services
ghl_integration = GHLIntegration()
agent_orchestrator = AgentOrchestrator()
conversation_manager = ConversationManager(agent_orchestrator)
memory_manager = MemoryManager()
knowledge_manager = KnowledgeBaseManager()

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

# Dependency for API key management
async def get_api_keys(org_id: str):
    api_keys = await db.get_api_keys(org_id)
    return api_keys or {}

# Root endpoint
@app.get("/api")
async def root():
    return {"message": "Welcome to AI Closer API", "version": "1.0.0"}

# Organization endpoints
@app.post("/api/organizations", response_model=Organization)
async def create_organization(org_data: OrganizationCreate):
    org_dict = org_data.dict()
    result = await db.create_organization(org_dict)
    return result

@app.get("/api/organizations", response_model=List[Organization])
async def get_organizations(skip: int = 0, limit: int = 100):
    orgs = await db.list_organizations(skip=skip, limit=limit)
    return orgs

@app.get("/api/organizations/{org_id}", response_model=Organization)
async def get_organization(org_id: str):
    org = await db.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@app.put("/api/organizations/{org_id}", response_model=Organization)
async def update_organization(org_id: str, org_data: OrganizationUpdate):
    # Filter out None values
    update_data = {k: v for k, v in org_data.dict().items() if v is not None}
    result = await db.update_organization(org_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Organization not found")
    return result

@app.delete("/api/organizations/{org_id}")
async def delete_organization(org_id: str):
    result = await db.delete_organization(org_id)
    if not result:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"status": "success", "message": "Organization deleted"}

# Lead profile endpoints
@app.post("/api/leads", response_model=LeadProfile)
async def create_lead(lead_data: LeadProfileCreate):
    lead_dict = lead_data.dict()
    result = await db.create_lead(lead_dict)
    return result

@app.get("/api/leads", response_model=List[LeadProfile])
async def get_leads(org_id: str, skip: int = 0, limit: int = 100):
    leads = await db.list_leads(org_id, skip=skip, limit=limit)
    return leads

@app.get("/api/leads/{lead_id}", response_model=LeadProfile)
async def get_lead(lead_id: str):
    lead = await db.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.put("/api/leads/{lead_id}", response_model=LeadProfile)
async def update_lead(lead_id: str, lead_data: LeadProfileUpdate):
    # Filter out None values
    update_data = {k: v for k, v in lead_data.dict().items() if v is not None}
    result = await db.update_lead(lead_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    return result

@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: str):
    result = await db.delete_lead(lead_id)
    if not result:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "success", "message": "Lead deleted"}

# Conversation endpoints
@app.post("/api/conversations", response_model=Conversation)
async def create_conversation(conversation_data: ConversationCreate):
    convo_dict = conversation_data.dict()
    result = await db.create_conversation(convo_dict)
    return result

@app.get("/api/conversations", response_model=List[Conversation])
async def get_conversations(lead_id: Optional[str] = None, skip: int = 0, limit: int = 100):
    conversations = await db.list_conversations(lead_id=lead_id, skip=skip, limit=limit)
    return conversations

@app.get("/api/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    conversation = await db.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

# Memory endpoints
@app.get("/api/memories", response_model=List[MemorySnapshot])
async def get_memories(lead_id: str, skip: int = 0, limit: int = 100):
    memories = await db.list_memories(lead_id, skip=skip, limit=limit)
    return memories

@app.get("/api/leads/{lead_id}/context")
async def get_lead_context(lead_id: str):
    lead = await db.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    context = await memory_manager.synthesize_lead_context(lead_id)
    return context

# Knowledge base endpoints
@app.post("/api/knowledge")
async def create_knowledge_item(
    org_id: str,
    title: str,
    content_type: str,
    content: str = Body(...),
    description: Optional[str] = None
):
    # Parse content based on content_type
    parsed_content = content
    if content_type in ["script", "faq"]:
        try:
            parsed_content = json.loads(content)
        except:
            parsed_content = content  # Fallback to string if not valid JSON
    
    result = await knowledge_manager.add_knowledge_item(
        org_id=org_id,
        title=title,
        content=parsed_content,
        content_type=content_type,
        description=description
    )
    return result

@app.get("/api/knowledge")
async def search_knowledge_base(
    org_id: str,
    query: str,
    content_type: Optional[str] = None,
    limit: int = 5
):
    results = await knowledge_manager.search_knowledge_base(
        org_id=org_id,
        query=query,
        content_type=content_type,
        limit=limit
    )
    return results

# Agent endpoints
@app.post("/api/agents/select")
async def select_agent(context: Dict[str, Any]):
    agent = await agent_orchestrator.select_agent(context)
    return agent

@app.post("/api/conversation/process")
async def process_message(
    message: str = Body(...),
    lead_id: str = Body(...),
    channel: str = Body(..., description="chat, sms, email, voice")
):
    # Get lead context
    lead = await db.get_lead(lead_id)
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
    await db.create_conversation(convo_data)
    
    # Store memory
    await memory_manager.store_memory(
        lead_id=lead_id,
        memory_data={
            "message": message,
            "response": result["response"]["response"],
            "analysis": result["response"].get("analysis", {})
        },
        memory_type="contextual"
    )
    
    return result

# GHL integration endpoints
@app.post("/api/ghl/webhook")
async def ghl_webhook(payload: Dict[str, Any], event_type: str = Header(None, alias="X-Event-Type")):
    logger.info(f"Received GHL webhook: {event_type}")
    
    # Handle different event types
    if event_type == "contact.created" or event_type == "contact.updated":
        contact_data = payload.get("contact", {})
        ghl_contact_id = contact_data.get("id")
        
        # Check if lead already exists
        existing_lead = await db.get_lead_by_ghl_id(ghl_contact_id)
        
        if existing_lead:
            # Update existing lead
            update_data = {
                "updated_at": datetime.now()
            }
            
            # Map GHL fields to lead profile fields
            if "name" in contact_data:
                update_data["name"] = contact_data["name"]
            
            if "email" in contact_data:
                update_data["email"] = contact_data["email"]
            
            if "phone" in contact_data:
                update_data["phone"] = contact_data["phone"]
            
            # Update custom fields if present
            if "custom_fields" in contact_data:
                custom_fields = contact_data["custom_fields"]
                
                # Example mapping of custom fields
                for field in custom_fields:
                    if field.get("name") == "Property Type":
                        if "property_preferences" not in update_data:
                            update_data["property_preferences"] = {}
                        update_data["property_preferences"]["property_type"] = field.get("value")
                    
                    elif field.get("name") == "Budget Maximum":
                        if "budget_analysis" not in update_data:
                            update_data["budget_analysis"] = {}
                        update_data["budget_analysis"]["max"] = float(field.get("value", "0"))
            
            # Update in database
            await db.update_lead(existing_lead["_id"], update_data)
            
            return {"status": "success", "message": "Lead updated"}
        else:
            # Create new lead
            # Get organization ID from contact data or use a default
            org_id = contact_data.get("location_id") or "default_org_id"
            
            lead_data = {
                "_id": str(uuid.uuid4()),
                "org_id": org_id,
                "ghl_contact_id": ghl_contact_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Map basic fields
            if "name" in contact_data:
                lead_data["name"] = contact_data["name"]
            
            if "email" in contact_data:
                lead_data["email"] = contact_data["email"]
            
            if "phone" in contact_data:
                lead_data["phone"] = contact_data["phone"]
            
            # Create in database
            await db.create_lead(lead_data)
            
            return {"status": "success", "message": "Lead created"}
    
    # Default response
    return {"status": "received", "event_type": event_type}

@app.get("/api/ghl/contacts")
async def get_ghl_contacts(org_id: str):
    # Get API keys for the organization
    api_keys = await get_api_keys(org_id)
    ghl_api_key = api_keys.get("ghl_api_key")
    
    if not ghl_api_key:
        raise HTTPException(status_code=400, detail="GHL API key not configured")
    
    # Set API key
    ghl_integration.set_api_key(ghl_api_key)
    
    # Fetch contacts
    contacts = await ghl_integration.get_contacts()
    return contacts

# API Keys management
@app.get("/api/settings/api-keys/{org_id}")
async def get_organization_api_keys(org_id: str):
    api_keys = await get_api_keys(org_id)
    
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
async def update_organization_api_keys(org_id: str, keys_data: ApiKeysUpdate):
    # Filter out None values
    update_data = {k: v for k, v in keys_data.dict().items() if v is not None}
    update_data["org_id"] = org_id
    
    result = await db.create_or_update_api_keys(org_id, update_data)
    
    # Mask sensitive data in response
    masked_result = {}
    for key_name, key_value in result.items():
        if key_name.endswith("_api_key") and key_value:
            # Show only last 4 characters
            masked_result[key_name] = "••••••••" + key_value[-4:] if len(key_value) > 4 else "••••"
        else:
            masked_result[key_name] = key_value
    
    return masked_result

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
