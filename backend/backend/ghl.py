import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class GHLIntegration:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://rest.gohighlevel.com/v1"
        self.headers = {}
        
        if self.api_key:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def set_api_key(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_contacts(self, query_params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get contacts from GHL"""
        if not self.api_key:
            logger.error("GHL API key not set")
            raise HTTPException(status_code=400, detail="GHL API key not configured")
        
        endpoint = f"{self.base_url}/contacts/"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers, params=query_params)
                response.raise_for_status()
                return response.json().get("contacts", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching contacts: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching contacts from GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get a specific contact from GHL"""
        if not self.api_key:
            logger.error("GHL API key not set")
            raise HTTPException(status_code=400, detail="GHL API key not configured")
        
        endpoint = f"{self.base_url}/contacts/{contact_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                return response.json().get("contact", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching contact: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching contact from GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact in GHL"""
        if not self.api_key:
            logger.error("GHL API key not set")
            raise HTTPException(status_code=400, detail="GHL API key not configured")
        
        endpoint = f"{self.base_url}/contacts/"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=self.headers, json=contact_data)
                response.raise_for_status()
                return response.json().get("contact", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating contact: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating contact in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a contact in GHL"""
        if not self.api_key:
            logger.error("GHL API key not set")
            raise HTTPException(status_code=400, detail="GHL API key not configured")
        
        endpoint = f"{self.base_url}/contacts/{contact_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(endpoint, headers=self.headers, json=contact_data)
                response.raise_for_status()
                return response.json().get("contact", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while updating contact: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error updating contact in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def send_message(self, contact_id: str, message: str, channel: str = "sms") -> Dict[str, Any]:
        """Send a message to a contact via GHL"""
        if not self.api_key:
            logger.error("GHL API key not set")
            raise HTTPException(status_code=400, detail="GHL API key not configured")
        
        # Different endpoints based on channel
        if channel == "sms":
            endpoint = f"{self.base_url}/contacts/{contact_id}/sms"
            data = {"message": message}
        elif channel == "email":
            endpoint = f"{self.base_url}/contacts/{contact_id}/email"
            data = {
                "subject": "New message from AI Closer",
                "body": message
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported channel: {channel}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=self.headers, json=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while sending message: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error sending message via GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def create_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new opportunity in GHL"""
        if not self.api_key:
            logger.error("GHL API key not set")
            raise HTTPException(status_code=400, detail="GHL API key not configured")
        
        endpoint = f"{self.base_url}/opportunities/"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=self.headers, json=opportunity_data)
                response.raise_for_status()
                return response.json().get("opportunity", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating opportunity: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating opportunity in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def create_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new appointment in GHL"""
        if not self.api_key:
            logger.error("GHL API key not set")
            raise HTTPException(status_code=400, detail="GHL API key not configured")
        
        endpoint = f"{self.base_url}/appointments/"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=self.headers, json=appointment_data)
                response.raise_for_status()
                return response.json().get("appointment", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating appointment: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating appointment in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def get_custom_fields(self) -> List[Dict[str, Any]]:
        """Get custom fields from GHL"""
        if not self.api_key:
            logger.error("GHL API key not set")
            raise HTTPException(status_code=400, detail="GHL API key not configured")
        
        endpoint = f"{self.base_url}/custom-fields"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                return response.json().get("customFields", [])
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching custom fields: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching custom fields from GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def create_custom_field(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom field in GHL"""
        if not self.api_key:
            logger.error("GHL API key not set")
            raise HTTPException(status_code=400, detail="GHL API key not configured")
        
        endpoint = f"{self.base_url}/custom-fields"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(endpoint, headers=self.headers, json=field_data)
                response.raise_for_status()
                return response.json().get("customField", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while creating custom field: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating custom field in GHL: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
