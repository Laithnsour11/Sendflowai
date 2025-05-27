from fastapi import FastAPI, HTTPException, Depends, Query, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Any, Optional
import logging
import os
import json
import time
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import asyncio

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

# Import GHL integration
import sys
sys.path.append('/app')
from ghl import GHLIntegration

# Initialize GHL integration
ghl_integration = GHLIntegration(
    client_id=os.environ.get('GHL_CLIENT_ID', '681a8d486b267326cb42a4db-mb5qftwj'),
    client_secret=os.environ.get('GHL_CLIENT_SECRET', '12395acc-c70b-4aee-b86f-abb4c7da3b62'),
    shared_secret=os.environ.get('GHL_SHARED_SECRET', '6a705549-ecb6-48cf-b5e4-8fe59b3bafa9')
)

# Set access token if available (for testing purposes)
if os.environ.get('GHL_ACCESS_TOKEN') and os.environ.get('GHL_REFRESH_TOKEN'):
    ghl_integration.set_tokens(
        access_token=os.environ.get('GHL_ACCESS_TOKEN'),
        refresh_token=os.environ.get('GHL_REFRESH_TOKEN')
    )

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

# GHL Integration endpoints
@app.get("/api/ghl/contacts")
async def get_ghl_contacts(page: int = 1, limit: int = 100):
    """Get contacts from GHL with pagination"""
    query_params = {
        "page": page,
        "limit": limit
    }
    
    contacts = await ghl_integration.get_contacts(query_params=query_params)
    return {"contacts": contacts}

@app.get("/api/ghl/contacts/{contact_id}")
async def get_ghl_contact(contact_id: str):
    """Get a specific contact from GHL"""
    contact = await ghl_integration.get_contact(contact_id)
    return {"contact": contact}

@app.post("/api/ghl/contacts")
async def create_ghl_contact(contact_data: Dict[str, Any]):
    """Create a new contact in GHL"""
    contact = await ghl_integration.create_contact(contact_data)
    return {"contact": contact}

@app.put("/api/ghl/contacts/{contact_id}")
async def update_ghl_contact(contact_id: str, contact_data: Dict[str, Any]):
    """Update a contact in GHL"""
    contact = await ghl_integration.update_contact(contact_id, contact_data)
    return {"contact": contact}

@app.get("/api/ghl/contacts/{contact_id}/notes")
async def get_ghl_contact_notes(contact_id: str, limit: int = 50):
    """Get notes for a specific contact"""
    notes = await ghl_integration.get_contact_notes(contact_id, limit=limit)
    return {"notes": notes}

@app.post("/api/ghl/contacts/{contact_id}/notes")
async def add_ghl_contact_note(contact_id: str, note: str = Body(...), user_id: Optional[str] = None):
    """Add a note to a contact"""
    result = await ghl_integration.add_note_to_contact(contact_id, note, user_id)
    return result

@app.get("/api/ghl/custom-fields")
async def get_ghl_custom_fields():
    """Get custom fields from GHL"""
    custom_fields = await ghl_integration.get_custom_fields()
    return {"custom_fields": custom_fields}

@app.post("/api/ghl/custom-fields")
async def create_ghl_custom_field(field_data: Dict[str, Any]):
    """Create a custom field in GHL"""
    custom_field = await ghl_integration.create_custom_field(field_data)
    return {"custom_field": custom_field}

@app.get("/api/ghl/pipelines")
async def get_ghl_pipelines():
    """Get all pipelines"""
    pipelines = await ghl_integration.get_pipelines()
    return {"pipelines": pipelines}

@app.get("/api/ghl/opportunities")
async def get_ghl_opportunities(contact_id: Optional[str] = None):
    """Get opportunities, optionally filtered by contact ID"""
    opportunities = await ghl_integration.get_opportunities(contact_id=contact_id)
    return {"opportunities": opportunities}

@app.post("/api/ghl/opportunities")
async def create_ghl_opportunity(opportunity_data: Dict[str, Any]):
    """Create a new opportunity"""
    opportunity = await ghl_integration.create_opportunity(opportunity_data)
    return {"opportunity": opportunity}

@app.put("/api/ghl/opportunities/{opportunity_id}")
async def update_ghl_opportunity(opportunity_id: str, opportunity_data: Dict[str, Any]):
    """Update an opportunity"""
    opportunity = await ghl_integration.update_opportunity(opportunity_id, opportunity_data)
    return {"opportunity": opportunity}

@app.put("/api/ghl/opportunities/{opportunity_id}/stage/{stage_id}")
async def move_ghl_opportunity_stage(opportunity_id: str, stage_id: str):
    """Move an opportunity to a different stage"""
    opportunity = await ghl_integration.move_opportunity_stage(opportunity_id, stage_id)
    return {"opportunity": opportunity}

@app.get("/api/ghl/tasks")
async def get_ghl_tasks(contact_id: Optional[str] = None):
    """Get tasks, optionally filtered by contact ID"""
    tasks = await ghl_integration.get_tasks(contact_id=contact_id)
    return {"tasks": tasks}

@app.post("/api/ghl/tasks")
async def create_ghl_task(task_data: Dict[str, Any]):
    """Create a new task"""
    task = await ghl_integration.create_task(task_data)
    return {"task": task}

@app.post("/api/ghl/contacts/{contact_id}/follow-up")
async def create_ghl_follow_up_task(contact_id: str, task_data: Dict[str, Any]):
    """Create a follow-up task for a human agent"""
    task = await ghl_integration.create_follow_up_task(contact_id, task_data)
    return {"task": task}

@app.get("/api/ghl/contacts/{contact_id}/comprehensive")
async def get_ghl_comprehensive_lead_data(contact_id: str):
    """Get comprehensive data about a lead"""
    data = await ghl_integration.get_comprehensive_lead_data(contact_id)
    return data

@app.post("/api/ghl/contacts/{contact_id}/ai-insights")
async def update_ghl_ai_insights(contact_id: str, ai_insights: Dict[str, Any]):
    """Update AI-specific insights in GHL custom fields"""
    result = await ghl_integration.update_ai_insights(contact_id, ai_insights)
    return result

@app.post("/api/ghl/contacts/{contact_id}/ai-interaction")
async def add_ghl_ai_interaction_note(contact_id: str, interaction_data: Dict[str, Any]):
    """Add a structured note about an AI interaction"""
    result = await ghl_integration.add_ai_interaction_note(contact_id, interaction_data)
    return result

# Testing endpoints
@app.post("/api/ghl/set-token")
async def set_ghl_token(access_token: str, refresh_token: str):
    """Set GHL access token for testing purposes"""
    ghl_integration.set_tokens(access_token=access_token, refresh_token=refresh_token)
    return {"status": "success", "message": "Token set successfully"}

@app.post("/api/ghl/test/create-contact")
async def test_create_contact(name: str, email: str, phone: str):
    """Create a test contact in our system"""
    # Prepare a test contact
    contact_data = {
        "_id": str(uuid.uuid4()),
        "org_id": "test_org",
        "name": name,
        "email": email,
        "phone": phone,
        "ghl_contact_id": str(uuid.uuid4()),  # Simulate a GHL contact ID
        "relationship_stage": "initial_contact",
        "trust_level": 0.5,
        "conversion_probability": 0.3,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    # Store in database
    await db.leads.insert_one(contact_data)
    
    return {
        "status": "success", 
        "message": "Test contact created", 
        "contact": contact_data
    }

# Webhook endpoint
@app.post("/api/ghl/webhook")
async def ghl_webhook(payload: Dict[str, Any], signature: str = Header(None, alias="X-GoHighLevel-Signature"), event_type: str = Header(None, alias="X-Event-Type")):
    """Handle GHL webhooks"""
    logger.info(f"Received GHL webhook: {event_type}")
    
    # Verify webhook signature if provided
    if signature:
        payload_str = json.dumps(payload)
        if not ghl_integration.verify_webhook_signature(signature, payload_str):
            logger.warning(f"Invalid webhook signature")
            raise HTTPException(status_code=403, detail="Invalid webhook signature")
    
    # Process webhook based on event type
    if event_type:
        logger.info(f"Processing {event_type} webhook")
        # Here you would handle different event types
        # For now, just log the event
    
    return {"status": "success", "message": f"Processed {event_type} webhook"}

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
