import os
import json
import logging
import httpx
import time
from typing import List, Dict, Any, Optional, Union
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class LLMService:
    """
    Abstracted LLM service that supports multiple providers:
    - OpenAI
    - Anthropic
    - OpenRouter (for accessing various models)
    """
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
        self.openrouter_api_key = os.environ.get('OPENROUTER_API_KEY')
        
        # Default configuration
        self.default_provider = "openrouter"
        self.default_model = "openai/gpt-4o"
        self.default_temperature = 0.7
        self.default_max_tokens = 1000
    
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a specific provider"""
        if provider == "openai":
            self.openai_api_key = api_key
        elif provider == "anthropic":
            self.anthropic_api_key = api_key
        elif provider == "openrouter":
            self.openrouter_api_key = api_key
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def get_available_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available models from the specified provider"""
        if provider == "openai":
            return await self._get_openai_models()
        elif provider == "anthropic":
            return await self._get_anthropic_models()
        elif provider == "openrouter" or provider is None:
            return await self._get_openrouter_models()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _get_openai_models(self) -> List[Dict[str, Any]]:
        """Get available OpenAI models"""
        if not self.openai_api_key:
            return [
                {"id": "gpt-4o", "name": "GPT-4o", "context_window": 128000, "provider": "openai"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context_window": 128000, "provider": "openai"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_window": 16000, "provider": "openai"}
            ]
        
        url = "https://api.openai.com/v1/models"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                models = response.json().get("data", [])
                
                # Filter for chat models
                chat_models = [
                    {
                        "id": model["id"],
                        "name": model["id"],
                        "context_window": self._get_context_window(model["id"]),
                        "provider": "openai"
                    }
                    for model in models
                    if model["id"].startswith("gpt-")
                ]
                
                return chat_models
        except Exception as e:
            logger.error(f"Error fetching OpenAI models: {e}")
            return [
                {"id": "gpt-4o", "name": "GPT-4o", "context_window": 128000, "provider": "openai"},
                {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context_window": 128000, "provider": "openai"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_window": 16000, "provider": "openai"}
            ]
    
    async def _get_anthropic_models(self) -> List[Dict[str, Any]]:
        """Get available Anthropic models"""
        return [
            {"id": "claude-3-opus", "name": "Claude 3 Opus", "context_window": 200000, "provider": "anthropic"},
            {"id": "claude-3-sonnet", "name": "Claude 3 Sonnet", "context_window": 200000, "provider": "anthropic"},
            {"id": "claude-3-haiku", "name": "Claude 3 Haiku", "context_window": 200000, "provider": "anthropic"}
        ]
    
    async def _get_openrouter_models(self) -> List[Dict[str, Any]]:
        """Get available OpenRouter models"""
        if not self.openrouter_api_key:
            return [
                {"id": "openai/gpt-4o", "name": "OpenAI GPT-4o", "context_window": 128000, "provider": "openrouter"},
                {"id": "anthropic/claude-3-opus", "name": "Anthropic Claude 3 Opus", "context_window": 200000, "provider": "openrouter"},
                {"id": "anthropic/claude-3-sonnet", "name": "Anthropic Claude 3 Sonnet", "context_window": 200000, "provider": "openrouter"},
                {"id": "anthropic/claude-3-haiku", "name": "Anthropic Claude 3 Haiku", "context_window": 200000, "provider": "openrouter"},
                {"id": "meta-llama/llama-3-70b-instruct", "name": "Meta Llama 3 70B", "context_window": 8000, "provider": "openrouter"},
                {"id": "google/gemini-pro", "name": "Google Gemini Pro", "context_window": 32000, "provider": "openrouter"}
            ]
        
        url = "https://openrouter.ai/api/v1/models"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": "https://ai-closer.com",  # Replace with your actual domain
            "X-Title": "AI Closer Bot"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                models = response.json().get("data", [])
                
                openrouter_models = [
                    {
                        "id": model["id"],
                        "name": model.get("name", model["id"]),
                        "context_window": model.get("context_length", 4096),
                        "provider": "openrouter"
                    }
                    for model in models
                ]
                
                return openrouter_models
        except Exception as e:
            logger.error(f"Error fetching OpenRouter models: {e}")
            return [
                {"id": "openai/gpt-4o", "name": "OpenAI GPT-4o", "context_window": 128000, "provider": "openrouter"},
                {"id": "anthropic/claude-3-opus", "name": "Anthropic Claude 3 Opus", "context_window": 200000, "provider": "openrouter"},
                {"id": "anthropic/claude-3-sonnet", "name": "Anthropic Claude 3 Sonnet", "context_window": 200000, "provider": "openrouter"},
                {"id": "meta-llama/llama-3-70b-instruct", "name": "Meta Llama 3 70B", "context_window": 8000, "provider": "openrouter"},
                {"id": "google/gemini-pro", "name": "Google Gemini Pro", "context_window": 32000, "provider": "openrouter"}
            ]
    
    def _get_context_window(self, model_id: str) -> int:
        """Get context window size for a specific model"""
        context_windows = {
            "gpt-4o": 128000,
            "gpt-4-turbo": 128000,
            "gpt-4": 8192,
            "gpt-3.5-turbo": 16000,
            "claude-3-opus": 200000,
            "claude-3-sonnet": 200000,
            "claude-3-haiku": 200000
        }
        
        for model_prefix, window in context_windows.items():
            if model_id.startswith(model_prefix):
                return window
        
        return 4096  # Default value
    
    async def generate_completion(self, 
                                 messages: List[Dict[str, str]],
                                 model: Optional[str] = None,
                                 provider: Optional[str] = None,
                                 temperature: Optional[float] = None,
                                 max_tokens: Optional[int] = None,
                                 functions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a completion using the specified provider and model
        
        Args:
            messages: List of messages in the conversation
            model: Model to use
            provider: Provider to use (openai, anthropic, openrouter)
            temperature: Temperature parameter (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            functions: Optional function definitions for function calling
            
        Returns:
            Dict containing the generated completion
        """
        provider = provider or self.default_provider
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens
        
        if provider == "openai":
            return await self._generate_openai_completion(messages, model, temperature, max_tokens, functions)
        elif provider == "anthropic":
            return await self._generate_anthropic_completion(messages, model, temperature, max_tokens)
        elif provider == "openrouter":
            return await self._generate_openrouter_completion(messages, model, temperature, max_tokens, functions)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _generate_openai_completion(self,
                                        messages: List[Dict[str, str]],
                                        model: str,
                                        temperature: float,
                                        max_tokens: int,
                                        functions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate a completion using OpenAI"""
        if not self.openai_api_key:
            raise HTTPException(status_code=400, detail="OpenAI API key not configured")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if functions:
            payload["functions"] = functions
            payload["function_call"] = "auto"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract completion
                completion = {
                    "id": result.get("id"),
                    "model": result.get("model"),
                    "content": result.get("choices", [{}])[0].get("message", {}).get("content"),
                    "finish_reason": result.get("choices", [{}])[0].get("finish_reason"),
                    "usage": result.get("usage", {}),
                    "provider": "openai"
                }
                
                # Handle function calls
                if result.get("choices", [{}])[0].get("message", {}).get("function_call"):
                    completion["function_call"] = result.get("choices", [{}])[0].get("message", {}).get("function_call")
                
                return completion
        except Exception as e:
            logger.error(f"Error generating OpenAI completion: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")
    
    async def _generate_anthropic_completion(self,
                                           messages: List[Dict[str, str]],
                                           model: str,
                                           temperature: float,
                                           max_tokens: int) -> Dict[str, Any]:
        """Generate a completion using Anthropic"""
        if not self.anthropic_api_key:
            raise HTTPException(status_code=400, detail="Anthropic API key not configured")
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        # Convert from OpenAI format to Anthropic format
        anthropic_messages = []
        system_prompt = None
        
        for message in messages:
            if message["role"] == "system":
                system_prompt = message["content"]
            else:
                anthropic_messages.append({
                    "role": "assistant" if message["role"] == "assistant" else "user",
                    "content": message["content"]
                })
        
        payload = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract completion
                completion = {
                    "id": result.get("id"),
                    "model": result.get("model"),
                    "content": result.get("content", [{}])[0].get("text", ""),
                    "finish_reason": result.get("stop_reason"),
                    "usage": {
                        "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                        "output_tokens": result.get("usage", {}).get("output_tokens", 0)
                    },
                    "provider": "anthropic"
                }
                
                return completion
        except Exception as e:
            logger.error(f"Error generating Anthropic completion: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")
    
    async def _generate_openrouter_completion(self,
                                            messages: List[Dict[str, str]],
                                            model: str,
                                            temperature: float,
                                            max_tokens: int,
                                            functions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate a completion using OpenRouter"""
        if not self.openrouter_api_key:
            raise HTTPException(status_code=400, detail="OpenRouter API key not configured")
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": "https://ai-closer.com",  # Replace with your actual domain
            "X-Title": "AI Closer Bot",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if functions:
            payload["functions"] = functions
            payload["function_call"] = "auto"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Extract completion
                completion = {
                    "id": result.get("id"),
                    "model": result.get("model"),
                    "content": result.get("choices", [{}])[0].get("message", {}).get("content"),
                    "finish_reason": result.get("choices", [{}])[0].get("finish_reason"),
                    "usage": result.get("usage", {}),
                    "provider": "openrouter",
                    "latency": result.get("proxy_latency", 0)
                }
                
                # Handle function calls
                if result.get("choices", [{}])[0].get("message", {}).get("function_call"):
                    completion["function_call"] = result.get("choices", [{}])[0].get("message", {}).get("function_call")
                
                return completion
        except Exception as e:
            logger.error(f"Error generating OpenRouter completion: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating completion: {str(e)}")
    
    async def generate_text_with_cadence(self,
                                      messages: List[Dict[str, str]],
                                      model: Optional[str] = None,
                                      provider: Optional[str] = None,
                                      temperature: Optional[float] = None,
                                      max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate text with natural cadence for messaging
        
        Args:
            messages: List of messages in the conversation
            model: Model to use
            provider: Provider to use
            temperature: Temperature parameter
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict containing the generated text with cadence information
        """
        # Add system instruction for cadence
        system_instruction = """
        You are generating a response that will be sent as a text message. Instead of sending one long message, 
        break your response into multiple smaller messages where natural pauses would occur in conversation.
        
        Format your response as JSON with the following structure:
        {
            "messages": [
                {"text": "First part of the message", "delay": 0},
                {"text": "Second part after a short pause", "delay": 1.5},
                {"text": "Third part after another pause", "delay": 2}
            ]
        }
        
        Delays are in seconds and represent how long to wait after the previous message before sending this one.
        The first message should always have a delay of 0.
        """
        
        # Create messages with cadence instruction
        cadence_messages = [
            {"role": "system", "content": system_instruction}
        ]
        
        # Add user context and history
        cadence_messages.extend(messages)
        
        # Add final instruction to ensure proper formatting
        cadence_messages.append({
            "role": "user",
            "content": "Remember to format your response as JSON with messages and delays as specified."
        })
        
        # Generate completion
        result = await self.generate_completion(
            messages=cadence_messages,
            model=model,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Parse the response
        try:
            content = result.get("content", "")
            
            # Extract JSON from the response if needed
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content
            
            # Parse JSON
            cadence_data = json.loads(json_str)
            
            return {
                "id": result.get("id"),
                "model": result.get("model"),
                "messages": cadence_data.get("messages", []),
                "usage": result.get("usage", {}),
                "provider": result.get("provider")
            }
        except Exception as e:
            logger.error(f"Error parsing cadence response: {e}")
            
            # Fallback: treat the entire response as a single message
            return {
                "id": result.get("id"),
                "model": result.get("model"),
                "messages": [{"text": result.get("content", ""), "delay": 0}],
                "usage": result.get("usage", {}),
                "provider": result.get("provider")
            }
