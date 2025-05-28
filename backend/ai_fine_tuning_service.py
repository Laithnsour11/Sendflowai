import logging
import json
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import os

from fastapi import HTTPException

# Try different import strategies for database module
try:
    import database as db
except ImportError:
    try:
        from . import database as db
    except ImportError:
        try:
            from app.backend import database as db
        except ImportError:
            print("Warning: Could not import database module in AIFineTuningService")
            db = None

logger = logging.getLogger(__name__)

class FineTuningStatus(str, Enum):
    PENDING = "pending"
    PREPARING_DATA = "preparing_data"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ModelProvider(str, Enum):
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    ANTHROPIC = "anthropic"

class FeedbackType(str, Enum):
    RESPONSE_QUALITY = "response_quality"
    TONE_APPROPRIATENESS = "tone_appropriateness"
    INFORMATION_ACCURACY = "information_accuracy"
    CONVERSATION_FLOW = "conversation_flow"
    OBJECTION_HANDLING = "objection_handling"
    APPOINTMENT_SETTING = "appointment_setting"

class AIFineTuningService:
    """
    Advanced AI Fine-Tuning Service for continuous agent improvement
    
    Processes RLHF feedback data and manages fine-tuning jobs to improve
    AI agent performance based on real-world interactions.
    """
    
    def __init__(self):
        self.active_jobs = {}  # In-memory tracking for active fine-tuning jobs
        
        # Check if database is available
        if db is None:
            print("Warning: Database not available for AIFineTuningService")
        
        # Get API keys from environment
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
    async def create_fine_tuning_job(
        self,
        org_id: str,
        job_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new fine-tuning job based on collected RLHF data
        
        Args:
            org_id: Organization ID
            job_config: Fine-tuning job configuration
            
        Returns:
            Created fine-tuning job object
        """
        try:
            if db is None:
                raise HTTPException(status_code=503, detail="Database service not available")
            
            # Validate job configuration
            self._validate_job_config(job_config)
            
            # Create fine-tuning job document
            job = {
                "_id": str(uuid.uuid4()),
                "org_id": org_id,
                "job_name": job_config["job_name"],
                "description": job_config.get("description", ""),
                "status": FineTuningStatus.PENDING,
                
                # Model Configuration
                "model_config": {
                    "base_model": job_config["model_config"]["base_model"],
                    "provider": job_config["model_config"]["provider"],
                    "agent_type": job_config["model_config"].get("agent_type", "all"),
                    "target_capabilities": job_config["model_config"].get("target_capabilities", [])
                },
                
                # Training Configuration
                "training_config": {
                    "feedback_date_range": job_config["training_config"]["feedback_date_range"],
                    "feedback_types": job_config["training_config"].get("feedback_types", []),
                    "minimum_feedback_score": job_config["training_config"].get("minimum_feedback_score", 3),
                    "include_conversation_context": job_config["training_config"].get("include_conversation_context", True),
                    "training_epochs": job_config["training_config"].get("training_epochs", 3),
                    "learning_rate": job_config["training_config"].get("learning_rate", 0.0001)
                },
                
                # Data Processing Status
                "data_processing": {
                    "total_feedback_items": 0,
                    "processed_training_examples": 0,
                    "validation_examples": 0,
                    "data_quality_score": 0.0
                },
                
                # Training Progress
                "training_progress": {
                    "current_epoch": 0,
                    "total_epochs": job_config["training_config"].get("training_epochs", 3),
                    "loss": None,
                    "validation_loss": None,
                    "estimated_completion": None
                },
                
                # Model Deployment
                "deployment": {
                    "model_id": None,
                    "deployment_status": "not_deployed",
                    "performance_metrics": {},
                    "a_b_test_config": None
                },
                
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "started_at": None,
                "completed_at": None,
                "error_message": None
            }
            
            # Save job to database
            saved_job = await db.create_document(db.db.fine_tuning_jobs, job)
            
            logger.info(f"Created fine-tuning job {job['_id']} for org {org_id}")
            
            return saved_job
            
        except Exception as e:
            logger.error(f"Error creating fine-tuning job: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create fine-tuning job: {str(e)}")
    
    async def start_fine_tuning_job(
        self,
        org_id: str,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Start a fine-tuning job
        
        Args:
            org_id: Organization ID
            job_id: Fine-tuning job ID
            
        Returns:
            Updated job status
        """
        try:
            # Get job
            job = await db.get_document(db.db.fine_tuning_jobs, job_id)
            
            if not job or job["org_id"] != org_id:
                raise HTTPException(status_code=404, detail="Fine-tuning job not found")
            
            if job["status"] not in [FineTuningStatus.PENDING, FineTuningStatus.FAILED]:
                raise HTTPException(status_code=400, detail=f"Cannot start job in {job['status']} status")
            
            # Update job status
            await db.update_document(
                db.db.fine_tuning_jobs,
                job_id,
                {
                    "status": FineTuningStatus.PREPARING_DATA,
                    "started_at": datetime.now()
                }
            )
            
            # Start processing in background
            asyncio.create_task(self._process_fine_tuning_job(org_id, job_id))
            
            # Track in memory
            self.active_jobs[job_id] = {
                "org_id": org_id,
                "started_at": datetime.now(),
                "status": FineTuningStatus.PREPARING_DATA
            }
            
            logger.info(f"Started fine-tuning job {job_id}")
            
            return {
                "job_id": job_id,
                "status": FineTuningStatus.PREPARING_DATA,
                "message": "Fine-tuning job started successfully"
            }
            
        except Exception as e:
            logger.error(f"Error starting fine-tuning job {job_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to start fine-tuning job: {str(e)}")
    
    async def cancel_fine_tuning_job(
        self,
        org_id: str,
        job_id: str
    ) -> Dict[str, Any]:
        """Cancel a running fine-tuning job"""
        try:
            job = await db.get_document(db.db.fine_tuning_jobs, job_id)
            
            if not job or job["org_id"] != org_id:
                raise HTTPException(status_code=404, detail="Fine-tuning job not found")
            
            if job["status"] not in [FineTuningStatus.PREPARING_DATA, FineTuningStatus.TRAINING]:
                raise HTTPException(status_code=400, detail="Can only cancel running jobs")
            
            # Update job status
            await db.update_document(
                db.db.fine_tuning_jobs,
                job_id,
                {"status": FineTuningStatus.CANCELLED}
            )
            
            # Remove from active tracking
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
            
            logger.info(f"Cancelled fine-tuning job {job_id}")
            
            return {
                "job_id": job_id,
                "status": FineTuningStatus.CANCELLED,
                "message": "Fine-tuning job cancelled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling fine-tuning job {job_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to cancel fine-tuning job: {str(e)}")
    
    async def get_job_status(
        self,
        org_id: str,
        job_id: str
    ) -> Dict[str, Any]:
        """Get detailed fine-tuning job status"""
        try:
            job = await db.get_document(db.db.fine_tuning_jobs, job_id)
            
            if not job or job["org_id"] != org_id:
                raise HTTPException(status_code=404, detail="Fine-tuning job not found")
            
            # Get training examples if available
            training_examples = await self._get_job_training_examples(job_id, limit=5)
            
            return {
                "job": job,
                "is_running": job_id in self.active_jobs,
                "sample_training_examples": training_examples
            }
            
        except Exception as e:
            logger.error(f"Error getting job status {job_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")
    
    async def list_fine_tuning_jobs(
        self,
        org_id: str,
        status_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List fine-tuning jobs for an organization"""
        try:
            filter_criteria = {"org_id": org_id}
            
            if status_filter:
                filter_criteria["status"] = status_filter
            
            jobs = await db.list_documents(
                db.db.fine_tuning_jobs,
                filter_criteria=filter_criteria,
                limit=limit,
                sort_by=[("created_at", -1)]
            )
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error listing fine-tuning jobs for org {org_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list fine-tuning jobs: {str(e)}")
    
    async def deploy_fine_tuned_model(
        self,
        org_id: str,
        job_id: str,
        deployment_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy a completed fine-tuned model"""
        try:
            job = await db.get_document(db.db.fine_tuning_jobs, job_id)
            
            if not job or job["org_id"] != org_id:
                raise HTTPException(status_code=404, detail="Fine-tuning job not found")
            
            if job["status"] != FineTuningStatus.COMPLETED:
                raise HTTPException(status_code=400, detail="Can only deploy completed models")
            
            # Update deployment configuration
            deployment_data = {
                "deployment.deployment_status": "deploying",
                "deployment.a_b_test_config": deployment_config.get("a_b_test_config"),
                "updated_at": datetime.now()
            }
            
            await db.update_document(db.db.fine_tuning_jobs, job_id, deployment_data)
            
            # Simulate deployment (in production, this would deploy to the model provider)
            asyncio.create_task(self._simulate_model_deployment(job_id))
            
            logger.info(f"Started deployment for fine-tuned model {job_id}")
            
            return {
                "job_id": job_id,
                "deployment_status": "deploying",
                "message": "Model deployment started"
            }
            
        except Exception as e:
            logger.error(f"Error deploying model {job_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to deploy model: {str(e)}")
    
    async def get_rlhf_analytics(
        self,
        org_id: str,
        date_range: Dict[str, str],
        agent_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get analytics on RLHF feedback data for fine-tuning insights"""
        try:
            # Parse date range
            start_date = datetime.fromisoformat(date_range["start_date"])
            end_date = datetime.fromisoformat(date_range["end_date"])
            
            # Build filter criteria
            filter_criteria = {
                "org_id": org_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            if agent_type:
                filter_criteria["agent_type"] = agent_type
            
            # Get RLHF feedback data
            feedback_data = await db.list_documents(
                db.db.rlhf_feedback,
                filter_criteria=filter_criteria,
                limit=1000
            )
            
            # Analyze feedback
            analytics = self._analyze_rlhf_feedback(feedback_data)
            
            return {
                "date_range": date_range,
                "agent_type": agent_type,
                "total_feedback_items": len(feedback_data),
                "analytics": analytics,
                "recommendations": self._generate_training_recommendations(analytics)
            }
            
        except Exception as e:
            logger.error(f"Error getting RLHF analytics: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get RLHF analytics: {str(e)}")
    
    def _validate_job_config(self, job_config: Dict[str, Any]) -> None:
        """Validate fine-tuning job configuration"""
        required_fields = ["job_name", "model_config", "training_config"]
        
        for field in required_fields:
            if field not in job_config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate model config
        model_config = job_config["model_config"]
        if "base_model" not in model_config or "provider" not in model_config:
            raise ValueError("Model config must include base_model and provider")
        
        # Validate provider
        if model_config["provider"] not in [p.value for p in ModelProvider]:
            raise ValueError(f"Invalid provider: {model_config['provider']}")
        
        # Validate training config
        training_config = job_config["training_config"]
        if "feedback_date_range" not in training_config:
            raise ValueError("Training config must include feedback_date_range")
    
    async def _process_fine_tuning_job(
        self,
        org_id: str,
        job_id: str
    ) -> None:
        """Background task to process fine-tuning job"""
        try:
            logger.info(f"Starting fine-tuning job processing for {job_id}")
            
            # Get job details
            job = await db.get_document(db.db.fine_tuning_jobs, job_id)
            
            if not job:
                return
            
            # Step 1: Prepare training data
            await self._prepare_training_data(job_id, job)
            
            # Step 2: Start training
            await self._start_model_training(job_id, job)
            
            # Step 3: Monitor training progress
            await self._monitor_training_progress(job_id, job)
            
            logger.info(f"Completed fine-tuning job processing for {job_id}")
            
        except Exception as e:
            logger.error(f"Error in fine-tuning job processing: {e}")
            
            # Mark job as failed
            await db.update_document(
                db.db.fine_tuning_jobs,
                job_id,
                {
                    "status": FineTuningStatus.FAILED,
                    "error_message": str(e),
                    "updated_at": datetime.now()
                }
            )
            
            # Remove from active tracking
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
    
    async def _prepare_training_data(
        self,
        job_id: str,
        job: Dict[str, Any]
    ) -> None:
        """Prepare training data from RLHF feedback"""
        try:
            # Update status
            await db.update_document(
                db.db.fine_tuning_jobs,
                job_id,
                {"status": FineTuningStatus.PREPARING_DATA}
            )
            
            # Get RLHF feedback data based on job configuration
            feedback_data = await self._collect_rlhf_data(job)
            
            # Process feedback into training examples
            training_examples = await self._convert_feedback_to_training_data(feedback_data, job)
            
            # Store training examples
            for example in training_examples:
                example["job_id"] = job_id
                await db.create_document(db.db.training_examples, example)
            
            # Update job with data processing results
            await db.update_document(
                db.db.fine_tuning_jobs,
                job_id,
                {
                    "data_processing.total_feedback_items": len(feedback_data),
                    "data_processing.processed_training_examples": len(training_examples),
                    "data_processing.validation_examples": max(1, len(training_examples) // 10),  # 10% for validation
                    "data_processing.data_quality_score": self._calculate_data_quality_score(training_examples),
                    "updated_at": datetime.now()
                }
            )
            
            logger.info(f"Prepared {len(training_examples)} training examples for job {job_id}")
            
        except Exception as e:
            logger.error(f"Error preparing training data for job {job_id}: {e}")
            raise
    
    async def _start_model_training(
        self,
        job_id: str,
        job: Dict[str, Any]
    ) -> None:
        """Start the actual model training process"""
        try:
            # Update status
            await db.update_document(
                db.db.fine_tuning_jobs,
                job_id,
                {
                    "status": FineTuningStatus.TRAINING,
                    "training_progress.current_epoch": 0,
                    "updated_at": datetime.now()
                }
            )
            
            # In production, this would initiate training with the model provider
            # For MVP, we simulate the training process
            logger.info(f"Started model training for job {job_id}")
            
        except Exception as e:
            logger.error(f"Error starting model training for job {job_id}: {e}")
            raise
    
    async def _monitor_training_progress(
        self,
        job_id: str,
        job: Dict[str, Any]
    ) -> None:
        """Monitor training progress and update job status"""
        try:
            total_epochs = job["training_config"]["training_epochs"]
            
            # Simulate training progress
            for epoch in range(1, total_epochs + 1):
                # Simulate training time
                await asyncio.sleep(2)  # 2 seconds per epoch for demo
                
                # Simulate loss calculation
                loss = 1.0 - (epoch / total_epochs) * 0.8  # Decreasing loss
                validation_loss = loss + 0.1  # Slightly higher validation loss
                
                # Update progress
                await db.update_document(
                    db.db.fine_tuning_jobs,
                    job_id,
                    {
                        "training_progress.current_epoch": epoch,
                        "training_progress.loss": loss,
                        "training_progress.validation_loss": validation_loss,
                        "updated_at": datetime.now()
                    }
                )
                
                logger.info(f"Job {job_id} - Epoch {epoch}/{total_epochs}, Loss: {loss:.4f}")
            
            # Mark as completed
            await db.update_document(
                db.db.fine_tuning_jobs,
                job_id,
                {
                    "status": FineTuningStatus.COMPLETED,
                    "completed_at": datetime.now(),
                    "deployment.model_id": f"fine_tuned_model_{job_id[:8]}",
                    "updated_at": datetime.now()
                }
            )
            
            # Remove from active tracking
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]
            
            logger.info(f"Completed training for job {job_id}")
            
        except Exception as e:
            logger.error(f"Error monitoring training progress for job {job_id}: {e}")
            raise
    
    async def _collect_rlhf_data(self, job: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect RLHF feedback data based on job configuration"""
        try:
            training_config = job["training_config"]
            date_range = training_config["feedback_date_range"]
            
            # Parse dates
            start_date = datetime.fromisoformat(date_range["start"])
            end_date = datetime.fromisoformat(date_range["end"])
            
            # Build filter criteria
            filter_criteria = {
                "org_id": job["org_id"],
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            # Add feedback type filter if specified
            if training_config.get("feedback_types"):
                filter_criteria["feedback_type"] = {"$in": training_config["feedback_types"]}
            
            # Add minimum score filter
            if training_config.get("minimum_feedback_score"):
                filter_criteria["score"] = {"$gte": training_config["minimum_feedback_score"]}
            
            # Get feedback data
            feedback_data = await db.list_documents(
                db.db.rlhf_feedback,
                filter_criteria=filter_criteria,
                limit=1000
            )
            
            return feedback_data
            
        except Exception as e:
            logger.error(f"Error collecting RLHF data: {e}")
            return []
    
    async def _convert_feedback_to_training_data(
        self,
        feedback_data: List[Dict[str, Any]],
        job: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert RLHF feedback to training examples"""
        training_examples = []
        
        for feedback in feedback_data:
            try:
                # Create training example based on feedback
                example = {
                    "_id": str(uuid.uuid4()),
                    "input": feedback.get("original_message", ""),
                    "output": feedback.get("improved_response", feedback.get("agent_response", "")),
                    "score": feedback.get("score", 3),
                    "feedback_type": feedback.get("feedback_type", "general"),
                    "context": feedback.get("context", {}),
                    "agent_type": feedback.get("agent_type", "general"),
                    "created_at": datetime.now()
                }
                
                # Only include examples with sufficient quality
                if example["score"] >= job["training_config"].get("minimum_feedback_score", 3):
                    training_examples.append(example)
                    
            except Exception as e:
                logger.error(f"Error converting feedback to training example: {e}")
                continue
        
        return training_examples
    
    def _calculate_data_quality_score(self, training_examples: List[Dict[str, Any]]) -> float:
        """Calculate a quality score for the training data"""
        if not training_examples:
            return 0.0
        
        total_score = sum(example.get("score", 0) for example in training_examples)
        average_score = total_score / len(training_examples)
        
        # Normalize to 0-1 scale (assuming scores are 1-5)
        quality_score = (average_score - 1) / 4
        
        return min(1.0, max(0.0, quality_score))
    
    async def _simulate_model_deployment(self, job_id: str) -> None:
        """Simulate model deployment process"""
        try:
            # Simulate deployment time
            await asyncio.sleep(5)
            
            # Update deployment status
            await db.update_document(
                db.db.fine_tuning_jobs,
                job_id,
                {
                    "deployment.deployment_status": "deployed",
                    "deployment.performance_metrics": {
                        "response_quality_improvement": 0.15,
                        "user_satisfaction_increase": 0.12,
                        "conversion_rate_improvement": 0.08
                    },
                    "updated_at": datetime.now()
                }
            )
            
            logger.info(f"Model deployment completed for job {job_id}")
            
        except Exception as e:
            logger.error(f"Error in model deployment simulation: {e}")
    
    async def _get_job_training_examples(
        self,
        job_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get sample training examples for a job"""
        try:
            examples = await db.list_documents(
                db.db.training_examples,
                filter_criteria={"job_id": job_id},
                limit=limit,
                sort_by=[("created_at", -1)]
            )
            
            return examples
            
        except Exception as e:
            logger.error(f"Error getting training examples: {e}")
            return []
    
    def _analyze_rlhf_feedback(self, feedback_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze RLHF feedback data for insights"""
        if not feedback_data:
            return {}
        
        # Analyze by feedback type
        feedback_by_type = {}
        for feedback in feedback_data:
            feedback_type = feedback.get("feedback_type", "general")
            if feedback_type not in feedback_by_type:
                feedback_by_type[feedback_type] = []
            feedback_by_type[feedback_type].append(feedback.get("score", 3))
        
        # Calculate averages by type
        avg_scores_by_type = {}
        for feedback_type, scores in feedback_by_type.items():
            avg_scores_by_type[feedback_type] = sum(scores) / len(scores)
        
        # Analyze by agent type
        feedback_by_agent = {}
        for feedback in feedback_data:
            agent_type = feedback.get("agent_type", "general")
            if agent_type not in feedback_by_agent:
                feedback_by_agent[agent_type] = []
            feedback_by_agent[agent_type].append(feedback.get("score", 3))
        
        avg_scores_by_agent = {}
        for agent_type, scores in feedback_by_agent.items():
            avg_scores_by_agent[agent_type] = sum(scores) / len(scores)
        
        return {
            "average_scores_by_feedback_type": avg_scores_by_type,
            "average_scores_by_agent_type": avg_scores_by_agent,
            "overall_average_score": sum(f.get("score", 3) for f in feedback_data) / len(feedback_data),
            "total_feedback_items": len(feedback_data),
            "feedback_distribution": feedback_by_type
        }
    
    def _generate_training_recommendations(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on RLHF analytics"""
        recommendations = []
        
        overall_avg = analytics.get("overall_average_score", 3.0)
        
        if overall_avg < 3.0:
            recommendations.append("Consider reviewing agent prompts and responses - overall quality is below average")
        
        # Check specific feedback types
        feedback_scores = analytics.get("average_scores_by_feedback_type", {})
        
        for feedback_type, score in feedback_scores.items():
            if score < 2.5:
                recommendations.append(f"Focus on improving {feedback_type.replace('_', ' ')} - current score: {score:.2f}")
        
        # Check agent types
        agent_scores = analytics.get("average_scores_by_agent_type", {})
        
        for agent_type, score in agent_scores.items():
            if score < 2.5:
                recommendations.append(f"Consider fine-tuning the {agent_type.replace('_', ' ')} agent - current score: {score:.2f}")
        
        if not recommendations:
            recommendations.append("Overall performance is good - consider fine-tuning to further enhance capabilities")
        
        return recommendations