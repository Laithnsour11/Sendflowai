import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Save, Bot, MessageSquare, Phone, Settings, Brain, Target, Mic, TestTube2 } from 'lucide-react';

const AgentConfiguration = ({ currentOrg }) => {
  const [activeAgent, setActiveAgent] = useState('initial_contact');
  const [agentConfigs, setAgentConfigs] = useState({});
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');
  const [expandedSections, setExpandedSections] = useState({
    llm: true,
    voice: true,
    behavior: false,
    advanced: false
  });

  // Agent types with comprehensive information
  const agentTypes = {
    initial_contact: {
      name: 'Initial Contact Agent',
      description: 'Specializes in first impressions and rapport building with new leads',
      icon: MessageSquare,
      color: 'bg-blue-500',
      use_cases: ['First interaction', 'Introduction', 'Welcome messages', 'Icebreaking'],
      strengths: ['Rapport building', 'Engagement', 'First impression', 'Trust establishment'],
      default_model: 'gpt-4o',
      default_temperature: 0.7,
      sample_prompt: 'You are a warm, professional real estate agent making first contact with a potential client. Your goal is to build rapport and establish trust while gathering basic information about their needs.'
    },
    qualifier: {
      name: 'Qualifier Agent',
      description: 'Specializes in lead qualification and comprehensive needs assessment',
      icon: Target,
      color: 'bg-green-500',
      use_cases: ['Qualification', 'Needs assessment', 'Discovery calls', 'Budget verification'],
      strengths: ['Information gathering', 'Assessment', 'Qualification', 'Needs analysis'],
      default_model: 'gpt-4o',
      default_temperature: 0.5,
      sample_prompt: 'You are a skilled real estate qualifier focused on understanding the client\'s specific needs, timeline, and budget. Ask strategic questions to determine if they are a qualified lead.'
    },
    nurturer: {
      name: 'Nurturing Agent',
      description: 'Specializes in relationship building and providing ongoing value',
      icon: Brain,
      color: 'bg-purple-500',
      use_cases: ['Follow-up', 'Relationship building', 'Education', 'Value provision'],
      strengths: ['Trust building', 'Value provision', 'Relationship development', 'Long-term engagement'],
      default_model: 'gpt-4o',
      default_temperature: 0.7,
      sample_prompt: 'You are a nurturing real estate agent focused on building long-term relationships. Provide valuable insights and maintain regular, helpful contact with leads who aren\'t ready to buy yet.'
    },
    objection_handler: {
      name: 'Objection Handler Agent',
      description: 'Specializes in addressing concerns and resolving objections',
      icon: Settings,
      color: 'bg-orange-500',
      use_cases: ['Objection handling', 'Concern addressing', 'Pushback resolution', 'Hesitation management'],
      strengths: ['Objection handling', 'Clarification', 'Reassurance', 'Problem solving'],
      default_model: 'gpt-4o',
      default_temperature: 0.4,
      sample_prompt: 'You are an expert at handling objections in real estate. Listen carefully to concerns and provide thoughtful, evidence-based responses that address the underlying issues.'
    },
    closer: {
      name: 'Closer Agent',
      description: 'Specializes in deal closing and securing commitments',
      icon: Phone,
      color: 'bg-red-500',
      use_cases: ['Closing', 'Commitment', 'Decision time', 'Contract negotiation'],
      strengths: ['Closing techniques', 'Urgency creation', 'Commitment securing', 'Deal finalization'],
      default_model: 'gpt-4o',
      default_temperature: 0.6,
      sample_prompt: 'You are a skilled closer focused on helping qualified leads make decisions. Use proven closing techniques while maintaining a consultative approach.'
    },
    appointment_setter: {
      name: 'Appointment Setter Agent',
      description: 'Specializes in appointment scheduling and calendar coordination',
      icon: Bot,
      color: 'bg-teal-500',
      use_cases: ['Scheduling', 'Appointment booking', 'Meeting coordination', 'Calendar management'],
      strengths: ['Scheduling', 'Confirmation', 'Follow-up', 'Time management'],
      default_model: 'gpt-4o',
      default_temperature: 0.5,
      sample_prompt: 'You are efficient at scheduling appointments and coordinating meetings. Focus on finding mutually convenient times and confirming all details clearly.'
    }
  };

  // Available LLM models with provider information
  const availableModels = [
    { value: 'gpt-4o', label: 'GPT-4o (Latest OpenAI)', provider: 'OpenAI', description: 'Most advanced model, excellent for complex conversations' },
    { value: 'gpt-4o-mini', label: 'GPT-4o Mini (Fast OpenAI)', provider: 'OpenAI', description: 'Faster and more cost-effective version' },
    { value: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet (Anthropic)', provider: 'Anthropic', description: 'Excellent reasoning and conversation skills' },
    { value: 'claude-3-5-haiku-20241022', label: 'Claude 3.5 Haiku (Anthropic)', provider: 'Anthropic', description: 'Fast and efficient for straightforward tasks' },
    { value: 'google/gemini-1.5-pro-latest', label: 'Gemini 1.5 Pro (Google)', provider: 'Google', description: 'Strong performance with long context windows' },
    { value: 'meta-llama/llama-3.1-405b-instruct', label: 'Llama 3.1 405B (Meta)', provider: 'Meta', description: 'Open source model with strong capabilities' },
    { value: 'anthropic/claude-3.5-sonnet', label: 'Claude 3.5 Sonnet (OpenRouter)', provider: 'OpenRouter', description: 'Via OpenRouter API' },
    { value: 'openai/gpt-4o', label: 'GPT-4o (OpenRouter)', provider: 'OpenRouter', description: 'Via OpenRouter API' }
  ];

  // Voice providers and configurations
  const voiceProviders = [
    { 
      value: 'elevenlabs', 
      label: 'ElevenLabs (Premium Quality)', 
      voices: [
        { id: 'amy', name: 'Amy', description: 'Professional female voice' },
        { id: 'brian', name: 'Brian', description: 'Professional male voice' },
        { id: 'chris', name: 'Chris', description: 'Friendly male voice' }
      ]
    },
    { 
      value: 'openai', 
      label: 'OpenAI TTS (Reliable)', 
      voices: [
        { id: 'alloy', name: 'Alloy', description: 'Neutral voice' },
        { id: 'echo', name: 'Echo', description: 'Professional voice' },
        { id: 'fable', name: 'Fable', description: 'Warm voice' },
        { id: 'onyx', name: 'Onyx', description: 'Deep voice' },
        { id: 'nova', name: 'Nova', description: 'Clear voice' },
        { id: 'shimmer', name: 'Shimmer', description: 'Bright voice' }
      ]
    },
    { 
      value: 'azure', 
      label: 'Azure Speech (Enterprise)', 
      voices: [
        { id: 'aria', name: 'Aria', description: 'Clear female voice' },
        { id: 'davis', name: 'Davis', description: 'Professional male voice' },
        { id: 'guy', name: 'Guy', description: 'Friendly male voice' },
        { id: 'jane', name: 'Jane', description: 'Warm female voice' }
      ]
    }
  ];

  const orgId = currentOrg?.id || 'production_org_123';

  // Load agent configurations
  useEffect(() => {
    loadAgentConfigs();
  }, [orgId]);

  const loadAgentConfigs = async () => {
    setLoading(true);
    try {
      // In real implementation, fetch from backend API
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent-configs?org_id=${orgId}`);
      
      if (response.ok) {
        const data = await response.json();
        setAgentConfigs(data.configs || {});
      } else {
        // Initialize with defaults if no configs exist
        initializeDefaultConfigs();
      }
    } catch (error) {
      console.error('Error loading agent configs:', error);
      initializeDefaultConfigs();
    } finally {
      setLoading(false);
    }
  };

  const initializeDefaultConfigs = () => {
    const defaultConfigs = {};
    Object.keys(agentTypes).forEach(agentType => {
      defaultConfigs[agentType] = {
        // LLM Configuration
        model: agentTypes[agentType].default_model,
        temperature: agentTypes[agentType].default_temperature,
        max_tokens: 800,
        
        // Voice Configuration
        voice_provider: 'elevenlabs',
        voice_id: 'amy',
        speech_rate: 1.0,
        
        // Behavior Configuration
        response_style: 'professional',
        personality: 'friendly',
        objection_handling: 'empathetic',
        max_response_length: 'medium',
        
        // Advanced Configuration
        custom_prompt: '',
        system_instructions: agentTypes[agentType].sample_prompt,
        use_context: true,
        use_memory: true,
        use_knowledge_base: true,
        
        // Conversation Flow
        greeting_style: 'warm',
        follow_up_style: 'professional',
        closing_style: 'consultative'
      };
    });
    setAgentConfigs(defaultConfigs);
  };

  const updateAgentConfig = (agentType, field, value) => {
    setAgentConfigs(prev => ({
      ...prev,
      [agentType]: {
        ...prev[agentType],
        [field]: value
      }
    }));
  };

  const saveAgentConfiguration = async (agentType) => {
    setLoading(true);
    setSaveStatus('saving');
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent-configs`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          org_id: orgId,
          agent_type: agentType,
          config: agentConfigs[agentType]
        })
      });

      if (response.ok) {
        setSaveStatus('saved');
      } else {
        throw new Error('Failed to save configuration');
      }
    } catch (error) {
      console.error('Error saving agent configuration:', error);
      setSaveStatus('error');
    } finally {
      setLoading(false);
      setTimeout(() => setSaveStatus(''), 2000);
    }
  };

  const testAgent = async (agentType) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/agent-test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          org_id: orgId,
          agent_type: agentType,
          test_message: "Hello, I'm interested in buying a home in the downtown area. Can you help me?"
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Test Response from ${agentTypes[agentType].name}:\n\n${result.response}`);
      } else {
        alert('Error testing agent. Please check your configuration.');
      }
    } catch (error) {
      console.error('Error testing agent:', error);
      alert('Error testing agent. Please try again.');
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const currentAgent = agentTypes[activeAgent];
  const currentConfig = agentConfigs[activeAgent] || {};
  const IconComponent = currentAgent?.icon || Bot;

  const currentVoiceProvider = voiceProviders.find(p => p.value === (currentConfig.voice_provider || 'elevenlabs'));
  const availableVoices = currentVoiceProvider?.voices || [];

  if (loading && Object.keys(agentConfigs).length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-sm border p-4 h-96"></div>
              <div className="lg:col-span-3 bg-white rounded-lg shadow-sm border p-6 h-96"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Agent Configuration</h1>
          <p className="text-gray-600">Configure and customize your specialized AI agents for optimal performance</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Agent Selection Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Agent</h2>
              <div className="space-y-2">
                {Object.entries(agentTypes).map(([key, agent]) => {
                  const IconComp = agent.icon;
                  return (
                    <button
                      key={key}
                      onClick={() => setActiveAgent(key)}
                      className={`w-full flex items-center space-x-3 p-3 rounded-lg text-left transition-colors ${
                        activeAgent === key
                          ? 'bg-blue-50 border border-blue-200 text-blue-900'
                          : 'hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <div className={`p-2 rounded-lg ${agent.color} text-white flex-shrink-0`}>
                        <IconComp size={16} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{agent.name}</p>
                        <p className="text-sm text-gray-500 truncate">{agent.description}</p>
                      </div>
                    </button>
                  );
                })}
              </div>

              {/* Quick Status */}
              <div className="mt-6 pt-4 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-700 mb-3">System Status</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Active Agents</span>
                    <span className="text-green-600 font-medium">6</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Configured</span>
                    <span className="text-blue-600 font-medium">{Object.keys(agentConfigs).length}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Configuration Area */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border">
              {/* Agent Header */}
              <div className="border-b border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`p-3 rounded-lg ${currentAgent?.color} text-white`}>
                      <IconComponent size={24} />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">{currentAgent?.name}</h2>
                      <p className="text-gray-600">{currentAgent?.description}</p>
                    </div>
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => testAgent(activeAgent)}
                      className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
                    >
                      <TestTube2 size={16} />
                      <span>Test Agent</span>
                    </button>
                    <button
                      onClick={() => saveAgentConfiguration(activeAgent)}
                      disabled={loading}
                      className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                    >
                      <Save size={16} />
                      <span>{loading ? 'Saving...' : 'Save Configuration'}</span>
                    </button>
                  </div>
                </div>

                {/* Agent Capabilities Overview */}
                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Primary Use Cases</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {currentAgent?.use_cases.map((useCase, idx) => (
                        <li key={idx}>• {useCase}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Key Strengths</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {currentAgent?.strengths.map((strength, idx) => (
                        <li key={idx}>• {strength}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Current Status</h4>
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm text-gray-600">Active & Configured</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span className="text-sm text-gray-600">Model: {currentConfig.model || 'gpt-4o'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Configuration Sections */}
              <div className="p-6 space-y-6">
                {/* LLM Configuration Section */}
                <div className="border border-gray-200 rounded-lg">
                  <button
                    onClick={() => toggleSection('llm')}
                    className="w-full flex items-center justify-between p-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <Brain className="h-5 w-5 text-blue-600" />
                      <h3 className="text-lg font-semibold text-gray-900">LLM Configuration</h3>
                    </div>
                    {expandedSections.llm ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </button>
                  
                  {expandedSections.llm && (
                    <div className="p-4 border-t border-gray-200 space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Model Selection
                          </label>
                          <select
                            value={currentConfig.model || ''}
                            onChange={(e) => updateAgentConfig(activeAgent, 'model', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            {availableModels.map(model => (
                              <option key={model.value} value={model.value}>
                                {model.label}
                              </option>
                            ))}
                          </select>
                          <p className="text-xs text-gray-500 mt-1">
                            {availableModels.find(m => m.value === currentConfig.model)?.description}
                          </p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Temperature ({currentConfig.temperature || 0.7})
                          </label>
                          <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={currentConfig.temperature || 0.7}
                            onChange={(e) => updateAgentConfig(activeAgent, 'temperature', parseFloat(e.target.value))}
                            className="w-full"
                          />
                          <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>More Focused</span>
                            <span>More Creative</span>
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Max Response Tokens
                          </label>
                          <input
                            type="number"
                            value={currentConfig.max_tokens || 800}
                            onChange={(e) => updateAgentConfig(activeAgent, 'max_tokens', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            min="100"
                            max="2000"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Response Style
                          </label>
                          <select
                            value={currentConfig.response_style || 'professional'}
                            onChange={(e) => updateAgentConfig(activeAgent, 'response_style', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value="professional">Professional</option>
                            <option value="friendly">Friendly</option>
                            <option value="casual">Casual</option>
                            <option value="formal">Formal</option>
                            <option value="consultative">Consultative</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Voice Configuration Section */}
                <div className="border border-gray-200 rounded-lg">
                  <button
                    onClick={() => toggleSection('voice')}
                    className="w-full flex items-center justify-between p-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <Mic className="h-5 w-5 text-purple-600" />
                      <h3 className="text-lg font-semibold text-gray-900">Voice Configuration</h3>
                    </div>
                    {expandedSections.voice ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </button>
                  
                  {expandedSections.voice && (
                    <div className="p-4 border-t border-gray-200 space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Voice Provider
                          </label>
                          <select
                            value={currentConfig.voice_provider || 'elevenlabs'}
                            onChange={(e) => updateAgentConfig(activeAgent, 'voice_provider', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            {voiceProviders.map(provider => (
                              <option key={provider.value} value={provider.value}>
                                {provider.label}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Voice Selection
                          </label>
                          <select
                            value={currentConfig.voice_id || 'amy'}
                            onChange={(e) => updateAgentConfig(activeAgent, 'voice_id', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            {availableVoices.map(voice => (
                              <option key={voice.id} value={voice.id}>
                                {voice.name}
                              </option>
                            ))}
                          </select>
                          <p className="text-xs text-gray-500 mt-1">
                            {availableVoices.find(v => v.id === currentConfig.voice_id)?.description}
                          </p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Speech Rate ({currentConfig.speech_rate || 1.0}x)
                          </label>
                          <input
                            type="range"
                            min="0.5"
                            max="2.0"
                            step="0.1"
                            value={currentConfig.speech_rate || 1.0}
                            onChange={(e) => updateAgentConfig(activeAgent, 'speech_rate', parseFloat(e.target.value))}
                            className="w-full"
                          />
                          <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>Slower</span>
                            <span>Faster</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-3">
                        <button className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                          Preview Voice
                        </button>
                        <button className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                          Test Call
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Behavior Configuration Section */}
                <div className="border border-gray-200 rounded-lg">
                  <button
                    onClick={() => toggleSection('behavior')}
                    className="w-full flex items-center justify-between p-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <Settings className="h-5 w-5 text-green-600" />
                      <h3 className="text-lg font-semibold text-gray-900">Behavior Configuration</h3>
                    </div>
                    {expandedSections.behavior ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </button>
                  
                  {expandedSections.behavior && (
                    <div className="p-4 border-t border-gray-200 space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Personality Style
                          </label>
                          <select
                            value={currentConfig.personality || 'friendly'}
                            onChange={(e) => updateAgentConfig(activeAgent, 'personality', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value="friendly">Friendly & Approachable</option>
                            <option value="professional">Professional & Formal</option>
                            <option value="empathetic">Empathetic & Understanding</option>
                            <option value="confident">Confident & Assertive</option>
                            <option value="consultative">Consultative & Advisory</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Objection Handling Style
                          </label>
                          <select
                            value={currentConfig.objection_handling || 'empathetic'}
                            onChange={(e) => updateAgentConfig(activeAgent, 'objection_handling', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value="empathetic">Empathetic & Understanding</option>
                            <option value="logical">Logical & Evidence-Based</option>
                            <option value="assertive">Assertive & Direct</option>
                            <option value="collaborative">Collaborative & Problem-Solving</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Response Length
                          </label>
                          <select
                            value={currentConfig.max_response_length || 'medium'}
                            onChange={(e) => updateAgentConfig(activeAgent, 'max_response_length', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value="short">Short (1-2 sentences)</option>
                            <option value="medium">Medium (2-4 sentences)</option>
                            <option value="long">Long (4+ sentences)</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Conversation Flow
                          </label>
                          <select
                            value={currentConfig.greeting_style || 'warm'}
                            onChange={(e) => updateAgentConfig(activeAgent, 'greeting_style', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value="warm">Warm & Personal</option>
                            <option value="professional">Professional & Direct</option>
                            <option value="casual">Casual & Relaxed</option>
                            <option value="formal">Formal & Respectful</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Advanced Configuration Section */}
                <div className="border border-gray-200 rounded-lg">
                  <button
                    onClick={() => toggleSection('advanced')}
                    className="w-full flex items-center justify-between p-4 text-left bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <Settings className="h-5 w-5 text-orange-600" />
                      <h3 className="text-lg font-semibold text-gray-900">Advanced Configuration</h3>
                    </div>
                    {expandedSections.advanced ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </button>
                  
                  {expandedSections.advanced && (
                    <div className="p-4 border-t border-gray-200 space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          System Instructions
                        </label>
                        <textarea
                          value={currentConfig.system_instructions || currentAgent?.sample_prompt || ''}
                          onChange={(e) => updateAgentConfig(activeAgent, 'system_instructions', e.target.value)}
                          rows={4}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Enter system instructions for this agent..."
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          These instructions define the agent's core behavior and role
                        </p>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Custom Prompt Enhancement (Optional)
                        </label>
                        <textarea
                          value={currentConfig.custom_prompt || ''}
                          onChange={(e) => updateAgentConfig(activeAgent, 'custom_prompt', e.target.value)}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="Add custom instructions to enhance the agent's behavior..."
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Additional instructions that will be added to the system prompt
                        </p>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-3">Context Integration</h4>
                        <div className="space-y-3">
                          <label className="flex items-center space-x-3">
                            <input
                              type="checkbox"
                              checked={currentConfig.use_context !== false}
                              onChange={(e) => updateAgentConfig(activeAgent, 'use_context', e.target.checked)}
                              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700">Use GHL Lead Context</span>
                          </label>
                          <label className="flex items-center space-x-3">
                            <input
                              type="checkbox"
                              checked={currentConfig.use_memory !== false}
                              onChange={(e) => updateAgentConfig(activeAgent, 'use_memory', e.target.checked)}
                              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700">Use Mem0 Memory System</span>
                          </label>
                          <label className="flex items-center space-x-3">
                            <input
                              type="checkbox"
                              checked={currentConfig.use_knowledge_base !== false}
                              onChange={(e) => updateAgentConfig(activeAgent, 'use_knowledge_base', e.target.checked)}
                              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            />
                            <span className="text-sm text-gray-700">Use Knowledge Base (RAG)</span>
                          </label>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Save Status */}
        {saveStatus && (
          <div className={`fixed bottom-4 right-4 px-6 py-3 rounded-lg text-white font-medium shadow-lg ${
            saveStatus === 'saved' ? 'bg-green-500' : 
            saveStatus === 'error' ? 'bg-red-500' : 'bg-blue-500'
          }`}>
            {saveStatus === 'saved' && '✓ Configuration saved successfully!'}
            {saveStatus === 'error' && '✗ Error saving configuration'}
            {saveStatus === 'saving' && '⏳ Saving configuration...'}
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentConfiguration;