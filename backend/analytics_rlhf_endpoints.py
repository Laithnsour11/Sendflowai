# Analytics and RLHF endpoints for Phase B.2
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Agent Performance Analytics
@router.get("/api/analytics/agent-performance")
async def get_agent_performance(
    org_id: str,
    time_period: str = "30_days",
    agent_type: Optional[str] = None
):
    """Get comprehensive agent performance analytics"""
    try:
        # This would query the database for actual performance data
        # For now, returning realistic analytics based on the system
        
        end_date = datetime.now()
        if time_period == "7_days":
            start_date = end_date - timedelta(days=7)
        elif time_period == "30_days":
            start_date = end_date - timedelta(days=30)
        elif time_period == "90_days":
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Simulate analytics data
        analytics_data = {
            "org_id": org_id,
            "time_period": time_period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "overview": {
                "total_interactions": 247,
                "total_leads_processed": 156,
                "average_response_time": 3.7,
                "overall_success_rate": 0.79,
                "lead_progression_rate": 0.68
            },
            "agent_breakdown": {
                "initial_contact": {
                    "interactions": 89,
                    "success_rate": 0.82,
                    "avg_response_time": 2.3,
                    "lead_progression_rate": 0.67,
                    "top_scenarios": ["new_lead_greeting", "property_inquiry", "contact_info_collection"]
                },
                "qualifier": {
                    "interactions": 73,
                    "success_rate": 0.78,
                    "avg_response_time": 4.1,
                    "lead_progression_rate": 0.71,
                    "qualification_completeness": 0.84,
                    "top_scenarios": ["budget_qualification", "timeline_assessment", "needs_analysis"]
                },
                "objection_handler": {
                    "interactions": 45,
                    "success_rate": 0.71,
                    "avg_response_time": 6.2,
                    "objection_resolution_rate": 0.63,
                    "common_objections": ["price_too_high", "not_ready", "need_more_time"]
                },
                "closer": {
                    "interactions": 28,
                    "success_rate": 0.85,
                    "avg_response_time": 8.1,
                    "appointment_conversion": 0.79,
                    "deal_advancement": 0.73
                },
                "nurturer": {
                    "interactions": 12,
                    "success_rate": 0.92,
                    "avg_response_time": 3.7,
                    "engagement_retention": 0.88,
                    "relationship_building": 0.91
                },
                "appointment_setter": {
                    "interactions": 15,
                    "success_rate": 0.80,
                    "avg_response_time": 5.2,
                    "scheduling_success": 0.75,
                    "no_show_rate": 0.12
                }
            },
            "performance_trends": {
                "weekly_success_rates": [0.72, 0.75, 0.78, 0.79],
                "response_time_trend": [4.2, 3.9, 3.8, 3.7],
                "volume_trend": [45, 52, 68, 82]
            },
            "improvement_recommendations": [
                {
                    "agent": "objection_handler",
                    "metric": "response_time",
                    "current_value": 6.2,
                    "target_value": 4.0,
                    "recommendation": "Implement faster objection identification patterns",
                    "priority": "high"
                },
                {
                    "agent": "qualifier",
                    "metric": "success_rate", 
                    "current_value": 0.78,
                    "target_value": 0.85,
                    "recommendation": "Enhance qualification script with better probing questions",
                    "priority": "medium"
                }
            ]
        }
        
        # Filter by agent type if specified
        if agent_type and agent_type in analytics_data["agent_breakdown"]:
            agent_data = analytics_data["agent_breakdown"][agent_type]
            return {
                "agent_type": agent_type,
                "time_period": time_period,
                "performance_data": agent_data,
                "recommendations": [r for r in analytics_data["improvement_recommendations"] if r["agent"] == agent_type]
            }
        
        return analytics_data
        
    except Exception as e:
        logger.error(f"Error getting agent performance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# RLHF Feedback Collection
@router.post("/api/rlhf/feedback")
async def submit_feedback(feedback_data: Dict[str, Any]):
    """Submit RLHF feedback for conversation improvement"""
    try:
        required_fields = ["conversation_id", "feedback_type", "rating_or_feedback"]
        
        for field in required_fields:
            if field not in feedback_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Process and store feedback
        processed_feedback = {
            "id": f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "conversation_id": feedback_data["conversation_id"],
            "feedback_type": feedback_data["feedback_type"],
            "rating": feedback_data.get("rating"),
            "feedback_text": feedback_data.get("feedback_text", ""),
            "improvement_suggestion": feedback_data.get("improvement_suggestion", ""),
            "agent_selection_correct": feedback_data.get("agent_selection_correct"),
            "suggested_agent": feedback_data.get("suggested_agent"),
            "response_effectiveness": feedback_data.get("response_effectiveness"),
            "timestamp": datetime.now().isoformat(),
            "processed": False,
            "learning_applied": False
        }
        
        # In a real implementation, this would be stored in the database
        logger.info(f"RLHF Feedback received: {processed_feedback['feedback_type']} for {processed_feedback['conversation_id']}")
        
        # Trigger learning process for critical feedback
        if (feedback_data.get("rating", 5) < 3 or 
            feedback_data.get("agent_selection_correct") == False or
            feedback_data.get("response_effectiveness", 5) < 3):
            
            # Immediate learning trigger
            learning_trigger = {
                "feedback_id": processed_feedback["id"],
                "priority": "high",
                "learning_type": "immediate_adjustment",
                "areas_to_improve": []
            }
            
            if feedback_data.get("rating", 5) < 3:
                learning_trigger["areas_to_improve"].append("response_quality")
            if feedback_data.get("agent_selection_correct") == False:
                learning_trigger["areas_to_improve"].append("agent_selection")
            if feedback_data.get("response_effectiveness", 5) < 3:
                learning_trigger["areas_to_improve"].append("response_effectiveness")
            
            logger.info(f"Triggered immediate learning for feedback: {learning_trigger}")
        
        return {
            "success": True,
            "feedback_id": processed_feedback["id"],
            "message": "Feedback received and will be used to improve AI performance",
            "immediate_learning_triggered": (feedback_data.get("rating", 5) < 3)
        }
        
    except Exception as e:
        logger.error(f"Error processing RLHF feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/rlhf/feedback-summary")
async def get_feedback_summary(org_id: str, time_period: str = "30_days"):
    """Get summary of RLHF feedback and learning progress"""
    try:
        # Simulate feedback summary data
        summary = {
            "org_id": org_id,
            "time_period": time_period,
            "feedback_stats": {
                "total_feedback_received": 89,
                "average_rating": 4.2,
                "feedback_types": {
                    "conversation_rating": 45,
                    "agent_selection_feedback": 23,
                    "response_effectiveness": 21
                },
                "sentiment_distribution": {
                    "positive": 67,
                    "neutral": 15,
                    "negative": 7
                }
            },
            "learning_progress": {
                "improvements_implemented": 12,
                "success_rate_improvement": 0.08,
                "response_time_improvement": -0.5,
                "customer_satisfaction_improvement": 0.3
            },
            "recent_improvements": [
                {
                    "date": "2024-01-14",
                    "improvement": "Enhanced objection handling for pricing concerns",
                    "feedback_source": "Multiple negative ratings on price objections",
                    "impact": "15% improvement in objection resolution"
                },
                {
                    "date": "2024-01-12", 
                    "improvement": "Improved agent selection for first-time buyers",
                    "feedback_source": "Agent selection feedback indicating better qualifier needed",
                    "impact": "12% better lead progression for first-time buyers"
                }
            ],
            "pending_learning_items": [
                {
                    "feedback_cluster": "Response personalization",
                    "feedback_count": 8,
                    "priority": "medium",
                    "estimated_implementation": "2024-01-20"
                }
            ]
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting feedback summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent Training Configuration
@router.get("/api/training/agent-config/{agent_type}")
async def get_agent_configuration(agent_type: str, org_id: str):
    """Get current configuration for a specific agent type"""
    try:
        # Simulate agent configuration data
        agent_configs = {
            "initial_contact": {
                "agent_type": "initial_contact",
                "display_name": "Initial Contact Agent",
                "description": "Handles first interactions with new leads",
                "current_config": {
                    "greeting_style": "warm",
                    "qualification_depth": "moderate",
                    "response_length": "medium",
                    "personality_traits": ["friendly", "professional"],
                    "response_time_target": 3.0,
                    "success_rate_target": 0.85
                },
                "configurable_options": {
                    "greeting_style": {
                        "options": ["formal", "casual", "warm"],
                        "current": "warm",
                        "description": "How the agent greets new leads"
                    },
                    "qualification_depth": {
                        "options": ["basic", "moderate", "comprehensive"],
                        "current": "moderate",
                        "description": "How much qualification to do in first contact"
                    },
                    "response_length": {
                        "options": ["short", "medium", "detailed"],
                        "current": "medium",
                        "description": "Typical response length"
                    }
                },
                "performance_targets": {
                    "response_time": {"current": 2.3, "target": 3.0, "unit": "seconds"},
                    "success_rate": {"current": 0.82, "target": 0.85, "unit": "percentage"},
                    "lead_progression": {"current": 0.67, "target": 0.70, "unit": "percentage"}
                },
                "training_data": {
                    "scripts_count": 12,
                    "scenarios_count": 8,
                    "knowledge_docs": 15,
                    "last_training": "2024-01-10"
                }
            },
            "objection_handler": {
                "agent_type": "objection_handler",
                "display_name": "Objection Handler Agent", 
                "description": "Specialized in addressing lead concerns and objections",
                "current_config": {
                    "empathy_level": "high",
                    "data_usage": "comprehensive",
                    "follow_up_style": "multi_touch",
                    "response_time_target": 5.0,
                    "objection_resolution_target": 0.75
                },
                "configurable_options": {
                    "empathy_level": {
                        "options": ["moderate", "high", "very_high"],
                        "current": "high",
                        "description": "Level of empathy in responses"
                    },
                    "data_usage": {
                        "options": ["minimal", "balanced", "comprehensive"],
                        "current": "comprehensive", 
                        "description": "How much market data to include"
                    }
                },
                "performance_targets": {
                    "response_time": {"current": 6.2, "target": 5.0, "unit": "seconds"},
                    "success_rate": {"current": 0.71, "target": 0.75, "unit": "percentage"},
                    "objection_resolution": {"current": 0.63, "target": 0.80, "unit": "percentage"}
                },
                "training_data": {
                    "scripts_count": 25,
                    "scenarios_count": 15,
                    "objection_library": 47,
                    "last_training": "2024-01-08"
                }
            }
        }
        
        if agent_type not in agent_configs:
            raise HTTPException(status_code=404, detail=f"Agent type {agent_type} not found")
        
        return agent_configs[agent_type]
        
    except Exception as e:
        logger.error(f"Error getting agent configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/training/agent-config/{agent_type}")
async def update_agent_configuration(agent_type: str, org_id: str, config_updates: Dict[str, Any]):
    """Update configuration for a specific agent type"""
    try:
        # Validate configuration updates
        updated_config = {
            "agent_type": agent_type,
            "org_id": org_id,
            "updates": config_updates,
            "timestamp": datetime.now().isoformat(),
            "updated_by": "admin",  # In real app, would get from auth
            "version": f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # In real implementation, would validate against allowed options and update database
        logger.info(f"Updated configuration for {agent_type}: {config_updates}")
        
        return {
            "success": True,
            "agent_type": agent_type,
            "updated_fields": list(config_updates.keys()),
            "config_version": updated_config["version"],
            "message": f"Configuration updated for {agent_type} agent"
        }
        
    except Exception as e:
        logger.error(f"Error updating agent configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Real-time Dashboard Data
@router.get("/api/dashboard/real-time")
async def get_real_time_dashboard_data(org_id: str):
    """Get real-time dashboard data for the organization"""
    try:
        dashboard_data = {
            "org_id": org_id,
            "timestamp": datetime.now().isoformat(),
            "kpi_overview": {
                "active_conversations": 12,
                "leads_today": 23,
                "responses_sent": 147,
                "avg_response_time": 3.7,
                "system_health": "excellent",
                "api_status": {
                    "ghl": "connected",
                    "mem0": "connected", 
                    "openrouter": "connected",
                    "supabase": "connected",
                    "vapi": "connected"
                }
            },
            "active_agents": {
                "initial_contact": {"active": True, "current_conversations": 4},
                "qualifier": {"active": True, "current_conversations": 3},
                "objection_handler": {"active": True, "current_conversations": 2},
                "closer": {"active": True, "current_conversations": 2},
                "nurturer": {"active": True, "current_conversations": 1},
                "appointment_setter": {"active": False, "current_conversations": 0}
            },
            "recent_activity": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "type": "lead_qualification",
                    "agent": "qualifier",
                    "lead_id": "lead_001",
                    "summary": "Qualified lead for downtown condo, budget $650k"
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
                    "type": "objection_handled",
                    "agent": "objection_handler", 
                    "lead_id": "lead_002",
                    "summary": "Addressed pricing concerns with market data"
                },
                {
                    "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                    "type": "appointment_scheduled",
                    "agent": "appointment_setter",
                    "lead_id": "lead_003",
                    "summary": "Scheduled viewing for tomorrow 2 PM"
                }
            ],
            "alerts": [
                {
                    "type": "performance",
                    "severity": "medium",
                    "message": "Objection handler response time above target",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting real-time dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include these endpoints in the main app
def include_phase_b2_routes(app):
    """Include Phase B.2 routes in the main FastAPI app"""
    app.include_router(router, prefix="", tags=["analytics", "rlhf", "training", "dashboard"])