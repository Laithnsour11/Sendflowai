import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_knowledge_base():
    """Test the knowledge base functionality and create initial schema"""
    print("\n🧪 Testing Knowledge Base functionality...")
    
    try:
        # Import our knowledge base manager
        from knowledge_base import KnowledgeBaseManager
        
        # Initialize the knowledge base manager
        kb_manager = KnowledgeBaseManager()
        
        print("✅ Knowledge Base Manager initialized successfully")
        
        # Test adding a document (this will create the table if it doesn't exist)
        print("🔄 Testing document addition...")
        test_doc = await kb_manager.add_document(
            org_id="test_org_123",
            title="Real Estate Objection Handling Guide",
            content="When a client says the price is too high, acknowledge their concern and provide market analysis data to justify the pricing. Always listen first, then provide value-based responses.",
            document_type="script",
            metadata={"category": "objection_handling", "priority": "high"}
        )
        
        print(f"✅ Successfully added document: {test_doc.get('title')}")
        
        # Test searching documents
        print("🔄 Testing document search...")
        search_results = await kb_manager.search_documents(
            org_id="test_org_123",
            query="price objection handling",
            limit=3
        )
        
        print(f"✅ Search returned {len(search_results)} results")
        for doc in search_results:
            print(f"   - {doc.get('title')} (similarity: {doc.get('similarity', 'N/A')})")
        
        # Test listing documents
        print("🔄 Testing document listing...")
        documents = await kb_manager.list_documents("test_org_123", limit=5)
        print(f"✅ Found {len(documents)} documents for organization")
        
        # Add a few more test documents for a realistic knowledge base
        print("🔄 Adding additional test documents...")
        
        additional_docs = [
            {
                "title": "Lead Qualification Script",
                "content": "Start by asking about their timeline, budget, and specific requirements. Use open-ended questions to understand their motivation for moving.",
                "document_type": "script",
                "metadata": {"category": "qualification", "priority": "high"}
            },
            {
                "title": "Follow-up Email Templates",
                "content": "Template 1: Thank you for your time today. As promised, I've attached the property details we discussed. Template 2: I wanted to follow up on the properties I showed you yesterday.",
                "document_type": "template",
                "metadata": {"category": "follow_up", "priority": "medium"}
            },
            {
                "title": "Market Analysis Guidelines",
                "content": "When preparing market analysis, include comparable sales from the last 6 months within 1 mile radius. Focus on similar square footage, lot size, and amenities.",
                "document_type": "guideline",
                "metadata": {"category": "analysis", "priority": "high"}
            }
        ]
        
        for doc_data in additional_docs:
            doc = await kb_manager.add_document(
                org_id="test_org_123",
                **doc_data
            )
            print(f"   ✅ Added: {doc.get('title')}")
        
        # Test different types of searches
        print("🔄 Testing various search queries...")
        
        search_queries = [
            "qualification questions",
            "follow up email",
            "market analysis",
            "objection handling"
        ]
        
        for query in search_queries:
            results = await kb_manager.search_documents(
                org_id="test_org_123",
                query=query,
                limit=2
            )
            print(f"   📝 Query '{query}': {len(results)} results")
        
        print("🎉 Knowledge Base is fully operational!")
        return True
        
    except Exception as e:
        print(f"❌ Knowledge Base test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_knowledge_base())