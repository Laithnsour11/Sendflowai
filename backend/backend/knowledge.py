import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import os

logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    """Manages knowledge base for training AI agents"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
    
    async def add_knowledge_item(self, org_id: str, title: str, content: Union[str, Dict[str, Any]], content_type: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Add an item to the knowledge base
        
        Args:
            org_id: Organization ID
            title: Title of the knowledge item
            content: Content of the knowledge item
            content_type: Type of content (document, script, faq)
            description: Optional description
            
        Returns:
            Dict containing the added knowledge item
        """
        item_id = str(uuid.uuid4())
        
        knowledge_item = {
            "id": item_id,
            "org_id": org_id,
            "title": title,
            "description": description,
            "content_type": content_type,
            "content": content,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # In a real implementation, this would be stored in a database
        # For MVP, we'll log it
        logger.info(f"Added knowledge item: {json.dumps(knowledge_item, default=str)}")
        
        return knowledge_item
    
    async def search_knowledge_base(self, org_id: str, query: str, content_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the knowledge base
        
        Args:
            org_id: Organization ID
            query: Search query
            content_type: Optional filter by content type
            limit: Maximum number of results
            
        Returns:
            List of relevant knowledge items
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not set, returning mock knowledge items")
            return self._get_mock_knowledge_items(org_id, query, content_type, limit)
        
        # In a real implementation, this would use vector search
        # For MVP, we'll return mock items
        return self._get_mock_knowledge_items(org_id, query, content_type, limit)
    
    def _get_mock_knowledge_items(self, org_id: str, query: str, content_type: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Generate mock knowledge items for testing without API keys"""
        # Mock knowledge items
        mock_items = [
            {
                "id": str(uuid.uuid4()),
                "org_id": org_id,
                "title": "Luxury Property Sales Guide",
                "description": "Best practices for selling luxury properties",
                "content_type": "document",
                "content": "This guide covers strategies for marketing luxury properties...",
                "created_at": "2023-01-10T10:30:00Z"
            },
            {
                "id": str(uuid.uuid4()),
                "org_id": org_id,
                "title": "First-Time Buyer FAQs",
                "description": "Common questions from first-time homebuyers",
                "content_type": "faq",
                "content": {
                    "What is a down payment?": "A down payment is the initial payment made when purchasing a home...",
                    "How much do I need for a down payment?": "Typically, you need 3-20% of the purchase price..."
                },
                "created_at": "2023-01-15T10:30:00Z"
            },
            {
                "id": str(uuid.uuid4()),
                "org_id": org_id,
                "title": "Objection Handling Scripts",
                "description": "Scripts for handling common real estate objections",
                "content_type": "script",
                "content": {
                    "Price too high": "I understand your concern about the price. Many buyers initially feel the same way...",
                    "Need to sell current home first": "That's a common situation. There are several ways we can approach this..."
                },
                "created_at": "2023-01-20T10:30:00Z"
            },
            {
                "id": str(uuid.uuid4()),
                "org_id": org_id,
                "title": "Downtown Market Report 2023",
                "description": "Comprehensive market analysis for downtown properties",
                "content_type": "document",
                "content": "This report analyzes the downtown real estate market trends for 2023...",
                "created_at": "2023-02-05T10:30:00Z"
            }
        ]
        
        # Filter by content type if specified
        if content_type:
            filtered_items = [i for i in mock_items if i["content_type"] == content_type]
        else:
            filtered_items = mock_items
        
        # Simple keyword-based search for MVP
        query_lower = query.lower()
        
        if "luxury" in query_lower:
            return [i for i in filtered_items if "luxury" in i["title"].lower() or (isinstance(i["description"], str) and "luxury" in i["description"].lower())]
        elif "faq" in query_lower or "question" in query_lower:
            return [i for i in filtered_items if i["content_type"] == "faq"]
        elif "objection" in query_lower or "script" in query_lower:
            return [i for i in filtered_items if i["content_type"] == "script"]
        elif "market" in query_lower or "report" in query_lower:
            return [i for i in filtered_items if "market" in i["title"].lower() or (isinstance(i["description"], str) and "market" in i["description"].lower())]
        
        # Return all items if no specific matches, limited by the specified limit
        return filtered_items[:limit]
    
    async def get_training_data(self, org_id: str) -> Dict[str, Any]:
        """
        Get formatted training data for AI agents
        
        Args:
            org_id: Organization ID
            
        Returns:
            Dict containing training data for different agent types
        """
        # Get all knowledge items for the organization
        all_items = await self._get_mock_knowledge_items(org_id, "", None, 100)
        
        # Format training data for different agent types
        training_data = {
            "initial_contact": self._format_training_data_for_agent("initial_contact", all_items),
            "qualifier": self._format_training_data_for_agent("qualifier", all_items),
            "nurturer": self._format_training_data_for_agent("nurturer", all_items),
            "objection_handler": self._format_training_data_for_agent("objection_handler", all_items),
            "closer": self._format_training_data_for_agent("closer", all_items),
            "appointment_setter": self._format_training_data_for_agent("appointment_setter", all_items)
        }
        
        return training_data
    
    def _format_training_data_for_agent(self, agent_type: str, knowledge_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format knowledge items as training data for a specific agent type"""
        # Different agent types need different types of knowledge
        if agent_type == "objection_handler":
            # Focus on scripts and FAQs
            relevant_items = [i for i in knowledge_items if i["content_type"] in ["script", "faq"]]
        elif agent_type == "qualifier":
            # Focus on FAQs and documents
            relevant_items = [i for i in knowledge_items if i["content_type"] in ["faq", "document"]]
        else:
            # Use all items
            relevant_items = knowledge_items
        
        # Extract and format content
        formatted_data = {
            "examples": [],
            "guidelines": {},
            "common_scenarios": {}
        }
        
        for item in relevant_items:
            # Add to appropriate section based on content type
            if item["content_type"] == "script":
                if isinstance(item["content"], dict):
                    formatted_data["examples"].extend([
                        {"scenario": scenario, "response": response}
                        for scenario, response in item["content"].items()
                    ])
            elif item["content_type"] == "faq":
                if isinstance(item["content"], dict):
                    formatted_data["common_scenarios"].update(item["content"])
            elif item["content_type"] == "document":
                # For documents, just add the title as a guideline with the content
                formatted_data["guidelines"][item["title"]] = item["content"] if isinstance(item["content"], str) else str(item["content"])
        
        return formatted_data
