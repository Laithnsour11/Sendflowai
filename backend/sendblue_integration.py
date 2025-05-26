import os
import json
import logging
import httpx
import asyncio
from typing import Dict, Any, List, Optional, Union
from fastapi import HTTPException, Request
from datetime import datetime
import uuid
import time

from langchain_agents import AgentOrchestrator, ConversationManager
from mem0 import Mem0Integration

logger = logging.getLogger(__name__)

class SendBlueIntegration:
    """Handles integration with SendBlue for SMS/MMS communication"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        agent_orchestrator: Optional[AgentOrchestrator] = None,
        mem0_client: Optional[Mem0Integration] = None
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.sendblue.co/api/v1"
        self.headers = {}
        self.agent_orchestrator = agent_orchestrator
        self.mem0_client = mem0_client
        
        if self.api_key and self.api_secret:
            self.headers = {
                "sb-api-key-id": self.api_key,
                "sb-api-secret-key": self.api_secret,
                "Content-Type": "application/json"
            }
    
    def set_api_credentials(self, api_key: str, api_secret: str):
        """Set the SendBlue API credentials"""
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "sb-api-key-id": self.api_key,
            "sb-api-secret-key": self.api_secret,
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self,
        lead_id: str,
        to_number: str,
        message: str,
        from_number: Optional[str] = None,
        media_urls: Optional[List[str]] = None,
        conversation_id: Optional[str] = None,
        message_parts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS/MMS message to a lead
        
        Args:
            lead_id: ID of the lead
            to_number: Recipient phone number
            message: Message content
            from_number: Sender phone number (if None, default account number is used)
            media_urls: Optional list of media URLs for MMS
            conversation_id: Optional ID of the conversation
            message_parts: Optional list of message parts with pauses for natural cadence
            
        Returns:
            Dict containing message information
        """
        if not self.api_key or not self.api_secret:
            logger.warning("SendBlue API credentials not set")
            return self._get_mock_message_response(lead_id, to_number, message)
        
        # If message parts are provided, send as multiple messages with natural pauses
        if message_parts and len(message_parts) > 1:
            return await self._send_message_with_cadence(lead_id, to_number, from_number, message_parts, conversation_id)
        
        # Otherwise, send as a single message
        payload = {
            "to_number": to_number,
            "content": message
        }
        
        if from_number:
            payload["from_number"] = from_number
        
        if media_urls:
            payload["media_urls"] = media_urls
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/send",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                # Store message in memory
                if self.mem0_client and lead_id:
                    await self.mem0_client.store_memory(
                        user_id=lead_id,
                        memory_data={
                            "direction": "outbound",
                            "channel": "sms",
                            "message": message,
                            "media_urls": media_urls,
                            "to_number": to_number,
                            "from_number": from_number,
                            "sendblue_message_id": result.get("id"),
                            "conversation_id": conversation_id,
                            "timestamp": datetime.now().isoformat()
                        },
                        memory_type="contextual",
                        metadata={
                            "direction": "outbound",
                            "channel": "sms",
                            "conversation_id": conversation_id
                        }
                    )
                
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while sending message: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"SendBlue API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error sending message with SendBlue: {e}")
            return self._get_mock_message_response(lead_id, to_number, message)
    
    async def _send_message_with_cadence(
        self,
        lead_id: str,
        to_number: str,
        from_number: Optional[str],
        message_parts: List[Dict[str, Any]],
        conversation_id: Optional[str]
    ) -> Dict[str, Any]:
        """Send multiple messages with natural pauses between them"""
        response_data = []
        
        for i, part in enumerate(message_parts):
            text = part.get("text", "")
            pause_seconds = part.get("pause_after", 0)
            
            # Skip empty messages
            if not text.strip():
                continue
            
            # Send this part
            try:
                payload = {
                    "to_number": to_number,
                    "content": text
                }
                
                if from_number:
                    payload["from_number"] = from_number
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/send",
                        headers=self.headers,
                        json=payload,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    result = response.json()
                    response_data.append(result)
                    
                    # Store message in memory
                    if self.mem0_client and lead_id:
                        await self.mem0_client.store_memory(
                            user_id=lead_id,
                            memory_data={
                                "direction": "outbound",
                                "channel": "sms",
                                "message": text,
                                "message_part": i + 1,
                                "total_parts": len(message_parts),
                                "to_number": to_number,
                                "from_number": from_number,
                                "sendblue_message_id": result.get("id"),
                                "conversation_id": conversation_id,
                                "timestamp": datetime.now().isoformat()
                            },
                            memory_type="contextual",
                            metadata={
                                "direction": "outbound",
                                "channel": "sms",
                                "conversation_id": conversation_id,
                                "message_part": i + 1,
                                "total_parts": len(message_parts)
                            }
                        )
                
                # Wait for the specified pause time before sending the next message
                if pause_seconds > 0 and i < len(message_parts) - 1:
                    await asyncio.sleep(pause_seconds)
                    
            except Exception as e:
                logger.error(f"Error sending message part {i+1}: {e}")
                # Continue with other parts even if one fails
        
        # Return combined response
        return {
            "message_parts_sent": len(response_data),
            "message_parts_total": len(message_parts),
            "responses": response_data,
            "conversation_id": conversation_id
        }
    
    async def process_webhook(self, request: Request) -> Dict[str, Any]:
        """
        Process an incoming webhook from SendBlue
        
        Args:
            request: The webhook request
            
        Returns:
            Response to the webhook
        """
        try:
            payload = await request.json()
            
            event_type = payload.get("type")
            message_data = payload.get("data", {})
            
            logger.info(f"Received SendBlue webhook: {event_type}")
            
            if event_type == "message.received":
                # Incoming message from a lead
                await self._handle_incoming_message(message_data)
            
            elif event_type == "message.sent":
                # Confirmation that our message was sent
                await self._handle_message_sent(message_data)
            
            elif event_type == "message.delivered":
                # Confirmation that our message was delivered
                await self._handle_message_delivered(message_data)
            
            elif event_type == "message.failed":
                # Our message failed to send
                await self._handle_message_failed(message_data)
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Error processing SendBlue webhook: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")
    
    async def _handle_incoming_message(self, message_data: Dict[str, Any]):
        """Handle an incoming message from a lead"""
        # Extract message information
        from_number = message_data.get("from_number")
        to_number = message_data.get("to_number")
        content = message_data.get("content", "")
        media_urls = message_data.get("media_urls", [])
        message_id = message_data.get("id")
        
        # Find the lead based on phone number
        lead_id = await self._find_lead_by_phone(from_number)
        
        if not lead_id:
            logger.warning(f"Received message from unknown number: {from_number}")
            lead_id = f"unknown_{from_number}"
        
        # Store the incoming message in memory
        if self.mem0_client:
            await self.mem0_client.store_memory(
                user_id=lead_id,
                memory_data={
                    "direction": "inbound",
                    "channel": "sms",
                    "message": content,
                    "media_urls": media_urls,
                    "from_number": from_number,
                    "to_number": to_number,
                    "sendblue_message_id": message_id,
                    "timestamp": datetime.now().isoformat()
                },
                memory_type="contextual",
                metadata={
                    "direction": "inbound",
                    "channel": "sms"
                }
            )
        
        # Process the message with an appropriate agent if we have the orchestrator
        if self.agent_orchestrator and lead_id:
            # Get lead context
            lead_context = await self._get_lead_context(lead_id)
            
            # Process message
            conversation_manager = ConversationManager(self.agent_orchestrator, self.mem0_client)
            result = await conversation_manager.process_message(
                message=content,
                lead_context=lead_context,
                channel="sms"
            )
            
            # Send the response
            response_message = result["response"]["response"]
            message_parts = result["response"].get("message_parts", [])
            
            # Use the conversation ID from the result
            conversation_id = result["conversation"]["id"]
            
            # Send the response with natural cadence if message parts are available
            await self.send_message(
                lead_id=lead_id,
                to_number=from_number,
                message=response_message,
                from_number=to_number,
                conversation_id=conversation_id,
                message_parts=message_parts
            )
    
    async def _handle_message_sent(self, message_data: Dict[str, Any]):
        """Handle confirmation that our message was sent"""
        message_id = message_data.get("id")
        to_number = message_data.get("to_number")
        
        logger.info(f"Message {message_id} to {to_number} was sent")
    
    async def _handle_message_delivered(self, message_data: Dict[str, Any]):
        """Handle confirmation that our message was delivered"""
        message_id = message_data.get("id")
        to_number = message_data.get("to_number")
        
        logger.info(f"Message {message_id} to {to_number} was delivered")
    
    async def _handle_message_failed(self, message_data: Dict[str, Any]):
        """Handle notification that our message failed to send"""
        message_id = message_data.get("id")
        to_number = message_data.get("to_number")
        error = message_data.get("error", {})
        
        logger.error(f"Message {message_id} to {to_number} failed: {error}")
    
    async def _find_lead_by_phone(self, phone_number: str) -> Optional[str]:
        """Find a lead by phone number"""
        # In a real implementation, this would query the database
        # For MVP, return a mock lead ID
        return f"lead_{phone_number.replace('+', '').replace('-', '')}"
    
    async def _get_lead_context(self, lead_id: str) -> Dict[str, Any]:
        """Get the lead context for a lead"""
        # In a real implementation, this would query the database and Mem0
        # For MVP, return mock lead context
        lead_context = {
            "id": lead_id,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "personality_type": "analytical",
            "communication_preference": "text",
            "trust_level": 0.7,
            "relationship_stage": "qualification",
            "property_preferences": {
                "bedrooms": 3,
                "bathrooms": 2,
                "location": "downtown",
                "property_type": "condo"
            }
        }
        
        # Enhance with Mem0 data if available
        if self.mem0_client:
            try:
                mem0_context = await self.mem0_client.synthesize_lead_context(lead_id)
                
                # Merge Mem0 context with basic lead context
                if mem0_context.get("factual_information"):
                    lead_context.update(mem0_context.get("factual_information", {}))
                
                # Update relationship insights
                if mem0_context.get("relationship_insights"):
                    insights = mem0_context.get("relationship_insights", {})
                    
                    if insights.get("trust_level"):
                        lead_context["trust_level"] = insights["trust_level"]
                    
                    if insights.get("communication_style_preferences"):
                        lead_context["communication_preference"] = insights["communication_style_preferences"].get("preferred_method", lead_context["communication_preference"])
                
            except Exception as e:
                logger.error(f"Error retrieving lead context from Mem0: {e}")
        
        return lead_context
    
    def _get_mock_message_response(
        self, 
        lead_id: str, 
        to_number: str, 
        message: str
    ) -> Dict[str, Any]:
        """Generate a mock message response for testing without API credentials"""
        message_id = str(uuid.uuid4())
        
        return {
            "id": message_id,
            "status": "queued",
            "to_number": to_number,
            "content": message,
            "created_at": datetime.now().isoformat(),
            "message": "Message queued successfully (mock)"
        }
