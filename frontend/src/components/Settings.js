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
    provider: 'openrouter',
    temperature: 0.7,
    voice_provider: 'vapi',
    voice_id: 'professional_male',
    speech_rate: 'normal',
    response_style: 'professional',
    max_response_length: 'medium',
    objection_style: 'consultative',
    // Agent-specific models
    initial_contact_model: '',
    qualifier_model: '',
    nurturer_model: '',
    objection_handler_model: '',
    appointment_setter_model: '',
    closer_model: ''
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
  
  // Validate Vapi API key
  const validateVapiApiKey = async () => {
    if (!apiKeys.vapi_api_key) {
      setValidationStatus(prev => ({ 
        ...prev, 
        vapi_api_key: { valid: false, message: 'API key is required' } 
      }));
      return;
    }
    
    try {
      const response = await axios.post(
        `${backendUrl}/api/settings/validate-vapi-key`,
        { api_key: apiKeys.vapi_api_key }
      );
      
      setValidationStatus(prev => ({ ...prev, vapi_api_key: response.data }));
    } catch (error) {
      console.error('Error validating Vapi API key:', error);
      setValidationStatus(prev => ({ 
        ...prev, 
        vapi_api_key: { 
          valid: false, 
          message: error.response?.data?.detail || 'Error validating API key' 
        } 
      }));
    }
  };
  
  // Validate SendBlue API key
  const validateSendBlueApiKey = async () => {
    if (!apiKeys.sendblue_api_key) {
      setValidationStatus(prev => ({ 
        ...prev, 
        sendblue_api_key: { valid: false, message: 'API key is required' } 
      }));
      return;
    }
    
    try {
      const response = await axios.post(
        `${backendUrl}/api/settings/validate-sendblue-key`,
        { api_key: apiKeys.sendblue_api_key }
      );
      
      setValidationStatus(prev => ({ ...prev, sendblue_api_key: response.data }));
    } catch (error) {
      console.error('Error validating SendBlue API key:', error);
      setValidationStatus(prev => ({ 
        ...prev, 
        sendblue_api_key: { 
          valid: false, 
          message: error.response?.data?.detail || 'Error validating API key' 
        } 
      }));
    }
  };
  
  // Validate OpenAI API key
  const validateOpenAIApiKey = async () => {
    if (!apiKeys.openai_api_key) {
      setValidationStatus(prev => ({ 
        ...prev, 
        openai_api_key: { valid: false, message: 'API key is required' } 
      }));
      return;
    }
    
    try {
      const response = await axios.post(
        `${backendUrl}/api/settings/validate-openai-key`,
        { api_key: apiKeys.openai_api_key }
      );
      
      setValidationStatus(prev => ({ ...prev, openai_api_key: response.data }));
    } catch (error) {
      console.error('Error validating OpenAI API key:', error);
      setValidationStatus(prev => ({ 
        ...prev, 
        openai_api_key: { 
          valid: false, 
          message: error.response?.data?.detail || 'Error validating API key' 
        } 
      }));
    }
  };
  
  // Validate OpenRouter API key
  const validateOpenRouterApiKey = async () => {
    if (!apiKeys.openrouter_api_key) {
      setValidationStatus(prev => ({ 
        ...prev, 
        openrouter_api_key: { valid: false, message: 'API key is required' } 
      }));
      return;
    }
    
    try {
      const response = await axios.post(
        `${backendUrl}/api/settings/validate-openrouter-key`,
        { api_key: apiKeys.openrouter_api_key }
      );
      
      setValidationStatus(prev => ({ ...prev, openrouter_api_key: response.data }));
    } catch (error) {
      console.error('Error validating OpenRouter API key:', error);
      setValidationStatus(prev => ({ 
        ...prev, 
        openrouter_api_key: { 
          valid: false, 
          message: error.response?.data?.detail || 'Error validating API key' 
        } 
      }));
    }
  };
  
  // Connect to GHL and initiate OAuth flow
  const handleConnectGHL = async () => {
    if (!currentOrg || !currentOrg.id) return;
    
    // Validate GHL credentials
    if (!apiKeys.ghl_client_id || !apiKeys.ghl_client_secret) {
      alert('GHL Client ID and Client Secret are required for connection');
      return;
    }
    
    try {
      // First save the credentials
      setSaving(true);
      
      // Save API keys
      await axios.put(
        `${backendUrl}/api/settings/api-keys/${currentOrg.id}`,
        apiKeys
      );
      
      // Initiate OAuth flow
      const response = await axios.post(
        `${backendUrl}/api/ghl/initiate-oauth`,
        { 
          org_id: currentOrg.id,
          redirect_uri: window.location.origin + '/ghl-callback'
        }
      );
      
      // Redirect to GHL OAuth page
      if (response.data && response.data.authorization_url) {
        window.location.href = response.data.authorization_url;
      } else {
        throw new Error('No authorization URL returned');
      }
      
    } catch (error) {
      console.error('Error connecting to GHL:', error);
      setSaveError('Failed to connect to GHL. Please check your credentials and try again.');
      setSaving(false);
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
            {/* GHL Client ID */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Go High Level Client ID
                <p className="mt-1 text-xs text-gray-400">Required for GHL integration</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <div className="flex-grow">
                    <input
                      type="password"
                      name="ghl_client_id"
                      value={apiKeys.ghl_client_id || ''}
                      onChange={handleApiKeyChange}
                      placeholder="Enter your GHL Client ID"
                      className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                  </div>
                  <div className="ml-2">
                    {renderConnectionStatus(integrationStatus.ghl)}
                  </div>
                </div>
              </dd>
            </div>
            
            {/* GHL Client Secret */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Go High Level Client Secret
                <p className="mt-1 text-xs text-gray-400">Required for GHL API authentication</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <div className="flex-grow">
                    <input
                      type="password"
                      name="ghl_client_secret"
                      value={apiKeys.ghl_client_secret || ''}
                      onChange={handleApiKeyChange}
                      placeholder="Enter your GHL Client Secret"
                      className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                  </div>
                </div>
              </dd>
            </div>
            
            {/* GHL Shared Secret */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Go High Level Webhook Shared Secret
                <p className="mt-1 text-xs text-gray-400">Required for verifying GHL webhooks</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="flex items-center">
                  <div className="flex-grow">
                    <input
                      type="password"
                      name="ghl_shared_secret"
                      value={apiKeys.ghl_shared_secret || ''}
                      onChange={handleApiKeyChange}
                      placeholder="Enter your GHL Webhook Shared Secret"
                      className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                  </div>
                  <div className="ml-3 flex items-center">
                    <button
                      onClick={handleConnectGHL}
                      type="button"
                      className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Connect GHL
                    </button>
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
                    {renderValidationStatus('mem0_api_key')}
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
                  <div className="flex-grow">
                    <input
                      type="password"
                      name="vapi_api_key"
                      value={apiKeys.vapi_api_key || ''}
                      onChange={handleApiKeyChange}
                      placeholder="Enter your Vapi.ai API key"
                      className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                    {renderValidationStatus('vapi_api_key')}
                  </div>
                  <div className="ml-3 flex items-center">
                    <button
                      onClick={validateVapiApiKey}
                      type="button"
                      className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Validate
                    </button>
                    <div className="ml-2">
                      {renderConnectionStatus(integrationStatus.vapi)}
                    </div>
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
                  <div className="flex-grow">
                    <input
                      type="password"
                      name="sendblue_api_key"
                      value={apiKeys.sendblue_api_key || ''}
                      onChange={handleApiKeyChange}
                      placeholder="Enter your SendBlue API key"
                      className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                    {renderValidationStatus('sendblue_api_key')}
                  </div>
                  <div className="ml-3 flex items-center">
                    <button
                      onClick={validateSendBlueApiKey}
                      type="button"
                      className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Validate
                    </button>
                    <div className="ml-2">
                      {renderConnectionStatus(integrationStatus.sendblue)}
                    </div>
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
                  <div className="flex-grow">
                    <input
                      type="password"
                      name="openai_api_key"
                      value={apiKeys.openai_api_key || ''}
                      onChange={handleApiKeyChange}
                      placeholder="Enter your OpenAI API key"
                      className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                    {renderValidationStatus('openai_api_key')}
                  </div>
                  <div className="ml-3 flex items-center">
                    <button
                      onClick={validateOpenAIApiKey}
                      type="button"
                      className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Validate
                    </button>
                    <div className="ml-2">
                      {renderConnectionStatus(integrationStatus.openai)}
                    </div>
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
                  <div className="flex-grow">
                    <input
                      type="password"
                      name="openrouter_api_key"
                      value={apiKeys.openrouter_api_key || ''}
                      onChange={handleApiKeyChange}
                      placeholder="Enter your OpenRouter API key"
                      className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    />
                    {renderValidationStatus('openrouter_api_key')}
                  </div>
                  <div className="ml-3 flex items-center">
                    <button
                      onClick={validateOpenRouterApiKey}
                      type="button"
                      className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Validate
                    </button>
                    <div className="ml-2">
                      {renderConnectionStatus(integrationStatus.openrouter)}
                    </div>
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
            {/* AI Configuration - Updated Structure */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Primary LLM Model
                <p className="mt-1 text-xs text-gray-400">Select the primary AI model for agents</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <select
                  name="model"
                  value={aiSettings.model}
                  onChange={handleAiSettingChange}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="gpt-4o">GPT-4o (OpenAI)</option>
                  <option value="gpt-4o-mini">GPT-4o Mini (OpenAI)</option>
                  <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet (Latest)</option>
                  <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku (Latest)</option>
                  <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                  <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                  <option value="llama-3.1-405b-instruct">Llama 3.1 405B</option>
                  <option value="llama-3.1-70b-instruct">Llama 3.1 70B</option>
                </select>
                <p className="mt-1 text-xs text-gray-500">
                  Latest models available through OpenRouter integration for best performance.
                </p>
              </dd>
            </div>
            
            {/* Model Provider Selection */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Model Provider
                <p className="mt-1 text-xs text-gray-400">Route through specific provider</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <select
                  name="provider"
                  value={aiSettings.provider || 'openrouter'}
                  onChange={handleAiSettingChange}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="openrouter">OpenRouter (Multi-Model Access)</option>
                  <option value="openai">OpenAI Direct</option>
                  <option value="anthropic">Anthropic Direct</option>
                  <option value="google">Google AI Direct</option>
                </select>
              </dd>
            </div>

            {/* Agent-Specific Model Selection */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Agent-Specific Models
                <p className="mt-1 text-xs text-gray-400">Configure different models for different agent types</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="space-y-3">
                  {[
                    { key: 'initial_contact_model', label: 'Initial Contact Agent' },
                    { key: 'qualifier_model', label: 'Qualifier Agent' },
                    { key: 'nurturer_model', label: 'Nurturer Agent' },
                    { key: 'objection_handler_model', label: 'Objection Handler Agent' },
                    { key: 'appointment_setter_model', label: 'Appointment Setter Agent' },
                    { key: 'closer_model', label: 'Closer Agent' }
                  ].map(agent => (
                    <div key={agent.key} className="flex items-center space-x-3">
                      <label className="text-sm text-gray-600 w-40">{agent.label}:</label>
                      <select
                        name={agent.key}
                        value={aiSettings[agent.key] || aiSettings.model}
                        onChange={handleAiSettingChange}
                        className="flex-1 text-sm border border-gray-300 rounded px-2 py-1 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="">Use Primary Model</option>
                        <option value="gpt-4o">GPT-4o (OpenAI)</option>
                        <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                        <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                        <option value="llama-3.1-405b-instruct">Llama 3.1 405B</option>
                      </select>
                    </div>
                  ))}
                </div>
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
                  <option value="vapi">Vapi.ai (Recommended)</option>
                  <option value="elevenlabs">ElevenLabs (Premium quality)</option>
                  <option value="openai">OpenAI TTS</option>
                  <option value="google">Google Cloud TTS</option>
                  <option value="azure">Azure Speech Services</option>
                </select>
              </dd>
            </div>
            
            {/* Voice Configuration */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Voice Configuration
                <p className="mt-1 text-xs text-gray-400">Configure voice settings for each agent type</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Default Voice</label>
                      <select
                        name="voice_id"
                        value={aiSettings.voice_id}
                        onChange={handleAiSettingChange}
                        className="w-full text-sm border border-gray-300 rounded px-2 py-1 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="professional_male">Professional Male</option>
                        <option value="professional_female">Professional Female</option>
                        <option value="friendly_male">Friendly Male</option>
                        <option value="friendly_female">Friendly Female</option>
                        <option value="authoritative_male">Authoritative Male</option>
                        <option value="warm_female">Warm Female</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">Speech Rate</label>
                      <select
                        name="speech_rate"
                        value={aiSettings.speech_rate || 'normal'}
                        onChange={handleAiSettingChange}
                        className="w-full text-sm border border-gray-300 rounded px-2 py-1 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="slow">Slow</option>
                        <option value="normal">Normal</option>
                        <option value="fast">Fast</option>
                      </select>
                    </div>
                  </div>
                  <div className="mt-2">
                    <button 
                      type="button"
                      className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                    >
                      🎵 Preview voice sample
                    </button>
                  </div>
                </div>
              </dd>
            </div>
            
            {/* Advanced AI Settings */}
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">
                Advanced AI Settings
                <p className="mt-1 text-xs text-gray-400">Fine-tune AI behavior and responses</p>
              </dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Response Style</label>
                    <select
                      name="response_style"
                      value={aiSettings.response_style || 'professional'}
                      onChange={handleAiSettingChange}
                      className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="professional">Professional & Direct</option>
                      <option value="conversational">Conversational & Friendly</option>
                      <option value="consultative">Consultative & Advisory</option>
                      <option value="aggressive">Aggressive Sales</option>
                      <option value="empathetic">Empathetic & Understanding</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Max Response Length</label>
                    <select
                      name="max_response_length"
                      value={aiSettings.max_response_length || 'medium'}
                      onChange={handleAiSettingChange}
                      className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="short">Short (1-2 sentences)</option>
                      <option value="medium">Medium (2-4 sentences)</option>
                      <option value="long">Long (4-6 sentences)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Objection Handling Style</label>
                    <select
                      name="objection_style"
                      value={aiSettings.objection_style || 'consultative'}
                      onChange={handleAiSettingChange}
                      className="w-full border border-gray-300 rounded px-3 py-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="consultative">Consultative Approach</option>
                      <option value="direct">Direct & Factual</option>
                      <option value="empathetic">Empathetic & Understanding</option>
                      <option value="educational">Educational & Informative</option>
                    </select>
                  </div>
                </div>
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
};

export default Settings;