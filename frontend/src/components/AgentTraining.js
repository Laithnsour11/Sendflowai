import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AgentTraining = ({ currentOrg }) => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [availableModels, setAvailableModels] = useState({
    openai: [],
    anthropic: [],
    openrouter: []
  });
  const [loadingModels, setLoadingModels] = useState(false);
  const [formData, setFormData] = useState({
    agent_type: 'initial_contact',
    name: '',
    description: '',
    system_prompt: '',
    llm_provider: 'openai',
    model_id: 'gpt-4o',
    configuration: {
      temperature: 0.7,
      top_p: 0.9,
      presence_penalty: 0.3,
      frequency_penalty: 0.3
    }
  });
  const [isEditing, setIsEditing] = useState(false);
  const [previewResponse, setPreviewResponse] = useState('');
  const [isGeneratingPreview, setIsGeneratingPreview] = useState(false);
  
  const agentTypes = [
    { value: 'initial_contact', label: 'Initial Contact Agent' },
    { value: 'qualifier', label: 'Qualification Agent' },
    { value: 'nurturer', label: 'Nurturing Agent' },
    { value: 'objection_handler', label: 'Objection Handler Agent' },
    { value: 'closer', label: 'Closing Agent' },
    { value: 'appointment_setter', label: 'Appointment Agent' }
  ];
  
  const llmProviders = [
    { value: 'openai', label: 'OpenAI' },
    { value: 'anthropic', label: 'Anthropic' },
    { value: 'openrouter', label: 'OpenRouter' }
  ];
  
  // Mock models for demonstration
  const mockModels = {
    openai: [
      { id: 'gpt-4o', name: 'GPT-4o' },
      { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' }
    ],
    anthropic: [
      { id: 'claude-3-opus-20240229', name: 'Claude 3 Opus' },
      { id: 'claude-3-sonnet-20240229', name: 'Claude 3 Sonnet' },
      { id: 'claude-3-haiku-20240307', name: 'Claude 3 Haiku' }
    ],
    openrouter: [
      { id: 'openai/gpt-4o', name: 'GPT-4o', provider: 'OpenAI' },
      { id: 'anthropic/claude-3-opus', name: 'Claude 3 Opus', provider: 'Anthropic' },
      { id: 'anthropic/claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'Anthropic' },
      { id: 'anthropic/claude-3-haiku', name: 'Claude 3 Haiku', provider: 'Anthropic' },
      { id: 'meta-llama/llama-3-70b-instruct', name: 'Llama 3 70B', provider: 'Meta' },
      { id: 'meta-llama/llama-3-8b-instruct', name: 'Llama 3 8B', provider: 'Meta' },
      { id: 'google/gemini-1.5-pro', name: 'Gemini 1.5 Pro', provider: 'Google' },
      { id: 'google/gemini-1.5-flash', name: 'Gemini 1.5 Flash', provider: 'Google' },
      { id: 'mistralai/mistral-large', name: 'Mistral Large', provider: 'Mistral AI' },
      { id: 'mistralai/mistral-medium', name: 'Mistral Medium', provider: 'Mistral AI' }
    ]
  };
  
  useEffect(() => {
    // Simulated data loading for demo
    const loadAgents = async () => {
      try {
        setLoading(true);
        
        // In a real app, we would fetch this data from the API
        // const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/agents/training?org_id=${currentOrg.id}`);
        
        // Mock data for demo
        setTimeout(() => {
          const mockAgents = [
            {
              id: '1',
              agent_type: 'initial_contact',
              name: 'Friendly Greeter',
              description: 'Warm and friendly initial contact agent that focuses on building rapport quickly.',
              system_prompt: 'You are a friendly real estate agent making first contact with a lead. Your goal is to build rapport, make them feel comfortable, and learn about their basic needs. Be warm, professional, and engaging. Ask open-ended questions to encourage conversation.',
              llm_provider: 'openai',
              model_id: 'gpt-4o',
              configuration: {
                temperature: 0.7,
                top_p: 0.9,
                presence_penalty: 0.6,
                frequency_penalty: 0.1
              },
              is_active: true,
              version: 1,
              created_at: '2023-02-15T10:30:00Z'
            },
            {
              id: '2',
              agent_type: 'qualifier',
              name: 'Detailed Qualifier',
              description: 'Thorough qualification agent that excels at discovering client needs and preferences.',
              system_prompt: 'You are a real estate qualification specialist. Your goal is to gather detailed information about the client property needs, budget, timeline, and preferences. Be thorough but conversational. Focus on collecting actionable information that will help match them with the right properties.',
              llm_provider: 'anthropic',
              model_id: 'claude-3-sonnet-20240229',
              configuration: {
                temperature: 0.5,
                top_p: 0.85,
                presence_penalty: 0.2,
                frequency_penalty: 0.3
              },
              is_active: true,
              version: 2,
              created_at: '2023-01-10T14:45:00Z'
            },
            {
              id: '3',
              agent_type: 'objection_handler',
              name: 'Price Objection Specialist',
              description: 'Specialist in handling price-related objections and concerns.',
              system_prompt: 'You are a real estate agent specialized in addressing price objections. When clients express concerns about property prices, acknowledge their concern, explain value proposition clearly, provide market context, and discuss financing options that might make properties more affordable. Be empathetic but confident.',
              llm_provider: 'openai',
              model_id: 'gpt-4o',
              configuration: {
                temperature: 0.6,
                top_p: 0.9,
                presence_penalty: 0.5,
                frequency_penalty: 0.5
              },
              is_active: true,
              version: 1,
              created_at: '2023-02-05T09:15:00Z'
            },
            {
              id: '4',
              agent_type: 'closer',
              name: 'Confident Closer',
              description: 'Direct and confident agent that excels at guiding leads to make decisions.',
              system_prompt: 'You are a real estate closing specialist. Your job is to help clients make confident decisions about purchasing property. Be clear, direct, and confident. Use assumptive language, create appropriate urgency, and guide prospects toward concrete next steps. Address final objections succinctly and focus on the value proposition.',
              llm_provider: 'openrouter',
              model_id: 'meta-llama/llama-3-70b-instruct',
              configuration: {
                temperature: 0.6,
                top_p: 0.8,
                presence_penalty: 0.3,
                frequency_penalty: 0.3
              },
              is_active: true,
              version: 3,
              created_at: '2023-01-25T16:20:00Z'
            }
          ];
          
          setAgents(mockAgents);
          setLoading(false);
          
          // Set mock available models
          setAvailableModels(mockModels);
        }, 1000);
      } catch (error) {
        console.error('Error loading agents:', error);
        setLoading(false);
      }
    };
    
    loadAgents();
  }, [currentOrg]);
  
  // Load models when provider changes
  useEffect(() => {
    const loadModels = async () => {
      // In a real app, we would fetch models from the API when provider changes
      // if (formData.llm_provider) {
      //   setLoadingModels(true);
      //   try {
      //     const response = await axios.get(
      //       `${process.env.REACT_APP_BACKEND_URL}/api/llm/models/${formData.llm_provider}?org_id=${currentOrg.id}`
      //     );
      //     setAvailableModels(prev => ({ ...prev, [formData.llm_provider]: response.data }));
      //   } catch (error) {
      //     console.error('Error loading models:', error);
      //   } finally {
      //     setLoadingModels(false);
      //   }
      // }
      
      // For demo, we'll use the mock data
      setLoadingModels(true);
      setTimeout(() => {
        setLoadingModels(false);
        // Models are already set in the initial load
      }, 500);
    };
    
    if (formData.llm_provider) {
      loadModels();
    }
  }, [formData.llm_provider, currentOrg]);
  
  const handleSelectAgent = (agent) => {
    setSelectedAgent(agent);
    setFormData({
      agent_type: agent.agent_type,
      name: agent.name,
      description: agent.description,
      system_prompt: agent.system_prompt,
      llm_provider: agent.llm_provider || 'openai',
      model_id: agent.model_id || 'gpt-4o',
      configuration: agent.configuration
    });
    setIsEditing(true);
  };
  
  const handleNewAgent = () => {
    setSelectedAgent(null);
    setFormData({
      agent_type: 'initial_contact',
      name: '',
      description: '',
      system_prompt: '',
      llm_provider: 'openai',
      model_id: 'gpt-4o',
      configuration: {
        temperature: 0.7,
        top_p: 0.9,
        presence_penalty: 0.3,
        frequency_penalty: 0.3
      }
    });
    setIsEditing(true);
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    // When provider changes, update model selection to first available model
    if (name === 'llm_provider') {
      const firstModel = mockModels[value]?.[0]?.id || '';
      setFormData(prev => ({
        ...prev,
        [name]: value,
        model_id: firstModel
      }));
    }
  };
  
  const handleConfigChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      configuration: {
        ...formData.configuration,
        [name]: parseFloat(value)
      }
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // In a real app, we would post this data to the API
      // const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/agents/training`, {
      //   org_id: currentOrg.id,
      //   ...formData
      // });
      
      // Mock adding/updating an agent
      if (selectedAgent) {
        // Update existing agent
        const updatedAgents = agents.map(agent => 
          agent.id === selectedAgent.id 
            ? { ...agent, ...formData, version: agent.version + 1, updated_at: new Date().toISOString() }
            : agent
        );
        setAgents(updatedAgents);
      } else {
        // Add new agent
        const newAgent = {
          id: String(agents.length + 1),
          ...formData,
          is_active: true,
          version: 1,
          created_at: new Date().toISOString()
        };
        setAgents([...agents, newAgent]);
      }
      
      setIsEditing(false);
      setSelectedAgent(null);
    } catch (error) {
      console.error('Error saving agent:', error);
    }
  };
  
  const handleGeneratePreview = async () => {
    setIsGeneratingPreview(true);
    
    try {
      // In a real app, we would call the API to generate a preview
      // const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/llm/generate`, {
      //   org_id: currentOrg.id,
      //   provider: formData.llm_provider,
      //   model_id: formData.model_id,
      //   prompt: "Tell me about your real estate services.",
      //   system_message: formData.system_prompt,
      //   temperature: formData.configuration.temperature
      // });
      
      // Mock preview generation
      setTimeout(() => {
        let previewText = '';
        
        switch (formData.agent_type) {
          case 'initial_contact':
            previewText = "Hi there! I'm Sarah with ABC Realty. I noticed you were looking at properties in the downtown area. I'd love to learn more about what you're looking for in your next home. Are you searching for a primary residence or an investment property?";
            break;
          case 'qualifier':
            previewText = "Thanks for sharing that information. Based on what you've told me, you're looking for a 3-bedroom property in the $400,000-$500,000 range. Could you tell me more about your timeline? Are you looking to move within the next few months, or do you have a more flexible timeframe?";
            break;
          case 'objection_handler':
            previewText = "I completely understand your concern about the price. Many of my clients initially feel the same way. This property is priced at market value for the area, and it offers several features that similar properties don't have, such as the renovated kitchen and larger backyard. Have you considered the long-term value appreciation in this neighborhood? It's been growing at about 5% annually.";
            break;
          case 'closer':
            previewText = "Based on everything we've discussed, this property at 123 Main Street checks all your boxes - it's in your preferred neighborhood, has the 4 bedrooms you need, and is within your budget. The market is moving quickly right now, and there are two other interested parties. If you're ready, I can help you prepare an offer today. Would you like to move forward?";
            break;
          default:
            previewText = "I'd be happy to help you with your real estate needs. Could you tell me more about what you're looking for?";
        }
        
        // Add some model-specific flavor
        if (formData.llm_provider === 'anthropic') {
          previewText += "\n\nI've analyzed recent market trends in your area and can provide detailed information on comparable properties if that would be helpful.";
        } else if (formData.llm_provider === 'openrouter' && formData.model_id.includes('llama')) {
          previewText += "\n\nAs someone who knows this market inside and out, I can also connect you with excellent mortgage brokers who can help secure the best possible rate.";
        }
        
        setPreviewResponse(previewText);
        setIsGeneratingPreview(false);
      }, 2000);
    } catch (error) {
      console.error('Error generating preview:', error);
      setIsGeneratingPreview(false);
    }
  };
  
  // Get current available models based on selected provider
  const currentModels = formData.llm_provider ? availableModels[formData.llm_provider] || [] : [];
  
  return (
    <div>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Agent Training</h1>
        {!isEditing && (
          <button
            onClick={handleNewAgent}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Create New Agent
          </button>
        )}
      </div>
      
      {isEditing ? (
        <div className="mt-6 bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h2 className="text-lg leading-6 font-medium text-gray-900">
              {selectedAgent ? `Edit ${selectedAgent.name}` : 'Create New Agent'}
            </h2>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Configure the agent's personality, behavior, and response patterns.
            </p>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div className="sm:col-span-3">
                  <label htmlFor="agent_type" className="block text-sm font-medium text-gray-700">Agent Type</label>
                  <select
                    id="agent_type"
                    name="agent_type"
                    value={formData.agent_type}
                    onChange={handleInputChange}
                    className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  >
                    {agentTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                
                <div className="sm:col-span-3">
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">Agent Name</label>
                  <input
                    type="text"
                    name="name"
                    id="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="e.g., Friendly Greeter"
                  />
                </div>
                
                <div className="sm:col-span-6">
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
                  <input
                    type="text"
                    name="description"
                    id="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    className="mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Brief description of the agent's purpose and characteristics"
                  />
                </div>
                
                {/* LLM Provider */}
                <div className="sm:col-span-3">
                  <label htmlFor="llm_provider" className="block text-sm font-medium text-gray-700">LLM Provider</label>
                  <select
                    id="llm_provider"
                    name="llm_provider"
                    value={formData.llm_provider}
                    onChange={handleInputChange}
                    className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  >
                    {llmProviders.map(provider => (
                      <option key={provider.value} value={provider.value}>{provider.label}</option>
                    ))}
                  </select>
                </div>
                
                {/* Model Selection */}
                <div className="sm:col-span-3">
                  <label htmlFor="model_id" className="block text-sm font-medium text-gray-700">
                    Model
                    {loadingModels && <span className="ml-2 text-xs text-gray-500">(Loading...)</span>}
                  </label>
                  <select
                    id="model_id"
                    name="model_id"
                    value={formData.model_id}
                    onChange={handleInputChange}
                    className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    disabled={loadingModels}
                  >
                    {currentModels.map(model => (
                      <option key={model.id} value={model.id}>
                        {formData.llm_provider === 'openrouter' 
                          ? `${model.name} (${model.provider})` 
                          : model.name}
                      </option>
                    ))}
                  </select>
                  {formData.llm_provider === 'openrouter' && (
                    <p className="mt-1 text-xs text-gray-500">
                      Note: Using OpenRouter requires an OpenRouter API key in Settings.
                    </p>
                  )}
                </div>
                
                <div className="sm:col-span-6">
                  <label htmlFor="system_prompt" className="block text-sm font-medium text-gray-700">System Prompt</label>
                  <p className="mt-1 text-sm text-gray-500">This is the instruction that defines the agent's behavior and personality.</p>
                  <textarea
                    id="system_prompt"
                    name="system_prompt"
                    rows={6}
                    value={formData.system_prompt}
                    onChange={handleInputChange}
                    required
                    className="mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="You are a real estate agent specialized in..."
                  />
                </div>
                
                <div className="sm:col-span-6">
                  <h3 className="text-sm font-medium text-gray-700">Model Configuration</h3>
                  <p className="mt-1 text-sm text-gray-500">Adjust these parameters to control the agent's creativity and response patterns.</p>
                  
                  <div className="mt-3 grid grid-cols-1 gap-y-4 gap-x-4 sm:grid-cols-2">
                    <div>
                      <label htmlFor="temperature" className="block text-sm font-medium text-gray-700">
                        Temperature: {formData.configuration.temperature}
                      </label>
                      <input
                        type="range"
                        id="temperature"
                        name="temperature"
                        min="0"
                        max="1"
                        step="0.1"
                        value={formData.configuration.temperature}
                        onChange={handleConfigChange}
                        className="mt-1 w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                      <p className="mt-1 text-xs text-gray-500">Controls randomness (0 = deterministic, 1 = creative)</p>
                    </div>
                    
                    <div>
                      <label htmlFor="top_p" className="block text-sm font-medium text-gray-700">
                        Top P: {formData.configuration.top_p}
                      </label>
                      <input
                        type="range"
                        id="top_p"
                        name="top_p"
                        min="0"
                        max="1"
                        step="0.05"
                        value={formData.configuration.top_p}
                        onChange={handleConfigChange}
                        className="mt-1 w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                      <p className="mt-1 text-xs text-gray-500">Controls diversity of word choices</p>
                    </div>
                    
                    <div>
                      <label htmlFor="presence_penalty" className="block text-sm font-medium text-gray-700">
                        Presence Penalty: {formData.configuration.presence_penalty}
                      </label>
                      <input
                        type="range"
                        id="presence_penalty"
                        name="presence_penalty"
                        min="0"
                        max="2"
                        step="0.1"
                        value={formData.configuration.presence_penalty}
                        onChange={handleConfigChange}
                        className="mt-1 w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                      <p className="mt-1 text-xs text-gray-500">Reduces repetition of topics</p>
                    </div>
                    
                    <div>
                      <label htmlFor="frequency_penalty" className="block text-sm font-medium text-gray-700">
                        Frequency Penalty: {formData.configuration.frequency_penalty}
                      </label>
                      <input
                        type="range"
                        id="frequency_penalty"
                        name="frequency_penalty"
                        min="0"
                        max="2"
                        step="0.1"
                        value={formData.configuration.frequency_penalty}
                        onChange={handleConfigChange}
                        className="mt-1 w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                      <p className="mt-1 text-xs text-gray-500">Reduces repetition of words and phrases</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-5 sm:mt-6 sm:flex sm:flex-row-reverse">
                <button
                  type="submit"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  {selectedAgent ? 'Update Agent' : 'Create Agent'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setSelectedAgent(null);
                    setPreviewResponse('');
                  }}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleGeneratePreview}
                  disabled={isGeneratingPreview || !formData.system_prompt}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
                >
                  {isGeneratingPreview ? 'Generating...' : 'Generate Preview'}
                </button>
              </div>
              
              {previewResponse && (
                <div className="mt-6 p-4 bg-gray-50 rounded-md">
                  <h3 className="text-sm font-medium text-gray-700">Preview Response</h3>
                  <div className="mt-2 p-3 bg-white rounded border border-gray-200">
                    <p className="text-sm text-gray-800 whitespace-pre-line">{previewResponse}</p>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">This is a simulated response based on your agent configuration.</p>
                </div>
              )}
            </form>
          </div>
        </div>
      ) : (
        <div className="mt-6">
          {loading ? (
            <div className="text-center py-10">
              <p className="text-gray-500">Loading agents...</p>
            </div>
          ) : agents.length === 0 ? (
            <div className="text-center py-10">
              <p className="text-gray-500">No agents configured yet</p>
              <button
                onClick={handleNewAgent}
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Create Your First Agent
              </button>
            </div>
          ) : (
            <div className="mt-2 grid gap-5 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
              {agents.map(agent => (
                <div key={agent.id} className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="px-4 py-5 sm:p-6">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-indigo-100 text-indigo-800">
                        {agent.agent_type === 'initial_contact' && (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                        )}
                        {agent.agent_type === 'qualifier' && (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                        {agent.agent_type === 'nurturer' && (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                          </svg>
                        )}
                        {agent.agent_type === 'objection_handler' && (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                          </svg>
                        )}
                        {agent.agent_type === 'closer' && (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                          </svg>
                        )}
                        {agent.agent_type === 'appointment_setter' && (
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        )}
                      </div>
                      <div className="ml-3">
                        <h3 className="text-lg leading-6 font-medium text-gray-900">{agent.name}</h3>
                        <p className="text-sm text-gray-500">
                          {agentTypes.find(t => t.value === agent.agent_type)?.label || agent.agent_type}
                        </p>
                      </div>
                    </div>
                    
                    <div className="mt-3">
                      <p className="text-sm text-gray-500">{agent.description}</p>
                    </div>
                    
                    <div className="mt-3">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-blue-100 text-blue-800 mr-2">
                        {agent.llm_provider === 'openai' ? 'OpenAI' : 
                         agent.llm_provider === 'anthropic' ? 'Anthropic' : 
                         agent.llm_provider === 'openrouter' ? 'OpenRouter' : 
                         agent.llm_provider}
                      </span>
                      
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-sm font-medium bg-purple-100 text-purple-800">
                        {agent.model_id.split('/').pop()}
                      </span>
                    </div>
                    
                    <div className="mt-3 flex justify-between items-center">
                      <div className="flex items-center">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          v{agent.version}
                        </span>
                        <span className="ml-2 text-xs text-gray-500">
                          Created {new Date(agent.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <div>
                        <button
                          onClick={() => handleSelectAgent(agent)}
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                          Edit
                        </button>
                      </div>
                    </div>
                  </div>
                  <div className="border-t border-gray-200 px-4 py-4 sm:px-6">
                    <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider">System Prompt Preview</h4>
                    <div className="mt-1 text-sm text-gray-800 max-h-20 overflow-hidden">
                      {agent.system_prompt.substring(0, 150)}...
                    </div>
                    <div className="mt-3 flex justify-between">
                      <button className="text-xs text-indigo-600 hover:text-indigo-500">
                        View Full Prompt
                      </button>
                      <div className="flex space-x-2">
                        <button className="text-xs text-gray-600 hover:text-gray-500">
                          Duplicate
                        </button>
                        <button className="text-xs text-red-600 hover:text-red-500">
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AgentTraining;