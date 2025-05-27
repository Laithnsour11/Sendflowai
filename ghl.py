import os
import json
import logging
import httpx
import time
import hmac
import hashlib
from typing import Dict, Any, List, Optional, Union
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class GHLIntegration:
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, shared_secret: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.shared_secret = shared_secret
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = 0
        
        self.base_url = "https://services.leadconnectorhq.com"
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def set_credentials(self, client_id: str, client_secret: str, shared_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.shared_secret = shared_secret
    
    def set_tokens(self, access_token: str, refresh_token: str, expires_in: int = 3600):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = int(time.time()) + expires_in
        self.headers["Authorization"] = f"Bearer {self.access_token}"
    
    async def get_oauth_url(self, redirect_uri: str) -> str:
        """Get OAuth URL for user authorization"""
        if not self.client_id:
            logger.error("GHL Client ID not set")
            raise HTTPException(status_code=400, detail="GHL Client ID not configured")
        
        return (
            f"{self.base_url}/oauth/chooselocation"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={redirect_uri}"
        )
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if not self.client_id or not self.client_secret:
            logger.error("GHL OAuth credentials not set")
            raise HTTPException(status_code=400, detail="GHL OAuth credentials not configured")
        
        endpoint = f"{self.base_url}/oauth/token"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect_uri
                    }
                )
                response.raise_for_status()
                token_data = response.json()
                
                # Save tokens
                self.set_tokens(
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    expires_in=token_data.get("expires_in", 3600)
                )
                
                return token_data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while exchanging code: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        if not self.client_id or not self.client_secret or not self.refresh_token:
            logger.error("GHL OAuth credentials or refresh token not set")
            raise HTTPException(status_code=400, detail="GHL OAuth credentials or refresh token not configured")
        
        endpoint = f"{self.base_url}/oauth/token"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "refresh_token",
                        "refresh_token": self.refresh_token
                    }
                )
                response.raise_for_status()
                token_data = response.json()
                
                # Save tokens
                self.set_tokens(
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    expires_in=token_data.get("expires_in", 3600)
                )
                
                return token_data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while refreshing token: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"GHL API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with GHL: {str(e)}")
    
    async def ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if not self.access_token or int(time.time()) >= self.token_expires_at:
            if self.refresh_token:
                await self.refresh_access_token()
            else:
                logger.error("No valid access token or refresh token")
                raise HTTPException(status_code=401, detail="No valid GHL access token")
    
    def verify_webhook_signature(self, signature: str, payload: str) -> bool:
        """Verify the webhook signature from GHL"""
        if not self.shared_secret:
            logger.error("GHL Shared Secret not set")
            return False
        
        calculated_signature = hmac.new(
            self.shared_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(calculated_signature, signature)
    
    # CONTACTS - Rich Data Read/Write Access
    
    async def get_contacts(self, query_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get contacts from GHL with pagination support"""
        await self.ensure_valid_token()
        
        endpoint = f"{self.base_url}/contacts/"
        if not query_params:
            query_params = {}
        
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
        """Get a specific contact from GHL with all details"""
        await self.ensure_valid_token()
        
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
        await self.ensure_valid_token()
        
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
        await self.ensure_valid_token()
        
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
