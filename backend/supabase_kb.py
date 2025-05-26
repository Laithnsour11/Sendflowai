import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional, Union
from fastapi import HTTPException
from datetime import datetime
import uuid
import base64

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Client for interacting with Supabase for knowledge base management"""
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = supabase_url or os.environ.get("SUPABASE_URL")
        self.supabase_key = supabase_key or os.environ.get("SUPABASE_KEY", "sbp_6ea3d96a8efc1a50026610a12c4728d5b9793434")
        self.headers = {}
        
        if self.supabase_key:
            self.headers = {
                "apikey": self.supabase_key,
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json"
            }
    
    def set_credentials(self, supabase_url: str, supabase_key: str):
        """Set the Supabase credentials"""
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }

class KnowledgeBaseManager:
    """Manages knowledge base for training AI agents"""
    
    def __init__(
        self, 
        supabase_client: Optional[SupabaseClient] = None,
        openai_api_key: Optional[str] = None
    ):
        self.supabase_client = supabase_client or SupabaseClient()
        self.openai_api_key = openai_api_key
        
        # Define the table names
        self.documents_table = "kb_documents"
        self.embeddings_table = "kb_embeddings"
    
    async def add_document(
        self,
        org_id: str,
        title: str,
        content: Union[str, Dict[str, Any]],
        content_type: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a document to the knowledge base
        
        Args:
            org_id: Organization ID
            title: Title of the document
            content: Content of the document
            content_type: Type of content (document, script, faq)
            description: Optional description
            tags: Optional tags
            
        Returns:
            Dict containing the added document
        """
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Convert content to string if it's a dictionary
        if isinstance(content, dict):
            content_str = json.dumps(content)
        else:
            content_str = content
        
        # Create document object
        document = {
            "id": document_id,
            "org_id": org_id,
            "title": title,
            "description": description,
            "content_type": content_type,
            "content": content_str,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            # Insert document into Supabase
            if self.supabase_client.supabase_url and self.supabase_client.supabase_key:
                url = f"{self.supabase_client.supabase_url}/rest/v1/{self.documents_table}"
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        headers=self.supabase_client.headers,
                        json=document,
                        timeout=30.0
                    )
                    response.raise_for_status()
                
                # Generate embeddings for the document
                if self.openai_api_key:
                    await self._generate_embeddings(document_id, content_str)
                
                return document
            else:
                logger.warning("Supabase credentials not set, storing document locally")
                return document
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while adding document: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Supabase API error: {e.response.text}")
        except Exception as e:
            logger.error(f"Error adding document to knowledge base: {e}")
            return document
    
    async def search_documents(
        self,
        org_id: str,
        query: str,
        content_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 5,
        use_embeddings: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for documents in the knowledge base
        
        Args:
            org_id: Organization ID
            query: Search query
            content_type: Optional filter by content type
            tags: Optional filter by tags
            limit: Maximum number of results
            use_embeddings: Whether to use embeddings for semantic search
            
        Returns:
            List of matching documents
        """
        try:
            if use_embeddings and self.openai_api_key:
                # Use semantic search with embeddings
                return await self._semantic_search(org_id, query, content_type, tags, limit)
            else:
                # Use basic text search
                return await self._basic_search(org_id, query, content_type, tags, limit)
                
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return self._get_mock_documents(org_id, query, content_type, limit)
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        try:
            if self.supabase_client.supabase_url and self.supabase_client.supabase_key:
                url = f"{self.supabase_client.supabase_url}/rest/v1/{self.documents_table}"
                params = {"id": f"eq.{document_id}", "limit": 1}
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url,
                        headers=self.supabase_client.headers,
                        params=params,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    
                    documents = response.json()
                    if documents and len(documents) > 0:
                        document = documents[0]
                        
                        # Parse content if it's JSON
                        if document.get("content_type") in ["script", "faq"]:
                            try:
                                document["content"] = json.loads(document["content"])
                            except:
                                pass
                        
                        return document
                    
                    return None
            else:
                logger.warning("Supabase credentials not set, returning mock document")
                return self._get_mock_document(document_id)
                
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return self._get_mock_document(document_id)
    
    async def update_document(
        self,
        document_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a document
        
        Args:
            document_id: Document ID
            update_data: Data to update
            
        Returns:
            Updated document if successful, None otherwise
        """
        try:
            # Get existing document
            existing_document = await self.get_document(document_id)
            if not existing_document:
                logger.error(f"Document {document_id} not found")
                return None
            
            # Convert content to string if it's a dictionary
            if "content" in update_data and isinstance(update_data["content"], dict):
                update_data["content"] = json.dumps(update_data["content"])
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.now().isoformat()
            
            if self.supabase_client.supabase_url and self.supabase_client.supabase_key:
                url = f"{self.supabase_client.supabase_url}/rest/v1/{self.documents_table}"
                params = {"id": f"eq.{document_id}"}
                
                async with httpx.AsyncClient() as client:
                    response = await client.patch(
                        url,
                        headers=self.supabase_client.headers,
                        params=params,
                        json=update_data,
                        timeout=30.0
                    )
                    response.raise_for_status()
                
                # Re-generate embeddings if content changed
                if "content" in update_data and self.openai_api_key:
                    await self._generate_embeddings(document_id, update_data["content"])
                
                # Get updated document
                return await self.get_document(document_id)
            else:
                logger.warning("Supabase credentials not set, returning mock updated document")
                # Merge update_data with existing_document
                updated_document = {**existing_document, **update_data}
                return updated_document
                
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document
        
        Args:
            document_id: Document ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.supabase_client.supabase_url and self.supabase_client.supabase_key:
                # Delete document
                url = f"{self.supabase_client.supabase_url}/rest/v1/{self.documents_table}"
                params = {"id": f"eq.{document_id}"}
                
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        url,
                        headers=self.supabase_client.headers,
                        params=params,
                        timeout=30.0
                    )
                    response.raise_for_status()
                
                # Delete embeddings
                url = f"{self.supabase_client.supabase_url}/rest/v1/{self.embeddings_table}"
                params = {"document_id": f"eq.{document_id}"}
                
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        url,
                        headers=self.supabase_client.headers,
                        params=params,
                        timeout=30.0
                    )
                    response.raise_for_status()
                
                return True
            else:
                logger.warning("Supabase credentials not set, simulating document deletion")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    async def get_agent_knowledge(self, org_id: str, agent_type: str) -> Dict[str, Any]:
        """
        Get knowledge relevant to a specific agent type
        
        Args:
            org_id: Organization ID
            agent_type: Type of agent
            
        Returns:
            Dict containing knowledge for the agent
        """
        # Map agent types to relevant content types
        agent_to_content_types = {
            "initial_contact": ["document", "script"],
            "qualifier": ["document", "script", "faq"],
            "nurturer": ["document", "script"],
            "objection_handler": ["script", "faq"],
            "closer": ["script", "document"],
            "appointment_setter": ["script", "faq"]
        }
        
        # Get relevant content types for this agent
        content_types = agent_to_content_types.get(agent_type, ["document", "script", "faq"])
        
        # Get documents for each content type
        all_documents = []
        for content_type in content_types:
            try:
                if self.supabase_client.supabase_url and self.supabase_client.supabase_key:
                    url = f"{self.supabase_client.supabase_url}/rest/v1/{self.documents_table}"
                    params = {
                        "org_id": f"eq.{org_id}",
                        "content_type": f"eq.{content_type}",
                        "limit": 10
                    }
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            url,
                            headers=self.supabase_client.headers,
                            params=params,
                            timeout=30.0
                        )
                        response.raise_for_status()
                        
                        documents = response.json()
                        all_documents.extend(documents)
                
            except Exception as e:
                logger.error(f"Error getting documents for agent knowledge: {e}")
        
        # If no documents found or no Supabase connection, use mock data
        if not all_documents:
            all_documents = self._get_mock_agent_documents(org_id, agent_type)
        
        # Format the knowledge for the agent
        return self._format_agent_knowledge(agent_type, all_documents)
    
    async def _generate_embeddings(self, document_id: str, content: str) -> bool:
        """
        Generate embeddings for a document using OpenAI
        
        Args:
            document_id: Document ID
            content: Document content
            
        Returns:
            True if successful, False otherwise
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not set, skipping embeddings generation")
            return False
        
        try:
            # Get embeddings from OpenAI
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "input": content,
                "model": "text-embedding-ada-002"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                
                result = response.json()
                embedding = result["data"][0]["embedding"]
            
            # Store embeddings in Supabase
            if self.supabase_client.supabase_url and self.supabase_client.supabase_key:
                url = f"{self.supabase_client.supabase_url}/rest/v1/{self.embeddings_table}"
                
                embedding_data = {
                    "id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "embedding": embedding,
                    "created_at": datetime.now().isoformat()
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        headers=self.supabase_client.headers,
                        json=embedding_data,
                        timeout=30.0
                    )
                    response.raise_for_status()
                
                return True
            else:
                logger.warning("Supabase credentials not set, skipping embeddings storage")
                return False
                
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return False
    
    async def _semantic_search(
        self,
        org_id: str,
        query: str,
        content_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using semantic search with embeddings
        
        Args:
            org_id: Organization ID
            query: Search query
            content_type: Optional filter by content type
            tags: Optional filter by tags
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            # Generate query embedding
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "input": query,
                "model": "text-embedding-ada-002"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                
                result = response.json()
                query_embedding = result["data"][0]["embedding"]
            
            # Use pgvector to search for similar documents
            # This is a simplified version - in a real implementation,
            # we would use Supabase's vector search capabilities
            
            # For MVP, we'll do a basic search and return mock results
            documents = await self._basic_search(org_id, query, content_type, tags, limit)
            return documents
            
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            return self._get_mock_documents(org_id, query, content_type, limit)
    
    async def _basic_search(
        self,
        org_id: str,
        query: str,
        content_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using basic text search
        
        Args:
            org_id: Organization ID
            query: Search query
            content_type: Optional filter by content type
            tags: Optional filter by tags
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            if self.supabase_client.supabase_url and self.supabase_client.supabase_key:
                url = f"{self.supabase_client.supabase_url}/rest/v1/{self.documents_table}"
                
                # Build query parameters
                params = {
                    "org_id": f"eq.{org_id}",
                    "limit": limit
                }
                
                if content_type:
                    params["content_type"] = f"eq.{content_type}"
                
                # Add full-text search
                # Note: This assumes Supabase has full-text search enabled on the content column
                if query:
                    params["content"] = f"ilike.*{query}*"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url,
                        headers=self.supabase_client.headers,
                        params=params,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    
                    documents = response.json()
                    
                    # Parse content for JSON content types
                    for doc in documents:
                        if doc.get("content_type") in ["script", "faq"]:
                            try:
                                doc["content"] = json.loads(doc["content"])
                            except:
                                pass
                    
                    return documents
            else:
                logger.warning("Supabase credentials not set, returning mock documents")
                return self._get_mock_documents(org_id, query, content_type, limit)
                
        except Exception as e:
            logger.error(f"Error performing basic search: {e}")
            return self._get_mock_documents(org_id, query, content_type, limit)
    
    def _format_agent_knowledge(self, agent_type: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format documents as knowledge for a specific agent type"""
        formatted_knowledge = {
            "examples": [],
            "guidelines": {},
            "common_scenarios": {}
        }
        
        for doc in documents:
            content_type = doc.get("content_type")
            
            # Parse content if it's still a string
            content = doc.get("content")
            if isinstance(content, str) and content_type in ["script", "faq"]:
                try:
                    content = json.loads(content)
                except:
                    content = {"error": "Failed to parse JSON content"}
            
            # Add to appropriate section based on content type
            if content_type == "script":
                if isinstance(content, dict):
                    for scenario, response in content.items():
                        formatted_knowledge["examples"].append({
                            "scenario": scenario,
                            "response": response
                        })
                else:
                    # Add as guideline if not a dict
                    formatted_knowledge["guidelines"][doc.get("title")] = content
                    
            elif content_type == "faq":
                if isinstance(content, dict):
                    formatted_knowledge["common_scenarios"].update(content)
                else:
                    # Add as guideline if not a dict
                    formatted_knowledge["guidelines"][doc.get("title")] = content
                    
            elif content_type == "document":
                formatted_knowledge["guidelines"][doc.get("title")] = content
        
        return formatted_knowledge
    
    def _get_mock_document(self, document_id: str) -> Dict[str, Any]:
        """Get a mock document for testing without Supabase"""
        return {
            "id": document_id,
            "org_id": "org123",
            "title": "Mock Document",
            "description": "This is a mock document for testing",
            "content_type": "document",
            "content": "This is the content of the mock document",
            "tags": ["mock", "test"],
            "created_at": "2023-01-15T10:30:00Z",
            "updated_at": "2023-01-15T10:30:00Z"
        }
    
    def _get_mock_documents(
        self,
        org_id: str,
        query: str,
        content_type: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get mock documents for testing without Supabase"""
        # Create different mock documents based on the query
        mock_documents = [
            {
                "id": str(uuid.uuid4()),
                "org_id": org_id,
                "title": "Luxury Property Sales Guide",
                "description": "Best practices for selling luxury properties",
                "content_type": "document",
                "content": "This guide covers strategies for marketing luxury properties...",
                "tags": ["luxury", "sales", "guide"],
                "created_at": "2023-01-10T10:30:00Z",
                "updated_at": "2023-01-10T10:30:00Z"
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
                "tags": ["first-time", "buyer", "faq"],
                "created_at": "2023-01-15T10:30:00Z",
                "updated_at": "2023-01-15T10:30:00Z"
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
                "tags": ["objection", "scripts", "sales"],
                "created_at": "2023-01-20T10:30:00Z",
                "updated_at": "2023-01-20T10:30:00Z"
            },
            {
                "id": str(uuid.uuid4()),
                "org_id": org_id,
                "title": "Downtown Market Report 2023",
                "description": "Comprehensive market analysis for downtown properties",
                "content_type": "document",
                "content": "This report analyzes the downtown real estate market trends for 2023...",
                "tags": ["market", "report", "downtown"],
                "created_at": "2023-02-05T10:30:00Z",
                "updated_at": "2023-02-05T10:30:00Z"
            }
        ]
        
        # Filter by content type if specified
        if content_type:
            filtered_docs = [d for d in mock_documents if d["content_type"] == content_type]
        else:
            filtered_docs = mock_documents
        
        # Simple keyword-based filtering based on query
        if query:
            query_lower = query.lower()
            results = []
            
            for doc in filtered_docs:
                title_match = query_lower in doc["title"].lower()
                desc_match = query_lower in doc["description"].lower()
                
                content_match = False
                if isinstance(doc["content"], str):
                    content_match = query_lower in doc["content"].lower()
                elif isinstance(doc["content"], dict):
                    # Check keys and values for dictionary content
                    for k, v in doc["content"].items():
                        if query_lower in k.lower() or query_lower in v.lower():
                            content_match = True
                            break
                
                if title_match or desc_match or content_match:
                    results.append(doc)
            
            return results[:limit]
        
        # If no query, return all filtered docs up to the limit
        return filtered_docs[:limit]
    
    def _get_mock_agent_documents(self, org_id: str, agent_type: str) -> List[Dict[str, Any]]:
        """Get mock documents for a specific agent type"""
        if agent_type == "initial_contact":
            return [
                {
                    "id": str(uuid.uuid4()),
                    "org_id": org_id,
                    "title": "Initial Contact Best Practices",
                    "description": "Guidelines for making first contact with leads",
                    "content_type": "document",
                    "content": "When making initial contact with a lead, focus on building rapport and understanding their needs...",
                    "tags": ["initial", "contact", "guide"],
                    "created_at": "2023-01-10T10:30:00Z"
                },
                {
                    "id": str(uuid.uuid4()),
                    "org_id": org_id,
                    "title": "Introduction Scripts",
                    "description": "Scripts for introducing yourself to new leads",
                    "content_type": "script",
                    "content": {
                        "Cold call": "Hi [Name], this is [Your Name] from [Company]. I noticed you were looking at properties in [Area]. Is this a good time to chat briefly about your real estate needs?",
                        "Website lead": "Hi [Name], this is [Your Name] from [Company]. I received your inquiry from our website about [Property/Area]. I'd love to learn more about what you're looking for."
                    },
                    "tags": ["introduction", "scripts"],
                    "created_at": "2023-01-15T10:30:00Z"
                }
            ]
        elif agent_type == "qualifier":
            return [
                {
                    "id": str(uuid.uuid4()),
                    "org_id": org_id,
                    "title": "Lead Qualification Guide",
                    "description": "Complete guide to qualifying real estate leads",
                    "content_type": "document",
                    "content": "Proper lead qualification involves understanding the lead's needs, timeline, budget, and motivation...",
                    "tags": ["qualification", "guide"],
                    "created_at": "2023-01-20T10:30:00Z"
                },
                {
                    "id": str(uuid.uuid4()),
                    "org_id": org_id,
                    "title": "Qualification Questions",
                    "description": "Essential questions for qualifying leads",
                    "content_type": "faq",
                    "content": {
                        "What is your timeline for buying/selling?": "This helps determine urgency and prioritize leads.",
                        "What is your budget range?": "This helps narrow down property options and determine financing needs.",
                        "Have you been pre-approved for financing?": "This indicates seriousness and readiness to proceed.",
                        "What are your must-have features?": "This helps identify property requirements and deal-breakers."
                    },
                    "tags": ["qualification", "questions"],
                    "created_at": "2023-01-25T10:30:00Z"
                }
            ]
        elif agent_type == "objection_handler":
            return [
                {
                    "id": str(uuid.uuid4()),
                    "org_id": org_id,
                    "title": "Objection Handling Guide",
                    "description": "Strategies for handling common objections",
                    "content_type": "document",
                    "content": "When handling objections, listen carefully, acknowledge the concern, provide information, and check for resolution...",
                    "tags": ["objection", "guide"],
                    "created_at": "2023-02-05T10:30:00Z"
                },
                {
                    "id": str(uuid.uuid4()),
                    "org_id": org_id,
                    "title": "Common Objections and Responses",
                    "description": "Scripts for handling frequent objections",
                    "content_type": "script",
                    "content": {
                        "The price is too high": "I understand price is a concern. Let's look at the comparable properties in the area to see how this one is priced relative to the market.",
                        "I need to think about it": "I understand you want to make the right decision. What specific aspects do you need more time to consider?",
                        "I want to see other properties first": "That's a smart approach. I can help arrange viewings of similar properties so you can make a confident comparison."
                    },
                    "tags": ["objection", "scripts"],
                    "created_at": "2023-02-10T10:30:00Z"
                }
            ]
        else:
            return [
                {
                    "id": str(uuid.uuid4()),
                    "org_id": org_id,
                    "title": "General Real Estate Guide",
                    "description": "General information about real estate",
                    "content_type": "document",
                    "content": "This guide covers various aspects of the real estate process...",
                    "tags": ["general", "guide"],
                    "created_at": "2023-01-05T10:30:00Z"
                }
            ]
