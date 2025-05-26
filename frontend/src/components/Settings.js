import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Settings = ({ currentOrg }) => {
  const [apiKeys, setApiKeys] = useState({
    ghl_client_id: '',
    ghl_client_secret: '',
    ghl_shared_secret: '',
    openai_api_key: '',
    vapi_api_key: '',
    mem0_api_key: '',
    openrouter_api_key: '',
    sendblue_api_key: '',
    sendblue_api_secret: '',
    supabase_url: '',
    supabase_key: ''
  });
  
  const [aiSettings, setAiSettings] = useState({
    model: 'gpt-4o',
    temperature: 0.7,
    voice_provider: 'elevenlabs',
    voice_id: 'voice1'
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState(null);
  
  // Load settings
  useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        
        // In a real app, we would fetch this data from the API
        // const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/settings/api-keys/${currentOrg.id}`);
        
        // Mock data for demo
        setTimeout(() => {
          setApiKeys({
            ghl_client_id: '681a8d486b267326cb42a4db-mb5qftwj',
            ghl_client_secret: '••••••••b62',
            ghl_shared_secret: '••••••••fa9',
            openai_api_key: '••••••••5678',
            vapi_api_key: '',
            mem0_api_key: 'm0-TTwLd8awIP6aFAixLPn1lgkIUR2DJlDTzApPil8E',
            openrouter_api_key: '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',
            sendblue_api_key: '',
            sendblue_api_secret: '',
            supabase_url: '',
            supabase_key: 'sbp_6ea3d96a8efc1a50026610a12c4728d5b9793434'
          });
          
          setAiSettings({
            model: 'gpt-4o',
            temperature: 0.7,
            voice_provider: 'elevenlabs',
            voice_id: 'voice1'
          });
          
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error loading settings:', error);
        setLoading(false);
      }
    };
    
    loadSettings();
  }, [currentOrg]);
  
  // Handle API key changes
  const handleApiKeyChange = (e) => {
    const { name, value } = e.target;
    setApiKeys(prev => ({ ...prev, [name]: value }));
  };
  
  // Handle AI settings changes
  const handleAiSettingChange = (e) => {
    const { name, value } = e.target;
    setAiSettings(prev => ({ ...prev, [name]: value }));
  };
  
  // Save settings
  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      setSaveSuccess(false);
      setSaveError(null);
      
      // In a real app, we would send this data to the API
      // const response = await axios.put(`${process.env.REACT_APP_BACKEND_URL}/api/settings/api-keys/${currentOrg.id}`, apiKeys);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSaveSuccess(true);
      setSaving(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSaveSuccess(false);
      }, 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveError('Failed to save settings. Please try again.');
      setSaving(false);
    }
  };
  
  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">Settings</h1>
      
      {/* API Keys Section */}
      <div className="mt-6 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h2 className="text-lg leading-6 font-medium text-gray-900">API Keys</h2>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">Configure your third-party API integrations.</p>
          </div>
          <button
            onClick={handleSaveSettings}
            disabled={saving}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
        
        {saveSuccess && (
          <div className="mx-4 mb-4 bg-green-50 p-4 rounded-md">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">Settings saved successfully!</p>
              </div>
            </div>
          </div>
        )}
        
        {saveError && (
          <div className="mx-4 mb-4 bg-red-50 p-4 rounded-md">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-red-800">{saveError}</p>
              </div>
            </div>
          </div>
        )}
        
        <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
          <dl className="sm:divide-y sm:divide-gray-200">
            <div className="py-4 sm:py-5 sm:px-6">
              <h3 className="text-md font-medium text-indigo-600">Core Integrations</h3>
            </div>
            
            {/* Go High Level OAuth Credentials */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Go High Level Client ID
                <p className="mt-1 text-xs text-gray-400">Required for GHL OAuth integration</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="text"
                  name="ghl_client_id"
                  value={apiKeys.ghl_client_id}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your GHL Client ID"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Go High Level Client Secret
                <p className="mt-1 text-xs text-gray-400">Required for GHL OAuth integration</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="password"
                  name="ghl_client_secret"
                  value={apiKeys.ghl_client_secret}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your GHL Client Secret"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Go High Level Shared Secret
                <p className="mt-1 text-xs text-gray-400">Required for GHL webhook verification</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="password"
                  name="ghl_shared_secret"
                  value={apiKeys.ghl_shared_secret}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your GHL Shared Secret"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            
            <div className="py-4 sm:py-5 sm:px-6">
              <h3 className="text-md font-medium text-indigo-600">AI & Memory Integrations</h3>
            </div>
            
            {/* OpenAI API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                OpenAI API Key
                <p className="mt-1 text-xs text-gray-400">Required for embeddings and knowledge base capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="password"
                  name="openai_api_key"
                  value={apiKeys.openai_api_key}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your OpenAI API key"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            
            {/* OpenRouter API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                OpenRouter API Key
                <p className="mt-1 text-xs text-gray-400">Required for multi-model AI capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="password"
                  name="openrouter_api_key"
                  value={apiKeys.openrouter_api_key}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your OpenRouter API key"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            
            {/* Mem0 API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Mem0 API Key
                <p className="mt-1 text-xs text-gray-400">Required for persistent memory capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="password"
                  name="mem0_api_key"
                  value={apiKeys.mem0_api_key}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your Mem0 API key"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            
            {/* Supabase URL */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Supabase URL
                <p className="mt-1 text-xs text-gray-400">Required for knowledge base storage</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="text"
                  name="supabase_url"
                  value={apiKeys.supabase_url}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your Supabase URL"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            
            {/* Supabase Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Supabase Key
                <p className="mt-1 text-xs text-gray-400">Required for knowledge base storage</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="password"
                  name="supabase_key"
                  value={apiKeys.supabase_key}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your Supabase Key"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            
            <div className="py-4 sm:py-5 sm:px-6">
              <h3 className="text-md font-medium text-indigo-600">Communication Integrations</h3>
            </div>
            
            {/* Vapi API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Vapi.ai API Key
                <p className="mt-1 text-xs text-gray-400">Required for voice capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="password"
                  name="vapi_api_key"
                  value={apiKeys.vapi_api_key}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your Vapi.ai API key"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            
            {/* SendBlue API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                SendBlue API Key
                <p className="mt-1 text-xs text-gray-400">Required for SMS capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="password"
                  name="sendblue_api_key"
                  value={apiKeys.sendblue_api_key}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your SendBlue API key"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
            
            {/* SendBlue API Secret */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                SendBlue API Secret
                <p className="mt-1 text-xs text-gray-400">Required for SMS capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <input
                  type="password"
                  name="sendblue_api_secret"
                  value={apiKeys.sendblue_api_secret}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your SendBlue API secret"
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </dd>
            </div>
          </dl>
        </div>
      </div>
      
      {/* AI Configuration */}
      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h2 className="text-lg leading-6 font-medium text-gray-900">AI Configuration</h2>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">Configure AI behavior and settings.</p>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
          <dl className="sm:divide-y sm:divide-gray-200">
            {/* LLM Model */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                LLM Model
                <p className="mt-1 text-xs text-gray-400">Select the AI model to use</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <select
                  name="model"
                  value={aiSettings.model}
                  onChange={handleAiSettingChange}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="gpt-4o">GPT-4o (Default)</option>
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                  <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                  <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                  <option value="anthropic/claude-3-opus">Claude 3 Opus (via OpenRouter)</option>
                  <option value="anthropic/claude-3-sonnet">Claude 3 Sonnet (via OpenRouter)</option>
                  <option value="anthropic/claude-3-haiku">Claude 3 Haiku (via OpenRouter)</option>
                  <option value="meta-llama/llama-3-70b-instruct">Llama 3 70B (via OpenRouter)</option>
                  <option value="google/gemini-1.5-pro">Gemini 1.5 Pro (via OpenRouter)</option>
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  Note: OpenRouter models require an OpenRouter API key.
                </p>
              </dd>
            </div>
            
            {/* Temperature */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Temperature
                <p className="mt-1 text-xs text-gray-400">Controls randomness (0.0 to 1.0)</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <input
                    type="range"
                    name="temperature"
                    min="0"
                    max="1"
                    step="0.1"
                    value={aiSettings.temperature}
                    onChange={handleAiSettingChange}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <span className="ml-2 text-gray-700">{aiSettings.temperature}</span>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Lower values produce more consistent results, higher values more creative ones.
                </p>
              </dd>
            </div>
            
            {/* Voice Provider */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Voice Provider
                <p className="mt-1 text-xs text-gray-400">Select the voice synthesis provider</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <select
                  name="voice_provider"
                  value={aiSettings.voice_provider}
                  onChange={handleAiSettingChange}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="elevenlabs">ElevenLabs (Premium quality)</option>
                  <option value="openai">OpenAI TTS</option>
                  <option value="google">Google Cloud TTS</option>
                </select>
              </dd>
            </div>
            
            {/* Voice ID */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Voice ID
                <p className="mt-1 text-xs text-gray-400">Select the voice to use</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <select
                  name="voice_id"
                  value={aiSettings.voice_id}
                  onChange={handleAiSettingChange}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="voice1">Professional Male (Default)</option>
                  <option value="voice2">Professional Female</option>
                  <option value="voice3">Friendly Male</option>
                  <option value="voice4">Friendly Female</option>
                </select>
                <p className="mt-2 text-xs text-gray-500">
                  <button className="text-indigo-600 hover:text-indigo-900">
                    Preview voice sample
                  </button>
                </p>
              </dd>
            </div>
          </dl>
        </div>
      </div>
      
      {/* GHL Integration */}
      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h2 className="text-lg leading-6 font-medium text-gray-900">Go High Level Integration</h2>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">Configure your GHL integration settings.</p>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
          <dl className="sm:divide-y sm:divide-gray-200">
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {apiKeys.ghl_client_id && apiKeys.ghl_client_secret && apiKeys.ghl_shared_secret ? (
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    Connected
                  </span>
                ) : (
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                    Not Connected
                  </span>
                )}
              </dd>
            </div>
            
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Webhook URL</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex">
                  <input
                    type="text"
                    readOnly
                    value={`${process.env.REACT_APP_BACKEND_URL}/api/ghl/webhook`}
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md bg-gray-50"
                  />
                  <button
                    onClick={() => navigator.clipboard.writeText(`${process.env.REACT_APP_BACKEND_URL}/api/ghl/webhook`)}
                    className="ml-2 inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Copy
                  </button>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Configure this webhook URL in your GHL account to receive events.
                </p>
              </dd>
            </div>
            
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Custom Fields</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <button className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                  Set Up Custom Fields
                </button>
                <p className="mt-1 text-xs text-gray-500">
                  Configure custom fields in GHL for AI-specific data.
                </p>
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
};

export default Settings;