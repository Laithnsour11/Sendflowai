from fastapi import FastAPI, HTTPException, Depends, Query, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
import logging
import os
import json
import httpx
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

# Initialize collections
organizations_collection = db.organizations
leads_collection = db.leads
conversations_collection = db.conversations
agent_interactions_collection = db.agent_interactions
memory_snapshots_collection = db.memory_snapshots
knowledge_base_collection = db.knowledge_base
api_keys_collection = db.api_keys

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

# Memory endpoints
@app.post("/api/settings/validate-mem0-key")
async def validate_mem0_api_key(api_key: str = Body(..., embed=True)):
    """
    Validate a Mem0 API key
    
    Args:
        api_key: The Mem0 API key to validate
    
    Returns:
        Dict with validation status
    """
    if not api_key:
        return {"valid": False, "message": "API key is required"}
    
    try:
        # Make a test request to Mem0 API
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            # Try to get a basic response from the Mem0 API
            payload = {
                "user_id": "test_user",
                "messages": [{"role": "system", "content": "Test message"}]
            }
            
            response = await client.post(
                    "https://api.mem0.ai/add",
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
            
            if response.status_code == 200:
                return {"valid": True, "message": "Mem0 API key is valid"}
            else:
                return {"valid": False, "message": f"Invalid Mem0 API key: {response.text}"}
    except Exception as e:
        logger.error(f"Error validating Mem0 API key: {e}")
        return {"valid": False, "message": f"Error validating Mem0 API key: {str(e)}"}

# Organization endpoints
@app.get("/api/organizations")
async def get_organizations():
    orgs = await organizations_collection.find().to_list(length=100)
    for org in orgs:
        org["id"] = str(org["_id"])
    return orgs

# Lead endpoints
@app.get("/api/leads")
async def get_leads(org_id: Optional[str] = None):
    query = {"org_id": org_id} if org_id else {}
    leads = await leads_collection.find(query).to_list(length=100)
    for lead in leads:
        lead["id"] = str(lead["_id"])
    return leads

# Conversation endpoints
@app.get("/api/conversations")
async def get_conversations(lead_id: Optional[str] = None):
    query = {"lead_id": lead_id} if lead_id else {}
    conversations = await conversations_collection.find(query).to_list(length=100)
    for convo in conversations:
        convo["id"] = str(convo["_id"])
    return conversations

# API Keys management
@app.get("/api/settings/api-keys/{org_id}")
async def get_organization_api_keys(org_id: str):
    api_keys = await api_keys_collection.find_one({"org_id": org_id})
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
    
    result = await api_keys_collection.update_one(
        {"org_id": org_id},
        {"$set": keys_data},
        upsert=True
    )
    
    api_keys = await api_keys_collection.find_one({"org_id": org_id})
    
    # Mask sensitive data in response
    masked_result = {}
    for key_name, key_value in api_keys.items():
        if key_name.endswith("_api_key") and key_value:
            # Show only last 4 characters
            masked_result[key_name] = "••••••••" + key_value[-4:] if len(key_value) > 4 else "••••"
        else:
            masked_result[key_name] = key_value
    
    return masked_result

# Integration status endpoint
@app.get("/api/settings/integration-status/{org_id}")
async def get_organization_integration_status(org_id: str):
    """Get the status of all integrations for an organization"""
    api_keys = await api_keys_collection.find_one({"org_id": org_id})
    
    if not api_keys:
        return {
            "ghl": {"connected": False, "status": "Not configured"},
            "vapi": {"connected": False, "status": "Not configured"},
            "mem0": {"connected": False, "status": "Not configured"},
            "sendblue": {"connected": False, "status": "Not configured"},
            "openai": {"connected": False, "status": "Not configured"},
            "openrouter": {"connected": False, "status": "Not configured"}
        }
    
    # GHL status
    ghl_status = {
        "connected": all(key in api_keys and api_keys[key] 
                        for key in ["ghl_client_id", "ghl_client_secret", "ghl_shared_secret"]),
        "status": "Connected" if all(key in api_keys and api_keys[key] 
                                 for key in ["ghl_client_id", "ghl_client_secret", "ghl_shared_secret"]) 
                 else "Not configured"
    }
    
    # Mem0 status
    mem0_configured = "mem0_api_key" in api_keys and api_keys["mem0_api_key"]
    mem0_status = {"connected": mem0_configured}
    
    if mem0_configured:
        # Validate the Mem0 API key
        try:
            # Make a test request to Mem0 API
            headers = {
                "Authorization": api_keys['mem0_api_key'],
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                # Try to get a basic response from the Mem0 API
                response = await client.get(
                    "https://api.mem0.ai/add",
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    mem0_status["status"] = "Connected"
                else:
                    mem0_status["status"] = f"Invalid credentials: {response.text}"
        except Exception as e:
            logger.error(f"Error validating Mem0 API key: {e}")
            mem0_status["status"] = f"Error: {str(e)}"
    else:
        mem0_status["status"] = "Not configured"
    
    # Vapi status
    vapi_configured = "vapi_api_key" in api_keys and api_keys["vapi_api_key"]
    vapi_status = {"connected": vapi_configured, "status": "Connected" if vapi_configured else "Not configured"}
    
    # SendBlue status
    sendblue_configured = "sendblue_api_key" in api_keys and api_keys["sendblue_api_key"]
    sendblue_status = {"connected": sendblue_configured, "status": "Connected" if sendblue_configured else "Not configured"}
    
    # OpenAI status
    openai_status = {
        "connected": "openai_api_key" in api_keys and api_keys["openai_api_key"],
        "status": "Connected" if "openai_api_key" in api_keys and api_keys["openai_api_key"] else "Not configured"
    }
    
    # OpenRouter status
    openrouter_status = {
        "connected": "openrouter_api_key" in api_keys and api_keys["openrouter_api_key"],
        "status": "Connected" if "openrouter_api_key" in api_keys and api_keys["openrouter_api_key"] else "Not configured"
    }
    
    return {
        "ghl": ghl_status,
        "vapi": vapi_status,
        "mem0": mem0_status,
        "sendblue": sendblue_status,
        "openai": openai_status,
        "openrouter": openrouter_status
    }

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
