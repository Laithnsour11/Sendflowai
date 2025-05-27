import logging
import json
from typing import Dict, Any, List, Optional, Union, Literal
from datetime import datetime
import uuid
import os
from fastapi import HTTPException

from sendblue_integration import SendBlueIntegration
import database as db

logger = logging.getLogger(__name__)

class SMSManager:
    """Manages SMS communication using SendBlue and GHL Native SMS"""
    
    def __init__(self):
        self.sendblue_integration = SendBlueIntegration()
        self.ghl_sms_enabled = False
    
    async def set_sendblue_credentials_for_org(self, org_id: str) -> bool:
        """
        Set the SendBlue API credentials for the organization
        
        Args:
            org_id: ID of the organization
            
        Returns:
            True if API credentials were set successfully, False otherwise
        """
        try:
            # Get API keys for the organization
            api_keys = await db.get_api_keys(org_id)
            
            if not api_keys or "sendblue_api_key" not in api_keys or not api_keys["sendblue_api_key"]:
                logger.warning(f"SendBlue API key not configured for organization {org_id}")
                return False
            
            # Get API secret if available
            api_secret = api_keys.get("sendblue_api_secret", "")
            if not api_secret:
                logger.warning(f"SendBlue API secret not configured for organization {org_id}")
                return False
            
            # Set the credentials in the SendBlue integration
            self.sendblue_integration.set_credentials(api_keys["sendblue_api_key"], api_secret)
            return True
            
        except Exception as e:
            logger.error(f"Error setting SendBlue credentials for organization {org_id}: {e}")
            return False
    
    async def validate_sendblue_credentials(self, api_key: str, api_secret: str) -> Dict[str, Any]:
        """
        Validate SendBlue API credentials
        
        Args:
            api_key: The SendBlue API key
            api_secret: The SendBlue API secret
            
        Returns:
            Dict with validation status
        """
        try:
            temp_integration = SendBlueIntegration(api_key, api_secret)
            valid = await temp_integration.validate_credentials()
            
            if valid:
                return {"valid": True, "message": "SendBlue API credentials are valid"}
            else:
                return {"valid": False, "message": "Invalid SendBlue API credentials"}
                
        except Exception as e:
            logger.error(f"Error validating SendBlue API credentials: {e}")
            return {"valid": False, "message": f"Error validating SendBlue API credentials: {str(e)}"}
    
    async def send_sms(
        self, 
        org_id: str,
        lead_id: str,
        phone_number: str,
        message: str,
        provider: Literal["sendblue", "ghl"] = "sendblue",
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS message to a lead
        
        Args:
            org_id: ID of the organization
            lead_id: ID of the lead
            phone_number: Phone number to send to
            message: Message content
            provider: SMS provider to use ("sendblue" or "ghl")
            media_urls: Optional list of media URLs for MMS
            
        Returns:
            Dict containing message information
        """
        if provider == "sendblue":
            return await self._send_via_sendblue(org_id, lead_id, phone_number, message, media_urls)
        elif provider == "ghl":
            return await self._send_via_ghl(org_id, lead_id, phone_number, message, media_urls)
        else:
            raise ValueError(f"Unsupported SMS provider: {provider}")
    
    async def _send_via_sendblue(
        self,
        org_id: str,
        lead_id: str,
        phone_number: str,
        message: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send SMS via SendBlue"""
        # Ensure we have the API credentials set
        credentials_set = await self.set_sendblue_credentials_for_org(org_id)
        
        if not credentials_set:
            raise HTTPException(status_code=400, detail="SendBlue API credentials not configured for this organization")
        
        try:
            # Get lead information for context
            lead = await db.get_lead(lead_id)
            if not lead:
                raise HTTPException(status_code=404, detail="Lead not found")
            
            # Determine intelligent cadence
            message_segments = await self.sendblue_integration.determine_intelligent_cadence(message)
            
            # Send messages with intelligent cadence
            if len(message_segments) > 1:
                send_result = await self.sendblue_integration.send_sms_with_intelligent_cadence(
                    to_number=phone_number,
                    messages=message_segments,
                    delay_seconds=2
                )
                
                # Store the conversation in database
                for i, segment_result in enumerate(send_result):
                    conversation_data = {
                        "_id": str(uuid.uuid4()),
                        "org_id": org_id,
                        "lead_id": lead_id,
                        "channel": "sms",
                        "direction": "outbound",
                        "provider": "sendblue",
                        "message_id": segment_result.get("id"),
                        "phone_number": phone_number,
                        "message": message_segments[i],
                        "segment_index": i,
                        "total_segments": len(message_segments),
                        "media_urls": media_urls if i == 0 and media_urls else [],
                        "status": "sent",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                    
                    # Store in database (in a real implementation)
                    # await db.create_conversation(conversation_data)
                
                return {
                    "message_id": send_result[0].get("id") if send_result else None,
                    "status": "sent",
                    "segments": len(message_segments),
                    "lead_id": lead_id,
                    "phone_number": phone_number,
                    "intelligent_cadence": True
                }
            else:
                # Send single message
                send_result = await self.sendblue_integration.send_sms(
                    to_number=phone_number,
                    message=message,
                    media_urls=media_urls
                )
                
                # Store the conversation in database
                conversation_data = {
                    "_id": str(uuid.uuid4()),
                    "org_id": org_id,
                    "lead_id": lead_id,
                    "channel": "sms",
                    "direction": "outbound",
                    "provider": "sendblue",
                    "message_id": send_result.get("id"),
                    "phone_number": phone_number,
                    "message": message,
                    "media_urls": media_urls or [],
                    "status": "sent",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                # Store in database (in a real implementation)
                # await db.create_conversation(conversation_data)
                
                return {
                    "message_id": send_result.get("id"),
                    "status": "sent",
                    "segments": 1,
                    "lead_id": lead_id,
                    "phone_number": phone_number,
                    "intelligent_cadence": False
                }
                
        except Exception as e:
            logger.error(f"Error sending SMS via SendBlue: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send SMS: {str(e)}")
    
    async def _send_via_ghl(
        self,
        org_id: str,
        lead_id: str,
        phone_number: str,
        message: str,
        media_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send SMS via GHL Native SMS"""
        # For MVP, this is a placeholder
        # In a real implementation, we would use GHL's API to send SMS
        
        if not self.ghl_sms_enabled:
            raise HTTPException(status_code=400, detail="GHL Native SMS is not enabled for this organization")
        
        try:
            # Get lead information for context
            lead = await db.get_lead(lead_id)
            if not lead:
                raise HTTPException(status_code=404, detail="Lead not found")
            
            # Determine intelligent cadence
            message_segments = await self.sendblue_integration.determine_intelligent_cadence(message)
            
            # Mock sending via GHL
            # In a real implementation, we would call GHL's API
            
            # Store the conversation in database
            for i, segment in enumerate(message_segments):
                conversation_data = {
                    "_id": str(uuid.uuid4()),
                    "org_id": org_id,
                    "lead_id": lead_id,
                    "channel": "sms",
                    "direction": "outbound",
                    "provider": "ghl",
                    "message_id": f"ghl_mock_{uuid.uuid4()}",
                    "phone_number": phone_number,
                    "message": segment,
                    "segment_index": i,
                    "total_segments": len(message_segments),
                    "media_urls": media_urls if i == 0 and media_urls else [],
                    "status": "sent",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                # Store in database (in a real implementation)
                # await db.create_conversation(conversation_data)
            
            return {
                "message_id": f"ghl_mock_{uuid.uuid4()}",
                "status": "sent",
                "segments": len(message_segments),
                "lead_id": lead_id,
                "phone_number": phone_number,
                "intelligent_cadence": len(message_segments) > 1
            }
                
        except Exception as e:
            logger.error(f"Error sending SMS via GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send SMS via GHL: {str(e)}")
    
    async def handle_sendblue_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a webhook event from SendBlue
        
        Args:
            event: The webhook event data
            
        Returns:
            Dict containing processed event information
        """
        try:
            # Process the event
            processed_event = self.sendblue_integration.process_webhook_event(event)
            event_type = processed_event.get("event_type")
            
            # For message_received events, trigger agent response
            if event_type == "message_received":
                # In a real implementation, we would:
                # 1. Find the lead associated with the phone number
                # 2. Get the lead context
                # 3. Select an appropriate agent
                # 4. Generate a response
                # 5. Send the response
                
                # Store the incoming message in database
                conversation_data = {
                    "_id": str(uuid.uuid4()),
                    "org_id": "unknown",  # Would be determined from phone number
                    "lead_id": "unknown",  # Would be determined from phone number
                    "channel": "sms",
                    "direction": "inbound",
                    "provider": "sendblue",
                    "message_id": processed_event.get("message_id"),
                    "phone_number": processed_event.get("from_number"),
                    "message": processed_event.get("body"),
                    "media_urls": processed_event.get("media_urls", []),
                    "status": "received",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                # Store in database (in a real implementation)
                # await db.create_conversation(conversation_data)
                
                processed_event["handled"] = True
            
            return processed_event
            
        except Exception as e:
            logger.error(f"Error handling SendBlue webhook event: {e}")
            return {
                "error": str(e),
                "processed": False
            }
    
    async def handle_ghl_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a webhook event from GHL
        
        Args:
            event: The webhook event data
            
        Returns:
            Dict containing processed event information
        """
        # For MVP, this is a placeholder
        # In a real implementation, we would process GHL webhook events
        
        event_type = event.get("type")
        
        if event_type == "ConversationProviderMessage":
            # This would be an incoming SMS message via GHL
            # We would process it similarly to SendBlue
            
            return {
                "event_type": "message_received_ghl",
                "processed": True,
                "handled": True
            }
        
        return {
            "event_type": event_type,
            "processed": False,
            "reason": "Unhandled GHL event type"
        }
