from fastapi import FastAPI, HTTPException, Depends, Query, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
import logging
import os
import json
import time
import uuid
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

# Import integrations
from backend.ghl import GHLIntegration
from backend.vapi import VapiIntegration
from backend.mem0 import Mem0Integration
from backend.sendblue import SendBlueIntegration

# Initialize integrations
ghl_integration = GHLIntegration()
vapi_integration = VapiIntegration(
    public_key=os.environ.get('VAPI_PUBLIC_KEY', 'd14070eb-c48a-45d5-9a53-6115b8c4d517'),
    private_key=os.environ.get('VAPI_PRIVATE_KEY', 'c948ca43-806d-4a15-8f7b-a29e019457b1')
)
mem0_integration = Mem0Integration()
sendblue_integration = SendBlueIntegration()

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
        if (key_name.endswith("_api_key") or key_name.endswith("_secret") or 
            key_name.endswith("_client_secret") or key_name.endswith("_private_key")) and key_value:
            # Show only last 4 characters
            masked_keys[key_name] = "••••••••" + key_value[-4:] if len(key_value) > 4 else "••••"
        else:
            masked_keys[key_name] = key_value
    
    # Get integration status
    integration_status = await get_integration_status(org_id)
    masked_keys["integration_status"] = integration_status
    
    return masked_keys

@app.put("/api/settings/api-keys/{org_id}")
async def update_organization_api_keys(org_id: str, keys_data: Dict[str, Any]):
    # Convert ObjectId to string to avoid serialization issues
    from bson import ObjectId
    from bson.json_util import dumps, loads
    
    # Helper function to convert ObjectId to str
    def convert_objectid_to_str(obj):
        if isinstance(obj, dict):
            return {k: convert_objectid_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_objectid_to_str(item) for item in obj]
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif hasattr(obj, '__dict__'):
            return convert_objectid_to_str(obj.__dict__)
        else:
            return obj
    
    keys_data["org_id"] = org_id
    keys_data["updated_at"] = datetime.now()
    
    # Update GHL integration with new credentials if provided
    if all(key in keys_data for key in ["ghl_client_id", "ghl_client_secret", "ghl_shared_secret"]):
        ghl_integration.set_credentials(
            client_id=keys_data["ghl_client_id"],
            client_secret=keys_data["ghl_client_secret"],
            shared_secret=keys_data["ghl_shared_secret"]
        )
    
    # Update Vapi integration with new credentials if provided
    if all(key in keys_data for key in ["vapi_public_key", "vapi_private_key"]):
        vapi_integration.set_api_keys(
            public_key=keys_data["vapi_public_key"],
            private_key=keys_data["vapi_private_key"]
        )
    
    # Update Mem0 integration with new API key if provided
    if "mem0_api_key" in keys_data and keys_data["mem0_api_key"]:
        mem0_integration.set_api_key(keys_data["mem0_api_key"])
    
    # Update SendBlue integration with new credentials if provided
    if all(key in keys_data for key in ["sendblue_api_key", "sendblue_api_secret"]):
        sendblue_integration.set_api_credentials(
            api_key=keys_data["sendblue_api_key"],
            api_secret=keys_data["sendblue_api_secret"]
        )
    
    result = await db.api_keys.update_one(
        {"org_id": org_id},
        {"$set": keys_data},
        upsert=True
    )
    
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    
    # Convert MongoDB ObjectId to string
    if api_keys and "_id" in api_keys:
        api_keys["_id"] = str(api_keys["_id"])
    
    # Convert all potential ObjectIds in the document
    api_keys = convert_objectid_to_str(api_keys)
    
    # Mask sensitive data in response
    masked_result = {}
    for key_name, key_value in api_keys.items():
        if (key_name.endswith("_api_key") or key_name.endswith("_secret") or 
            key_name.endswith("_client_secret") or key_name.endswith("_private_key")) and key_value:
            # Show only last 4 characters
            masked_result[key_name] = "••••••••" + key_value[-4:] if len(key_value) > 4 else "••••"
        else:
            masked_result[key_name] = key_value
    
    # Get updated integration status
    integration_status = await get_integration_status(org_id)
    masked_result["integration_status"] = integration_status
    
    return masked_result

async def get_integration_status(org_id: str) -> Dict[str, Any]:
    """Get the status of all integrations for an organization"""
    api_keys = await db.api_keys.find_one({"org_id": org_id})
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
    
    # Vapi status
    vapi_configured = all(key in api_keys and api_keys[key] 
                         for key in ["vapi_public_key", "vapi_private_key"])
    vapi_status = {"connected": vapi_configured}
    
    if vapi_configured:
        # Update Vapi integration with keys from database
        vapi_integration.set_api_keys(
            public_key=api_keys["vapi_public_key"],
            private_key=api_keys["vapi_private_key"]
        )
        
        # Validate the keys
        valid = await vapi_integration.validate_keys()
        vapi_status["status"] = "Connected" if valid else "Invalid credentials"
    else:
        vapi_status["status"] = "Not configured"
    
    # Mem0 status
    mem0_configured = "mem0_api_key" in api_keys and api_keys["mem0_api_key"]
    mem0_status = {"connected": mem0_configured}
    
    if mem0_configured:
        # Update Mem0 integration with key from database
        mem0_integration.set_api_key(api_keys["mem0_api_key"])
        
        # Validate the key
        valid = await mem0_integration.validate_key()
        mem0_status["status"] = "Connected" if valid else "Invalid credentials"
    else:
        mem0_status["status"] = "Not configured"
    
    # SendBlue status
    sendblue_configured = all(key in api_keys and api_keys[key] 
                             for key in ["sendblue_api_key", "sendblue_api_secret"])
    sendblue_status = {"connected": sendblue_configured}
    
    if sendblue_configured:
        # Update SendBlue integration with keys from database
        sendblue_integration.set_api_credentials(
            api_key=api_keys["sendblue_api_key"],
            api_secret=api_keys["sendblue_api_secret"]
        )
        
        # Validate the keys
        valid = await sendblue_integration.validate_credentials()
        sendblue_status["status"] = "Connected" if valid else "Invalid credentials"
    else:
        sendblue_status["status"] = "Not configured"
    
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

@app.get("/api/settings/integration-status/{org_id}")
async def get_organization_integration_status(org_id: str):
    """Get the status of all integrations for an organization"""
    return await get_integration_status(org_id)

# GHL OAuth endpoints
@app.get("/api/ghl/oauth-url")
async def get_ghl_oauth_url(org_id: str):
    # Get the GHL credentials
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    if not api_keys or "ghl_client_id" not in api_keys:
        raise HTTPException(status_code=400, detail="GHL Client ID not configured")
    
    # Set up GHL integration
    ghl_integration.set_credentials(
        client_id=api_keys["ghl_client_id"],
        client_secret=api_keys.get("ghl_client_secret", ""),
        shared_secret=api_keys.get("ghl_shared_secret", "")
    )
    
    # Generate OAuth URL
    redirect_uri = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/ghl-callback"
    oauth_url = await ghl_integration.get_oauth_url(redirect_uri)
    
    return {"oauth_url": oauth_url}

@app.post("/api/ghl/oauth-callback")
async def ghl_oauth_callback(org_id: str, code: str):
    # Get the GHL credentials
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    if not api_keys or "ghl_client_id" not in api_keys or "ghl_client_secret" not in api_keys:
        raise HTTPException(status_code=400, detail="GHL OAuth credentials not configured")
    
    # Set up GHL integration
    ghl_integration.set_credentials(
        client_id=api_keys["ghl_client_id"],
        client_secret=api_keys["ghl_client_secret"],
        shared_secret=api_keys.get("ghl_shared_secret", "")
    )
    
    # Exchange code for token
    redirect_uri = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/ghl-callback"
    try:
        token_data = await ghl_integration.exchange_code_for_token(code, redirect_uri)
        
        # Store tokens in database
        await db.api_keys.update_one(
            {"org_id": org_id},
            {"$set": {
                "ghl_access_token": token_data["access_token"],
                "ghl_refresh_token": token_data["refresh_token"],
                "ghl_token_expires_at": int(time.time()) + token_data["expires_in"],
                "ghl_location_id": token_data.get("locationId", ""),
                "ghl_company_id": token_data.get("companyId", ""),
                "updated_at": datetime.now()
            }}
        )
        
        return {"success": True, "message": "GHL account connected successfully"}
    except Exception as e:
        logger.error(f"Error exchanging GHL OAuth code: {e}")
        raise HTTPException(status_code=500, detail=f"Error connecting GHL account: {str(e)}")

# Vapi endpoints
@app.post("/api/vapi/create-call")
async def create_vapi_call(
    org_id: str, 
    phone_number: str = Body(...), 
    agent_type: str = Body(...),
    lead_id: Optional[str] = Body(None)
):
    """Create a new voice call using Vapi.ai"""
    # Get the API keys
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    if not api_keys or "vapi_public_key" not in api_keys or "vapi_private_key" not in api_keys:
        raise HTTPException(status_code=400, detail="Vapi API keys not configured")
    
    # Set up Vapi integration
    vapi_integration.set_api_keys(
        public_key=api_keys["vapi_public_key"],
        private_key=api_keys["vapi_private_key"]
    )
    
    # Get lead information if lead_id is provided
    lead_context = {}
    if lead_id:
        lead = await db.leads.find_one({"_id": lead_id})
        if lead:
            # Basic lead information
            lead_context = {
                "id": str(lead["_id"]),
                "name": lead.get("name", ""),
                "email": lead.get("email", ""),
                "phone": lead.get("phone", ""),
                "personality_type": lead.get("personality_type"),
                "relationship_stage": lead.get("relationship_stage", "initial_contact"),
                "property_preferences": lead.get("property_preferences", {}),
                "budget": lead.get("budget_analysis", {})
            }
            
            # Get memory context if Mem0 is configured
            if "mem0_api_key" in api_keys and api_keys["mem0_api_key"]:
                mem0_integration.set_api_key(api_keys["mem0_api_key"])
                memory_context = await mem0_integration.synthesize_lead_context(str(lead["_id"]))
                
                # Merge memory context with lead context
                lead_context.update(memory_context)
    
    # Configure agent based on type
    agent_config = {
        "type": agent_type,
        "name": f"{agent_type.replace('_', ' ').title()} Agent",
        "from_number": "+12345678901",  # Would be configured properly in production
        "webhook_url": f"{os.environ.get('BACKEND_URL', 'http://localhost:8000')}/api/vapi/webhook",
        "webhook_auth": f"Bearer {uuid.uuid4()}",  # Simple auth token for webhook
        "llm_provider": "openai",  # Would use org's preferred provider
        "llm_model": "gpt-4o",  # Would use org's preferred model
        "temperature": 0.7,
        "first_message": f"Hello, this is AI Closer calling from {api_keys.get('company_name', 'Real Estate Partners')}. How are you doing today?"
    }
    
    # Create the call
    try:
        result = await vapi_integration.create_intelligent_call(
            phone_number=phone_number,
            agent_config=agent_config,
            lead_context=lead_context
        )
        
        # Save the call in the database
        call_record = {
            "_id": str(uuid.uuid4()),
            "org_id": org_id,
            "lead_id": lead_id,
            "vapi_call_id": result.get("id"),
            "phone_number": phone_number,
            "agent_type": agent_type,
            "status": result.get("status", "initiated"),
            "created_at": datetime.now()
        }
        
        await db.calls.insert_one(call_record)
        
        return {
            "success": True,
            "call_id": call_record["_id"],
            "vapi_call_id": result.get("id"),
            "status": result.get("status")
        }
    except Exception as e:
        logger.error(f"Error creating Vapi call: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating call: {str(e)}")

@app.post("/api/vapi/webhook")
async def vapi_webhook(payload: Dict[str, Any]):
    """Handle webhooks from Vapi.ai"""
    logger.info(f"Received Vapi webhook: {payload.get('type')}")
    
    try:
        # Process the webhook
        result = await vapi_integration.process_webhook(payload)
        
        # Update call status in database
        call_id = payload.get("call_id")
        if call_id:
            call = await db.calls.find_one({"vapi_call_id": call_id})
            if call:
                update_data = {
                    "status": payload.get("status", call["status"]),
                    "updated_at": datetime.now()
                }
                
                # If call ended, store additional data
                if payload.get("type") == "call-ended":
                    update_data["duration"] = payload.get("duration")
                    update_data["recording_url"] = payload.get("recording_url")
                    
                    # If we have a lead_id, store memory
                    if call.get("lead_id"):
                        # Get the full call details from Vapi
                        call_details = await vapi_integration.get_call(call_id)
                        
                        # Store memory if Mem0 is configured
                        api_keys = await db.api_keys.find_one({"org_id": call["org_id"]})
                        if api_keys and "mem0_api_key" in api_keys:
                            mem0_integration.set_api_key(api_keys["mem0_api_key"])
                            
                            # Analyze the call
                            analysis = await vapi_integration.analyze_call(
                                call_id=call_id,
                                agent_config={"type": call["agent_type"]}
                            )
                            
                            # Store in Mem0
                            await mem0_integration.store_conversation_memory(
                                user_id=call["lead_id"],
                                conversation={
                                    "id": call["_id"],
                                    "channel": "voice",
                                    "agent_type": call["agent_type"],
                                    "duration_seconds": call_details.get("duration"),
                                    "transcript": call_details.get("transcript"),
                                    "created_at": datetime.now().isoformat()
                                },
                                analysis=analysis
                            )
                            
                            update_data["analysis"] = analysis
                
                await db.calls.update_one(
                    {"vapi_call_id": call_id},
                    {"$set": update_data}
                )
        
        return result
    except Exception as e:
        logger.error(f"Error processing Vapi webhook: {e}")
        return {"success": False, "error": str(e)}

# Mem0 endpoints
@app.get("/api/memory/lead/{lead_id}")
async def get_lead_memory(lead_id: str, org_id: str):
    """Get the memory context for a lead"""
    # Get the API keys
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    if not api_keys or "mem0_api_key" not in api_keys:
        raise HTTPException(status_code=400, detail="Mem0 API key not configured")
    
    # Set up Mem0 integration
    mem0_integration.set_api_key(api_keys["mem0_api_key"])
    
    try:
        # Get lead context from Mem0
        context = await mem0_integration.synthesize_lead_context(lead_id)
        return context
    except Exception as e:
        logger.error(f"Error getting lead memory: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving memory: {str(e)}")

@app.post("/api/memory/store")
async def store_memory(
    org_id: str,
    lead_id: str = Body(...),
    memory_type: str = Body(...),
    memory_data: Dict[str, Any] = Body(...)
):
    """Store a memory for a lead"""
    # Get the API keys
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    if not api_keys or "mem0_api_key" not in api_keys:
        raise HTTPException(status_code=400, detail="Mem0 API key not configured")
    
    # Set up Mem0 integration
    mem0_integration.set_api_key(api_keys["mem0_api_key"])
    
    try:
        # Store memory in Mem0
        result = await mem0_integration.store_multi_layered_memory(
            user_id=lead_id,
            memory_data=memory_data,
            memory_type=memory_type
        )
        
        return {
            "success": True,
            "memory_id": result.get("id"),
            "memory_type": memory_type
        }
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise HTTPException(status_code=500, detail=f"Error storing memory: {str(e)}")

# SendBlue endpoints
@app.post("/api/sendblue/send-message")
async def send_sendblue_message(
    org_id: str,
    to_number: str = Body(...),
    message: str = Body(...),
    from_number: Optional[str] = Body(None),
    media_urls: Optional[List[str]] = Body(None)
):
    """Send an SMS message using SendBlue"""
    # Get the API keys
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    if not api_keys or "sendblue_api_key" not in api_keys or "sendblue_api_secret" not in api_keys:
        raise HTTPException(status_code=400, detail="SendBlue API credentials not configured")
    
    # Set up SendBlue integration
    sendblue_integration.set_api_credentials(
        api_key=api_keys["sendblue_api_key"],
        api_secret=api_keys["sendblue_api_secret"]
    )
    
    try:
        # Send message via SendBlue
        result = await sendblue_integration.send_message(
            to_number=to_number,
            message=message,
            from_number=from_number,
            media_urls=media_urls
        )
        
        return {
            "success": True,
            "message_id": result.get("id"),
            "status": result.get("status")
        }
    except Exception as e:
        logger.error(f"Error sending SendBlue message: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@app.post("/api/sendblue/send-sequence")
async def send_sendblue_sequence(
    org_id: str,
    to_number: str = Body(...),
    messages: List[Dict[str, Any]] = Body(...),
    from_number: Optional[str] = Body(None),
    lead_id: Optional[str] = Body(None)
):
    """Send a sequence of SMS messages with intelligent cadence using SendBlue"""
    # Get the API keys
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    if not api_keys or "sendblue_api_key" not in api_keys or "sendblue_api_secret" not in api_keys:
        raise HTTPException(status_code=400, detail="SendBlue API credentials not configured")
    
    # Set up SendBlue integration
    sendblue_integration.set_api_credentials(
        api_key=api_keys["sendblue_api_key"],
        api_secret=api_keys["sendblue_api_secret"]
    )
    
    # Get lead context if lead_id is provided
    agent_config = {}
    if lead_id:
        lead = await db.leads.find_one({"_id": lead_id})
        if lead and lead.get("personality_type"):
            # Adjust cadence based on personality type
            if lead["personality_type"] == "analytical":
                agent_config["cadence_multiplier"] = 1.5  # Longer pauses for analytical types
            elif lead["personality_type"] == "driver":
                agent_config["cadence_multiplier"] = 0.7  # Shorter pauses for driver types
    
    try:
        # Send message sequence via SendBlue
        result = await sendblue_integration.send_multi_part_message(
            to_number=to_number,
            messages=messages,
            from_number=from_number,
            agent_config=agent_config
        )
        
        # Store in Mem0 if configured
        if lead_id and "mem0_api_key" in api_keys and api_keys["mem0_api_key"]:
            mem0_integration.set_api_key(api_keys["mem0_api_key"])
            
            # Combine all messages into a single string for context
            combined_message = "\n".join([msg["content"] for msg in messages])
            
            # Store in Mem0
            await mem0_integration.store_contextual_memory(
                user_id=lead_id,
                contextual_data={
                    "channel": "sms",
                    "direction": "outbound",
                    "content": combined_message,
                    "timestamp": datetime.now().isoformat(),
                    "message_count": len(messages)
                }
            )
        
        return {
            "success": True,
            "message_count": result.get("message_count"),
            "successful_sends": result.get("successful_sends")
        }
    except Exception as e:
        logger.error(f"Error sending SendBlue message sequence: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending message sequence: {str(e)}")

@app.post("/api/sendblue/webhook")
async def sendblue_webhook(payload: Dict[str, Any]):
    """Handle webhooks from SendBlue"""
    logger.info(f"Received SendBlue webhook: {payload.get('event_type')}")
    
    try:
        # Process the webhook
        result = await sendblue_integration.process_webhook(payload)
        
        return result
    except Exception as e:
        logger.error(f"Error processing SendBlue webhook: {e}")
        return {"success": False, "error": str(e)}

# Conversation processing endpoint
@app.post("/api/conversation/process")
async def process_message(
    org_id: str = Body(...),
    lead_id: str = Body(...),
    message: str = Body(...),
    channel: str = Body(...),  # "sms", "email", "chat"
    agent_type: Optional[str] = Body(None)
):
    """Process a message and get an AI response"""
    # Get the API keys and organization settings
    api_keys = await db.api_keys.find_one({"org_id": org_id})
    if not api_keys:
        raise HTTPException(status_code=400, detail="Organization API keys not configured")
    
    # Get the lead information
    lead = await db.leads.find_one({"_id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get lead context from Mem0 if configured
    lead_context = {
        "id": lead_id,
        "name": lead.get("name", ""),
        "email": lead.get("email", ""),
        "phone": lead.get("phone", ""),
        "personality_type": lead.get("personality_type"),
        "relationship_stage": lead.get("relationship_stage", "initial_contact"),
        "property_preferences": lead.get("property_preferences", {}),
        "budget_analysis": lead.get("budget_analysis", {})
    }
    
    if "mem0_api_key" in api_keys and api_keys["mem0_api_key"]:
        mem0_integration.set_api_key(api_keys["mem0_api_key"])
        
        try:
            memory_context = await mem0_integration.synthesize_lead_context(lead_id)
            lead_context.update(memory_context)
        except Exception as e:
            logger.error(f"Error retrieving memory context: {e}")
    
    # For demo, return a mock response based on the message and lead context
    # In a real implementation, this would use an LLM via OpenAI or OpenRouter
    
    # Determine relationship stage
    relationship_stage = lead_context.get("relationship_stage", "initial_contact")
    
    # Mock agent selection based on stage and message content
    selected_agent_type = agent_type
    
    if not selected_agent_type:
        if "appointment" in message.lower() or "schedule" in message.lower():
            selected_agent_type = "appointment_setter"
        elif "price" in message.lower() or "expensive" in message.lower() or "afford" in message.lower():
            selected_agent_type = "objection_handler"
        elif relationship_stage == "initial_contact":
            selected_agent_type = "initial_contact"
        elif relationship_stage == "qualification":
            selected_agent_type = "qualifier"
        elif relationship_stage == "nurturing":
            selected_agent_type = "nurturer"
        elif relationship_stage == "closing":
            selected_agent_type = "closer"
        else:
            selected_agent_type = "initial_contact"
    
    # Generate mock response based on agent type
    responses = {
        "initial_contact": f"Hi {lead_context.get('name', 'there')}! I'm excited to help with your real estate journey. Could you tell me what you're looking for in a property?",
        "qualifier": f"Based on what you've shared, it sounds like you're looking for a property with {lead_context.get('property_preferences', {}).get('bedrooms', '3')} bedrooms. What's your ideal price range?",
        "nurturer": f"I thought you might be interested in this new market report for {lead_context.get('property_preferences', {}).get('location', 'your area')}. Property values have increased 5% since we last spoke.",
        "objection_handler": f"I understand your concern about the price. Many of my clients have felt the same way initially. Have you considered looking at properties in nearby neighborhoods that offer similar features at a lower price point?",
        "closer": f"Based on everything we've discussed, this property at 123 Main St seems to be a perfect match for your needs. Would you like to move forward with making an offer?",
        "appointment_setter": f"I'd be happy to show you the property at 123 Main St. Would Tuesday at 2pm or Wednesday at 4pm work better for your schedule?"
    }
    
    response_text = responses.get(selected_agent_type, responses["initial_contact"])
    
    # Store the conversation
    conversation = {
        "_id": str(uuid.uuid4()),
        "org_id": org_id,
        "lead_id": lead_id,
        "message": message,
        "response": response_text,
        "channel": channel,
        "agent_type": selected_agent_type,
        "created_at": datetime.now()
    }
    
    await db.conversations.insert_one(conversation)
    
    # Store in Mem0 if configured
    if "mem0_api_key" in api_keys and api_keys["mem0_api_key"]:
        mem0_integration.set_api_key(api_keys["mem0_api_key"])
        
        # Mock analysis
        mock_analysis = {
            "factual_statements": [],
            "expressed_preferences": {},
            "sentiment_trajectory": [{"time": 0, "sentiment": "positive"}],
            "buying_indicators": []
        }
        
        # Extract basic factual statements from message
        if "bedroom" in message.lower():
            mock_analysis["factual_statements"].append("Mentioned bedrooms")
            if "3" in message:
                mock_analysis["expressed_preferences"]["bedrooms"] = 3
        
        if "bathroom" in message.lower():
            mock_analysis["factual_statements"].append("Mentioned bathrooms")
            if "2" in message:
                mock_analysis["expressed_preferences"]["bathrooms"] = 2
        
        if "budget" in message.lower() or "afford" in message.lower() or "price" in message.lower():
            mock_analysis["factual_statements"].append("Mentioned budget/price")
            # Try to extract numbers that could be prices
            import re
            numbers = re.findall(r'\d+', message)
            if numbers:
                largest_number = max([int(num) for num in numbers])
                if largest_number > 100000:  # Likely a property price
                    mock_analysis["expressed_preferences"]["budget_max"] = largest_number
        
        # Store in Mem0
        try:
            await mem0_integration.store_conversation_memory(
                user_id=lead_id,
                conversation=conversation,
                analysis=mock_analysis
            )
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
    
    # Return the response
    return {
        "id": conversation["_id"],
        "response": response_text,
        "agent_type": selected_agent_type,
        "lead_context": lead_context,
        "channel": channel
    }

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
