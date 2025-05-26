import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid
import httpx
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client

logger = logging.getLogger(__name__)

class KnowledgeBaseManager:
    """Manages knowledge base with Supabase and pgvector integration"""
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        self.supabase_url = supabase_url or os.environ.get('SUPABASE_URL')
        self.supabase_key = supabase_key or os.environ.get('SUPABASE_KEY')
        self.model_name = "all-MiniLM-L6-v2"  # 384 dimensions
        self.supabase_client = None
        self.embedding_model = None
        
        # Initialize if keys are available
        if self.supabase_url and self.supabase_key:
            self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Supabase client and embedding model"""
        try:
            self.supabase_client = create_client(self.supabase_url, self.supabase_key)
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info("Knowledge base clients initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing knowledge base clients: {e}")
            raise HTTPException(status_code=500, detail=f"Knowledge base initialization error: {str(e)}")
    
    def set_api_keys(self, supabase_url: str, supabase_key: str):
        """Set API keys and initialize clients"""
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self._initialize_clients()
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for the given text"""
        if not self.embedding_model:
            raise HTTPException(status_code=400, detail="Embedding model not initialized")
        
        try:
            embedding = self.embedding_model.encode(text).tolist()
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise HTTPException(status_code=500, detail=f"Embedding generation error: {str(e)}")
    
    async def add_document(self, 
                          org_id: str, 
                          title: str, 
                          content: str,
                          document_type: str,
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add a document to the knowledge base
        
        Args:
            org_id: Organization ID
            title: Document title
            content: Document content
            document_type: Type of document (sop, script, training, etc.)
            metadata: Additional metadata
            
        Returns:
            Dict containing the added document info
        """
        if not self.supabase_client:
            raise HTTPException(status_code=400, detail="Supabase client not initialized")
        
        try:
            # Generate embedding
            embedding = await self._generate_embedding(content)
            
            # Prepare document data
            document_data = {
                "id": str(uuid.uuid4()),
                "org_id": org_id,
                "title": title,
                "content": content,
                "document_type": document_type,
                "metadata": metadata or {},
                "embedding": embedding,
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insert into Supabase
            result = self.supabase_client.table('documents').insert(document_data).execute()
            
            return result.data[0] if result.data else document_data
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")
    
    async def search_documents(self, 
                              org_id: str,
                              query: str,
                              document_type: Optional[str] = None,
                              limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents using vector similarity
        
        Args:
            org_id: Organization ID
            query: Search query
            document_type: Optional filter by document type
            limit: Maximum number of results
            
        Returns:
            List of matching documents with similarity scores
        """
        if not self.supabase_client:
            raise HTTPException(status_code=400, detail="Supabase client not initialized")
        
        try:
            # Generate embedding for query
            query_embedding = await self._generate_embedding(query)
            
            # Search using RPC
            rpc_params = {
                "org_id_input": org_id,
                "query_embedding": query_embedding,
                "match_count": limit,
                "document_type_filter": document_type
            }
            
            result = self.supabase_client.rpc('match_documents', rpc_params).execute()
            
            if result.data:
                # Format results
                formatted_results = []
                for doc in result.data:
                    formatted_doc = {
                        "id": doc.get("id"),
                        "title": doc.get("title"),
                        "content": doc.get("content"),
                        "document_type": doc.get("document_type"),
                        "metadata": doc.get("metadata", {}),
                        "version": doc.get("version"),
                        "similarity": doc.get("similarity"),
                        "created_at": doc.get("created_at")
                    }
                    formatted_results.append(formatted_doc)
                return formatted_results
            return []
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")
    
    async def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get a specific document by ID"""
        if not self.supabase_client:
            raise HTTPException(status_code=400, detail="Supabase client not initialized")
        
        try:
            result = self.supabase_client.table('documents').select('*').eq('id', document_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Document not found")
            
            return result.data[0]
        except Exception as e:
            logger.error(f"Error retrieving document: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")
    
    async def update_document(self, 
                             document_id: str, 
                             title: Optional[str] = None,
                             content: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update a document in the knowledge base
        
        Args:
            document_id: Document ID
            title: Optional new title
            content: Optional new content
            metadata: Optional new metadata
            
        Returns:
            Updated document
        """
        if not self.supabase_client:
            raise HTTPException(status_code=400, detail="Supabase client not initialized")
        
        try:
            # Get current document to update version
            current_doc = await self.get_document(document_id)
            
            # Prepare update data
            update_data = {
                "updated_at": datetime.now().isoformat(),
                "version": (current_doc.get("version") or 1) + 1
            }
            
            if title is not None:
                update_data["title"] = title
                
            if metadata is not None:
                update_data["metadata"] = metadata
                
            if content is not None:
                update_data["content"] = content
                # Generate new embedding if content changed
                update_data["embedding"] = await self._generate_embedding(content)
            
            # Update in Supabase
            result = self.supabase_client.table('documents').update(update_data).eq('id', document_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="Document not found or update failed")
            
            return result.data[0]
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document from the knowledge base"""
        if not self.supabase_client:
            raise HTTPException(status_code=400, detail="Supabase client not initialized")
        
        try:
            result = self.supabase_client.table('documents').delete().eq('id', document_id).execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
    
    async def list_documents(self, 
                            org_id: str, 
                            document_type: Optional[str] = None,
                            skip: int = 0,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """
        List documents in the knowledge base
        
        Args:
            org_id: Organization ID
            document_type: Optional filter by document type
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of documents
        """
        if not self.supabase_client:
            raise HTTPException(status_code=400, detail="Supabase client not initialized")
        
        try:
            query = self.supabase_client.table('documents').select('*').eq('org_id', org_id)
            
            if document_type:
                query = query.eq('document_type', document_type)
                
            # Apply pagination
            query = query.range(skip, skip + limit - 1).order('created_at', desc=True)
            
            result = query.execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")
