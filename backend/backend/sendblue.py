import os
import json
import logging
import httpx
import time
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)

class SendBlueIntegration:
    """
    Implements full integration with SendBlue for SMS/MMS communications
    Supports intelligent message cadence and webhook handling
    """
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.sendblue.co/api"
        self.headers = {}
        self.update_headers()
    
    def set_api_credentials(self, api_key: str, api_secret: str):
        """Set the SendBlue API credentials"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.update_headers()
        
    def update_headers(self):
        """Update the headers with the current API credentials"""
        if self.api_key and self.api_secret:
            self.headers = {
                "Content-Type": "application/json",
                "sb-api-key-id": self.api_key,
                "sb-api-secret-key": self.api_secret
            }
    
    def is_configured(self) -> bool:
        """Check if the SendBlue integration is configured with valid API credentials"""
        return bool(self.api_key and self.api_secret)
    
    async def validate_credentials(self) -> bool:
        """Validate that the API credentials are correct by making a simple API call"""
        if not self.is_configured():
            return False
            
        try:
            # Try to list phone numbers as a simple validation
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/number/list",
                    headers=self.headers
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error validating SendBlue API credentials: {e}")
            return False
    
    async def list_phone_numbers(self) -> List[Dict[str, Any]]:
        """List all phone numbers in the SendBlue account"""
        if not self.is_configured():
            logger.error("SendBlue API credentials not configured")
            raise HTTPException(status_code=400, detail="SendBlue API credentials not configured")
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/number/list",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json().get("data", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while listing phone numbers: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"SendBlue API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error listing phone numbers from SendBlue: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with SendBlue: {str(e)}")
    
    async def send_message(
        self, 
        to_number: str, 
        message: str,
        from_number: Optional[str] = None,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send a single message via SendBlue
        
        Args:
            to_number: The phone number to send to
            message: The message content
            from_number: The phone number to send from (optional)
            media_urls: List of media URLs to include (optional)
            
        Returns:
            Dict containing the send result
        """
        if not self.is_configured():
            logger.error("SendBlue API credentials not configured")
            raise HTTPException(status_code=400, detail="SendBlue API credentials not configured")
            
        # If no from_number provided, get the first available number
        if not from_number:
            numbers = await self.list_phone_numbers()
            if not numbers:
                raise HTTPException(status_code=400, detail="No phone numbers available in SendBlue account")
            from_number = numbers[0].get("phone_number")
        
        try:
            payload = {
                "number_from": from_number,
                "number_to": to_number,
                "body": message,
                "status_callback": ""  # Would be configured in a production environment
            }
            
            # Add media URLs if provided
            if media_urls:
                payload["media_urls"] = media_urls
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/send",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while sending message: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"SendBlue API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error sending message via SendBlue: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with SendBlue: {str(e)}")
    
    async def send_multi_part_message(
        self,
        to_number: str,
        messages: List[Dict[str, Any]],
        from_number: Optional[str] = None,
        base_delay: int = 2,  # Base delay in seconds
        agent_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a multi-part message with intelligent cadence
        
        Args:
            to_number: The phone number to send to
            messages: List of message parts with content and optional media
            from_number: The phone number to send from (optional)
            base_delay: Base delay between messages in seconds
            agent_config: Configuration for the AI agent (for customizing cadence)
            
        Returns:
            Dict containing the send results
        """
        if not self.is_configured():
            logger.error("SendBlue API credentials not configured")
            raise HTTPException(status_code=400, detail="SendBlue API credentials not configured")
        
        results = []
        
        # Calculate intelligent delays
        delays = self._calculate_message_cadence(messages, base_delay, agent_config)
        
        for i, message in enumerate(messages):
            try:
                # Send the message
                result = await self.send_message(
                    to_number=to_number,
                    message=message["content"],
                    from_number=from_number,
                    media_urls=message.get("media_urls")
                )
                
                results.append({
                    "part": i + 1,
                    "content": message["content"],
                    "result": result,
                    "sent_at": datetime.now().isoformat()
                })
                
                # Wait the calculated delay before sending the next message
                # Skip delay after the last message
                if i < len(messages) - 1:
                    # Get the delay for this message
                    delay = delays[i]
                    logger.info(f"Waiting {delay}s before sending next message part")
                    time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error sending message part {i+1}: {e}")
                results.append({
                    "part": i + 1,
                    "content": message["content"],
                    "error": str(e),
                    "sent_at": datetime.now().isoformat()
                })
                # Continue to next message despite error
        
        return {
            "to_number": to_number,
            "from_number": from_number,
            "message_count": len(messages),
            "successful_sends": len([r for r in results if "error" not in r]),
            "results": results,
            "completed_at": datetime.now().isoformat()
        }
    
    def _calculate_message_cadence(
        self,
        messages: List[Dict[str, Any]],
        base_delay: int,
        agent_config: Optional[Dict[str, Any]] = None
    ) -> List[int]:
        """
        Calculate intelligent delays between messages based on content
        
        Args:
            messages: List of message parts
            base_delay: Base delay between messages in seconds
            agent_config: Configuration for the AI agent
            
        Returns:
            List of delays in seconds between messages
        """
        delays = []
        
        for i, message in enumerate(messages):
            if i >= len(messages) - 1:
                continue  # No delay needed after the last message
                
            # Get the current and next message
            current_msg = message["content"]
            next_msg = messages[i + 1]["content"]
            
            # Calculate delay based on message length and content
            delay = base_delay
            
            # 1. Adjust based on current message length
            current_length = len(current_msg)
            if current_length > 100:
                delay += 2  # Add more time for longer messages
            elif current_length < 20:
                delay -= 1  # Reduce time for very short messages
            
            # 2. Adjust based on content
            # If the message ends with a question, add delay for "thinking"
            if current_msg.rstrip().endswith("?"):
                delay += 3
            
            # If the next message is a new thought/topic, add more delay
            if self._is_new_thought(current_msg, next_msg):
                delay += 2
            
            # 3. Adjust for emotional content
            if "!" in current_msg:
                delay += 1  # Slight pause after excited messages
            
            # 4. Ensure minimum delay
            delay = max(delay, 1)
            
            # Add any agent-specific adjustments
            if agent_config and "cadence_multiplier" in agent_config:
                delay = delay * agent_config["cadence_multiplier"]
            
            delays.append(int(delay))
        
        return delays
    
    def _is_new_thought(self, current_msg: str, next_msg: str) -> bool:
        """Determine if the next message is a new thought/topic"""
        # Check if the next message starts with a transition phrase
        transition_starters = [
            "anyway", "by the way", "on another note", 
            "speaking of", "also", "oh", "actually"
        ]
        
        next_lower = next_msg.lower().strip()
        
        for starter in transition_starters:
            if next_lower.startswith(starter):
                return True
        
        # Check if there's low semantic similarity between messages
        # In a real implementation, this could use embedding similarity
        # For now, use a simple heuristic based on shared words
        current_words = set(current_msg.lower().split())
        next_words = set(next_msg.lower().split())
        
        # Calculate Jaccard similarity
        if not current_words or not next_words:
            return True
            
        intersection = current_words.intersection(next_words)
        union = current_words.union(next_words)
        
        similarity = len(intersection) / len(union)
        
        # If similarity is low, it's likely a new thought
        return similarity < 0.2
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhooks from SendBlue
        
        Args:
            webhook_data: The webhook payload from SendBlue
            
        Returns:
            Dict containing the processed result
        """
        event_type = webhook_data.get("event_type")
        message_id = webhook_data.get("message_id")
        
        logger.info(f"Received SendBlue webhook: {event_type} for message {message_id}")
        
        # In a real implementation, this would:
        # 1. Store the message in Mem0 and GHL if it's incoming
        # 2. Update the message status in our system if it's a status update
        # 3. Trigger agent response for incoming messages
        
        # For now, just return success
        return {
            "success": True,
            "event_type": event_type,
            "message_id": message_id,
            "processed_at": datetime.now().isoformat()
        }