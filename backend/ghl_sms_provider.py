import logging
import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class GHLSMSProvider:
    """GHL Native SMS Provider for sending/receiving SMS through GoHighLevel"""
    
    def __init__(self, ghl_integration):
        self.ghl_integration = ghl_integration
    
    async def send_sms(
        self, 
        org_id: str,
        to_number: str, 
        message: str, 
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS via GHL Conversation API
        
        Args:
            org_id: Organization ID
            to_number: Recipient phone number
            message: Message content
            from_number: Sender phone number (optional, will use org default)
            
        Returns:
            Dict with send results
        """
        try:
            # Get organization settings to determine API credentials and phone number
            org_settings = await self.ghl_integration.get_organization_settings(org_id)
            
            if not org_settings:
                raise ValueError(f"Organization settings not found for {org_id}")
            
            # Get GHL API credentials
            access_token = org_settings.get("ghl_access_token")
            location_id = org_settings.get("ghl_location_id")
            
            if not access_token or not location_id:
                raise ValueError("GHL credentials not properly configured")
            
            # Use provided from_number or get from org settings
            sender_number = from_number or org_settings.get("ghl_phone_number")
            
            if not sender_number:
                raise ValueError("No sender phone number configured")
            
            # Find or create contact in GHL
            contact_id = await self._get_or_create_contact(
                access_token, location_id, to_number
            )
            
            # Send message via GHL Conversation API
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            message_payload = {
                "type": "SMS",
                "message": message,
                "html": message,
                "contactId": contact_id,
                "conversationId": f"conv_{uuid.uuid4()}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://services.leadconnectorhq.com/conversations/messages",
                    headers=headers,
                    json=message_payload,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    result = response.json()
                    
                    logger.info(f"SMS sent successfully via GHL to {to_number}")
                    
                    return {
                        "success": True,
                        "message_id": result.get("id"),
                        "status": "sent",
                        "to": to_number,
                        "from": sender_number,
                        "message": message,
                        "provider": "ghl_native",
                        "sent_at": datetime.now().isoformat()
                    }
                else:
                    logger.error(f"GHL SMS send failed: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"GHL SMS send failed: {response.text}"
                    )
                
        except Exception as e:
            logger.error(f"Error sending SMS via GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to send SMS via GHL: {str(e)}")
    
    async def _get_or_create_contact(
        self, 
        access_token: str, 
        location_id: str, 
        phone_number: str
    ) -> str:
        """Get existing contact or create new one in GHL"""
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Search for existing contact
        search_params = {
            "phone": phone_number,
            "locationId": location_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Search for contact
                response = await client.get(
                    "https://services.leadconnectorhq.com/contacts/",
                    headers=headers,
                    params=search_params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    contacts = response.json().get("contacts", [])
                    if contacts:
                        return contacts[0]["id"]
                
                # Create new contact if not found
                contact_payload = {
                    "firstName": "SMS",
                    "lastName": "Lead",
                    "phone": phone_number,
                    "locationId": location_id,
                    "source": "ai_closer_bot"
                }
                
                create_response = await client.post(
                    "https://services.leadconnectorhq.com/contacts/",
                    headers=headers,
                    json=contact_payload,
                    timeout=30.0
                )
                
                if create_response.status_code == 201:
                    new_contact = create_response.json()
                    return new_contact["contact"]["id"]
                else:
                    raise Exception(f"Failed to create contact: {create_response.text}")
                    
        except Exception as e:
            logger.error(f"Error getting/creating contact: {e}")
            raise
    
    async def handle_incoming_sms(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming SMS webhook from GHL
        
        Args:
            webhook_data: Webhook payload from GHL
            
        Returns:
            Dict with processing results
        """
        try:
            message_data = webhook_data.get("message", {})
            contact_data = webhook_data.get("contact", {})
            
            # Extract message details
            message_body = message_data.get("body", "")
            from_number = message_data.get("from", "")
            to_number = message_data.get("to", "")
            message_type = message_data.get("messageType", "")
            
            if message_type != "SMS":
                return {"processed": False, "reason": "Not an SMS message"}
            
            # Extract contact details
            contact_id = contact_data.get("id", "")
            contact_name = contact_data.get("name", "Unknown")
            
            # Create standardized message object
            standardized_message = {
                "id": str(uuid.uuid4()),
                "from": from_number,
                "to": to_number,
                "message": message_body,
                "contact_id": contact_id,
                "contact_name": contact_name,
                "channel": "sms",
                "provider": "ghl_native",
                "received_at": datetime.now().isoformat(),
                "raw_webhook": webhook_data
            }
            
            logger.info(f"Processed incoming GHL SMS from {from_number}: {message_body[:50]}...")
            
            return {
                "processed": True,
                "message": standardized_message,
                "requires_response": True,
                "contact_info": {
                    "id": contact_id,
                    "name": contact_name,
                    "phone": from_number
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing incoming GHL SMS: {e}")
            return {
                "processed": False,
                "error": str(e)
            }
    
    async def apply_intelligent_cadence(
        self, 
        messages: List[str], 
        recipient: str,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Apply intelligent cadence to a series of messages
        
        Args:
            messages: List of messages to send
            recipient: Recipient phone number
            context: Additional context for cadence decisions
            
        Returns:
            List of message objects with timing
        """
        cadenced_messages = []
        
        for i, message in enumerate(messages):
            # Calculate intelligent delay based on message content and position
            if i == 0:
                delay_seconds = 0  # First message immediately
            elif len(message) > 100:
                delay_seconds = 8 + (len(message) // 20)  # Longer messages need more time
            elif i == len(messages) - 1:
                delay_seconds = 15  # Final message gets longer pause
            else:
                delay_seconds = 5 + (i * 2)  # Progressive delays
            
            cadenced_message = {
                "message": message,
                "delay_seconds": delay_seconds,
                "sequence_number": i + 1,
                "total_messages": len(messages),
                "recipient": recipient,
                "estimated_read_time": len(message) // 10  # Rough estimate
            }
            
            cadenced_messages.append(cadenced_message)
        
        return cadenced_messages

