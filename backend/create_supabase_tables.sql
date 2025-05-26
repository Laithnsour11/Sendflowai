-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table for knowledge base
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY,
  org_id UUID NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  document_type TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  embedding vector(384) NOT NULL,
  version INTEGER DEFAULT 1,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for organization ID lookups
CREATE INDEX IF NOT EXISTS idx_documents_org_id ON documents(org_id);

-- Create index for document type lookups
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type);

-- Create index for metadata lookups
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents USING GIN (metadata);

-- Create vector similarity search index
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create function for vector similarity search
CREATE OR REPLACE FUNCTION match_documents(
  org_id_input UUID,
  query_embedding vector(384),
  match_count INTEGER,
  document_type_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  org_id UUID,
  title TEXT,
  content TEXT,
  document_type TEXT,
  metadata JSONB,
  version INTEGER,
  similarity FLOAT,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    d.id,
    d.org_id,
    d.title,
    d.content,
    d.document_type,
    d.metadata,
    d.version,
    1 - (d.embedding <=> query_embedding) AS similarity,
    d.created_at,
    d.updated_at
  FROM
    documents d
  WHERE
    d.org_id = org_id_input
    AND (document_type_filter IS NULL OR d.document_type = document_type_filter)
  ORDER BY
    d.embedding <=> query_embedding
  LIMIT
    match_count;
END;
$$ LANGUAGE plpgsql;

-- Create agent_training table
CREATE TABLE IF NOT EXISTS agent_training (
  id UUID PRIMARY KEY,
  org_id UUID NOT NULL,
  agent_type TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  system_prompt TEXT,
  configuration JSONB DEFAULT '{}',
  version INTEGER DEFAULT 1,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for organization ID lookups in agent_training
CREATE INDEX IF NOT EXISTS idx_agent_training_org_id ON agent_training(org_id);

-- Create index for agent type lookups
CREATE INDEX IF NOT EXISTS idx_agent_training_agent_type ON agent_training(agent_type);

-- Create model_versions table for fine-tuned models
CREATE TABLE IF NOT EXISTS model_versions (
  id UUID PRIMARY KEY,
  org_id UUID NOT NULL,
  name TEXT NOT NULL,
  base_model TEXT NOT NULL,
  fine_tuned_model_id TEXT,
  training_file_id TEXT,
  status TEXT DEFAULT 'pending',
  metrics JSONB DEFAULT '{}',
  configuration JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for organization ID lookups in model_versions
CREATE INDEX IF NOT EXISTS idx_model_versions_org_id ON model_versions(org_id);

-- Create conversation_analytics table
CREATE TABLE IF NOT EXISTS conversation_analytics (
  id UUID PRIMARY KEY,
  org_id UUID NOT NULL,
  lead_id UUID NOT NULL,
  conversation_id UUID NOT NULL,
  agent_type TEXT NOT NULL,
  channel TEXT NOT NULL,
  duration_seconds INTEGER,
  message_count INTEGER,
  sentiment_score FLOAT,
  effectiveness_score FLOAT,
  metrics JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for organization ID lookups in conversation_analytics
CREATE INDEX IF NOT EXISTS idx_conversation_analytics_org_id ON conversation_analytics(org_id);

-- Create index for lead ID lookups
CREATE INDEX IF NOT EXISTS idx_conversation_analytics_lead_id ON conversation_analytics(lead_id);
