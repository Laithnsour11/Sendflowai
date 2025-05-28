import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_mem0_integration():
    """Test Mem0 integration with configured API key"""
    print("🧪 Testing Mem0 Integration...")
    
    try:
        from mem0_integration import Mem0Integration
        
        # Initialize Mem0 integration
        mem0 = Mem0Integration()
        
        if not mem0.use_mem0:
            print("❌ Mem0 not configured properly")
            return False
        
        print("✅ Mem0 Integration initialized successfully")
        
        # Test organization and lead setup
        org_id = "test_org_123"
        lead_id = "test_lead_456"
        
        print(f"🔄 Testing memory operations for org: {org_id}, lead: {lead_id}")
        
        # Test storing factual memory
        print("🔄 Storing factual memory...")
        factual_result = await mem0.store_factual_memory(
            org_id=org_id,
            lead_id=lead_id,
            data={
                "name": "John Smith",
                "phone": "+1-555-0123",
                "email": "john.smith@email.com",
                "budget": "$500,000",
                "location_preference": "Downtown area",
                "bedrooms": 3,
                "bathrooms": 2,
                "property_type": "Condo"
            }
        )
        print(f"✅ Factual memory stored: {factual_result}")
        
        # Test storing emotional memory
        print("🔄 Storing emotional memory...")
        emotional_result = await mem0.store_emotional_memory(
            org_id=org_id,
            lead_id=lead_id,
            data={
                "sentiment": "excited",
                "concerns": ["pricing", "commute time"],
                "motivations": ["first-time buyer", "growing family"],
                "trust_level": "medium",
                "personality_type": "analytical"
            }
        )
        print(f"✅ Emotional memory stored: {emotional_result}")
        
        # Test storing strategic memory
        print("🔄 Storing strategic memory...")
        strategic_result = await mem0.store_strategic_memory(
            org_id=org_id,
            lead_id=lead_id,
            data={
                "last_contact": "2024-01-15",
                "next_followup": "2024-01-18",
                "stage": "qualification",
                "objections_raised": ["price too high"],
                "properties_shown": ["123 Main St", "456 Oak Ave"],
                "preferred_contact_method": "phone",
                "best_contact_time": "evenings"
            }
        )
        print(f"✅ Strategic memory stored: {strategic_result}")
        
        # Test storing contextual memory
        print("🔄 Storing contextual memory...")
        contextual_result = await mem0.store_contextual_memory(
            org_id=org_id,
            lead_id=lead_id,
            data={
                "last_conversation": "Discussed downtown condos, showed interest in amenities",
                "key_points": ["wants modern kitchen", "parking important", "near public transit"],
                "agent_notes": "Very responsive to emails, prefers detailed information"
            }
        )
        print(f"✅ Contextual memory stored: {contextual_result}")
        
        # Test retrieving comprehensive memory
        print("🔄 Retrieving comprehensive lead memory...")
        comprehensive_memory = await mem0.get_comprehensive_memory(org_id, lead_id)
        
        print("✅ Comprehensive memory retrieved:")
        for memory_type, data in comprehensive_memory.items():
            print(f"   📝 {memory_type}: {len(str(data))} characters")
        
        # Test updating memory
        print("🔄 Testing memory updates...")
        update_result = await mem0.update_emotional_memory(
            org_id=org_id,
            lead_id=lead_id,
            updates={
                "trust_level": "high",
                "recent_sentiment": "very interested"
            }
        )
        print(f"✅ Memory updated: {update_result}")
        
        # Test memory search
        print("🔄 Testing memory search...")
        search_results = await mem0.search_memories(
            org_id=org_id,
            query="downtown condo preferences",
            limit=3
        )
        print(f"✅ Search returned {len(search_results)} results")
        
        print("🎉 Mem0 Integration is fully operational!")
        return True
        
    except Exception as e:
        print(f"❌ Mem0 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_memory_manager():
    """Test the Memory Manager that orchestrates Mem0"""
    print("\n🧪 Testing Memory Manager...")
    
    try:
        from memory_manager import MemoryManager
        
        # Initialize memory manager
        memory_manager = MemoryManager()
        
        print("✅ Memory Manager initialized")
        
        # Test interaction logging
        org_id = "test_org_123"
        lead_id = "test_lead_456"
        
        interaction_data = {
            "message": "I'm looking for a 3-bedroom condo downtown with parking",
            "channel": "sms",
            "agent_type": "qualifier",
            "response": "Great! I understand you're interested in downtown condos. Can you tell me more about your budget range?",
            "sentiment": "positive",
            "key_points": ["3-bedroom", "downtown", "parking", "condo"],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        print("🔄 Logging interaction with memory updates...")
        result = await memory_manager.log_interaction(
            org_id=org_id,
            lead_id=lead_id,
            interaction_data=interaction_data
        )
        
        print(f"✅ Interaction logged: {result}")
        
        # Test context retrieval
        print("🔄 Retrieving context for agent...")
        context = await memory_manager.get_context_for_agent(
            org_id=org_id,
            lead_id=lead_id,
            agent_type="nurturer"
        )
        
        print("✅ Agent context retrieved:")
        print(f"   📊 Context length: {len(str(context))} characters")
        print(f"   🔑 Context keys: {list(context.keys())}")
        
        print("🎉 Memory Manager is fully operational!")
        return True
        
    except Exception as e:
        print(f"❌ Memory Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("TESTING MEM0 PERSISTENT MEMORY SYSTEM")
        print("=" * 60)
        
        mem0_success = await test_mem0_integration()
        if mem0_success:
            memory_manager_success = await test_memory_manager()
            
            if memory_manager_success:
                print("\n🎉 STEP 1 COMPLETE: Mem0 Persistent Memory is fully operational!")
            else:
                print("\n⚠️  Mem0 works but Memory Manager needs attention")
        else:
            print("\n❌ Mem0 integration needs to be fixed")
    
    asyncio.run(main())