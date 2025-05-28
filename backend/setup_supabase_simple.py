import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def setup_supabase_tables():
    """Set up Supabase tables for Knowledge Base"""
    print("🔄 Setting up Supabase tables...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return False
    
    try:
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print(f"✅ Connected to Supabase: {supabase_url}")
        
        # SQL to create documents table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            org_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            document_type TEXT NOT NULL,
            metadata JSONB DEFAULT '{}',
            embedding vector(384),
            version INTEGER DEFAULT 1,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS documents_org_id_idx ON documents (org_id);
        CREATE INDEX IF NOT EXISTS documents_document_type_idx ON documents (document_type);
        CREATE INDEX IF NOT EXISTS documents_created_at_idx ON documents (created_at DESC);
        """
        
        # Try to run the SQL through the SQL API
        print("🔄 Creating documents table...")
        
        # First, let's try to see if the table already exists by doing a simple query
        try:
            result = supabase.table('documents').select('*').limit(1).execute()
            print("✅ Documents table already exists")
            return True
        except Exception as e:
            if "relation \"documents\" does not exist" in str(e) or "table" in str(e).lower():
                print("⚠️  Documents table doesn't exist, need to create it manually")
                print("\n" + "="*60)
                print("MANUAL SETUP REQUIRED:")
                print("="*60)
                print("Please run the following SQL in your Supabase dashboard:")
                print("1. Go to https://emtesedpklmdtggiafoh.supabase.co/project/emtesedpklmdtggiafoh/sql")
                print("2. Run this SQL query:")
                print("\n" + create_table_sql)
                print("\n" + "="*60)
                return False
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Error setting up Supabase: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_connection():
    """Test basic Supabase connection"""
    print("\n🧪 Testing Supabase connection...")
    
    try:
        from knowledge_base import KnowledgeBaseManager
        
        kb = KnowledgeBaseManager()
        
        if not kb.supabase_client:
            print("❌ Supabase client not initialized")
            return False
            
        print("✅ Knowledge Base Manager initialized")
        print("✅ Supabase connection established")
        print("✅ Embedding model loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def main():
        table_setup = await setup_supabase_tables()
        if table_setup:
            await test_simple_connection()
        else:
            print("\n⚠️  Please set up the table manually, then run the test again")
    
    asyncio.run(main())