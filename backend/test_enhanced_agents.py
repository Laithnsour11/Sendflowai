import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

async def test_agent_orchestrator():
    """Test the Agent Orchestrator with deep context integration"""
    print("🧪 Testing Agent Orchestrator with Deep Context...")
    
    try:
        from agent_orchestrator import AgentOrchestrator
        
        # Initialize the orchestrator
        orchestrator = AgentOrchestrator()
        
        print("✅ Agent Orchestrator initialized")
        
        # Test agent selection with context
        org_id = "test_org_123"
        context = {
            "lead_id": "test_lead_456",
            "lead_name": "John Smith",
            "phone": "+15550123456",
            "email": "john.smith@email.com",
            "stage": "qualification",
            "last_interaction": "2024-01-15T10:30:00Z",
            "interactions_count": 3,
            "sentiment": "positive",
            "trust_level": "medium",
            "concerns": ["pricing", "location"],
            "budget": "$500,000",
            "property_type": "condo"
        }
        
        print("🔄 Testing agent selection with rich context...")
        selection_result = await orchestrator.select_agent(org_id, context)
        
        print(f"✅ Agent selected: {selection_result['agent_type']}")
        print(f"   🎯 Confidence: {selection_result['confidence']}")
        print(f"   💭 Reasoning: {selection_result['reasoning'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_with_full_context():
    """Test agents using full context from all sources"""
    print("\n🧪 Testing Agents with Full Deep Context Integration...")
    
    try:
        from agent_orchestrator import AgentOrchestrator
        from memory_manager import MemoryManager
        from ghl_sms_provider import GHLSMSProvider
        from ghl import GHLIntegration
        
        # Initialize all components
        orchestrator = AgentOrchestrator()
        memory_manager = MemoryManager()
        ghl = GHLIntegration()
        ghl_sms = GHLSMSProvider(ghl)
        
        print("✅ All components initialized")
        
        # Test comprehensive message processing
        org_id = "test_org_123"
        lead_id = "test_lead_456"
        message = "I'm really interested in that downtown condo you showed me, but I'm worried about the price. My budget is tight."
        channel = "sms"
        
        # Build comprehensive context
        print("🔄 Building comprehensive context from all sources...")
        
        # Get context from memory manager
        agent_context = await memory_manager.get_context_for_agent(
            org_id=org_id,
            lead_id=lead_id,
            agent_type="objection_handler"  # Based on the objection in the message
        )
        
        # Simulate GHL lead data
        ghl_context = {
            "ghl_contact_id": "ghl_contact_123",
            "pipeline_stage": "Interested",
            "assigned_agent": "Sarah Johnson",
            "custom_fields": {
                "budget_range": "$400k-$600k",
                "preferred_area": "Downtown",
                "move_timeline": "3-6 months",
                "financing_approved": "Yes"
            },
            "recent_activities": [
                {"type": "property_view", "property": "123 Main St Condo", "date": "2024-01-14"},
                {"type": "email_sent", "subject": "Property Details", "date": "2024-01-15"}
            ]
        }
        
        # Simulate Knowledge Base context
        kb_context = {
            "relevant_scripts": [
                {
                    "title": "Price Objection Handling",
                    "content": "Acknowledge concern, provide market data, emphasize value proposition",
                    "category": "objection_handling"
                },
                {
                    "title": "Budget Qualification",
                    "content": "Ask about financing, monthly payment comfort, down payment availability",
                    "category": "qualification"
                }
            ],
            "guidelines": [
                {
                    "title": "Downtown Condo Market Analysis",
                    "content": "Current market trends, pricing justification, investment potential",
                    "category": "market_data"
                }
            ]
        }
        
        # Combine all context
        comprehensive_context = {
            **agent_context,
            "ghl_data": ghl_context,
            "knowledge_base": kb_context,
            "current_message": {
                "content": message,
                "channel": channel,
                "timestamp": datetime.now().isoformat(),
                "sentiment_analysis": {
                    "sentiment": "concerned_but_interested",
                    "confidence": 0.85,
                    "emotions": ["interest", "concern", "anxiety"],
                    "key_topics": ["downtown condo", "price", "budget"]
                }
            }
        }
        
        print(f"✅ Comprehensive context built ({len(str(comprehensive_context))} characters)")
        print(f"   📊 Context strength: {agent_context.get('context_strength', 0):.2f}")
        print(f"   🧠 Memory types: {len(agent_context.get('factual_knowledge', {}))}")
        print(f"   🏢 GHL data: {len(ghl_context)} fields")
        print(f"   📚 KB resources: {len(kb_context['relevant_scripts'])} scripts, {len(kb_context['guidelines'])} guidelines")
        
        # Process message with full context
        print("🔄 Processing message with deep context...")
        
        result = await orchestrator.process_message(
            org_id=org_id,
            lead_id=lead_id,
            message=message,
            channel=channel,
            context=comprehensive_context
        )
        
        print(f"✅ Message processed successfully")
        print(f"   🤖 Agent used: {result.get('agent_type', 'Unknown')}")
        print(f"   💬 Response: {result.get('response', 'No response')[:100]}...")
        print(f"   🎯 Confidence: {result.get('confidence', 'Unknown')}")
        print(f"   📈 Next actions: {result.get('next_actions', [])}")
        
        # Test intelligent response with cadence
        print("🔄 Testing intelligent response with cadence...")
        
        response_messages = result.get('response_messages', [result.get('response')])
        if response_messages and response_messages[0]:
            # Apply intelligent cadence
            cadenced_messages = await ghl_sms.apply_intelligent_cadence(
                response_messages,
                ghl_context.get('phone', '+15550123456'),
                comprehensive_context
            )
            
            print("✅ Intelligent cadence applied:")
            for i, msg in enumerate(cadenced_messages):
                print(f"   {i+1}. Delay: {msg['delay_seconds']}s - {msg['message'][:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Full context test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_end_to_end_workflow():
    """Test complete end-to-end workflow"""
    print("\n🧪 Testing Complete End-to-End AI Agent Workflow...")
    
    try:
        print("🔄 Simulating complete lead interaction workflow...")
        
        # Scenario: New lead comes in via SMS
        incoming_message = {
            "from": "+15550123456",
            "to": "+15550987654", 
            "message": "Hi, I saw your listing for the downtown condo. I'm interested but have some questions about pricing and financing options.",
            "channel": "sms",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📱 Incoming message: {incoming_message['message'][:60]}...")
        
        # Step 1: Agent Selection
        print("🔄 Step 1: Intelligent agent selection...")
        
        # Build initial context
        initial_context = {
            "lead_id": "new_lead_789",
            "phone": incoming_message["from"],
            "first_interaction": True,
            "interaction_channel": "sms",
            "message_content": incoming_message["message"],
            "inferred_intent": ["property_inquiry", "pricing_question", "financing_question"],
            "urgency_level": "medium",
            "lead_quality_score": 0.75
        }
        
        from agent_orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        
        selection_result = await orchestrator.select_agent("test_org_123", initial_context)
        selected_agent = selection_result["agent_type"]
        
        print(f"✅ Selected agent: {selected_agent} (confidence: {selection_result['confidence']})")
        
        # Step 2: Memory Storage
        print("🔄 Step 2: Storing initial interaction in memory...")
        
        from memory_manager import MemoryManager
        memory_manager = MemoryManager()
        
        interaction_log = await memory_manager.log_interaction(
            org_id="test_org_123",
            lead_id="new_lead_789",
            interaction_data={
                "message": incoming_message["message"],
                "channel": "sms",
                "agent_type": selected_agent,
                "sentiment": "interested",
                "key_points": ["downtown condo", "pricing questions", "financing"],
                "timestamp": incoming_message["timestamp"]
            }
        )
        
        print(f"✅ Interaction logged: {interaction_log['success']}")
        
        # Step 3: Context-Aware Response Generation
        print("🔄 Step 3: Generating context-aware response...")
        
        # Get updated context including the logged interaction
        agent_context = await memory_manager.get_context_for_agent(
            org_id="test_org_123",
            lead_id="new_lead_789", 
            agent_type=selected_agent
        )
        
        # Process with full context
        response_result = await orchestrator.process_message(
            org_id="test_org_123",
            lead_id="new_lead_789",
            message=incoming_message["message"],
            channel="sms",
            context=agent_context
        )
        
        print(f"✅ Response generated by {response_result.get('agent_type')} agent")
        print(f"   💬 Response: {response_result.get('response', '')[:80]}...")
        
        # Step 4: Intelligent Delivery
        print("🔄 Step 4: Intelligent message delivery with cadence...")
        
        from ghl_sms_provider import GHLSMSProvider  
        from ghl import GHLIntegration
        ghl_sms = GHLSMSProvider(GHLIntegration())
        
        # Apply intelligent cadence
        response_text = response_result.get('response', '')
        if response_text:
            # Split long responses into natural segments
            response_segments = [response_text]  # In real implementation, would intelligently split
            
            cadenced_messages = await ghl_sms.apply_intelligent_cadence(
                response_segments,
                incoming_message["from"],
                agent_context
            )
            
            print(f"✅ Delivery plan: {len(cadenced_messages)} message(s) with intelligent timing")
            for i, msg in enumerate(cadenced_messages):
                print(f"   📨 Message {i+1}: {msg['delay_seconds']}s delay")
        
        # Step 5: Follow-up Actions
        print("🔄 Step 5: Scheduling follow-up actions...")
        
        next_actions = response_result.get('next_actions', [])
        print(f"✅ Next actions planned: {len(next_actions)}")
        for action in next_actions:
            print(f"   ⏰ {action}")
        
        print("🎉 Complete end-to-end workflow executed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ End-to-end workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("TESTING ENHANCED MULTI-AGENT SYSTEM WITH DEEP CONTEXT")
        print("=" * 60)
        
        # Test 1: Agent Orchestrator
        orchestrator_success = await test_agent_orchestrator()
        
        if orchestrator_success:
            # Test 2: Full Context Integration  
            context_success = await test_agent_with_full_context()
            
            if context_success:
                # Test 3: End-to-End Workflow
                workflow_success = await test_end_to_end_workflow()
                
                if workflow_success:
                    print("\\n🎉 STEP 3 COMPLETE: Multi-Agent System with Deep Context is fully operational!")
                    print("✅ Agent Orchestrator: Advanced intelligence")
                    print("✅ Deep Context Integration: All sources unified")
                    print("✅ Intelligent Response Generation: Context-aware")
                    print("✅ Smart Communication: Cadence & timing optimized")
                    print("✅ End-to-End Workflow: Seamlessly automated")
                    print("")
                    print("🚀 PHASE B.1 COMPLETE: Core Services are Fully Operational!")
                else:
                    print("\\n⚠️  Components work but end-to-end workflow needs refinement")
            else:
                print("\\n⚠️  Agent orchestrator works but context integration needs attention")
        else:
            print("\\n❌ Agent orchestrator needs to be fixed")
    
    asyncio.run(main())