from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from datetime import datetime
import uuid

class AgentType(str, Enum):
    INITIAL_CONTACT = "initial_contact"
    QUALIFIER = "qualifier"
    NURTURER = "nurturer"
    OBJECTION_HANDLER = "objection_handler"
    CLOSER = "closer"
    APPOINTMENT_SETTER = "appointment_setter"

class ConversationChannel(str, Enum):
    VOICE = "voice"
    SMS = "sms"
    EMAIL = "email"
    CHAT = "chat"

class RelationshipStage(str, Enum):
    INITIAL_CONTACT = "initial_contact"
    QUALIFICATION = "qualification"
    NURTURING = "nurturing"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    POST_SALE = "post_sale"

class PersonalityType(str, Enum):
    ANALYTICAL = "analytical"
    DRIVER = "driver"
    EXPRESSIVE = "expressive"
    AMIABLE = "amiable"

class Organization(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    subscription_tier: str = "starter"
    ghl_account_id: Optional[str] = None
    ai_configuration: Dict[str, Any] = {}
    voice_settings: Dict[str, Any] = {}
    memory_settings: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "ABC Realty",
                "subscription_tier": "starter",
                "ghl_account_id": "12345",
                "ai_configuration": {"model": "gpt-4o", "temperature": 0.7},
                "voice_settings": {"provider": "elevenlabs", "voice_id": "voice1"},
                "memory_settings": {"retention_days": 90}
            }
        }

class LeadProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str
    ghl_contact_id: Optional[str] = None
    mem0_user_id: Optional[str] = None
    
    # AI-Generated Intelligence
    personality_type: Optional[PersonalityType] = None
    communication_preference: Optional[str] = None
    decision_making_style: Optional[str] = None
    trust_level: float = 0.5
    relationship_stage: RelationshipStage = RelationshipStage.INITIAL_CONTACT
    
    # Behavioral Analysis
    response_patterns: Dict[str, Any] = {}
    engagement_history: Dict[str, Any] = {}
    objection_patterns: Dict[str, Any] = {}
    success_indicators: Dict[str, Any] = {}
    
    # Property & Financial Intelligence
    property_preferences: Dict[str, Any] = {}
    budget_analysis: Dict[str, Any] = {}
    timeline_urgency: int = 5
    motivation_factors: Dict[str, Any] = {}
    
    # Performance Metrics
    conversion_probability: float = 0.0
    engagement_score: float = 0.0
    rapport_level: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "org_id": "org123",
                "ghl_contact_id": "contact123",
                "personality_type": "analytical",
                "communication_preference": "email",
                "trust_level": 0.7,
                "relationship_stage": "nurturing",
                "property_preferences": {"bedrooms": 3, "location": "downtown"},
                "budget_analysis": {"min": 300000, "max": 450000}
            }
        }

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lead_id: str
    channel: ConversationChannel
    agent_type: Optional[AgentType] = None
    
    # Conversation Data
    transcript: Optional[str] = None
    audio_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    
    # AI Analysis
    sentiment_analysis: Dict[str, Any] = {}
    intent_classification: Dict[str, Any] = {}
    objections_detected: Dict[str, Any] = {}
    buying_signals: Dict[str, Any] = {}
    
    # Outcomes
    outcome: Optional[str] = None
    effectiveness_score: Optional[float] = None
    next_best_action: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "lead_id": "lead123",
                "channel": "voice",
                "agent_type": "qualifier",
                "transcript": "Sample conversation transcript...",
                "sentiment_analysis": {"overall": "positive", "changes": [{"time": 120, "sentiment": "neutral"}]},
                "next_best_action": "Schedule property viewing"
            }
        }

class AgentInteraction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    agent_type: AgentType
    
    # Agent Decision Making
    agent_reasoning: Optional[str] = None
    confidence_score: Optional[float] = None
    strategy_used: Optional[str] = None
    
    # Performance Metrics
    effectiveness_score: Optional[float] = None
    lead_engagement_change: Optional[float] = None
    objective_progress: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "conversation_id": "conv123",
                "agent_type": "qualifier",
                "agent_reasoning": "Detected interest in downtown properties...",
                "confidence_score": 0.85,
                "strategy_used": "needs_assessment"
            }
        }

class MemorySnapshot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lead_id: str
    mem0_memory_id: Optional[str] = None
    
    # Memory Content
    memory_type: str  # factual, emotional, strategic, contextual
    memory_content: Dict[str, Any]
    confidence_level: Optional[float] = None
    
    # Performance Tracking
    retrieval_count: int = 0
    effectiveness_score: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "lead_id": "lead123",
                "memory_type": "factual",
                "memory_content": {"preferences": {"property_type": "condo"}, "constraints": {"max_price": 450000}},
                "confidence_level": 0.9
            }
        }

class KnowledgeBase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str
    title: str
    description: Optional[str] = None
    content_type: str  # document, script, faq
    content: Union[str, Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "org_id": "org123",
                "title": "Luxury Property Sales Guide",
                "description": "Best practices for selling luxury properties",
                "content_type": "document",
                "content": "This guide covers strategies for marketing luxury properties..."
            }
        }

class ApiKeys(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str
    ghl_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    vapi_api_key: Optional[str] = None
    mem0_api_key: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        schema_extra = {
            "example": {
                "org_id": "org123",
                "ghl_api_key": "ghl_api_key_example",
                "openai_api_key": "openai_api_key_example"
            }
        }

# Request and Response Models
class OrganizationCreate(BaseModel):
    name: str
    subscription_tier: Optional[str] = "starter"
    ghl_account_id: Optional[str] = None
    ai_configuration: Optional[Dict[str, Any]] = {}
    voice_settings: Optional[Dict[str, Any]] = {}
    memory_settings: Optional[Dict[str, Any]] = {}

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    subscription_tier: Optional[str] = None
    ghl_account_id: Optional[str] = None
    ai_configuration: Optional[Dict[str, Any]] = None
    voice_settings: Optional[Dict[str, Any]] = None
    memory_settings: Optional[Dict[str, Any]] = None

class LeadProfileCreate(BaseModel):
    org_id: str
    ghl_contact_id: Optional[str] = None
    personality_type: Optional[PersonalityType] = None
    communication_preference: Optional[str] = None
    decision_making_style: Optional[str] = None
    trust_level: Optional[float] = 0.5
    relationship_stage: Optional[RelationshipStage] = RelationshipStage.INITIAL_CONTACT
    property_preferences: Optional[Dict[str, Any]] = {}
    budget_analysis: Optional[Dict[str, Any]] = {}
    timeline_urgency: Optional[int] = 5
    motivation_factors: Optional[Dict[str, Any]] = {}

class LeadProfileUpdate(BaseModel):
    ghl_contact_id: Optional[str] = None
    personality_type: Optional[PersonalityType] = None
    communication_preference: Optional[str] = None
    decision_making_style: Optional[str] = None
    trust_level: Optional[float] = None
    relationship_stage: Optional[RelationshipStage] = None
    response_patterns: Optional[Dict[str, Any]] = None
    engagement_history: Optional[Dict[str, Any]] = None
    objection_patterns: Optional[Dict[str, Any]] = None
    success_indicators: Optional[Dict[str, Any]] = None
    property_preferences: Optional[Dict[str, Any]] = None
    budget_analysis: Optional[Dict[str, Any]] = None
    timeline_urgency: Optional[int] = None
    motivation_factors: Optional[Dict[str, Any]] = None
    conversion_probability: Optional[float] = None
    engagement_score: Optional[float] = None
    rapport_level: Optional[float] = None

class ConversationCreate(BaseModel):
    lead_id: str
    channel: ConversationChannel
    agent_type: Optional[AgentType] = None
    transcript: Optional[str] = None
    audio_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    sentiment_analysis: Optional[Dict[str, Any]] = {}
    intent_classification: Optional[Dict[str, Any]] = {}
    objections_detected: Optional[Dict[str, Any]] = {}
    buying_signals: Optional[Dict[str, Any]] = {}
    outcome: Optional[str] = None
    effectiveness_score: Optional[float] = None
    next_best_action: Optional[str] = None

class ApiKeysUpdate(BaseModel):
    ghl_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    vapi_api_key: Optional[str] = None
    mem0_api_key: Optional[str] = None
