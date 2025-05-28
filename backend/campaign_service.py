import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
from fastapi import HTTPException
from enum import Enum

import database as db
from agent_orchestrator import AgentOrchestrator
from ghl_integration import GHLIntegration

logger = logging.getLogger(__name__)

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignType(str, Enum):
    OUTBOUND_VOICE = "outbound_voice"
    OUTBOUND_SMS = "outbound_sms"
    MIXED_CHANNEL = "mixed_channel"

class LeadProcessingStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    FAILED = "failed"
    SKIPPED = "skipped"

class CampaignService:
    """
    Smart Campaign Management Service for AI-driven proactive outreach
    
    Manages campaign creation, lead queuing, intelligent throttling,
    and interaction initiation at scale.
    """
    
    def __init__(self):
        self.agent_orchestrator = AgentOrchestrator()
        self.ghl_integration = GHLIntegration()
        self.active_campaigns = {}  # In-memory tracking for active campaigns
        
    async def create_campaign(
        self,
        org_id: str,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new AI-driven outreach campaign
        
        Args:
            org_id: Organization ID
            campaign_data: Campaign configuration
            
        Returns:
            Created campaign object
        """
        try:
            # Validate campaign data
            self._validate_campaign_data(campaign_data)
            
            # Create campaign document
            campaign = {
                "_id": str(uuid.uuid4()),
                "org_id": org_id,
                "name": campaign_data["name"],
                "description": campaign_data.get("description", ""),
                "campaign_type": campaign_data["campaign_type"],
                "status": CampaignStatus.DRAFT,
                
                # Target Configuration
                "target_config": {
                    "ghl_segment_criteria": campaign_data["target_config"]["ghl_segment_criteria"],
                    "lead_filters": campaign_data["target_config"].get("lead_filters", {}),
                    "estimated_leads": 0  # Will be calculated
                },
                
                # Agent Configuration
                "agent_config": {
                    "initial_agent_type": campaign_data["agent_config"]["initial_agent_type"],
                    "campaign_objective": campaign_data["agent_config"]["campaign_objective"],
                    "communication_channels": campaign_data["agent_config"]["communication_channels"],
                    "llm_model": campaign_data["agent_config"].get("llm_model", "gpt-4o")
                },
                
                # Schedule & Throttling Configuration
                "schedule_config": {
                    "daily_contact_limit": campaign_data["schedule_config"].get("daily_contact_limit", 50),
                    "hourly_contact_limit": campaign_data["schedule_config"].get("hourly_contact_limit", 10),
                    "contact_hours": campaign_data["schedule_config"].get("contact_hours", {
                        "start": "09:00",
                        "end": "17:00",
                        "timezone": "America/New_York"
                    }),
                    "contact_days": campaign_data["schedule_config"].get("contact_days", [1, 2, 3, 4, 5]),  # Mon-Fri
                    "retry_failed_after_hours": campaign_data["schedule_config"].get("retry_failed_after_hours", 24)
                },
                
                # Campaign Metrics
                "metrics": {
                    "total_leads": 0,
                    "leads_contacted": 0,
                    "leads_responded": 0,
                    "leads_converted": 0,
                    "calls_made": 0,
                    "sms_sent": 0,
                    "response_rate": 0.0,
                    "conversion_rate": 0.0
                },
                
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "started_at": None,
                "completed_at": None
            }
            
            # Save campaign to database
            saved_campaign = await db.create_document(db.db.campaigns, campaign)
            
            # Estimate lead count based on criteria
            estimated_leads = await self._estimate_lead_count(org_id, campaign["target_config"])
            
            # Update campaign with estimated lead count
            await db.update_document(
                db.db.campaigns,
                campaign["_id"],
                {"target_config.estimated_leads": estimated_leads}
            )
            
            logger.info(f"Created campaign {campaign['_id']} for org {org_id}")
            
            return {
                **saved_campaign,
                "target_config": {
                    **saved_campaign["target_config"],
                    "estimated_leads": estimated_leads
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")
    
    async def start_campaign(
        self,
        org_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """
        Start an active campaign and begin lead processing
        
        Args:
            org_id: Organization ID
            campaign_id: Campaign ID to start
            
        Returns:
            Updated campaign status
        """
        try:
            # Get campaign
            campaign = await db.get_document(db.db.campaigns, campaign_id)
            
            if not campaign or campaign["org_id"] != org_id:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            if campaign["status"] not in [CampaignStatus.DRAFT, CampaignStatus.PAUSED]:
                raise HTTPException(status_code=400, detail=f"Cannot start campaign in {campaign['status']} status")
            
            # Load leads into campaign queue
            leads_loaded = await self._load_campaign_leads(org_id, campaign_id, campaign["target_config"])
            
            # Update campaign status
            updated_campaign = await db.update_document(
                db.db.campaigns,
                campaign_id,
                {
                    "status": CampaignStatus.ACTIVE,
                    "started_at": datetime.now(),
                    "metrics.total_leads": leads_loaded
                }
            )
            
            # Start campaign processing in background
            asyncio.create_task(self._process_campaign_queue(org_id, campaign_id))
            
            # Track in memory
            self.active_campaigns[campaign_id] = {
                "org_id": org_id,
                "started_at": datetime.now(),
                "last_processed_at": None,
                "processing": True
            }
            
            logger.info(f"Started campaign {campaign_id} with {leads_loaded} leads")
            
            return {
                "campaign_id": campaign_id,
                "status": CampaignStatus.ACTIVE,
                "leads_loaded": leads_loaded,
                "message": f"Campaign started successfully with {leads_loaded} leads"
            }
            
        except Exception as e:
            logger.error(f"Error starting campaign {campaign_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to start campaign: {str(e)}")
    
    async def pause_campaign(
        self,
        org_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """Pause an active campaign"""
        try:
            campaign = await db.get_document(db.db.campaigns, campaign_id)
            
            if not campaign or campaign["org_id"] != org_id:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            if campaign["status"] != CampaignStatus.ACTIVE:
                raise HTTPException(status_code=400, detail="Can only pause active campaigns")
            
            # Update campaign status
            await db.update_document(
                db.db.campaigns,
                campaign_id,
                {"status": CampaignStatus.PAUSED}
            )
            
            # Update in-memory tracking
            if campaign_id in self.active_campaigns:
                self.active_campaigns[campaign_id]["processing"] = False
            
            logger.info(f"Paused campaign {campaign_id}")
            
            return {
                "campaign_id": campaign_id,
                "status": CampaignStatus.PAUSED,
                "message": "Campaign paused successfully"
            }
            
        except Exception as e:
            logger.error(f"Error pausing campaign {campaign_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to pause campaign: {str(e)}")
    
    async def stop_campaign(
        self,
        org_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """Stop and complete a campaign"""
        try:
            campaign = await db.get_document(db.db.campaigns, campaign_id)
            
            if not campaign or campaign["org_id"] != org_id:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            # Update campaign status
            await db.update_document(
                db.db.campaigns,
                campaign_id,
                {
                    "status": CampaignStatus.COMPLETED,
                    "completed_at": datetime.now()
                }
            )
            
            # Remove from active tracking
            if campaign_id in self.active_campaigns:
                del self.active_campaigns[campaign_id]
            
            logger.info(f"Stopped campaign {campaign_id}")
            
            return {
                "campaign_id": campaign_id,
                "status": CampaignStatus.COMPLETED,
                "message": "Campaign stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"Error stopping campaign {campaign_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to stop campaign: {str(e)}")
    
    async def get_campaign_status(
        self,
        org_id: str,
        campaign_id: str
    ) -> Dict[str, Any]:
        """Get detailed campaign status and metrics"""
        try:
            campaign = await db.get_document(db.db.campaigns, campaign_id)
            
            if not campaign or campaign["org_id"] != org_id:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            # Get lead processing stats
            lead_stats = await self._get_campaign_lead_stats(campaign_id)
            
            # Get recent interactions
            recent_interactions = await self._get_recent_campaign_interactions(campaign_id, limit=10)
            
            return {
                "campaign": campaign,
                "lead_processing_stats": lead_stats,
                "recent_interactions": recent_interactions,
                "is_processing": campaign_id in self.active_campaigns
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign status {campaign_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get campaign status: {str(e)}")
    
    async def list_campaigns(
        self,
        org_id: str,
        status_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List campaigns for an organization"""
        try:
            filter_criteria = {"org_id": org_id}
            
            if status_filter:
                filter_criteria["status"] = status_filter
            
            campaigns = await db.list_documents(
                db.db.campaigns,
                filter_criteria=filter_criteria,
                limit=limit,
                sort_by=[("created_at", -1)]
            )
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Error listing campaigns for org {org_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list campaigns: {str(e)}")
    
    def _validate_campaign_data(self, campaign_data: Dict[str, Any]) -> None:
        """Validate campaign configuration data"""
        required_fields = ["name", "campaign_type", "target_config", "agent_config", "schedule_config"]
        
        for field in required_fields:
            if field not in campaign_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate campaign type
        if campaign_data["campaign_type"] not in [t.value for t in CampaignType]:
            raise ValueError(f"Invalid campaign type: {campaign_data['campaign_type']}")
        
        # Validate target config
        target_config = campaign_data["target_config"]
        if "ghl_segment_criteria" not in target_config:
            raise ValueError("Missing GHL segment criteria in target config")
        
        # Validate agent config
        agent_config = campaign_data["agent_config"]
        required_agent_fields = ["initial_agent_type", "campaign_objective", "communication_channels"]
        for field in required_agent_fields:
            if field not in agent_config:
                raise ValueError(f"Missing required agent config field: {field}")
    
    async def _estimate_lead_count(
        self,
        org_id: str,
        target_config: Dict[str, Any]
    ) -> int:
        """Estimate the number of leads that match the campaign criteria"""
        try:
            # Use GHL integration to count leads matching criteria
            criteria = target_config["ghl_segment_criteria"]
            
            # For MVP, return a mock estimate
            # In production, this would query GHL API with the actual criteria
            return 25  # Mock estimate
            
        except Exception as e:
            logger.error(f"Error estimating lead count: {e}")
            return 0
    
    async def _load_campaign_leads(
        self,
        org_id: str,
        campaign_id: str,
        target_config: Dict[str, Any]
    ) -> int:
        """Load leads into campaign processing queue"""
        try:
            # Get leads from GHL based on criteria
            criteria = target_config["ghl_segment_criteria"]
            
            # For MVP, create some mock campaign leads
            mock_leads = [
                {
                    "_id": str(uuid.uuid4()),
                    "campaign_id": campaign_id,
                    "org_id": org_id,
                    "lead_id": f"lead_{i}",
                    "ghl_contact_id": f"ghl_contact_{i}",
                    "contact_info": {
                        "name": f"Lead {i}",
                        "phone": f"+1555000{i:04d}",
                        "email": f"lead{i}@example.com"
                    },
                    "processing_status": LeadProcessingStatus.QUEUED,
                    "scheduled_contact_time": None,
                    "attempts": 0,
                    "last_attempt_at": None,
                    "created_at": datetime.now()
                }
                for i in range(1, 26)  # 25 mock leads
            ]
            
            # Insert campaign leads into database
            for lead in mock_leads:
                await db.create_document(db.db.campaign_leads, lead)
            
            logger.info(f"Loaded {len(mock_leads)} leads for campaign {campaign_id}")
            
            return len(mock_leads)
            
        except Exception as e:
            logger.error(f"Error loading campaign leads: {e}")
            return 0
    
    async def _process_campaign_queue(
        self,
        org_id: str,
        campaign_id: str
    ) -> None:
        """Background task to process campaign lead queue with intelligent throttling"""
        try:
            logger.info(f"Starting campaign queue processing for {campaign_id}")
            
            while campaign_id in self.active_campaigns and self.active_campaigns[campaign_id]["processing"]:
                # Get campaign to check status and limits
                campaign = await db.get_document(db.db.campaigns, campaign_id)
                
                if not campaign or campaign["status"] != CampaignStatus.ACTIVE:
                    break
                
                # Check if we're within contact hours
                if not self._is_within_contact_hours(campaign["schedule_config"]):
                    await asyncio.sleep(300)  # Wait 5 minutes and check again
                    continue
                
                # Check daily and hourly limits
                if not await self._can_contact_now(campaign_id, campaign["schedule_config"]):
                    await asyncio.sleep(600)  # Wait 10 minutes and check again
                    continue
                
                # Get next lead to process
                lead = await self._get_next_lead_to_process(campaign_id)
                
                if not lead:
                    # No more leads to process
                    logger.info(f"No more leads to process for campaign {campaign_id}")
                    break
                
                # Process the lead
                await self._process_campaign_lead(org_id, campaign_id, lead, campaign)
                
                # Update in-memory tracking
                self.active_campaigns[campaign_id]["last_processed_at"] = datetime.now()
                
                # Wait between contacts (intelligent spacing)
                await asyncio.sleep(30)  # 30 seconds between contacts
            
            logger.info(f"Finished campaign queue processing for {campaign_id}")
            
        except Exception as e:
            logger.error(f"Error in campaign queue processing: {e}")
    
    def _is_within_contact_hours(self, schedule_config: Dict[str, Any]) -> bool:
        """Check if current time is within allowed contact hours"""
        # For MVP, always return True
        # In production, implement proper timezone-aware hour checking
        return True
    
    async def _can_contact_now(
        self,
        campaign_id: str,
        schedule_config: Dict[str, Any]
    ) -> bool:
        """Check if campaign can make contact now based on throttling limits"""
        # For MVP, always return True
        # In production, implement proper daily/hourly limit checking
        return True
    
    async def _get_next_lead_to_process(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get the next lead in queue for processing"""
        try:
            # Find next queued lead
            leads = await db.list_documents(
                db.db.campaign_leads,
                filter_criteria={
                    "campaign_id": campaign_id,
                    "processing_status": LeadProcessingStatus.QUEUED
                },
                limit=1,
                sort_by=[("created_at", 1)]
            )
            
            return leads[0] if leads else None
            
        except Exception as e:
            logger.error(f"Error getting next lead: {e}")
            return None
    
    async def _process_campaign_lead(
        self,
        org_id: str,
        campaign_id: str,
        lead: Dict[str, Any],
        campaign: Dict[str, Any]
    ) -> None:
        """Process a single lead through the campaign"""
        try:
            # Update lead status to processing
            await db.update_document(
                db.db.campaign_leads,
                lead["_id"],
                {
                    "processing_status": LeadProcessingStatus.PROCESSING,
                    "last_attempt_at": datetime.now(),
                    "attempts": lead["attempts"] + 1
                }
            )
            
            # Prepare context for agent
            context = {
                "campaign_objective": campaign["agent_config"]["campaign_objective"],
                "campaign_type": campaign["campaign_type"],
                "lead_info": lead["contact_info"],
                "channel": "sms" if campaign["campaign_type"] == CampaignType.OUTBOUND_SMS else "voice"
            }
            
            # Use agent orchestrator to initiate contact
            try:
                response = await self.agent_orchestrator.process_message(
                    org_id=org_id,
                    lead_id=lead["lead_id"],
                    message="CAMPAIGN_INITIATED",  # Special message to indicate campaign start
                    channel=context["channel"],
                    context=context
                )
                
                # Update lead status to contacted
                await db.update_document(
                    db.db.campaign_leads,
                    lead["_id"],
                    {"processing_status": LeadProcessingStatus.CONTACTED}
                )
                
                # Update campaign metrics
                await self._update_campaign_metrics(campaign_id, "contacted")
                
                logger.info(f"Successfully processed lead {lead['lead_id']} for campaign {campaign_id}")
                
            except Exception as agent_error:
                logger.error(f"Agent processing failed for lead {lead['lead_id']}: {agent_error}")
                
                # Update lead status to failed
                await db.update_document(
                    db.db.campaign_leads,
                    lead["_id"],
                    {"processing_status": LeadProcessingStatus.FAILED}
                )
                
        except Exception as e:
            logger.error(f"Error processing campaign lead {lead['_id']}: {e}")
    
    async def _update_campaign_metrics(
        self,
        campaign_id: str,
        metric_type: str
    ) -> None:
        """Update campaign metrics"""
        try:
            campaign = await db.get_document(db.db.campaigns, campaign_id)
            
            if not campaign:
                return
            
            metrics = campaign.get("metrics", {})
            
            if metric_type == "contacted":
                metrics["leads_contacted"] = metrics.get("leads_contacted", 0) + 1
            elif metric_type == "responded":
                metrics["leads_responded"] = metrics.get("leads_responded", 0) + 1
            elif metric_type == "converted":
                metrics["leads_converted"] = metrics.get("leads_converted", 0) + 1
            
            # Calculate rates
            total_leads = metrics.get("total_leads", 1)
            metrics["response_rate"] = metrics.get("leads_responded", 0) / total_leads
            metrics["conversion_rate"] = metrics.get("leads_converted", 0) / total_leads
            
            await db.update_document(
                db.db.campaigns,
                campaign_id,
                {"metrics": metrics}
            )
            
        except Exception as e:
            logger.error(f"Error updating campaign metrics: {e}")
    
    async def _get_campaign_lead_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get lead processing statistics for a campaign"""
        try:
            # Count leads by status
            all_leads = await db.list_documents(
                db.db.campaign_leads,
                filter_criteria={"campaign_id": campaign_id},
                limit=1000
            )
            
            stats = {
                "total": len(all_leads),
                "queued": 0,
                "processing": 0,
                "contacted": 0,
                "responded": 0,
                "failed": 0,
                "skipped": 0
            }
            
            for lead in all_leads:
                status = lead.get("processing_status", LeadProcessingStatus.QUEUED)
                stats[status] = stats.get(status, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting campaign lead stats: {e}")
            return {}
    
    async def _get_recent_campaign_interactions(
        self,
        campaign_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent interactions for a campaign"""
        try:
            # Get recent campaign leads that have been processed
            recent_leads = await db.list_documents(
                db.db.campaign_leads,
                filter_criteria={
                    "campaign_id": campaign_id,
                    "processing_status": {"$in": [LeadProcessingStatus.CONTACTED, LeadProcessingStatus.RESPONDED]}
                },
                limit=limit,
                sort_by=[("last_attempt_at", -1)]
            )
            
            interactions = []
            for lead in recent_leads:
                interactions.append({
                    "lead_name": lead["contact_info"]["name"],
                    "contact_method": "SMS" if lead.get("channel") == "sms" else "Voice",
                    "status": lead["processing_status"],
                    "timestamp": lead["last_attempt_at"],
                    "attempts": lead["attempts"]
                })
            
            return interactions
            
        except Exception as e:
            logger.error(f"Error getting recent campaign interactions: {e}")
            return []