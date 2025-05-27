import logging
import json
import httpx
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import os
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class SendBlueIntegration:
    """Integration with SendBlue for SMS/MMS capabilities"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.sendblue.co/api"
        self.headers = {}
        
        if self.api_key and self.api_secret:
            self.headers = {
                "sb-api-key-id": self.api_key,
                "sb-api-secret-key": self.api_secret,
                "Content-Type": "application/json"
            }
    
    def set_credentials(self, api_key: str, api_secret: str):
        """Set the SendBlue API credentials and update headers"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "sb-api-key-id": self.api_key,
            "sb-api-secret-key": self.api_secret,
            "Content-Type": "application/json"
        }
    
    async def validate_credentials(self) -> bool:
        """Validate the API credentials by making a test request"""
        if not self.api_key or not self.api_secret:
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
            logger.error(f"Failed to validate SendBlue API credentials: {e}")
            return False
    
    async def send_sms(
        self, 
        to_number: str, 
        message: str,
        from_number: Optional[str] = None,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS/MMS message
        
        Args:
            to_number: The recipient's phone number
            message: The message content
            from_number: Optional sender phone number (if account has multiple numbers)
            media_urls: Optional list of media URLs for MMS
            
        Returns:
            Dict containing the message information
        """
        if not self.api_key or not self.api_secret:
            logger.warning("SendBlue API credentials not set, cannot send SMS")
            raise ValueError("SendBlue API credentials not configured")
        
        # Create message payload
        payload = {
            "to": to_number,
            "body": message
        }
        
        # Add from_number if provided
        if from_number:
            payload["from"] = from_number
        
        # Add media_urls if provided for MMS
        if media_urls and len(media_urls) > 0:
            payload["mediaUrls"] = media_urls
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/send",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error sending SMS with SendBlue: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send SMS with SendBlue: {str(e)}")
    
    async def send_sms_with_intelligent_cadence(
        self,
        to_number: str,
        messages: List[str],
        delay_seconds: int = 2,
        from_number: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Send multiple SMS messages with intelligent cadence
        
        Args:
            to_number: The recipient's phone number
            messages: List of message content
            delay_seconds: Delay between messages in seconds
            from_number: Optional sender phone number (if account has multiple numbers)
            
        Returns:
            List of Dicts containing message information
        """
        if not self.api_key or not self.api_secret:
            logger.warning("SendBlue API credentials not set, cannot send SMS")
            raise ValueError("SendBlue API credentials not configured")
        
        results = []
        
        for i, message in enumerate(messages):
            try:
                # Create message payload
                payload = {
                    "to": to_number,
                    "body": message,
                    "delaySeconds": delay_seconds * i  # Increasing delay for cadence
                }
                
                # Add from_number if provided
                if from_number:
                    payload["from"] = from_number
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/v1/send",
                        headers=self.headers,
                        json=payload,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    results.append(response.json())
                    
            except Exception as e:
                logger.error(f"Error sending SMS with SendBlue (message {i+1}): {e}")
                results.append({
                    "error": str(e),
                    "message_index": i,
                    "message": message
                })
        
        return results
    
    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        Get information about a message
        
        Args:
            message_id: The ID of the message
            
        Returns:
            Dict containing message information
        """
        if not self.api_key or not self.api_secret:
            logger.warning("SendBlue API credentials not set, cannot get message")
            raise ValueError("SendBlue API credentials not configured")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/messages/{message_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error getting message from SendBlue: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get message from SendBlue: {str(e)}")
    
    def process_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a webhook event from SendBlue
        
        Args:
            event: The webhook event data
            
        Returns:
            Dict containing processed event information
        """
        event_type = event.get("type")
        
        if not event_type:
            logger.error("Invalid webhook event: missing type")
            raise ValueError("Invalid webhook event: missing type")
        
        # Process different event types
        if event_type == "message.received":
            return self._process_message_received(event)
        elif event_type == "message.sent":
            return self._process_message_sent(event)
        elif event_type == "message.delivered":
            return self._process_message_delivered(event)
        elif event_type == "message.failed":
            return self._process_message_failed(event)
        else:
            logger.warning(f"Unhandled webhook event type: {event_type}")
            return {
                "event_type": event_type,
                "processed": False,
                "reason": "Unknown event type"
            }
    
    def _process_message_received(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process message.received event"""
        message_data = event.get("data", {})
        
        return {
            "event_type": "message_received",
            "message_id": message_data.get("id"),
            "from_number": message_data.get("from"),
            "to_number": message_data.get("to"),
            "body": message_data.get("body"),
            "media_urls": message_data.get("mediaUrls", []),
            "timestamp": message_data.get("createdAt", datetime.now().isoformat()),
            "processed": True
        }
    
    def _process_message_sent(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process message.sent event"""
        message_data = event.get("data", {})
        
        return {
            "event_type": "message_sent",
            "message_id": message_data.get("id"),
            "from_number": message_data.get("from"),
            "to_number": message_data.get("to"),
            "body": message_data.get("body"),
            "media_urls": message_data.get("mediaUrls", []),
            "timestamp": message_data.get("createdAt", datetime.now().isoformat()),
            "processed": True
        }
    
    def _process_message_delivered(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process message.delivered event"""
        message_data = event.get("data", {})
        
        return {
            "event_type": "message_delivered",
            "message_id": message_data.get("id"),
            "from_number": message_data.get("from"),
            "to_number": message_data.get("to"),
            "body": message_data.get("body"),
            "delivered_at": message_data.get("deliveredAt", datetime.now().isoformat()),
            "processed": True
        }
    
    def _process_message_failed(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process message.failed event"""
        message_data = event.get("data", {})
        
        return {
            "event_type": "message_failed",
            "message_id": message_data.get("id"),
            "from_number": message_data.get("from"),
            "to_number": message_data.get("to"),
            "body": message_data.get("body"),
            "error": message_data.get("error"),
            "timestamp": message_data.get("createdAt", datetime.now().isoformat()),
            "processed": True
        }
    
    async def determine_intelligent_cadence(
        self, 
        message: str,
        openai_api_key: Optional[str] = None
    ) -> List[str]:
        """
        Determine intelligent cadence for a message
        
        Args:
            message: The full message content
            openai_api_key: Optional OpenAI API key for analysis
            
        Returns:
            List of message segments with appropriate cadence
        """
        # For MVP, use a simplified approach without LLM
        # In a real implementation, we would use OpenAI or another AI service
        
        # Split long messages
        if len(message) <= 160:
            # Short message, no need to split
            return [message]
        
        # Simple sentence-based splitting for longer messages
        sentences = message.replace('!', '.').replace('?', '.').split('.')
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would make the segment too long, start a new segment
            if len(current_segment) + len(sentence) + 2 > 160:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence + ". "
            else:
                current_segment += sentence + ". "
        
        # Add the last segment if not empty
        if current_segment:
            segments.append(current_segment.strip())
        
        # Ensure we have at least one segment
        if not segments:
            segments = [message]
        
        return segments
