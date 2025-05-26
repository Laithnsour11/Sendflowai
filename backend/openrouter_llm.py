import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional, Union, Literal
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for interacting with the OpenRouter API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {}
        
        if self.api_key:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://aicloser.ai",  # Replace with your actual domain
                "X-Title": "AI Closer",  # Replace with your actual app name
                "Content-Type": "application/json"
            }
    
    def set_api_key(self, api_key: str):
        """Set the OpenRouter API key"""
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://aicloser.ai",  # Replace with your actual domain
            "X-Title": "AI Closer",  # Replace with your actual app name
            "Content-Type": "application/json"
        }
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        if not self.api_key:
            logger.warning("OpenRouter API key not set")
            return self._get_mock_models()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                
                return result.get("data", [])
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while fetching models: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"OpenRouter API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error fetching models from OpenRouter: {e}")
            return self._get_mock_models()
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a chat completion
        
        Args:
            messages: List of message objects
            model: Model ID (e.g. "openai/gpt-4o", "anthropic/claude-3-opus")
            temperature: Temperature (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p (nucleus) sampling
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            functions: Function definitions
            function_call: Function call control
            
        Returns:
            Chat completion response
        """
        if not self.api_key:
            logger.warning("OpenRouter API key not set, using mock response")
            return self._get_mock_completion(messages, model)
        
        try:
            # Build request payload
            payload = {
                "messages": messages,
                "model": model,
                "temperature": temperature
            }
            
            # Add optional parameters if provided
            if max_tokens is not None:
                payload["max_tokens"] = max_tokens
            
            if top_p is not None:
                payload["top_p"] = top_p
            
            if frequency_penalty is not None:
                payload["frequency_penalty"] = frequency_penalty
            
            if presence_penalty is not None:
                payload["presence_penalty"] = presence_penalty
            
            if functions:
                payload["functions"] = functions
                
                if function_call:
                    payload["function_call"] = function_call
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred during chat completion: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"OpenRouter API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error during chat completion with OpenRouter: {e}")
            return self._get_mock_completion(messages, model)
    
    def _get_mock_models(self) -> List[Dict[str, Any]]:
        """Return mock models list for testing without API key"""
        return [
            {
                "id": "openai/gpt-4o",
                "name": "GPT-4o",
                "description": "OpenAI's flagship model, stronger than GPT-4 Turbo",
                "context_length": 128000,
                "pricing": {
                    "prompt": 0.000005,
                    "completion": 0.000015
                }
            },
            {
                "id": "anthropic/claude-3-opus",
                "name": "Claude 3 Opus",
                "description": "Anthropic's most powerful model for complex tasks",
                "context_length": 200000,
                "pricing": {
                    "prompt": 0.000015,
                    "completion": 0.000075
                }
            },
            {
                "id": "anthropic/claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "description": "Excellent balance of intelligence and speed",
                "context_length": 200000,
                "pricing": {
                    "prompt": 0.000003,
                    "completion": 0.000015
                }
            },
            {
                "id": "anthropic/claude-3-haiku",
                "name": "Claude 3 Haiku",
                "description": "Fast, compact and capable model",
                "context_length": 200000,
                "pricing": {
                    "prompt": 0.00000025,
                    "completion": 0.000001250
                }
            },
            {
                "id": "meta-llama/llama-3-70b-instruct",
                "name": "Llama 3 70B",
                "description": "Meta's most capable open model",
                "context_length": 8192,
                "pricing": {
                    "prompt": 0.0000009,
                    "completion": 0.0000009
                }
            },
            {
                "id": "google/gemini-pro",
                "name": "Gemini Pro",
                "description": "Google's top performer for chat, reasoning and coding",
                "context_length": 32768,
                "pricing": {
                    "prompt": 0.0000005,
                    "completion": 0.0000005
                }
            }
        ]
    
    def _get_mock_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str
    ) -> Dict[str, Any]:
        """Generate a mock completion for testing without API key"""
        # Extract the last user message
        last_user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break
        
        # Generate a simple response based on the model and message
        model_name = model.split('/')[-1] if '/' in model else model
        
        response_content = f"This is a mock response from {model_name}. "
        
        if "property" in last_user_message.lower():
            response_content += "I understand you're interested in real estate properties. How can I help you with your property search today?"
        elif "budget" in last_user_message.lower():
            response_content += "Budget is an important consideration. What price range are you comfortable with for your property search?"
        elif "location" in last_user_message.lower():
            response_content += "Location is key in real estate. Which neighborhoods or areas are you most interested in?"
        else:
            response_content += "How can I assist you with your real estate needs today?"
        
        return {
            "id": "mock-completion-id",
            "object": "chat.completion",
            "created": 1678945500,
            "model": model,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": response_content
                    },
                    "index": 0,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": len(response_content.split()) * 1.3,
                "total_tokens": 100 + (len(response_content.split()) * 1.3)
            }
        }
