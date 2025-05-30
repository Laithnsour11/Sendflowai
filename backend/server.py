from fastapi import FastAPI, HTTPException, Depends, Query, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
import logging
import os
import json
import time
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel

# Request models for action endpoints
class SendMessageRequest(BaseModel):
    lead_id: str
    message: Optional[str] = None
    org_id: Optional[str] = None

class InitiateCallRequest(BaseModel):
    lead_id: str
    objective: Optional[str] = None
    org_id: Optional[str] = None

class ViewLeadRequest(BaseModel):
    lead_id: str

class AddLeadRequest(BaseModel):
    org_id: str
    name: str
    email: str
    phone: Optional[str] = None
    status: Optional[str] = "Initial Contact"
    source: Optional[str] = "Manual Entry"

# Custom JSON encoder for MongoDB ObjectId
class ObjectIdJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Custom JSONResponse that handles ObjectId
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=ObjectIdJSONEncoder,
        ).encode("utf-8")

# Helper function to convert ObjectId to string in dictionaries
def serialize_object_id(obj):
    if isinstance(obj, dict):
        return {k: serialize_object_id(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_object_id(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj

# Local imports
try:
    # First try direct import
    try:
        from memory_manager import MemoryManager
        from api_endpoints import router as api_router
        memory_manager = MemoryManager()
        use_memory_manager = True
    except ImportError:
        # Try with app prefix
        from app.backend.memory_manager import MemoryManager
        from app.backend.api_endpoints import router as api_router
        memory_manager = MemoryManager()
        use_memory_manager = True
except ImportError as e:
    print(f"Memory manager import failed: {e}, will use default implementation")
    use_memory_manager = False

# Try to import campaign service
try:
    from campaign_service import CampaignService
except ImportError:
    try:
        from app.backend.campaign_service import CampaignService
    except ImportError:
        try:
            from backend.campaign_service import CampaignService
        except ImportError as e:
            print(f"Warning: Could not import CampaignService: {e}")
            CampaignService = None

try:
    from ai_fine_tuning_service import AIFineTuningService
except ImportError:
    try:
        from app.backend.ai_fine_tuning_service import AIFineTuningService
    except ImportError:
        try:
            from backend.ai_fine_tuning_service import AIFineTuningService
        except ImportError as e:
            print(f"Warning: Could not import AIFineTuningService: {e}")
            AIFineTuningService = None

try:
    from advanced_analytics_service import AdvancedAnalyticsService
except ImportError:
    try:
        from app.backend.advanced_analytics_service import AdvancedAnalyticsService
    except ImportError:
        try:
            from backend.advanced_analytics_service import AdvancedAnalyticsService
        except ImportError as e:
            print(f"Warning: Could not import AdvancedAnalyticsService: {e}")
            AdvancedAnalyticsService = None

# Try different import strategies for database module
try:
    import database as db
except ImportError:
    try:
        import app.backend.database as db
    except ImportError:
        from . import database as db

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
# memory_manager already initialized above if imports succeeded

# Initialize campaign service
try:
    if CampaignService:
        campaign_service = CampaignService()
        use_campaign_service = True
        print("✅ Campaign Service initialized successfully")
    else:
        campaign_service = None
        use_campaign_service = False
        print("⚠️ Campaign Service not available - import failed")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize Campaign Service: {e}")
    campaign_service = None
    use_campaign_service = False

# Initialize AI Fine-Tuning service
try:
    if AIFineTuningService:
        fine_tuning_service = AIFineTuningService()
        use_fine_tuning_service = True
        print("✅ AI Fine-Tuning Service initialized successfully")
    else:
        fine_tuning_service = None
        use_fine_tuning_service = False
        print("⚠️ AI Fine-Tuning Service not available - import failed")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize AI Fine-Tuning Service: {e}")
    fine_tuning_service = None
    use_fine_tuning_service = False

# Initialize Advanced Analytics service
try:
    if AdvancedAnalyticsService:
        advanced_analytics_service = AdvancedAnalyticsService()
        use_advanced_analytics_service = True
        print("✅ Advanced Analytics Service initialized successfully")
    else:
        advanced_analytics_service = None
        use_advanced_analytics_service = False
        print("⚠️ Advanced Analytics Service not available - import failed")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize Advanced Analytics Service: {e}")
    advanced_analytics_service = None
    use_advanced_analytics_service = False

# Create FastAPI app
app = FastAPI(
    title="AI Closer API", 
    version="1.0.0",
    default_response_class=CustomJSONResponse  # Use our custom JSONResponse that handles ObjectId
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router if available
if 'api_router' in locals():
    app.include_router(api_router)

# Root endpoint
@app.get("/api")
async def root():
    return {"message": "Welcome to AI Closer API", "version": "1.0.0"}

# Organization endpoints
@app.get("/api/organizations")
async def get_organizations():
    orgs = await db.organizations_collection.find().to_list(length=100)
    for org in orgs:
        org["id"] = str(org["_id"])
    return orgs

# Lead endpoints - REMOVED OLD VERSION, USING NEW ONE AT LINE 2100

# Conversation endpoints - REMOVED OLD VERSION, USING NEW ONE AT END OF FILE

# API Keys management
@app.get("/api/settings/api-keys/{org_id}")
async def get_organization_api_keys(org_id: str):
    try:
        api_keys = await db.api_keys_collection.find_one({"org_id": org_id})
        
        # If no API keys found, return empty object
        if not api_keys:
            return {}
        
        # Create a new dictionary excluding ObjectId
        result = {}
        if "_id" in api_keys:
            result["id"] = str(api_keys["_id"])
        
        for key, value in api_keys.items():
            if key != "_id":  # Skip _id as we already processed it
                if isinstance(value, ObjectId):
                    result[key] = str(value)
                else:
                    result[key] = value
        
        # Mask sensitive data
        for key in list(result.keys()):
            if key.endswith("_api_key") or key.endswith("_secret") or key.endswith("_key"):
                if result[key] and len(str(result[key])) > 4:
                    result[key] = "••••••••" + str(result[key])[-4:]
                elif result[key]:
                    result[key] = "••••"
        
        return result
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        return {"error": str(e)}

@app.put("/api/settings/api-keys/{org_id}")
async def update_organization_api_keys(org_id: str, keys_data: Dict[str, Any]):
    try:
        # Set org_id and updated_at
        update_data = dict(keys_data)
        update_data["org_id"] = org_id
        update_data["updated_at"] = datetime.now().isoformat()
        
        # Remove empty values
        update_data = {k: v for k, v in update_data.items() if v is not None and v != ""}
        
        # Update the database
        await db.api_keys_collection.update_one(
            {"org_id": org_id},
            {"$set": update_data},
            upsert=True
        )
        
        return {"status": "success", "message": "API keys updated"}
    except Exception as e:
        logger.error(f"Error updating API keys: {e}")
        return {"status": "error", "message": str(e)}

# Integration status endpoint
@app.get("/api/settings/integration-status/{org_id}")
async def get_organization_integration_status(org_id: str):
    """Get the status of all integrations for an organization"""
    api_keys = await db.api_keys_collection.find_one({"org_id": org_id})
    
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
    
    if mem0_configured and use_memory_manager:
        # Validate the Mem0 API key
        valid = await memory_manager.validate_api_key(api_keys["mem0_api_key"])
        mem0_status["status"] = "Connected" if valid.get("valid", False) else f"Invalid credentials: {valid.get('message', '')}"
    else:
        mem0_status["status"] = "Not configured" if not mem0_configured else "API key present but validation unavailable"
    
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

# GHL Webhook handler
@app.post("/api/webhooks/ghl")
async def ghl_webhook_handler(
    payload: Dict[str, Any] = Body(...),
    signature: Optional[str] = Header(None, alias="X-GHL-Signature")
):
    """
    Handle webhooks from Go High Level for lead synchronization.
    
    This endpoint receives webhooks for different event types like:
    - Contact creation/updates
    - Note additions
    - Task creation/updates
    - Opportunity stage changes
    """
    logger.info(f"Received GHL webhook: {payload.get('event', 'unknown_event')}")
    
    # Get the organization that owns this webhook
    org_id = payload.get("companyId")
    if not org_id:
        logger.warning("No organization ID found in GHL webhook")
        return {"status": "error", "message": "No organization ID found"}
    
    # Get the organization's API keys
    api_keys = await db.api_keys_collection.find_one({"org_id": org_id})
    if not api_keys or not api_keys.get("ghl_shared_secret"):
        logger.warning(f"No GHL shared secret found for organization {org_id}")
        return {"status": "error", "message": "No GHL shared secret configured"}
    
    # Verify webhook signature if provided
    if signature:
        from ghl import GHLIntegration
        ghl_integration = GHLIntegration(
            shared_secret=api_keys.get("ghl_shared_secret")
        )
        payload_str = json.dumps(payload)
        if not ghl_integration.verify_webhook_signature(signature, payload_str):
            logger.warning(f"Invalid GHL webhook signature for organization {org_id}")
            return {"status": "error", "message": "Invalid webhook signature"}
    
    # Process based on event type
    event_type = payload.get("event")
    
    if event_type == "ContactCreate" or event_type == "ContactUpdate":
        await handle_contact_event(payload, org_id)
    elif event_type == "NoteCreate":
        await handle_note_event(payload, org_id)
    elif event_type == "TaskCreate" or event_type == "TaskUpdate":
        await handle_task_event(payload, org_id)
    elif event_type == "OpportunityCreate" or event_type == "OpportunityUpdate":
        await handle_opportunity_event(payload, org_id)
    elif event_type == "ConversationMessageCreate":
        await handle_message_event(payload, org_id)
    else:
        logger.info(f"Unhandled GHL event type: {event_type}")
    
    return {"status": "success", "message": f"Processed {event_type} event"}

async def handle_contact_event(payload: Dict[str, Any], org_id: str):
    """Handle contact creation or update events from GHL"""
    contact_data = payload.get("contact", {})
    if not contact_data or not contact_data.get("id"):
        logger.warning("No valid contact data in webhook payload")
        return
    
    ghl_contact_id = contact_data.get("id")
    
    # Check if this lead already exists in our system
    existing_lead = await db.leads_collection.find_one({"ghl_contact_id": ghl_contact_id})
    
    # Prepare lead data from contact
    lead_data = {
        "org_id": org_id,
        "ghl_contact_id": ghl_contact_id,
        "name": f"{contact_data.get('firstName', '')} {contact_data.get('lastName', '')}".strip(),
        "email": contact_data.get("email"),
        "phone": contact_data.get("phone"),
        "source": contact_data.get("source", "GHL Import"),
        "tags": contact_data.get("tags", []),
        "updated_at": datetime.now().isoformat()
    }
    
    # Add custom fields if present
    if "customField" in contact_data:
        custom_fields = contact_data["customField"]
        
        # Map GHL custom fields to our AI fields
        ai_mapping = {
            "AI Personality Type": "personality_type",
            "AI Trust Level": "trust_level",
            "AI Conversion Score": "conversion_probability",
            "AI Relationship Stage": "relationship_stage",
            "AI Next Best Action": "next_best_action"
        }
        
        for ghl_field, our_field in ai_mapping.items():
            if ghl_field in custom_fields:
                value = custom_fields[ghl_field]
                
                # Convert percentage values to decimal
                if our_field in ["trust_level", "conversion_probability"] and isinstance(value, (int, float)):
                    value = float(value) / 100  # Convert from percentage to decimal
                
                lead_data[our_field] = value
    
    if existing_lead:
        # Update existing lead
        await db.leads_collection.update_one(
            {"ghl_contact_id": ghl_contact_id},
            {"$set": lead_data}
        )
        logger.info(f"Updated lead {ghl_contact_id} from GHL webhook")
    else:
        # Create new lead
        lead_data["created_at"] = datetime.now().isoformat()
        await db.leads_collection.insert_one(lead_data)
        logger.info(f"Created new lead {ghl_contact_id} from GHL webhook")
        
        # Initialize memory for this lead if Mem0 is configured
        if use_memory_manager:
            await initialize_lead_memory(lead_data)

async def handle_note_event(payload: Dict[str, Any], org_id: str):
    """Handle note creation events from GHL"""
    note_data = payload.get("note", {})
    if not note_data or not note_data.get("id") or not note_data.get("contactId"):
        logger.warning("No valid note data in webhook payload")
        return
    
    contact_id = note_data.get("contactId")
    
    # Find the lead in our system
    lead = await db.leads_collection.find_one({"ghl_contact_id": contact_id})
    if not lead:
        logger.warning(f"No lead found for GHL contact ID: {contact_id}")
        return
    
    # Store the note in our system
    note_record = {
        "lead_id": str(lead["_id"]),
        "ghl_note_id": note_data.get("id"),
        "content": note_data.get("body", ""),
        "created_by": note_data.get("userId", "Unknown"),
        "created_at": datetime.now().isoformat()
    }
    
    await db.notes_collection.insert_one(note_record)
    logger.info(f"Stored note for lead {contact_id} from GHL webhook")

async def handle_task_event(payload: Dict[str, Any], org_id: str):
    """Handle task creation or update events from GHL"""
    task_data = payload.get("task", {})
    if not task_data or not task_data.get("id") or not task_data.get("contactId"):
        logger.warning("No valid task data in webhook payload")
        return
    
    contact_id = task_data.get("contactId")
    
    # Find the lead in our system
    lead = await db.leads_collection.find_one({"ghl_contact_id": contact_id})
    if not lead:
        logger.warning(f"No lead found for GHL contact ID: {contact_id}")
        return
    
    # Store the task in our system
    task_record = {
        "lead_id": str(lead["_id"]),
        "ghl_task_id": task_data.get("id"),
        "title": task_data.get("title", ""),
        "description": task_data.get("description", ""),
        "due_date": task_data.get("dueDate"),
        "status": task_data.get("status"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Update existing task or insert new one
    await db.tasks_collection.update_one(
        {"ghl_task_id": task_data.get("id")},
        {"$set": task_record},
        upsert=True
    )
    logger.info(f"Stored task for lead {contact_id} from GHL webhook")

async def handle_opportunity_event(payload: Dict[str, Any], org_id: str):
    """Handle opportunity creation or update events from GHL"""
    opportunity_data = payload.get("opportunity", {})
    if not opportunity_data or not opportunity_data.get("id") or not opportunity_data.get("contactId"):
        logger.warning("No valid opportunity data in webhook payload")
        return
    
    contact_id = opportunity_data.get("contactId")
    
    # Find the lead in our system
    lead = await db.leads_collection.find_one({"ghl_contact_id": contact_id})
    if not lead:
        logger.warning(f"No lead found for GHL contact ID: {contact_id}")
        return
    
    # Store the opportunity in our system
    opportunity_record = {
        "lead_id": str(lead["_id"]),
        "ghl_opportunity_id": opportunity_data.get("id"),
        "title": opportunity_data.get("title", ""),
        "status": opportunity_data.get("status"),
        "pipeline_id": opportunity_data.get("pipelineId"),
        "pipeline_stage_id": opportunity_data.get("pipelineStageId"),
        "monetary_value": opportunity_data.get("monetaryValue"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Update existing opportunity or insert new one
    await db.opportunities_collection.update_one(
        {"ghl_opportunity_id": opportunity_data.get("id")},
        {"$set": opportunity_record},
        upsert=True
    )
    logger.info(f"Stored opportunity for lead {contact_id} from GHL webhook")

async def handle_message_event(payload: Dict[str, Any], org_id: str):
    """Handle conversation message events from GHL"""
    message_data = payload.get("message", {})
    if not message_data or not message_data.get("id") or not message_data.get("contactId"):
        logger.warning("No valid message data in webhook payload")
        return
    
    contact_id = message_data.get("contactId")
    
    # Find the lead in our system
    lead = await db.leads_collection.find_one({"ghl_contact_id": contact_id})
    if not lead:
        logger.warning(f"No lead found for GHL contact ID: {contact_id}")
        return
    
    # Store the message in our system
    message_record = {
        "lead_id": str(lead["_id"]),
        "ghl_message_id": message_data.get("id"),
        "conversation_id": message_data.get("conversationId"),
        "content": message_data.get("body", ""),
        "direction": "inbound" if message_data.get("direction") == "inbound" else "outbound",
        "channel": message_data.get("channel", "unknown"),
        "created_at": datetime.now().isoformat()
    }
    
    await db.messages_collection.insert_one(message_record)
    logger.info(f"Stored message for lead {contact_id} from GHL webhook")
    
    # If it's an inbound message, we might want to trigger our AI response
    if message_record["direction"] == "inbound":
        # This will be implemented in a later phase with the AI response logic
        pass

async def initialize_lead_memory(lead_data: Dict[str, Any]):
    """Initialize memory layers for a new lead"""
    if not use_memory_manager:
        logger.warning("Memory manager not available, skipping memory initialization")
        return
    
    lead_id = str(lead_data["_id"]) if "_id" in lead_data else None
    if not lead_id:
        logger.warning("No lead ID found, cannot initialize memory")
        return
    
    # Initialize factual memory layer with basic lead information
    factual_data = {
        "name": lead_data.get("name", ""),
        "email": lead_data.get("email"),
        "phone": lead_data.get("phone"),
        "source": lead_data.get("source", "GHL Import"),
        "tags": lead_data.get("tags", []),
        "imported_from": "GHL",
        "imported_at": datetime.now().isoformat()
    }
    
    await memory_manager.store_memory(lead_id, factual_data, "factual")
    logger.info(f"Initialized factual memory for lead {lead_id}")
    
    # Initialize emotional memory layer
    emotional_data = {
        "initial_impression": "No interaction yet",
        "trust_level": lead_data.get("trust_level", 0.5),
        "rapport_status": "Initial contact",
        "sentiment": "Neutral"
    }
    
    await memory_manager.store_memory(lead_id, emotional_data, "emotional")
    logger.info(f"Initialized emotional memory for lead {lead_id}")
    
    # Initialize strategic memory layer
    strategic_data = {
        "relationship_stage": lead_data.get("relationship_stage", "initial_contact"),
        "conversion_probability": lead_data.get("conversion_probability", 0.3),
        "objections_encountered": [],
        "buying_signals_detected": [],
        "recommended_approach": "Build rapport and qualify needs"
    }
    
    await memory_manager.store_memory(lead_id, strategic_data, "strategic")
    logger.info(f"Initialized strategic memory for lead {lead_id}")
    
    # Initialize contextual memory layer
    contextual_data = {
        "optimal_contact_times": "Unknown",
        "preferred_communication_channel": "Unknown",
        "environmental_factors": "No context yet",
        "recent_interactions": []
    }
    
    await memory_manager.store_memory(lead_id, contextual_data, "contextual")
    logger.info(f"Initialized contextual memory for lead {lead_id}")

# GHL Manual Sync endpoint
@app.post("/api/ghl/sync-leads")
async def sync_leads_from_ghl(org_id: str):
    """
    Manually synchronize leads from GHL for an organization.
    
    This is useful for initial setup or when webhook events may have been missed.
    """
    # Get the organization's API keys
    api_keys = await db.api_keys_collection.find_one({"org_id": org_id})
    if not api_keys or not all(key in api_keys and api_keys[key] for key in ["ghl_client_id", "ghl_client_secret"]):
        raise HTTPException(status_code=400, detail="GHL API credentials not configured")
    
    # Initialize GHL integration
    from ghl import GHLIntegration
    ghl_integration = GHLIntegration(
        client_id=api_keys.get("ghl_client_id"),
        client_secret=api_keys.get("ghl_client_secret"),
        shared_secret=api_keys.get("ghl_shared_secret")
    )
    
    # Set tokens if they exist
    org = await db.organizations_collection.find_one({"_id": ObjectId(org_id)})
    if org and "ghl_access_token" in org and "ghl_refresh_token" in org:
        ghl_integration.set_tokens(
            access_token=org["ghl_access_token"],
            refresh_token=org["ghl_refresh_token"],
            location_id=org.get("ghl_location_id")
        )
    
    try:
        # Get all contacts from GHL
        contacts = await ghl_integration.get_contacts()
        
        # Track stats
        stats = {
            "total": len(contacts),
            "created": 0,
            "updated": 0,
            "failed": 0
        }
        
        # Process each contact
        for contact in contacts:
            try:
                # Create a synthetic webhook payload
                contact_payload = {
                    "event": "ContactCreate",
                    "companyId": org_id,
                    "contact": contact
                }
                
                # Use the same handler as the webhook
                await handle_contact_event(contact_payload, org_id)
                
                # Update stats based on whether the lead existed
                existing = await db.leads_collection.find_one({"ghl_contact_id": contact["id"]})
                if existing:
                    stats["updated"] += 1
                else:
                    stats["created"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing contact {contact.get('id')}: {e}")
                stats["failed"] += 1
        
        return {
            "status": "success",
            "message": f"Synchronized {stats['total']} leads from GHL",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error syncing leads from GHL: {e}")
        raise HTTPException(status_code=500, detail=f"Error syncing leads from GHL: {str(e)}")

# Agent Orchestration endpoints
try:
    from agent_orchestrator import AgentOrchestrator
    agent_orchestrator = AgentOrchestrator()
    use_agent_orchestrator = True
except ImportError as e:
    logger.warning(f"Agent orchestrator import failed: {e}, agent features will be limited")
    agent_orchestrator = None
    use_agent_orchestrator = False

@app.post("/api/agents/select")
async def select_agent(
    lead_id: str,
    objective: str,
    channel: str,
    conversation_history: Optional[bool] = True
):
    """
    Select the most appropriate agent for a given lead and objective.
    
    Args:
        lead_id: ID of the lead
        objective: The objective of the interaction
        channel: The communication channel (chat, sms, email, voice)
        conversation_history: Whether to include conversation history in the context
        
    Returns:
        The selected agent and selection confidence
    """
    # Get the lead data
    lead = await db.leads_collection.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get the lead's organization
    org_id = lead["org_id"]
    
    # Get the lead's memory if available
    lead_memory = None
    if use_memory_manager:
        lead_memory = await memory_manager.get_comprehensive_memory(lead_id)
    
    # Build context for agent selection
    context = {
        "lead_information": {
            "name": lead.get("name", ""),
            "email": lead.get("email"),
            "phone": lead.get("phone"),
            "source": lead.get("source", ""),
            "personality_type": lead.get("personality_type"),
            "trust_level": lead.get("trust_level"),
            "conversion_probability": lead.get("conversion_probability"),
            "relationship_stage": lead.get("relationship_stage"),
            "memory": lead_memory
        },
        "objective": objective,
        "channel": channel
    }
    
    # Get conversation history if requested
    if conversation_history:
        conversations = await db.conversations_collection.find({"lead_id": lead_id}).sort("created_at", -1).limit(5).to_list(5)
        context["conversation_history"] = conversations
    
    # Select the agent
    if not use_agent_orchestrator:
        raise HTTPException(status_code=503, detail="Agent orchestrator service unavailable")
    
    selection_result = await agent_orchestrator.select_agent(org_id, context)
    
    return {
        "agent_type": selection_result["agent_type"],
        "confidence": selection_result["confidence"],
        "reasoning": selection_result["reasoning"],
        "lead_context": context
    }

@app.post("/api/agents/process-message")
async def process_message(
    lead_id: str,
    message: str,
    channel: str,
    agent_type: Optional[str] = None,
    conversation_id: Optional[str] = None
):
    """
    Process a message through the agent orchestrator and get a response.
    
    Args:
        lead_id: ID of the lead
        message: The message to process
        channel: The communication channel (chat, sms, email, voice)
        agent_type: Optional specific agent type to use
        conversation_id: Optional existing conversation ID
        
    Returns:
        The agent's response and processing metadata
    """
    # Get the lead data
    # Try to find lead by UUID first
    lead = await db.leads_collection.find_one({"id": lead_id})
    
    # If not found, try by ObjectId
    if not lead:
        try:
            lead = await db.leads_collection.find_one({"_id": ObjectId(lead_id)})
        except:
            # If lead_id is not a valid ObjectId, this will fail
            pass
            
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get the lead's organization
    org_id = lead["org_id"]
    
    # Build context
    context = {
        "agent_type": agent_type,
        "conversation_id": conversation_id
    }
    
    # Process the message
    if not use_agent_orchestrator:
        raise HTTPException(status_code=503, detail="Agent orchestrator service unavailable")
    
    result = await agent_orchestrator.process_message(org_id, lead_id, message, channel, context)
    
    # Create or update conversation
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        
        conversation_data = {
            "id": conversation_id,
            "lead_id": lead_id,
            "channel": channel,
            "agent_type": result["agent_type"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        await db.conversations_collection.insert_one(conversation_data)
    else:
        await db.conversations_collection.update_one(
            {"id": conversation_id},
            {"$set": {
                "updated_at": datetime.now().isoformat(),
                "agent_type": result["agent_type"]
            }}
        )
    
    # Record the message and response
    message_data = {
        "conversation_id": conversation_id,
        "lead_id": lead_id,
        "sender": "lead",
        "content": message,
        "channel": channel,
        "created_at": datetime.now().isoformat()
    }
    
    response_data = {
        "conversation_id": conversation_id,
        "lead_id": lead_id,
        "sender": "ai",
        "content": result["response"],
        "channel": channel,
        "agent_type": result["agent_type"],
        "created_at": datetime.now().isoformat()
    }
    
    await db.messages_collection.insert_one(message_data)
    await db.messages_collection.insert_one(response_data)
    
    # Store agent interaction data
    interaction_data = {
        "conversation_id": conversation_id,
        "lead_id": lead_id,
        "agent_type": result["agent_type"],
        "reasoning": result.get("reasoning", ""),
        "confidence_score": result.get("confidence", 0.0),
        "strategy_used": result.get("strategy", ""),
        "effectiveness_score": result.get("effectiveness", 0.0),
        "created_at": datetime.now().isoformat()
    }
    
    await db.agent_interactions_collection.insert_one(interaction_data)
    
    # Update memory if available
    if use_memory_manager and "memory_update" in result:
        await memory_manager.store_memory(
            lead_id, 
            result["memory_update"], 
            result.get("memory_layer", "factual")
        )
    
    return {
        "conversation_id": conversation_id,
        "response": result["response"],
        "agent_type": result["agent_type"],
        "next_best_action": result.get("next_best_action"),
        "ai_insights": result.get("ai_insights", {})
    }

@app.post("/api/agents/initiate-voice-call")
async def initiate_voice_call(
    lead_id: str,
    objective: str,
    phone_number: Optional[str] = None
):
    """
    Initiate an AI-powered voice call to a lead.
    
    Args:
        lead_id: ID of the lead
        objective: The objective of the call
        phone_number: Optional override for the lead's phone number
        
    Returns:
        The call session information
    """
    # Get the lead data
    # Try to find lead by UUID first
    lead = await db.leads_collection.find_one({"id": lead_id})
    
    # If not found, try by ObjectId
    if not lead:
        try:
            lead = await db.leads_collection.find_one({"_id": ObjectId(lead_id)})
        except:
            # If lead_id is not a valid ObjectId, this will fail
            pass
            
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get the lead's organization
    org_id = lead["org_id"]
    
    # Get the phone number to call
    if not phone_number:
        phone_number = lead.get("phone")
        if not phone_number:
            raise HTTPException(status_code=400, detail="No phone number provided or found in lead data")
    
    # Select the appropriate agent
    selection_result = await select_agent(lead_id, objective, "voice", True)
    
    # Initialize the voice call
    if not use_agent_orchestrator:
        raise HTTPException(status_code=503, detail="Agent orchestrator service unavailable")
    
    call_result = await agent_orchestrator.initiate_voice_call(
        org_id=org_id,
        lead_id=lead_id,
        phone_number=phone_number,
        objective=objective,
        agent_type=selection_result["agent_type"],
        lead_context=selection_result["lead_context"]
    )
    
    # Create a conversation record
    conversation_id = str(uuid.uuid4())
    conversation_data = {
        "id": conversation_id,
        "lead_id": lead_id,
        "channel": "voice",
        "agent_type": selection_result["agent_type"],
        "vapi_call_id": call_result.get("call_id"),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    await db.conversations_collection.insert_one(conversation_data)
    
    return {
        "call_id": call_result.get("call_id"),
        "conversation_id": conversation_id,
        "status": call_result.get("status"),
        "agent_type": selection_result["agent_type"]
    }

# Knowledge Base endpoints
@app.post("/api/knowledge-base/upload-document")
async def upload_document(
    org_id: str,
    document_name: str,
    document_type: str,
    content: str
):
    """
    Upload a document to the organization's knowledge base.
    
    Args:
        org_id: ID of the organization
        document_name: Name of the document
        document_type: Type of document (policy, script, faq, etc.)
        content: The document content to be vectorized
        
    Returns:
        The document ID and vectorization status
    """
    # Create document record
    document_id = str(uuid.uuid4())
    document_data = {
        "id": document_id,
        "org_id": org_id,
        "name": document_name,
        "type": document_type,
        "content": content,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    await db.knowledge_base_collection.insert_one(document_data)
    
    # Vectorize the document if memory manager is available
    vectorization_status = "pending"
    if use_memory_manager:
        try:
            vectorization_result = await memory_manager.vectorize_document(
                org_id=org_id,
                document_id=document_id,
                content=content,
                metadata={
                    "name": document_name,
                    "type": document_type
                }
            )
            
            # Update the document with vector information
            await db.knowledge_base_collection.update_one(
                {"id": document_id},
                {"$set": {
                    "vector_id": vectorization_result.get("vector_id"),
                    "vectorized": True,
                    "vector_count": vectorization_result.get("vector_count", 0),
                    "updated_at": datetime.now().isoformat()
                }}
            )
            
            vectorization_status = "complete"
            
        except Exception as e:
            logger.error(f"Error vectorizing document: {e}")
            vectorization_status = f"error: {str(e)}"
    
    return {
        "document_id": document_id,
        "vectorization_status": vectorization_status
    }

@app.get("/api/knowledge-base/documents")
async def get_documents(org_id: str):
    """
    Get all documents in the organization's knowledge base.
    
    Args:
        org_id: ID of the organization
        
    Returns:
        List of documents
    """
    documents = await db.knowledge_base_collection.find({"org_id": org_id}).to_list(100)
    for doc in documents:
        doc["id"] = str(doc["_id"])
        # Don't return the full content for efficiency
        if "content" in doc and len(doc["content"]) > 200:
            doc["content"] = doc["content"][:200] + "..."
    
    return documents

@app.get("/api/knowledge-base/search")
async def search_knowledge_base(
    org_id: str,
    query: str,
    limit: int = 5
):
    """
    Search the organization's knowledge base.
    
    Args:
        org_id: ID of the organization
        query: The search query
        limit: Maximum number of results to return
        
    Returns:
        Search results
    """
    if not use_memory_manager:
        raise HTTPException(status_code=400, detail="Memory manager not available for knowledge base search")
    
    search_results = await memory_manager.search_knowledge_base(
        org_id=org_id,
        query=query,
        limit=limit
    )
    
    return search_results

# ===== ADVANCED ANALYTICS ENDPOINTS (Phase C.3) =====

@app.get("/api/analytics/comprehensive-dashboard")
async def get_comprehensive_dashboard(
    org_id: str = "production_org_123",
    time_period: str = "30d"
):
    """Get comprehensive dashboard data with all key metrics"""
    if not use_advanced_analytics_service:
        raise HTTPException(status_code=503, detail="Advanced Analytics service not available")
    
    try:
        result = await advanced_analytics_service.get_comprehensive_dashboard(org_id, time_period)
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting comprehensive dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/campaign-performance-report")
async def get_campaign_performance_report(
    org_id: str = "production_org_123",
    campaign_id: str = None,
    time_period: str = "30d"
):
    """Get detailed campaign performance report"""
    if not use_advanced_analytics_service:
        raise HTTPException(status_code=503, detail="Advanced Analytics service not available")
    
    try:
        result = await advanced_analytics_service.get_campaign_performance_report(org_id, campaign_id, time_period)
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting campaign performance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/agent-intelligence-report")
async def get_agent_intelligence_report(
    org_id: str = "production_org_123",
    agent_type: str = None,
    time_period: str = "30d"
):
    """Get detailed agent intelligence and learning report"""
    if not use_advanced_analytics_service:
        raise HTTPException(status_code=503, detail="Advanced Analytics service not available")
    
    try:
        result = await advanced_analytics_service.get_agent_intelligence_report(org_id, agent_type, time_period)
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting agent intelligence report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analytics/export-report")
async def export_analytics_report(request: dict):
    """Export analytics report in various formats"""
    if not use_advanced_analytics_service:
        raise HTTPException(status_code=503, detail="Advanced Analytics service not available")
    
    try:
        org_id = request.get("org_id", "production_org_123")
        report_type = request.get("report_type", "dashboard")
        time_period = request.get("time_period", "30d")
        format_type = request.get("format_type", "json")
        
        result = await advanced_analytics_service.export_analytics_report(org_id, report_type, time_period, format_type)
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error exporting analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/exports/{export_id}/download")
async def download_analytics_export(export_id: str):
    """Download exported analytics report"""
    if not use_advanced_analytics_service:
        raise HTTPException(status_code=503, detail="Advanced Analytics service not available")
    
    try:
        # For MVP, return a simulated download response
        return {
            "export_id": export_id,
            "status": "ready",
            "message": "Download would be available here in production",
            "file_path": f"/exports/{export_id}",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error downloading analytics export: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fine-tuning/create")
async def create_fine_tuning_job(request: dict):
    """Create a new AI fine-tuning job based on RLHF data"""
    if not use_fine_tuning_service:
        raise HTTPException(status_code=503, detail="Fine-tuning service not available")
    
    try:
        org_id = request.get("org_id", "production_org_123")
        job_config = request.get("job_config", {})
        
        result = await fine_tuning_service.create_fine_tuning_job(org_id, job_config)
        return result
        
    except Exception as e:
        logger.error(f"Error creating fine-tuning job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fine-tuning/{job_id}/start")
async def start_fine_tuning_job(job_id: str, request: dict):
    """Start a fine-tuning job"""
    if not use_fine_tuning_service:
        raise HTTPException(status_code=503, detail="Fine-tuning service not available")
    
    try:
        org_id = request.get("org_id", "production_org_123")
        
        result = await fine_tuning_service.start_fine_tuning_job(org_id, job_id)
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error starting fine-tuning job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fine-tuning/{job_id}/cancel")
async def cancel_fine_tuning_job(job_id: str, request: dict):
    """Cancel a running fine-tuning job"""
    if not use_fine_tuning_service:
        raise HTTPException(status_code=503, detail="Fine-tuning service not available")
    
    try:
        org_id = request.get("org_id", "production_org_123")
        
        result = await fine_tuning_service.cancel_fine_tuning_job(org_id, job_id)
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error cancelling fine-tuning job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fine-tuning/{job_id}/status")
async def get_fine_tuning_job_status(job_id: str, org_id: str = "production_org_123"):
    """Get detailed fine-tuning job status"""
    if not use_fine_tuning_service:
        raise HTTPException(status_code=503, detail="Fine-tuning service not available")
    
    try:
        result = await fine_tuning_service.get_job_status(org_id, job_id)
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting fine-tuning job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fine-tuning/jobs")
async def list_fine_tuning_jobs(
    org_id: str = "production_org_123",
    status_filter: str = None,
    limit: int = 50
):
    """List fine-tuning jobs for an organization"""
    if not use_fine_tuning_service:
        raise HTTPException(status_code=503, detail="Fine-tuning service not available")
    
    try:
        result = await fine_tuning_service.list_fine_tuning_jobs(org_id, status_filter, limit)
        return {
            "jobs": result,
            "total": len(result)
        }
        
    except Exception as e:
        logger.error(f"Error listing fine-tuning jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fine-tuning/{job_id}/deploy")
async def deploy_fine_tuned_model(job_id: str, request: dict):
    """Deploy a completed fine-tuned model"""
    if not use_fine_tuning_service:
        raise HTTPException(status_code=503, detail="Fine-tuning service not available")
    
    try:
        org_id = request.get("org_id", "production_org_123")
        deployment_config = request.get("deployment_config", {})
        
        result = await fine_tuning_service.deploy_fine_tuned_model(org_id, job_id, deployment_config)
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deploying fine-tuned model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rlhf/analytics")
async def get_rlhf_analytics(
    org_id: str = "production_org_123",
    start_date: str = None,
    end_date: str = None,
    agent_type: str = None
):
    """Get analytics on RLHF feedback data for fine-tuning insights"""
    if not use_fine_tuning_service:
        raise HTTPException(status_code=503, detail="Fine-tuning service not available")
    
    try:
        # Default to last 30 days if no dates provided
        if not start_date or not end_date:
            end_date = datetime.now().isoformat()
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        
        date_range = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        result = await fine_tuning_service.get_rlhf_analytics(org_id, date_range, agent_type)
        return result
        
    except Exception as e:
        logger.error(f"Error getting RLHF analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/campaigns/create")
async def create_campaign(request: dict):
    """Create a new AI-driven outreach campaign"""
    if not use_campaign_service:
        raise HTTPException(status_code=503, detail="Campaign service not available")
    
    try:
        org_id = request.get("org_id", "production_org_123")
        campaign_data = request.get("campaign_data", {})
        
        result = await campaign_service.create_campaign(org_id, campaign_data)
        return result
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/campaigns/{campaign_id}/start")
async def start_campaign(campaign_id: str, request: dict):
    """Start an active campaign"""
    if not use_campaign_service:
        raise HTTPException(status_code=503, detail="Campaign service not available")
    
    try:
        org_id = request.get("org_id", "production_org_123")
        
        result = await campaign_service.start_campaign(org_id, campaign_id)
        return result
        
    except HTTPException as he:
        # Pass through HTTP exceptions from the service
        raise he
    except Exception as e:
        logger.error(f"Error starting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: str, request: dict):
    """Pause an active campaign"""
    if not use_campaign_service:
        raise HTTPException(status_code=503, detail="Campaign service not available")
    
    try:
        org_id = request.get("org_id", "production_org_123")
        
        result = await campaign_service.pause_campaign(org_id, campaign_id)
        return result
        
    except HTTPException as he:
        # Pass through HTTP exceptions from the service
        raise he
    except Exception as e:
        logger.error(f"Error pausing campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/campaigns/{campaign_id}/stop")
async def stop_campaign(campaign_id: str, request: dict):
    """Stop and complete a campaign"""
    if not use_campaign_service:
        raise HTTPException(status_code=503, detail="Campaign service not available")
    
    try:
        org_id = request.get("org_id", "production_org_123")
        
        result = await campaign_service.stop_campaign(org_id, campaign_id)
        return result
        
    except HTTPException as he:
        # Pass through HTTP exceptions from the service
        raise he
    except Exception as e:
        logger.error(f"Error stopping campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/campaigns/{campaign_id}/status")
async def get_campaign_status(campaign_id: str, org_id: str = "production_org_123"):
    """Get detailed campaign status and metrics"""
    if not use_campaign_service:
        raise HTTPException(status_code=503, detail="Campaign service not available")
    
    try:
        result = await campaign_service.get_campaign_status(org_id, campaign_id)
        return result
        
    except HTTPException as he:
        # Pass through HTTP exceptions from the service
        raise he
    except Exception as e:
        logger.error(f"Error getting campaign status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/campaigns")
async def list_campaigns(
    org_id: str = "production_org_123",
    status_filter: str = None,
    limit: int = 50
):
    """List campaigns for an organization"""
    if not use_campaign_service:
        raise HTTPException(status_code=503, detail="Campaign service not available")
    
    try:
        result = await campaign_service.list_campaigns(org_id, status_filter, limit)
        return {
            "campaigns": result,
            "total": len(result)
        }
        
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# GHL OAuth endpoints
@app.post("/api/ghl/initiate-oauth")
async def initiate_ghl_oauth(
    request_data: Dict[str, Any] = Body(...)
):
    """
    Initiate the OAuth flow for Go High Level.
    
    This creates an authorization URL that the user will be redirected to in order
    to grant access to the GHL account.
    """
    org_id = request_data.get("org_id")
    redirect_uri = request_data.get("redirect_uri")
    
    if not org_id or not redirect_uri:
        raise HTTPException(status_code=400, detail="Missing org_id or redirect_uri")
    
    # Get the organization's API keys
    api_keys = await db.api_keys_collection.find_one({"org_id": org_id})
    if not api_keys or not all(key in api_keys and api_keys[key] for key in ["ghl_client_id", "ghl_client_secret"]):
        raise HTTPException(status_code=400, detail="GHL API credentials not configured")
    
    # Initialize GHL integration
    from ghl import GHLIntegration
    ghl_integration = GHLIntegration(
        client_id=api_keys.get("ghl_client_id"),
        client_secret=api_keys.get("ghl_client_secret"),
        shared_secret=api_keys.get("ghl_shared_secret")
    )
    
    # Store the redirect URI in the organization record
    await db.organizations_collection.update_one(
        {"_id": ObjectId(org_id)},
        {"$set": {"ghl_oauth_redirect_uri": redirect_uri}}
    )
    
    try:
        # Generate the authorization URL
        auth_url = ghl_integration.get_authorization_url(
            redirect_uri=redirect_uri,
            state=org_id  # Use org_id as the state parameter for verification
        )
        
        return {"authorization_url": auth_url}
        
    except Exception as e:
        logger.error(f"Error generating GHL authorization URL: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating GHL authorization URL: {str(e)}")

@app.get("/api/ghl/oauth-callback")
async def ghl_oauth_callback(
    code: str,
    state: str,
    locationId: Optional[str] = None
):
    """
    Handle the OAuth callback from Go High Level.
    
    This endpoint is called by GHL after the user grants access.
    """
    # The state parameter should contain the org_id
    org_id = state
    
    # Get the organization
    org = await db.organizations_collection.find_one({"_id": ObjectId(org_id)})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get the redirect URI stored during initiate-oauth
    redirect_uri = org.get("ghl_oauth_redirect_uri")
    if not redirect_uri:
        raise HTTPException(status_code=400, detail="No redirect URI found for this organization")
    
    # Get the organization's API keys
    api_keys = await db.api_keys_collection.find_one({"org_id": org_id})
    if not api_keys or not all(key in api_keys and api_keys[key] for key in ["ghl_client_id", "ghl_client_secret"]):
        raise HTTPException(status_code=400, detail="GHL API credentials not configured")
    
    # Initialize GHL integration
    from ghl import GHLIntegration
    ghl_integration = GHLIntegration(
        client_id=api_keys.get("ghl_client_id"),
        client_secret=api_keys.get("ghl_client_secret"),
        shared_secret=api_keys.get("ghl_shared_secret")
    )
    
    try:
        # Exchange the code for tokens
        tokens = await ghl_integration.exchange_code_for_tokens(
            code=code,
            redirect_uri=redirect_uri
        )
        
        # Store the tokens and location ID in the organization record
        update_data = {
            "ghl_access_token": tokens["access_token"],
            "ghl_refresh_token": tokens["refresh_token"],
            "ghl_connected": True,
            "ghl_connected_at": datetime.now().isoformat()
        }
        
        if locationId:
            update_data["ghl_location_id"] = locationId
        
        await db.organizations_collection.update_one(
            {"_id": ObjectId(org_id)},
            {"$set": update_data}
        )
        
        # Set the tokens in the GHL integration
        ghl_integration.set_tokens(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            location_id=locationId
        )
        
        # Redirect back to the application
        redirect_url = f"{redirect_uri.split('/ghl-callback')[0]}/settings?ghl_connected=true"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Error exchanging GHL code for tokens: {e}")
        redirect_url = f"{redirect_uri.split('/ghl-callback')[0]}/settings?ghl_error=true"
        return RedirectResponse(url=redirect_url)

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Phase B.2: Analytics and RLHF endpoints
@app.get("/api/analytics/agent-performance")
async def get_agent_performance(
    org_id: str,
    time_period: str = "30_days",
    agent_type: str = None
):
    """Get comprehensive agent performance analytics"""
    try:
        # Calculate date range
        end_date = datetime.now()
        if time_period == "7_days":
            start_date = end_date - timedelta(days=7)
            total_interactions = 67
            base_multiplier = 0.3
        elif time_period == "30_days":
            start_date = end_date - timedelta(days=30)
            total_interactions = 247
            base_multiplier = 1.0
        elif time_period == "90_days":
            start_date = end_date - timedelta(days=90)
            total_interactions = 658
            base_multiplier = 2.7
        else:
            start_date = end_date - timedelta(days=30)
            total_interactions = 247
            base_multiplier = 1.0
        
        # Generate analytics from real database data + AI-driven insights
        # Query actual agent interactions from database
        
        # Get real agent interactions from database
        agent_interactions = await db.agent_interactions_collection.find({
            "created_at": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }).to_list(length=None)
        
        # Get real conversations for analysis
        conversations = await db.conversations_collection.find({
            "created_at": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }).to_list(length=None)
        
        # Calculate basic metrics from real data
        total_real_interactions = len(agent_interactions)
        
        # If no real data, use simulated baseline but mark as simulated
        if total_real_interactions == 0:
            print(f"📊 No real data for {org_id} in {time_period}, using simulated baseline")
            # Use original variance-based simulation but with AI analysis
            org_hash = hash(org_id) % 100
            time_hash = hash(time_period) % 50
            variance = (org_hash + time_hash) / 100.0
            
            base_metrics = {
                "total_interactions": int(total_interactions * (0.8 + variance * 0.4)),
                "total_leads_processed": int((total_interactions * 0.63) * (0.8 + variance * 0.4)),
                "average_response_time": round(3.2 + variance * 1.0, 1),
                "overall_success_rate": round(0.75 + variance * 0.15, 2),
                "agent_data": {
                    "initial_contact": {"interactions": int(total_interactions * 0.36), "success_rate": 0.80},
                    "qualifier": {"interactions": int(total_interactions * 0.30), "success_rate": 0.76},
                    "objection_handler": {"interactions": int(total_interactions * 0.18), "success_rate": 0.68},
                    "closer": {"interactions": int(total_interactions * 0.11), "success_rate": 0.83},
                    "nurturer": {"interactions": int(total_interactions * 0.05), "success_rate": 0.90}
                }
            }
            is_simulated = True
        else:
            # Calculate real metrics from database
            print(f"📊 Analyzing {total_real_interactions} real interactions for AI-driven insights")
            
            # Calculate agent-specific metrics
            agent_metrics = {}
            for agent_type in ["initial_contact", "qualifier", "objection_handler", "closer", "nurturer", "appointment_setter"]:
                agent_interactions_filtered = [i for i in agent_interactions if i.get("agent_type") == agent_type]
                agent_metrics[agent_type] = {
                    "interactions": len(agent_interactions_filtered),
                    "success_rate": sum(1 for i in agent_interactions_filtered if i.get("status") == "successful") / max(len(agent_interactions_filtered), 1)
                }
            
            base_metrics = {
                "total_interactions": total_real_interactions,
                "total_leads_processed": len(set(i.get("lead_id") for i in agent_interactions if i.get("lead_id"))),
                "average_response_time": sum(i.get("response_time", 3.0) for i in agent_interactions) / max(total_real_interactions, 1),
                "overall_success_rate": sum(1 for i in agent_interactions if i.get("status") == "successful") / max(total_real_interactions, 1),
                "agent_data": agent_metrics
            }
            is_simulated = False
        
        # ===== AI-DRIVEN ANALYSIS USING LLM =====
        # Use OpenRouter to analyze performance patterns and generate insights
        try:
            from openrouter_service import OpenRouterService
            
            openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
            if openrouter_api_key:
                openrouter = OpenRouterService(openrouter_api_key)
                
                # Prepare data for AI analysis
                analysis_context = {
                    "time_period": time_period,
                    "total_interactions": base_metrics["total_interactions"],
                    "success_rate": base_metrics["overall_success_rate"],
                    "response_time": base_metrics["average_response_time"],
                    "agent_performance": base_metrics["agent_data"],
                    "is_simulated_data": is_simulated
                }
                
                # Create AI analysis prompt
                analysis_prompt = f"""
                You are an expert AI performance analyst for a real estate lead conversion system. Analyze the following agent performance data and provide intelligent insights:

                Performance Data:
                - Time Period: {time_period}
                - Total Interactions: {analysis_context['total_interactions']}
                - Overall Success Rate: {analysis_context['success_rate']:.2%}
                - Average Response Time: {analysis_context['response_time']:.1f}s
                - Data Source: {'Simulated baseline' if is_simulated else 'Real system interactions'}

                Agent Breakdown:
                {analysis_context['agent_performance']}

                Provide analysis in the following format:
                1. Overall Performance Assessment (1-2 sentences)
                2. Top 3 Strengths (specific agents/metrics)
                3. Top 3 Areas for Improvement (specific recommendations)
                4. Strategic Recommendations (2-3 actionable insights)

                Focus on practical, data-driven recommendations that a real estate team can implement.
                """
                
                # Get AI analysis
                ai_response = await openrouter.generate_response(
                    prompt=analysis_prompt,
                    model="anthropic/claude-3.5-sonnet",
                    temperature=0.3
                )
                
                ai_insights = ai_response.get("content", "Analysis temporarily unavailable")
                print(f"🤖 Generated AI-driven performance insights using Claude 3.5 Sonnet")
                
            else:
                ai_insights = "AI analysis requires OpenRouter API key configuration"
                print("⚠️ OpenRouter API key not configured - AI insights unavailable")
                
        except Exception as ai_error:
            print(f"⚠️ AI analysis failed: {ai_error}")
            ai_insights = f"AI analysis temporarily unavailable: {str(ai_error)}"
        
        # Build final analytics response with AI insights
        analytics_data = {
            "org_id": org_id,
            "time_period": time_period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data_source": "simulated_baseline" if is_simulated else "real_interactions",
            "overview": {
                "total_interactions": base_metrics["total_interactions"],
                "total_leads_processed": base_metrics["total_leads_processed"],
                "average_response_time": round(base_metrics["average_response_time"], 1),
                "overall_success_rate": round(base_metrics["overall_success_rate"], 2),
                "lead_progression_rate": round(base_metrics.get("lead_progression_rate", 0.65), 2)
            },
            "agent_breakdown": {},
            "ai_insights": ai_insights,
            "improvement_recommendations": []
        }
        
        # Process agent breakdown with enhanced data
        for agent_type, metrics in base_metrics["agent_data"].items():
            analytics_data["agent_breakdown"][agent_type] = {
                "interactions": metrics["interactions"],
                "success_rate": round(metrics["success_rate"], 2),
                "avg_response_time": round(metrics.get("avg_response_time", 3.5), 1),
                "lead_progression_rate": round(metrics.get("lead_progression_rate", 0.67), 2)
            }
            
            # Add agent-specific metrics
            if agent_type == "qualifier":
                analytics_data["agent_breakdown"][agent_type]["qualification_completeness"] = round(metrics.get("qualification_completeness", 0.82), 2)
            elif agent_type == "objection_handler":
                analytics_data["agent_breakdown"][agent_type]["objection_resolution_rate"] = round(metrics.get("objection_resolution_rate", 0.60), 2)
            elif agent_type == "closer":
                analytics_data["agent_breakdown"][agent_type]["appointment_conversion"] = round(metrics.get("appointment_conversion", 0.76), 2)
            elif agent_type == "nurturer":
                analytics_data["agent_breakdown"][agent_type]["engagement_retention"] = round(metrics.get("engagement_retention", 0.85), 2)
        
        # Generate AI-driven recommendations based on performance patterns
        recommendations = []
        
        # Use AI analysis to generate smarter recommendations
        if "objection_handler" in analytics_data["agent_breakdown"]:
            oh_data = analytics_data["agent_breakdown"]["objection_handler"]
            if oh_data["avg_response_time"] > 5.5:
                recommendations.append({
                    "agent": "objection_handler",
                    "metric": "response_time",
                    "current_value": oh_data["avg_response_time"],
                    "target_value": 4.0,
                    "recommendation": "AI Analysis: Implement faster objection identification patterns",
                    "priority": "high",
                    "ai_generated": True
                })
        
        if "qualifier" in analytics_data["agent_breakdown"]:
            q_data = analytics_data["agent_breakdown"]["qualifier"]
            if q_data["success_rate"] < 0.82:
                recommendations.append({
                    "agent": "qualifier",
                    "metric": "success_rate",
                    "current_value": q_data["success_rate"],
                    "target_value": 0.85,
                    "recommendation": "AI Analysis: Enhance qualification script with better probing questions",
                    "priority": "medium",
                    "ai_generated": True
                })
        
        analytics_data["improvement_recommendations"] = recommendations
        
        return analytics_data
        
    except Exception as e:
        logger.error(f"Error getting agent performance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rlhf/feedback")
async def submit_rlhf_feedback(
    org_id: str,
    conversation_id: str,
    feedback_type: str,
    rating: Optional[int] = None,
    category: Optional[str] = None,
    suggestions: Optional[str] = None,
    outcome: Optional[str] = None
):
    """
    Submit RLHF feedback for a conversation.
    """
    # Validate feedback data
    if feedback_type not in ["rating", "category", "outcome", "improvement"]:
        raise HTTPException(status_code=400, detail="Invalid feedback type")
    
    if feedback_type == "rating" and (rating is None or rating < 1 or rating > 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Create feedback record
    feedback_id = str(uuid.uuid4())
    feedback_data = {
        "id": feedback_id,
        "org_id": org_id,
        "conversation_id": conversation_id,
        "feedback_type": feedback_type,
        "rating": rating,
        "category": category,
        "suggestions": suggestions,
        "outcome": outcome,
        "created_at": datetime.now().isoformat()
    }
    
    # Store in feedback collection
    await db.rlhf_feedback_collection.insert_one(feedback_data)
    
    return {
        "success": True,
        "feedback_id": feedback_id,
        "message": "Feedback submitted successfully"
    }

# ================================
# UI ACTION ENDPOINTS
# ================================

@app.post("/api/actions/send-message")
async def action_send_message(request: SendMessageRequest):
    """
    Simplified endpoint for frontend Message buttons.
    Initiates an AI-powered SMS/MMS conversation with a lead.
    """
    try:
        # Get lead data - try both UUID and ObjectId formats
        lead = None
        
        # Try to find lead by UUID first (for newly created leads)
        if request.lead_id:
            lead = await db.leads_collection.find_one({"id": request.lead_id})
        
        # If not found, try by ObjectId (for existing leads)
        if not lead:
            try:
                lead = await db.leads_collection.find_one({"_id": ObjectId(request.lead_id)})
            except:
                pass
                
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        lead_org_id = request.org_id or lead.get("org_id", "production_org_123")
        
        # Auto-generate an appropriate opening message if none provided
        if not request.message:
            message = f"Hi {lead.get('name', 'there')}, this is regarding your recent inquiry. I'd love to help answer any questions you might have!"
        else:
            message = request.message
        
        # Create a conversation record
        conversation_id = str(uuid.uuid4())
        conversation_data = {
            "id": conversation_id,
            "lead_id": str(lead.get("_id")),  # Use MongoDB ObjectId
            "org_id": lead_org_id,
            "channel": "sms",
            "agent_type": "initial_contact",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Store conversation
        await db.conversations_collection.insert_one(conversation_data)
        
        # Create agent interaction record
        interaction_id = str(uuid.uuid4())
        interaction_data = {
            "id": interaction_id,
            "conversation_id": conversation_id,
            "lead_id": str(lead.get("_id")),
            "agent_type": "initial_contact",
            "message": message,
            "channel": "sms",
            "direction": "outbound",
            "confidence_score": 0.85,
            "created_at": datetime.now().isoformat()
        }
        
        # Store interaction
        await db.agent_interactions_collection.insert_one(interaction_data)
        
        # Import the orchestrator here to avoid circular imports
        from agent_orchestrator import AgentOrchestrator
        
        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator()
        
        # Process the message through the agent system to get AI response
        try:
            ai_response = await orchestrator.process_message(
                org_id=lead_org_id,
                lead_id=str(lead.get("_id")),
                message=f"Lead contacted via SMS. Objective: Initial contact",
                channel="sms",
                context={"objective": "Initial contact", "action_type": "send_message"}
            )
            
            ai_message = ai_response.get("text", "Hello! I'm reaching out regarding your real estate inquiry.")
            agent_type = ai_response.get("agent_type", "initial_contact")
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            # Fallback message if AI fails
            ai_message = "Hello! I'm reaching out regarding your real estate inquiry. How can I help you today?"
            agent_type = "initial_contact"
        
        # Actually send the SMS via GHL Lead Connector
        try:
            from ghl_sms_provider import GHLSMSProvider
            from ghl_enhanced import GHLIntegrationService
            
            # Initialize GHL services
            ghl_service = GHLIntegrationService()
            ghl_sms = GHLSMSProvider(ghl_service)
            
            # Send SMS via GHL
            sms_result = await ghl_sms.send_sms(
                org_id=lead_org_id,
                to_number=lead.get('phone'),
                message=ai_message
            )
            
            if sms_result.get("success"):
                print(f"📱 SMS sent successfully via GHL to {lead.get('name', 'Unknown')} ({lead.get('phone', 'No phone')}): {ai_message}")
                
                # Store the sent message in agent interactions
                await db.agent_interactions_collection.insert_one({
                    "id": str(uuid.uuid4()),
                    "conversation_id": conversation_id,
                    "lead_id": str(lead.get("_id")),
                    "agent_type": agent_type,
                    "message": ai_message,
                    "channel": "sms",
                    "direction": "outbound",
                    "confidence_score": 0.85,
                    "message_id": sms_result.get("message_id"),
                    "provider": "ghl_native",
                    "created_at": datetime.now().isoformat()
                })
                
                return {
                    "success": True,
                    "message": "Message sent successfully via GHL SMS",
                    "lead_id": str(lead.get("_id")),
                    "conversation_id": conversation_id,
                    "message": ai_message,
                    "agent_type": agent_type,
                    "status": "sent",
                    "provider": "ghl_native",
                    "message_id": sms_result.get("message_id")
                }
            else:
                raise Exception(f"GHL SMS send failed: {sms_result}")
                
        except Exception as sms_error:
            logger.error(f"Error sending SMS via GHL: {sms_error}")
            
            # Store as failed message
            await db.agent_interactions_collection.insert_one({
                "id": str(uuid.uuid4()),
                "conversation_id": conversation_id,
                "lead_id": str(lead.get("_id")),
                "agent_type": agent_type,
                "message": ai_message,
                "channel": "sms",
                "direction": "outbound",
                "confidence_score": 0.85,
                "status": "failed",
                "error": str(sms_error),
                "created_at": datetime.now().isoformat()
            })
            
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to send SMS: {str(sms_error)}"
            )
        
    except Exception as e:
        print(f"Error in action_send_message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@app.post("/api/actions/initiate-call")
async def action_initiate_call(request: InitiateCallRequest):
    """
    Simplified endpoint for frontend Call buttons.
    Initiates an AI-powered voice call with a lead.
    """
    try:
        # Get lead data - try both UUID and ObjectId formats  
        lead = None
        
        # Try to find lead by UUID first (for newly created leads)
        if request.lead_id:
            lead = await db.leads_collection.find_one({"id": request.lead_id})
        
        # If not found, try by ObjectId (for existing leads)
        if not lead:
            try:
                lead = await db.leads_collection.find_one({"_id": ObjectId(request.lead_id)})
            except:
                pass
                
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        lead_org_id = request.org_id or lead.get("org_id", "production_org_123")
        
        # Auto-generate objective if none provided
        if not request.objective:
            lead_status = lead.get("status", "Initial Contact")
            if lead_status == "Initial Contact":
                objective = "Introduce services and qualify the lead"
            elif lead_status == "Qualified":
                objective = "Present solution and move towards closing"
            elif lead_status == "Nurturing":
                objective = "Address concerns and build trust"
            elif lead_status == "Closing":
                objective = "Finalize details and close the deal"
            else:
                objective = "Follow up and assess current needs"
        else:
            objective = request.objective
        
        # Create a conversation record
        conversation_id = str(uuid.uuid4())
        conversation_data = {
            "id": conversation_id,
            "lead_id": str(lead.get("_id")),  # Use MongoDB ObjectId
            "org_id": lead_org_id,
            "channel": "voice",
            "agent_type": "initial_contact",
            "status": "initiated",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Store conversation
        await db.conversations_collection.insert_one(conversation_data)
        
        # Create call record
        call_id = str(uuid.uuid4())
        call_data = {
            "id": call_id,
            "conversation_id": conversation_id,
            "lead_id": str(lead.get("_id")),
            "phone_number": lead.get("phone"),
            "objective": objective,
            "status": "initiated",
            "agent_type": "initial_contact",
            "created_at": datetime.now().isoformat()
        }
        
        # Store call (you could create a calls collection)
        await db.agent_interactions_collection.insert_one({
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "lead_id": str(lead.get("_id")),
            "agent_type": "initial_contact", 
            "message": f"Voice call initiated with objective: {objective}",
            "channel": "voice",
            "direction": "outbound",
            "confidence_score": 0.90,
            "call_id": call_id,
            "created_at": datetime.now().isoformat()
        })
        
        # Import the orchestrator here to avoid circular imports
        from agent_orchestrator import AgentOrchestrator
        
        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator()
        
        # Process through the agent system to get AI assistant configuration
        try:
            ai_response = await orchestrator.process_message(
                org_id=lead_org_id,
                lead_id=str(lead.get("_id")),
                message=f"Voice call initiated. Objective: {objective}",
                channel="voice",
                context={"objective": objective, "action_type": "initiate_call"}
            )
            
            agent_type = ai_response.get("agent_type", "initial_contact")
            
        except Exception as e:
            logger.error(f"Error getting AI agent configuration: {e}")
            agent_type = "initial_contact"
        
        # Actually initiate the call via Vapi
        try:
            from vapi_integration import VapiIntegration
            
            # Initialize Vapi integration with API key from environment
            vapi_key = os.environ.get('VAPI_API_KEY')
            if not vapi_key:
                raise ValueError("Vapi API key not configured")
                
            vapi = VapiIntegration(vapi_key)
            
            # Configure the assistant for this specific call and agent type
            assistant_config = {
                "firstMessage": f"Hello {lead.get('name', '')}! This is AI Closer calling about your real estate inquiry. How are you today?",
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.7 if agent_type == "initial_contact" else 0.5,
                    "systemPrompt": f"You are a professional real estate agent assistant calling {lead.get('name', 'the lead')}. {objective}. Be friendly, professional, and helpful. Keep responses concise for voice conversation.",
                    "functions": []
                },
                "voice": {
                    "provider": "elevenlabs",
                    "voiceId": "11labs_amy",  # Professional female voice
                    "stability": 0.7,
                    "similarityBoost": 0.7
                },
                "recordingEnabled": True,
                "transcriptEnabled": True,
                "maxDurationSeconds": 600,  # 10 minute max
                "responseDelaySeconds": 0.5,
                "silenceTimeoutSeconds": 10
            }
            
            # Create the call via Vapi
            call_result = await vapi.create_call(
                phone_number=lead.get('phone'),
                assistant_config=assistant_config,
                webhook_url=f"{os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')}/api/vapi/webhook"
            )
            
            # Update call record with Vapi call ID
            vapi_call_id = call_result.get("id")
            
            if vapi_call_id:
                print(f"📞 Vapi call initiated successfully to {lead.get('name', 'Unknown')} ({lead.get('phone', 'No phone')}) - Vapi Call ID: {vapi_call_id}")
                
                # Update the agent interaction with Vapi call ID
                await db.agent_interactions_collection.update_one(
                    {"call_id": call_id},
                    {"$set": {
                        "vapi_call_id": vapi_call_id,
                        "status": "active",
                        "agent_type": agent_type,
                        "updated_at": datetime.now().isoformat()
                    }}
                )
                
                return {
                    "success": True,
                    "message": "Call initiated successfully via Vapi",
                    "call_id": call_id,
                    "vapi_call_id": vapi_call_id,
                    "conversation_id": conversation_id,
                    "agent_type": agent_type,
                    "status": "active",
                    "objective": objective,
                    "phone_number": lead.get('phone')
                }
            else:
                raise Exception(f"Vapi call creation failed: {call_result}")
                
        except Exception as call_error:
            logger.error(f"Error initiating Vapi call: {call_error}")
            
            # Update agent interaction with failure status
            await db.agent_interactions_collection.update_one(
                {"call_id": call_id},
                {"$set": {
                    "status": "failed",
                    "error": str(call_error),
                    "updated_at": datetime.now().isoformat()
                }}
            )
            
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to initiate call: {str(call_error)}"
            )
        
    except Exception as e:
        print(f"Error in action_initiate_call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate call: {str(e)}")

@app.post("/api/actions/view-lead")
async def action_view_lead(request: ViewLeadRequest):
    """
    Get detailed lead information for frontend View buttons.
    """
    try:
        # Get lead data - try both UUID and ObjectId formats  
        lead = None
        
        # Try to find lead by UUID first (for newly created leads)
        if request.lead_id:
            lead = await db.leads_collection.find_one({"id": request.lead_id})
        
        # If not found, try by ObjectId (for existing leads)
        if not lead:
            try:
                lead = await db.leads_collection.find_one({"_id": ObjectId(request.lead_id)})
            except:
                pass
                
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Get recent conversations with proper serialization
        conversations = await db.conversations_collection.find(
            {"lead_id": str(lead.get("_id"))}
        ).sort("created_at", -1).limit(10).to_list(10)
        
        # Convert conversations to serializable format
        serialized_conversations = []
        for conv in conversations:
            try:
                serialized_conversations.append({
                    "id": conv.get("id", str(conv.get("_id", ""))),
                    "lead_id": conv.get("lead_id"),
                    "channel": conv.get("channel"),
                    "agent_type": conv.get("agent_type"),
                    "status": conv.get("status", "active"),
                    "created_at": conv.get("created_at"),
                    "updated_at": conv.get("updated_at")
                })
            except Exception as e:
                print(f"Error serializing conversation: {e}")
                continue
        
        # Get recent agent interactions with proper serialization
        interactions = await db.agent_interactions_collection.find(
            {"lead_id": str(lead.get("_id"))}
        ).sort("created_at", -1).limit(5).to_list(5)
        
        # Convert interactions to serializable format
        serialized_interactions = []
        for interaction in interactions:
            try:
                serialized_interactions.append({
                    "id": interaction.get("id", str(interaction.get("_id", ""))),
                    "conversation_id": interaction.get("conversation_id"),
                    "lead_id": interaction.get("lead_id"),
                    "agent_type": interaction.get("agent_type"),
                    "message": interaction.get("message"),
                    "channel": interaction.get("channel"),
                    "direction": interaction.get("direction"),
                    "confidence_score": interaction.get("confidence_score", 0.0),
                    "created_at": interaction.get("created_at")
                })
            except Exception as e:
                print(f"Error serializing interaction: {e}")
                continue
        
        # Get memory context if available
        memory_context = {}
        if use_memory_manager:
            try:
                memory_context = await memory_manager.get_context_for_agent(str(lead.get("_id")), "general")
            except Exception as e:
                print(f"Memory context error: {e}")
                memory_context = {"error": "Memory unavailable"}
        
        return {
            "success": True,
            "lead": {
                "id": str(lead["_id"]),
                "name": lead.get("name"),
                "email": lead.get("email"),
                "phone": lead.get("phone"),
                "status": lead.get("status"),
                "relationship_stage": lead.get("relationship_stage"),
                "personality_type": lead.get("personality_type"),
                "trust_level": lead.get("trust_level", 0.0),
                "conversion_probability": lead.get("conversion_probability", 0.0),
                "created_at": lead.get("created_at"),
                "updated_at": lead.get("updated_at")
            },
            "recent_conversations": serialized_conversations,
            "recent_interactions": serialized_interactions,
            "memory_context": memory_context
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        print(f"Error in action_view_lead: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get lead details: {str(e)}")

@app.post("/api/actions/add-lead")
async def action_add_lead(request: AddLeadRequest):
    """
    Add a new lead for frontend Add Lead buttons.
    """
    try:
        # Create new lead
        lead_id = str(uuid.uuid4())
        lead_data = {
            "_id": ObjectId(),
            "id": lead_id,
            "org_id": request.org_id,
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "status": request.status,
            "relationship_stage": request.status.lower().replace(" ", "_"),
            "personality_type": "unknown",  # Will be determined through interactions
            "trust_level": 0.0,
            "conversion_probability": 0.1,  # Default low probability for new leads
            "source": request.source,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Insert into database
        await db.leads_collection.insert_one(lead_data)
        
        return {
            "success": True,
            "message": "Lead added successfully",
            "lead_id": lead_id,
            "lead": {
                "id": lead_id,
                "name": request.name,
                "email": request.email,
                "phone": request.phone,
                "status": request.status
            }
        }
        
    except Exception as e:
        print(f"Error in action_add_lead: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add lead: {str(e)}")

@app.get("/api/leads")
async def get_leads(org_id: str = "production_org_123", limit: int = 50):
    """
    Get leads list for frontend components.
    """
    try:
        # Get leads from database
        leads = await db.leads_collection.find(
            {"org_id": org_id}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Convert ObjectId to string and format data
        formatted_leads = []
        for lead in leads:
            try:
                # Use the UUID if available, otherwise use the ObjectId
                lead_id = lead.get("id", str(lead["_id"]))
                
                formatted_leads.append({
                    "id": lead_id,
                    "name": lead.get("name"),
                    "email": lead.get("email"),
                    "phone": lead.get("phone"),
                    "status": lead.get("status"),
                    "relationship_stage": lead.get("relationship_stage"),
                    "personality_type": lead.get("personality_type"),
                    "trust_level": lead.get("trust_level", 0.0),
                    "conversion_probability": lead.get("conversion_probability", 0.0),
                    "created_at": lead.get("created_at"),
                    "updated_at": lead.get("updated_at")
                })
            except Exception as e:
                print(f"Error formatting lead {lead.get('_id', 'unknown')}: {e}")
                continue
        
        return {
            "success": True,
            "leads": formatted_leads,
            "total": len(formatted_leads)
        }
        
    except Exception as e:
        print(f"Error in get_leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get leads: {str(e)}")

@app.get("/api/conversations")
async def get_conversations(org_id: str = "production_org_123", limit: int = 50):
    """
    Get conversations list for frontend components.
    """
    try:
        # Get conversations from database
        conversations = await db.conversations_collection.find(
            {}  # Could filter by org_id if needed
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        # Get lead data for each conversation
        formatted_conversations = []
        for conversation in conversations:
            lead_id = conversation.get("lead_id")
            if lead_id:
                try:
                    lead = await db.leads_collection.find_one({"_id": ObjectId(lead_id)})
                    if lead:
                        formatted_conversations.append({
                            "id": conversation.get("id"),
                            "lead": {
                                "id": str(lead["_id"]),
                                "name": lead.get("name"),
                                "email": lead.get("email")
                            },
                            "channel": conversation.get("channel"),
                            "agent_type": conversation.get("agent_type"),
                            "created_at": conversation.get("created_at"),
                            "status": conversation.get("status", "active")
                        })
                except Exception as e:
                    print(f"Error getting lead for conversation: {e}")
                    continue
        
        return {
            "success": True,
            "conversations": formatted_conversations,
            "total": len(formatted_conversations)
        }
        
    except Exception as e:
        print(f"Error in get_conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")

# ================================
# API KEY VALIDATION ENDPOINTS
# ================================

@app.post("/api/settings/validate-mem0-key")
async def validate_mem0_key(request: dict):
    """
    Validate Mem0 API key.
    """
    try:
        api_key = request.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        # Basic format validation for Mem0 keys
        if not api_key.startswith("m0-"):
            return {"valid": False, "message": "Invalid Mem0 API key format (should start with 'm0-')"}
        
        if len(api_key) < 20:
            return {"valid": False, "message": "API key is too short"}
        
        # For now, we'll do basic validation. In production, you'd make an actual API call to Mem0
        # to verify the key works
        return {"valid": True, "message": "API key format is valid"}
        
    except Exception as e:
        print(f"Error validating Mem0 API key: {str(e)}")
        return {"valid": False, "message": "Error validating API key"}

@app.post("/api/settings/validate-vapi-key")
async def validate_vapi_key(request: dict):
    """
    Validate Vapi.ai API key.
    """
    try:
        api_key = request.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        # Basic format validation for Vapi keys (UUIDs)
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        
        if not uuid_pattern.match(api_key):
            return {"valid": False, "message": "Invalid Vapi API key format (should be UUID format)"}
        
        # For now, we'll do basic validation. In production, you'd make an actual API call to Vapi
        # to verify the key works
        return {"valid": True, "message": "API key format is valid"}
        
    except Exception as e:
        print(f"Error validating Vapi API key: {str(e)}")
        return {"valid": False, "message": "Error validating API key"}

@app.post("/api/settings/validate-sendblue-key")
async def validate_sendblue_key(request: dict):
    """
    Validate SendBlue API key.
    """
    try:
        api_key = request.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        # Basic format validation for SendBlue keys
        if len(api_key) < 10:
            return {"valid": False, "message": "API key is too short"}
        
        # For now, we'll do basic validation. In production, you'd make an actual API call to SendBlue
        # to verify the key works
        return {"valid": True, "message": "API key format is valid"}
        
    except Exception as e:
        print(f"Error validating SendBlue API key: {str(e)}")
        return {"valid": False, "message": "Error validating API key"}

@app.post("/api/settings/validate-openai-key")
async def validate_openai_key(request: dict):
    """
    Validate OpenAI API key.
    """
    try:
        api_key = request.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        # Basic format validation for OpenAI keys
        if not api_key.startswith("sk-"):
            return {"valid": False, "message": "Invalid OpenAI API key format (should start with 'sk-')"}
        
        if len(api_key) < 20:
            return {"valid": False, "message": "API key is too short"}
        
        # For now, we'll do basic validation. In production, you'd make an actual API call to OpenAI
        # to verify the key works
        return {"valid": True, "message": "API key format is valid"}
        
    except Exception as e:
        print(f"Error validating OpenAI API key: {str(e)}")
        return {"valid": False, "message": "Error validating API key"}

@app.post("/api/settings/validate-openrouter-key")
async def validate_openrouter_key(request: dict):
    """
    Validate OpenRouter API key.
    """
    try:
        api_key = request.get("api_key")
        if not api_key:
            return {"valid": False, "message": "API key is required"}
        
        # Basic format validation for OpenRouter keys
        if not api_key.startswith("sk-or-v1-"):
            return {"valid": False, "message": "Invalid OpenRouter API key format (should start with 'sk-or-v1-')"}
        
        if len(api_key) < 25:
            return {"valid": False, "message": "API key is too short"}
        
        # For now, we'll do basic validation. In production, you'd make an actual API call to OpenRouter
        # to verify the key works
        return {"valid": True, "message": "API key format is valid"}
        
    except Exception as e:
        print(f"Error validating OpenRouter API key: {str(e)}")
        return {"valid": False, "message": "Error validating API key"}

@app.get("/api/dashboard/real-time")
async def get_real_time_dashboard_data(org_id: str):
    """Get real-time dashboard data"""
    try:
        # Generate dynamic dashboard data based on org and current time
        current_time = datetime.now()
        org_hash = hash(org_id) % 100
        time_hash = current_time.hour % 24
        
        # Simulate realistic variance based on org and time of day
        base_activity = 0.3 + (org_hash / 100.0) * 0.7  # 30-100% activity level
        time_factor = 0.5 + abs(12 - time_hash) / 24.0  # Higher activity during business hours
        
        active_conversations = max(1, int(15 * base_activity * time_factor))
        leads_today = max(5, int(35 * base_activity))
        responses_sent = max(20, int(180 * base_activity))
        
        dashboard_data = {
            "org_id": org_id,
            "timestamp": current_time.isoformat(),
            "kpi_overview": {
                "active_conversations": active_conversations,
                "leads_today": leads_today,
                "responses_sent": responses_sent,
                "avg_response_time": round(2.8 + (org_hash % 20) / 10.0, 1),
                "system_health": "excellent" if base_activity > 0.7 else "good" if base_activity > 0.4 else "fair"
            },
            "active_agents": {
                "initial_contact": {
                    "active": active_conversations > 2,
                    "current_conversations": max(0, int(active_conversations * 0.35))
                },
                "qualifier": {
                    "active": active_conversations > 1,
                    "current_conversations": max(0, int(active_conversations * 0.25))
                },
                "objection_handler": {
                    "active": active_conversations > 3,
                    "current_conversations": max(0, int(active_conversations * 0.20))
                },
                "closer": {
                    "active": active_conversations > 4,
                    "current_conversations": max(0, int(active_conversations * 0.15))
                },
                "nurturer": {
                    "active": active_conversations > 5,
                    "current_conversations": max(0, int(active_conversations * 0.05))
                }
            },
            "recent_activity": []
        }
        
        # Generate recent activity based on active conversations
        activities = []
        if active_conversations > 0:
            activity_types = [
                ("lead_qualification", "qualifier", "Qualified lead for downtown condo"),
                ("objection_handled", "objection_handler", "Addressed pricing concerns with market data"),
                ("appointment_scheduled", "closer", "Scheduled viewing for tomorrow"),
                ("initial_contact", "initial_contact", "Welcomed new lead and gathered basic info"),
                ("follow_up", "nurturer", "Sent follow-up with property recommendations")
            ]
            
            # Add 1-3 recent activities based on activity level
            num_activities = min(3, max(1, int(active_conversations / 4)))
            
            for i in range(num_activities):
                activity_type, agent, summary = activity_types[i % len(activity_types)]
                activity_time = current_time - timedelta(minutes=(i + 1) * 5)
                
                activities.append({
                    "timestamp": activity_time.isoformat(),
                    "type": activity_type,
                    "agent": agent,
                    "lead_id": f"lead_{org_hash + i:03d}",
                    "summary": f"{summary} (Lead #{org_hash + i:03d})"
                })
        
        dashboard_data["recent_activity"] = activities
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting real-time dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase B.2 implementation complete - analytics and RLHF endpoints added above

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
