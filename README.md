# AI Closer - Next-Generation Lead Conversion Platform

AI Closer is a sophisticated AI-powered omnichannel communication platform designed specifically for real estate lead conversion. The platform integrates with Go High Level (GHL) and combines cutting-edge AI technologies including OpenRouter for diverse LLM access, Vapi.ai for voice, Mem0 for persistent memory, and implements multi-agent orchestration patterns.

## Core Features

### 1. Multi-LLM Support via OpenRouter
- Access to a diverse range of AI models (OpenAI, Anthropic, Meta, Google, etc.)
- Dynamic model selection for different agent types
- Flexible configuration for temperature, presence penalty, and more

### 2. Multi-Agent Conversation System
- Specialized agents for different stages of the sales process:
  - Initial Contact Agent
  - Qualification Agent
  - Nurturing Agent
  - Objection Handler Agent
  - Closing Agent
  - Appointment Setting Agent
- Intelligent agent selection based on conversation context

### 3. Persistent Memory System
- Multi-layered memory architecture (factual, emotional, strategic, contextual)
- Cross-conversation context preservation
- Comprehensive lead profiles with AI-generated insights

### 4. Knowledge Base
- Document storage with vector embeddings
- Semantic search capabilities
- Training materials for AI agents

### 5. GHL Integration
- Seamless lead synchronization
- Custom field management
- Webhook processing

### 6. Voice & SMS Capabilities
- Vapi.ai integration for natural voice conversations
- SMS/MMS with intelligent multi-text cadence

## Technology Stack

- **Frontend**: Next.js with React, Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: MongoDB for document storage, Supabase with pgvector for knowledge base
- **AI Integrations**: OpenRouter, OpenAI, Anthropic, Vapi.ai, Mem0
- **CRM Integration**: Go High Level (GHL)

## Getting Started

### Prerequisites
- Node.js and npm/yarn
- Python 3.8+
- MongoDB
- Supabase account with pgvector extension

### Installation

1. Clone the repository
```bash
git clone https://github.com/laithnsour11/Sendflowai.git
cd Sendflowai
```

2. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies
```bash
cd frontend
yarn install
```

4. Configure environment variables
- Create `.env` files in both the `/backend` and `/frontend` directories
- Set up the required API keys and configuration values

5. Start the services
```bash
# Start backend
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001

# Start frontend
cd frontend
yarn start
```

## API Keys Required

The platform requires the following API keys, which can be configured in the Settings page:

1. **Language Model APIs**
   - OpenAI API Key
   - Anthropic API Key
   - OpenRouter API Key

2. **Communication APIs**
   - Vapi.ai API Key
   - SendBlue API Key

3. **Integration & Memory APIs**
   - Go High Level API Key
   - Mem0 API Key

## Architecture

The platform is built on a modular architecture with the following key components:

### Backend Services

- **LLM Service**: Abstracted layer for interacting with multiple AI providers
- **Knowledge Base Manager**: Handles document storage, embedding generation, and semantic search
- **Memory System**: Manages persistent memory across conversations
- **Multi-Agent Orchestrator**: Coordinates specialized agents based on context
- **GHL Integration**: Synchronizes data with Go High Level

### Frontend Components

- **Dashboard**: Overview of leads, conversations, and key metrics
- **Leads Management**: View and manage lead profiles
- **Conversation Interface**: Track and analyze conversations
- **Knowledge Base UI**: Manage training documents for AI agents
- **Agent Training**: Configure specialized agents with different LLMs
- **Settings**: Manage API keys and system configuration

## Development Roadmap

### Phase 1: Core Intelligence & Memory (Current)
- ✅ Full OpenRouter integration for diverse LLM access
- 🔄 Complete Mem0 integration for persistent memory
- 🔄 Full multi-agent system with LangChain

### Phase 2: Omni-Channel Communication
- 🔄 Vapi.ai integration for voice capabilities
- 🔄 SendBlue integration for SMS/MMS
- 🔄 Smart campaign management

### Phase 3: Advanced Learning & Analytics
- 🔄 Enhanced analytics dashboard
- 🔄 Fine-tuning capabilities
- 🔄 RLHF feedback mechanisms

### Phase 4: Platform Polish
- 🔄 Proactive engagement engine
- 🔄 Explainability layer
- 🔄 Advanced simulation environment

## License

[MIT](LICENSE)

## Contact

For more information, please contact [your-email@example.com](mailto:your-email@example.com).
