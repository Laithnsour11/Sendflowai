import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Settings = ({ currentOrg }) => {
  const [apiKeys, setApiKeys] = useState({
    ghl_api_key: '',
    openai_api_key: '',
    vapi_api_key: '',
    mem0_api_key: '',
    sendblue_api_key: '',
    openrouter_api_key: ''
  });
  
  const [validationStatus, setValidationStatus] = useState({
    mem0_api_key: null,
    vapi_api_key: null,
    sendblue_api_key: null,
    openai_api_key: null,
    openrouter_api_key: null
  });
  
  const [aiSettings, setAiSettings] = useState({
    model: 'gpt-4o',
    temperature: 0.7,
    voice_provider: 'elevenlabs',
    voice_id: 'voice1'
  });
  
  const [integrationStatus, setIntegrationStatus] = useState({
    ghl: { connected: false, status: 'Not configured' },
    vapi: { connected: false, status: 'Not configured' },
    mem0: { connected: false, status: 'Not configured' },
    sendblue: { connected: false, status: 'Not configured' },
    openai: { connected: false, status: 'Not configured' },
    openrouter: { connected: false, status: 'Not configured' }
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState(null);
  
  const backendUrl = process.env.REACT_APP_BACKEND_URL;
  
  // Load settings
  useEffect(() => {
    const loadSettings = async () => {
      if (!currentOrg || !currentOrg.id) return;
      
      try {
        setLoading(true);
        
        // Load API keys
        const keysResponse = await axios.get(
          `${backendUrl}/api/settings/api-keys/${currentOrg.id}`
        );
        
        if (keysResponse.data) {
          setApiKeys(keysResponse.data);
        }
        
        // Load integration status
        const statusResponse = await axios.get(
          `${backendUrl}/api/settings/integration-status/${currentOrg.id}`
        );
        
        if (statusResponse.data) {
          setIntegrationStatus(statusResponse.data);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error loading settings:', error);
        setLoading(false);
      }
    };
    
    loadSettings();
  }, [currentOrg, backendUrl]);
  
  // Handle API key changes
  const handleApiKeyChange = (e) => {
    const { name, value } = e.target;
    setApiKeys(prev => ({ ...prev, [name]: value }));
    
    // Reset validation status when the key changes
    if (validationStatus.hasOwnProperty(name)) {
      setValidationStatus(prev => ({ ...prev, [name]: null }));
    }
  };
  
  // Validate Mem0 API key
  const validateMem0ApiKey = async () => {
    if (!apiKeys.mem0_api_key) {
      setValidationStatus(prev => ({ 
        ...prev, 
        mem0_api_key: { valid: false, message: 'API key is required' } 
      }));
      return;
    }
    
    try {
      const response = await axios.post(
        `${backendUrl}/api/settings/validate-mem0-key`,
        { api_key: apiKeys.mem0_api_key }
      );
      
      setValidationStatus(prev => ({ ...prev, mem0_api_key: response.data }));
    } catch (error) {
      console.error('Error validating Mem0 API key:', error);
      setValidationStatus(prev => ({ 
        ...prev, 
        mem0_api_key: { 
          valid: false, 
          message: error.response?.data?.detail || 'Error validating API key' 
        } 
      }));
    }
  };
  
  // Handle AI settings changes
  const handleAiSettingChange = (e) => {
    const { name, value } = e.target;
    setAiSettings(prev => ({ ...prev, [name]: value }));
  };
  
  // Save settings
  const handleSaveSettings = async () => {
    if (!currentOrg || !currentOrg.id) return;
    
    try {
      setSaving(true);
      setSaveSuccess(false);
      setSaveError(null);
      
      // Save API keys
      const response = await axios.put(
        `${backendUrl}/api/settings/api-keys/${currentOrg.id}`,
        apiKeys
      );
      
      if (response.data) {
        setApiKeys(response.data);
      }
      
      // Refresh integration status
      const statusResponse = await axios.get(
        `${backendUrl}/api/settings/integration-status/${currentOrg.id}`
      );
      
      if (statusResponse.data) {
        setIntegrationStatus(statusResponse.data);
      }
      
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
  
  // Render connection status badge
  const renderConnectionStatus = (status) => {
    if (!status) return null;
    
    if (status.connected) {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
          {status.status || 'Connected'}
        </span>
      );
    } else {
      return (
        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
          {status.status || 'Not Connected'}
        </span>
      );
    }
  };
  
  // Render API key validation status
  const renderValidationStatus = (key) => {
    const status = validationStatus[key];
    
    if (!status) return null;
    
    if (status.valid) {
      return (
        <div className="mt-1 text-sm text-green-600">
          ✓ {status.message || 'API key is valid'}
        </div>
      );
    } else {
      return (
        <div className="mt-1 text-sm text-red-600">
          ✗ {status.message || 'Invalid API key'}
        </div>
      );
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
            {/* Go High Level API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Go High Level API Key
                <p className="mt-1 text-xs text-gray-400">Required for GHL integration</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <input
                    type="password"
                    name="ghl_api_key"
                    value={apiKeys.ghl_api_key || ''}
                    onChange={handleApiKeyChange}
                    placeholder="Enter your GHL API key"
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                  <div className="ml-3">
                    {renderConnectionStatus(integrationStatus.ghl)}
                  </div>
                </div>
              </dd>
            </div>
            
            {/* Mem0 API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Mem0 API Key
                <p className="mt-1 text-xs text-gray-400">Required for memory capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <div className="flex-grow">
                    <input
                      type="password"
                      name="mem0_api_key"
                      value={apiKeys.mem0_api_key || ''}
                      onChange={handleApiKeyChange}
                      placeholder="Enter your Mem0 API key"
                      className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                    {renderMem0ValidationStatus()}
                  </div>
                  <div className="ml-3 flex items-center">
                    <button
                      onClick={validateMem0ApiKey}
                      type="button"
                      className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Validate
                    </button>
                    <div className="ml-2">
                      {renderConnectionStatus(integrationStatus.mem0)}
                    </div>
                  </div>
                </div>
              </dd>
            </div>
            
            {/* Vapi API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Vapi.ai API Key
                <p className="mt-1 text-xs text-gray-400">Required for voice capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <input
                    type="password"
                    name="vapi_api_key"
                    value={apiKeys.vapi_api_key || ''}
                    onChange={handleApiKeyChange}
                    placeholder="Enter your Vapi.ai API key"
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                  <div className="ml-3">
                    {renderConnectionStatus(integrationStatus.vapi)}
                  </div>
                </div>
              </dd>
            </div>
            
            {/* SendBlue API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                SendBlue API Key
                <p className="mt-1 text-xs text-gray-400">Required for SMS capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <input
                    type="password"
                    name="sendblue_api_key"
                    value={apiKeys.sendblue_api_key || ''}
                    onChange={handleApiKeyChange}
                    placeholder="Enter your SendBlue API key"
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                  <div className="ml-3">
                    {renderConnectionStatus(integrationStatus.sendblue)}
                  </div>
                </div>
              </dd>
            </div>
            
            {/* OpenAI API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                OpenAI API Key
                <p className="mt-1 text-xs text-gray-400">Required for AI capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <input
                    type="password"
                    name="openai_api_key"
                    value={apiKeys.openai_api_key || ''}
                    onChange={handleApiKeyChange}
                    placeholder="Enter your OpenAI API key"
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                  <div className="ml-3">
                    {renderConnectionStatus(integrationStatus.openai)}
                  </div>
                </div>
              </dd>
            </div>
            
            {/* OpenRouter API Key */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                OpenRouter API Key
                <p className="mt-1 text-xs text-gray-400">For multi-model AI capabilities</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <input
                    type="password"
                    name="openrouter_api_key"
                    value={apiKeys.openrouter_api_key || ''}
                    onChange={handleApiKeyChange}
                    placeholder="Enter your OpenRouter API key"
                    className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                  <div className="ml-3">
                    {renderConnectionStatus(integrationStatus.openrouter)}
                  </div>
                </div>
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
                  <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                  <option value="claude-3-haiku">Claude 3 Haiku</option>
                </select>
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
    </div>
  );
};

export default Settings;