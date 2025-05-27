import logging
import json
import httpx
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import os
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class VapiIntegration:
    """Integration with Vapi.ai for voice capabilities"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.vapi.ai"
        self.headers = {}
        
        if self.api_key:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def set_api_key(self, api_key: str):
        """Set the Vapi API key and update headers"""
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def validate_key(self) -> bool:
        """Validate the API key by making a test request"""
        if not self.api_key:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/account",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to validate Vapi API key: {e}")
            return False
    
    async def create_call(
        self, 
        phone_number: str, 
        assistant_config: Dict[str, Any],
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new outgoing call
        
        Args:
            phone_number: The phone number to call
            assistant_config: Configuration for the assistant
            webhook_url: Optional webhook URL for call events
            
        Returns:
            Dict containing the call information
        """
        if not self.api_key:
            logger.warning("Vapi API key not set, cannot create call")
            raise ValueError("Vapi API key not configured")
        
        # Default configuration
        default_config = {
            "firstMessage": "Hello, this is AI Closer. I'm calling about your real estate inquiry. How are you today?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.7,
                "systemPrompt": "You are a professional real estate agent assistant. Be friendly, helpful, and concise. Your goal is to qualify the lead and understand their needs.",
                "functions": []
            },
            "voice": {
                "provider": "elevenlabs",
                "voiceId": "11labs_amy",
                "stability": 0.7,
                "similarityBoost": 0.7
            },
            "recordingEnabled": True,
            "transcriptEnabled": True,
            "endCallFunctionEnabled": True,
            "maxDurationSeconds": 300,
            "responseDelaySeconds": 0.5,
            "silenceTimeoutSeconds": 10
        }
        
        # Merge with provided configuration
        config = {**default_config, **assistant_config}
        
        # Create call payload
        payload = {
            "phoneNumber": phone_number,
            "firstMessage": config["firstMessage"],
            "model": config["model"],
            "voice": config["voice"],
            "recordingEnabled": config["recordingEnabled"],
            "transcriptEnabled": config["transcriptEnabled"],
            "endCallFunctionEnabled": config["endCallFunctionEnabled"],
            "maxDurationSeconds": config["maxDurationSeconds"],
            "responseDelaySeconds": config["responseDelaySeconds"],
            "silenceTimeoutSeconds": config["silenceTimeoutSeconds"]
        }
        
        # Add webhook URL if provided
        if webhook_url:
            payload["serverUrl"] = webhook_url
            # In a real implementation, we would also add a server URL secret for security
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/calls",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error creating call with Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create call with Vapi: {str(e)}")
    
    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """
        Get information about a call
        
        Args:
            call_id: The ID of the call
            
        Returns:
            Dict containing call information
        """
        if not self.api_key:
            logger.warning("Vapi API key not set, cannot get call")
            raise ValueError("Vapi API key not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/calls/{call_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting call from Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get call from Vapi: {str(e)}")
    
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """
        End an active call
        
        Args:
            call_id: The ID of the call to end
            
        Returns:
            Dict containing the result
        """
        if not self.api_key:
            logger.warning("Vapi API key not set, cannot end call")
            raise ValueError("Vapi API key not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/calls/{call_id}/end",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error ending call with Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to end call with Vapi: {str(e)}")
    
    async def get_recording(self, call_id: str) -> Dict[str, Any]:
        """
        Get recording URL for a completed call
        
        Args:
            call_id: The ID of the call
            
        Returns:
            Dict containing recording information
        """
        if not self.api_key:
            logger.warning("Vapi API key not set, cannot get recording")
            raise ValueError("Vapi API key not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/calls/{call_id}/recording",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting recording from Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get recording from Vapi: {str(e)}")
    
    async def get_transcript(self, call_id: str) -> Dict[str, Any]:
        """
        Get transcript for a completed call
        
        Args:
            call_id: The ID of the call
            
        Returns:
            Dict containing transcript information
        """
        if not self.api_key:
            logger.warning("Vapi API key not set, cannot get transcript")
            raise ValueError("Vapi API key not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/calls/{call_id}/transcript",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting transcript from Vapi: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get transcript from Vapi: {str(e)}")
    
    def process_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a webhook event from Vapi
        
        Args:
            event: The webhook event data
            
        Returns:
            Dict containing processed event information
        """
        event_type = event.get("type")
        call_id = event.get("callId")
        
        if not event_type or not call_id:
            logger.error("Invalid webhook event: missing type or callId")
            raise ValueError("Invalid webhook event: missing type or callId")
        
        # Process different event types
        if event_type == "call-started":
            return self._process_call_started(event)
        elif event_type == "speech-update":
            return self._process_speech_update(event)
        elif event_type == "function-call":
            return self._process_function_call(event)
        elif event_type == "conversation-update":
            return self._process_conversation_update(event)
        elif event_type == "call-ended":
            return self._process_call_ended(event)
        elif event_type == "end-of-call-report":
            return self._process_end_of_call_report(event)
        else:
            logger.warning(f"Unhandled webhook event type: {event_type}")
            return {
                "event_type": event_type,
                "call_id": call_id,
                "processed": False,
                "reason": "Unknown event type"
            }
    
    def _process_call_started(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process call-started event"""
        return {
            "event_type": "call-started",
            "call_id": event.get("callId"),
            "phone_number": event.get("phoneNumber"),
            "direction": event.get("direction", "outbound"),
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
            "processed": True
        }
    
    def _process_speech_update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process speech-update event"""
        return {
            "event_type": "speech-update",
            "call_id": event.get("callId"),
            "role": event.get("role"),
            "transcript": event.get("transcript"),
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
            "processed": True
        }
    
    def _process_function_call(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process function-call event"""
        function_call = event.get("functionCall", {})
        
        return {
            "event_type": "function-call",
            "call_id": event.get("callId"),
            "function_name": function_call.get("name"),
            "function_arguments": function_call.get("arguments"),
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
            "processed": True
        }
    
    def _process_conversation_update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process conversation-update event"""
        return {
            "event_type": "conversation-update",
            "call_id": event.get("callId"),
            "messages": event.get("messages", []),
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
            "processed": True
        }
    
    def _process_call_ended(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process call-ended event"""
        return {
            "event_type": "call-ended",
            "call_id": event.get("callId"),
            "reason": event.get("reason"),
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
            "processed": True
        }
    
    def _process_end_of_call_report(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process end-of-call-report event"""
        return {
            "event_type": "end-of-call-report",
            "call_id": event.get("callId"),
            "summary": event.get("summary"),
            "action_items": event.get("actionItems", []),
            "transcript": event.get("transcript"),
            "recording_url": event.get("recordingUrl"),
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
            "processed": True
        }
    
    async def analyze_call(self, call_id: str, openai_api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a completed call using AI
        
        Args:
            call_id: The ID of the call
            openai_api_key: Optional OpenAI API key for analysis
            
        Returns:
            Dict containing call analysis
        """
        try:
            # Get call transcript
            transcript_data = await self.get_transcript(call_id)
            transcript = transcript_data.get("transcript", "")
            
            if not transcript:
                return {
                    "call_id": call_id,
                    "analysis": {
                        "error": "No transcript available for analysis"
                    }
                }
            
            # For MVP, return a simple analysis
            # In a real implementation, we would use OpenAI or another AI service for analysis
            analysis = {
                "call_id": call_id,
                "sentiment": "positive" if "thank you" in transcript.lower() or "appreciate" in transcript.lower() else "neutral",
                "key_topics": self._extract_key_topics(transcript),
                "next_best_action": self._determine_next_action(transcript),
                "transcript_summary": self._summarize_transcript(transcript)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing call: {e}")
            return {
                "call_id": call_id,
                "analysis": {
                    "error": f"Failed to analyze call: {str(e)}"
                }
            }
    
    def _extract_key_topics(self, transcript: str) -> List[str]:
        """Extract key topics from transcript (simplified for MVP)"""
        topics = []
        
        # Simple keyword-based topic extraction
        if "price" in transcript.lower() or "cost" in transcript.lower() or "budget" in transcript.lower():
            topics.append("Budget/Price")
        
        if "bedroom" in transcript.lower() or "bathroom" in transcript.lower() or "square foot" in transcript.lower():
            topics.append("Property Features")
        
        if "location" in transcript.lower() or "neighborhood" in transcript.lower() or "area" in transcript.lower():
            topics.append("Location/Neighborhood")
        
        if "mortgage" in transcript.lower() or "loan" in transcript.lower() or "financing" in transcript.lower():
            topics.append("Financing")
        
        if "timeframe" in transcript.lower() or "when" in transcript.lower() or "timeline" in transcript.lower():
            topics.append("Timeline")
        
        # Default if no topics detected
        if not topics:
            topics.append("General Inquiry")
        
        return topics
    
    def _determine_next_action(self, transcript: str) -> str:
        """Determine next best action (simplified for MVP)"""
        transcript_lower = transcript.lower()
        
        if "see the property" in transcript_lower or "tour" in transcript_lower or "visit" in transcript_lower:
            return "Schedule property showing"
        
        if "more information" in transcript_lower or "details" in transcript_lower:
            return "Send property information"
        
        if "call back" in transcript_lower or "later" in transcript_lower:
            return "Schedule follow-up call"
        
        if "not interested" in transcript_lower or "don't call" in transcript_lower:
            return "Mark as not interested"
        
        # Default next action
        return "Follow up with more property options"
    
    def _summarize_transcript(self, transcript: str) -> str:
        """Summarize transcript (simplified for MVP)"""
        # In a real implementation, we would use AI for summarization
        # For MVP, just return a shortened version
        if len(transcript) > 500:
            return transcript[:500] + "..."
        return transcript
