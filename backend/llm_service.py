import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from fastapi import HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_text(self, prompt: str, system_message: str, 
                          temperature: float = 0.7, max_tokens: int = 1000, 
                          functions: Optional[List[Dict[str, Any]]] = None,
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate text from the LLM
        
        Args:
            prompt: The user prompt
            system_message: The system message/instructions
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            functions: Optional list of function definitions
            user_id: Optional user ID for tracking
            
        Returns:
            Dict containing the generated text and metadata
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from this provider
        
        Returns:
            List of available models with metadata
        """
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.api_url = "https://api.openai.com/v1"
    
    def set_api_key(self, api_key: str):
        """Set OpenAI API key"""
        self.api_key = api_key
    
    async def generate_text(self, prompt: str, system_message: str, 
                          temperature: float = 0.7, max_tokens: int = 1000, 
                          functions: Optional[List[Dict[str, Any]]] = None,
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate text using OpenAI API"""
        if not self.api_key:
            logger.warning("OpenAI API key not set")
            raise HTTPException(status_code=400, detail="OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        data = {
            "model": "gpt-4o",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if functions:
            data["functions"] = functions
        
        if user_id:
            data["user"] = user_id
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "text": result["choices"][0]["message"]["content"],
                    "model": result["model"],
                    "provider": "openai",
                    "finish_reason": result["choices"][0]["finish_reason"],
                    "usage": result.get("usage", {}),
                    "created": datetime.now().isoformat()
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"OpenAI API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error generating text from OpenAI: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with OpenAI: {str(e)}")
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models from OpenAI"""
        if not self.api_key:
            logger.warning("OpenAI API key not set")
            raise HTTPException(status_code=400, detail="OpenAI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/models",
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                # Filter for relevant models
                chat_models = [
                    {"id": model["id"], "name": model["id"], "provider": "openai", "created": model.get("created")}
                    for model in result["data"]
                    if "gpt" in model["id"]
                ]
                
                return chat_models
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"OpenAI API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error getting models from OpenAI: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with OpenAI: {str(e)}")

class AnthropicProvider(LLMProvider):
    """Anthropic API provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.api_url = "https://api.anthropic.com/v1"
    
    def set_api_key(self, api_key: str):
        """Set Anthropic API key"""
        self.api_key = api_key
    
    async def generate_text(self, prompt: str, system_message: str, 
                          temperature: float = 0.7, max_tokens: int = 1000, 
                          functions: Optional[List[Dict[str, Any]]] = None,
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate text using Anthropic API"""
        if not self.api_key:
            logger.warning("Anthropic API key not set")
            raise HTTPException(status_code=400, detail="Anthropic API key not configured")
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "claude-3-opus-20240229",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_message,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        if user_id:
            data["metadata"] = {"user_id": user_id}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/messages",
                    headers=headers,
                    json=data,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "text": result["content"][0]["text"],
                    "model": result["model"],
                    "provider": "anthropic",
                    "finish_reason": result.get("stop_reason", ""),
                    "usage": {
                        "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                        "output_tokens": result.get("usage", {}).get("output_tokens", 0)
                    },
                    "created": datetime.now().isoformat()
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Anthropic API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error generating text from Anthropic: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with Anthropic: {str(e)}")
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models from Anthropic"""
        # Anthropic doesn't have a models endpoint yet, so we return hardcoded values
        models = [
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "provider": "anthropic", "created": None},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "provider": "anthropic", "created": None},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "provider": "anthropic", "created": None}
        ]
        return models

class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1"
    
    def set_api_key(self, api_key: str):
        """Set OpenRouter API key"""
        self.api_key = api_key
    
    async def generate_text(self, prompt: str, system_message: str, 
                          temperature: float = 0.7, max_tokens: int = 1000, 
                          functions: Optional[List[Dict[str, Any]]] = None,
                          user_id: Optional[str] = None,
                          model_id: str = "openai/gpt-4o") -> Dict[str, Any]:
        """Generate text using OpenRouter API"""
        if not self.api_key:
            logger.warning("OpenRouter API key not set")
            raise HTTPException(status_code=400, detail="OpenRouter API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-closer.com",  # Replace with your actual domain
            "X-Title": "AI Closer"  # Replace with your actual app name
        }
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        data = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if functions:
            data["functions"] = functions
        
        if user_id:
            data["user"] = user_id
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "text": result["choices"][0]["message"]["content"],
                    "model": result["model"],
                    "provider": "openrouter",
                    "finish_reason": result["choices"][0]["finish_reason"],
                    "usage": result.get("usage", {}),
                    "created": datetime.now().isoformat()
                }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"OpenRouter API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error generating text from OpenRouter: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with OpenRouter: {str(e)}")
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models from OpenRouter"""
        if not self.api_key:
            logger.warning("OpenRouter API key not set")
            raise HTTPException(status_code=400, detail="OpenRouter API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/models",
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
                
                # Format models for consistency
                formatted_models = []
                for model in result["data"]:
                    formatted_models.append({
                        "id": model["id"],
                        "name": model.get("name", model["id"]),
                        "provider": "openrouter",
                        "context_length": model.get("context_length"),
                        "pricing": {
                            "prompt": model.get("pricing", {}).get("prompt"),
                            "completion": model.get("pricing", {}).get("completion")
                        },
                        "created": None  # OpenRouter doesn't provide creation dates
                    })
                
                return formatted_models
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"OpenRouter API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error getting models from OpenRouter: {e}")
            raise HTTPException(status_code=500, detail=f"Error communicating with OpenRouter: {str(e)}")

class LLMService:
    """Service for interacting with various LLM providers"""
    
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "openrouter": OpenRouterProvider()
        }
    
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a specific provider"""
        if provider in self.providers:
            self.providers[provider].set_api_key(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def generate_text(self, provider: str, prompt: str, system_message: str, 
                          temperature: float = 0.7, max_tokens: int = 1000,
                          functions: Optional[List[Dict[str, Any]]] = None,
                          user_id: Optional[str] = None,
                          model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate text from a specific provider
        
        Args:
            provider: The provider to use (openai, anthropic, openrouter)
            prompt: The user prompt
            system_message: The system message/instructions
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            functions: Optional list of function definitions
            user_id: Optional user ID for tracking
            model_id: Optional model ID (required for OpenRouter)
            
        Returns:
            Dict containing the generated text and metadata
        """
        if provider not in self.providers:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        provider_instance = self.providers[provider]
        
        if provider == "openrouter" and not model_id:
            raise HTTPException(status_code=400, detail="model_id is required for OpenRouter")
        
        # Generate text from the selected provider
        if provider == "openrouter":
            return await provider_instance.generate_text(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
                functions=functions,
                user_id=user_id,
                model_id=model_id
            )
        else:
            return await provider_instance.generate_text(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
                functions=functions,
                user_id=user_id
            )
    
    async def get_available_models(self, provider: str) -> List[Dict[str, Any]]:
        """
        Get available models from a specific provider
        
        Args:
            provider: The provider to use (openai, anthropic, openrouter)
            
        Returns:
            List of available models with metadata
        """
        if provider not in self.providers:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        
        return await self.providers[provider].get_available_models()
