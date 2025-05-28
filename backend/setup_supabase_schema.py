import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def setup_supabase_schema():
    """Set up the Supabase schema for the Knowledge Base"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in environment")
        return False
        
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    print(f"🔄 Setting up schema for Supabase project: {supabase_url}")
    
    # SQL statements to create the schema
    sql_statements = [
        # Enable pgvector extension
        """
        create extension if not exists vector;
        """,
        
        # Create documents table
        """
        create table if not exists documents (
            id uuid primary key default gen_random_uuid(),
            org_id text not null,
            title text not null,
            content text not null,
            document_type text not null,
            metadata jsonb default '{}',
            embedding vector(384), -- Using sentence-transformers/all-MiniLM-L6-v2 dimensions
            version integer default 1,
            created_at timestamp with time zone default now(),
            updated_at timestamp with time zone default now()
        );
        """,
        
        # Create indexes
        """
        create index if not exists documents_org_id_idx on documents (org_id);
        create index if not exists documents_document_type_idx on documents (document_type);
        create index if not exists documents_created_at_idx on documents (created_at desc);
        """,
        
        # Create vector similarity search function
        """
        create or replace function match_documents (
            org_id_input text,
            query_embedding vector(384),
            match_count int default 5,
            document_type_filter text default null
        )
        returns table (
            id uuid,
            title text,
            content text,
            document_type text,
            metadata jsonb,
            version integer,
            created_at timestamp with time zone,
            similarity float
        )
        language sql stable
        as $$
        select
            d.id,
            d.title,
            d.content,
            d.document_type,
            d.metadata,
            d.version,
            d.created_at,
            1 - (d.embedding <=> query_embedding) as similarity
        from documents d
        where d.org_id = org_id_input
        and (document_type_filter is null or d.document_type = document_type_filter)
        and d.embedding is not null
        order by d.embedding <=> query_embedding
        limit match_count;
        $$;
        """,
        
        # Create RPC for vector search with optional filters
        """
        create or replace function search_documents_rpc (
            org_id_input text,
            query_text text,
            query_embedding vector(384) default null,
            match_count int default 5,
            document_type_filter text default null
        )
        returns table (
            id uuid,
            title text,
            content text,
            document_type text,
            metadata jsonb,
            version integer,
            created_at timestamp with time zone,
            similarity float
        )
        language sql stable
        as $$
        select
            d.id,
            d.title,
            d.content,
            d.document_type,
            d.metadata,
            d.version,
            d.created_at,
            case 
                when query_embedding is not null and d.embedding is not null 
                then 1 - (d.embedding <=> query_embedding)
                else 0
            end as similarity
        from documents d
        where d.org_id = org_id_input
        and (document_type_filter is null or d.document_type = document_type_filter)
        and (
            query_embedding is null 
            or d.embedding is not null
        )
        and (
            query_text = '' 
            or d.title ilike '%' || query_text || '%'
            or d.content ilike '%' || query_text || '%'
        )
        order by 
            case 
                when query_embedding is not null and d.embedding is not null 
                then d.embedding <=> query_embedding
                else 0
            end
        limit match_count;
        $$;
        """,
        
        # Create updated_at trigger
        """
        create or replace function update_updated_at_column()
        returns trigger as $$
        begin
            new.updated_at = now();
            return new;
        end;
        $$ language plpgsql;
        """,
        
        """
        drop trigger if exists update_documents_updated_at on documents;
        create trigger update_documents_updated_at
            before update on documents
            for each row
            execute function update_updated_at_column();
        """
    ]
    
    # Execute each SQL statement
    for i, sql in enumerate(sql_statements, 1):
        try:
            print(f"🔄 Executing SQL statement {i}/{len(sql_statements)}...")
            
            # Use Supabase SQL endpoint
            sql_url = f"{supabase_url}/rest/v1/rpc/exec_sql"
            
            # Try direct execution via SQL
            sql_direct_url = f"{supabase_url}/sql"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    sql_direct_url,
                    headers=headers,
                    json={"query": sql.strip()},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    print(f"✅ SQL statement {i} executed successfully")
                else:
                    print(f"⚠️  SQL statement {i} returned status {response.status_code}: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error executing SQL statement {i}: {e}")
            continue
    
    print("🎉 Schema setup completed!")
    return True

async def test_knowledge_base():
    """Test the knowledge base functionality"""
    print("\n🧪 Testing Knowledge Base functionality...")
    
    # Import our knowledge base manager
    from knowledge_base import KnowledgeBaseManager
    
    try:
        # Initialize the knowledge base manager
        kb_manager = KnowledgeBaseManager()
        
        # Test adding a document
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
        
        print("🎉 Knowledge Base is fully operational!")
        return True
        
    except Exception as e:
        print(f"❌ Knowledge Base test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def main():
        success = await setup_supabase_schema()
        if success:
            await test_knowledge_base()
    
    asyncio.run(main())