import React, { useState, useEffect } from 'react';
import { Plus, Play, Pause, Square, Eye, Users, Target, MessageSquare, Clock, TrendingUp } from 'lucide-react';

const Campaigns = ({ currentOrg }) => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [showStatusModal, setShowStatusModal] = useState(false);

  const orgId = currentOrg?.id || 'production_org_123';

  useEffect(() => {
    fetchCampaigns();
  }, [orgId]);

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/campaigns?org_id=${orgId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch campaigns: ${response.status}`);
      }
      
      const data = await response.json();
      setCampaigns(data.campaigns || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching campaigns:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStartCampaign = async (campaignId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/campaigns/${campaignId}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ org_id: orgId })
      });

      if (!response.ok) {
        throw new Error(`Failed to start campaign: ${response.status}`);
      }

      await fetchCampaigns(); // Refresh campaigns list
    } catch (err) {
      console.error('Error starting campaign:', err);
      setError(`Failed to start campaign: ${err.message}`);
    }
  };

  const handlePauseCampaign = async (campaignId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/campaigns/${campaignId}/pause`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ org_id: orgId })
      });

      if (!response.ok) {
        throw new Error(`Failed to pause campaign: ${response.status}`);
      }

      await fetchCampaigns(); // Refresh campaigns list
    } catch (err) {
      console.error('Error pausing campaign:', err);
      setError(`Failed to pause campaign: ${err.message}`);
    }
  };

  const handleStopCampaign = async (campaignId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/campaigns/${campaignId}/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ org_id: orgId })
      });

      if (!response.ok) {
        throw new Error(`Failed to stop campaign: ${response.status}`);
      }

      await fetchCampaigns(); // Refresh campaigns list
    } catch (err) {
      console.error('Error stopping campaign:', err);
      setError(`Failed to stop campaign: ${err.message}`);
    }
  };

  const handleViewStatus = async (campaign) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/campaigns/${campaign._id}/status?org_id=${orgId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch campaign status: ${response.status}`);
      }
      
      const statusData = await response.json();
      setSelectedCampaign({ ...campaign, statusData });
      setShowStatusModal(true);
    } catch (err) {
      console.error('Error fetching campaign status:', err);
      setError(`Failed to fetch campaign status: ${err.message}`);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'completed':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'outbound_voice':
        return <MessageSquare className="h-4 w-4" />;
      case 'outbound_sms':
        return <MessageSquare className="h-4 w-4" />;
      case 'mixed_channel':
        return <Target className="h-4 w-4" />;
      default:
        return <Users className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="bg-white rounded-lg p-6 shadow">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="h-20 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Error Loading Campaigns</h3>
          <p className="text-red-600 mt-1">{error}</p>
          <button 
            onClick={fetchCampaigns}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Campaigns</h1>
          <p className="text-gray-600">Manage proactive outreach campaigns</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Create Campaign</span>
        </button>
      </div>

      {/* Campaigns Grid */}
      {campaigns.length === 0 ? (
        <div className="text-center py-12">
          <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns yet</h3>
          <p className="text-gray-600 mb-6">Create your first AI-driven outreach campaign to start engaging leads automatically.</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 mx-auto"
          >
            <Plus className="h-5 w-5" />
            <span>Create Your First Campaign</span>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {campaigns.map((campaign) => (
            <div key={campaign._id} className="bg-white rounded-lg p-6 shadow hover:shadow-lg transition-shadow">
              {/* Campaign Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-2">
                  {getTypeIcon(campaign.campaign_type)}
                  <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full border capitalize ${getStatusColor(campaign.status)}`}>
                  {campaign.status}
                </span>
              </div>

              {/* Campaign Description */}
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                {campaign.description || 'No description provided'}
              </p>

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-lg font-bold text-blue-600">
                    {campaign.metrics?.total_leads || campaign.target_config?.estimated_leads || 0}
                  </div>
                  <div className="text-xs text-gray-500">Total Leads</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-green-600">
                    {campaign.metrics?.leads_contacted || 0}
                  </div>
                  <div className="text-xs text-gray-500">Contacted</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-purple-600">
                    {campaign.metrics?.leads_responded || 0}
                  </div>
                  <div className="text-xs text-gray-500">Responded</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-orange-600">
                    {((campaign.metrics?.response_rate || 0) * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500">Response Rate</div>
                </div>
              </div>

              {/* Campaign Info */}
              <div className="border-t pt-4 mb-4">
                <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                  <span>Agent:</span>
                  <span className="capitalize font-medium">{campaign.agent_config?.initial_agent_type?.replace('_', ' ')}</span>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                  <span>Channel:</span>
                  <span className="capitalize">{campaign.campaign_type?.replace('_', ' ')}</span>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Created:</span>
                  <span>{new Date(campaign.created_at).toLocaleDateString()}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleViewStatus(campaign)}
                  className="flex-1 bg-gray-100 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-200 transition-colors flex items-center justify-center space-x-1"
                >
                  <Eye className="h-4 w-4" />
                  <span>Status</span>
                </button>

                {campaign.status === 'draft' || campaign.status === 'paused' ? (
                  <button
                    onClick={() => handleStartCampaign(campaign._id)}
                    className="flex-1 bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 transition-colors flex items-center justify-center space-x-1"
                  >
                    <Play className="h-4 w-4" />
                    <span>Start</span>
                  </button>
                ) : campaign.status === 'active' ? (
                  <div className="flex space-x-1 flex-1">
                    <button
                      onClick={() => handlePauseCampaign(campaign._id)}
                      className="flex-1 bg-yellow-600 text-white px-2 py-2 rounded text-sm hover:bg-yellow-700 transition-colors flex items-center justify-center"
                    >
                      <Pause className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleStopCampaign(campaign._id)}
                      className="flex-1 bg-red-600 text-white px-2 py-2 rounded text-sm hover:bg-red-700 transition-colors flex items-center justify-center"
                    >
                      <Square className="h-4 w-4" />
                    </button>
                  </div>
                ) : null}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Campaign Modal */}
      {showCreateModal && (
        <CreateCampaignModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={fetchCampaigns}
          orgId={orgId}
        />
      )}

      {/* Campaign Status Modal */}
      {showStatusModal && selectedCampaign && (
        <CampaignStatusModal
          isOpen={showStatusModal}
          onClose={() => setShowStatusModal(false)}
          campaign={selectedCampaign}
        />
      )}
    </div>
  );
};

// Create Campaign Modal Component
const CreateCampaignModal = ({ isOpen, onClose, onSuccess, orgId }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    campaign_type: 'outbound_sms',
    target_config: {
      ghl_segment_criteria: {
        tags: [],
        pipeline_stage: '',
        custom_fields: {}
      },
      lead_filters: {}
    },
    agent_config: {
      initial_agent_type: 'initial_contact',
      campaign_objective: 'Lead qualification and initial engagement',
      communication_channels: ['sms'],
      llm_model: 'gpt-4o'
    },
    schedule_config: {
      daily_contact_limit: 50,
      hourly_contact_limit: 10,
      contact_hours: {
        start: '09:00',
        end: '17:00',
        timezone: 'America/New_York'
      },
      contact_days: [1, 2, 3, 4, 5]
    }
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/campaigns/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          org_id: orgId,
          campaign_data: formData
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to create campaign: ${response.status}`);
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error creating campaign:', err);
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const updateFormData = (path, value) => {
    setFormData(prev => {
      const newData = { ...prev };
      const keys = path.split('.');
      let current = newData;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newData;
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Campaign</h2>
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => updateFormData('name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter campaign name"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => updateFormData('description', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe your campaign objective"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Type</label>
                <select
                  value={formData.campaign_type}
                  onChange={(e) => updateFormData('campaign_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="outbound_sms">Outbound SMS</option>
                  <option value="outbound_voice">Outbound Voice</option>
                  <option value="mixed_channel">Mixed Channel</option>
                </select>
              </div>
            </div>
          </div>

          {/* Agent Configuration */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Configuration</h3>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Initial Agent Type</label>
                <select
                  value={formData.agent_config.initial_agent_type}
                  onChange={(e) => updateFormData('agent_config.initial_agent_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="initial_contact">Initial Contact</option>
                  <option value="qualifier">Qualifier</option>
                  <option value="nurturer">Nurturer</option>
                  <option value="appointment_setter">Appointment Setter</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Campaign Objective</label>
                <input
                  type="text"
                  value={formData.agent_config.campaign_objective}
                  onChange={(e) => updateFormData('agent_config.campaign_objective', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="What should this campaign achieve?"
                />
              </div>
            </div>
          </div>

          {/* Schedule Configuration */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Schedule & Limits</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Daily Contact Limit</label>
                <input
                  type="number"
                  value={formData.schedule_config.daily_contact_limit}
                  onChange={(e) => updateFormData('schedule_config.daily_contact_limit', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="1"
                  max="200"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Hourly Contact Limit</label>
                <input
                  type="number"
                  value={formData.schedule_config.hourly_contact_limit}
                  onChange={(e) => updateFormData('schedule_config.hourly_contact_limit', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="1"
                  max="50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Start Time</label>
                <input
                  type="time"
                  value={formData.schedule_config.contact_hours.start}
                  onChange={(e) => updateFormData('schedule_config.contact_hours.start', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">End Time</label>
                <input
                  type="time"
                  value={formData.schedule_config.contact_hours.end}
                  onChange={(e) => updateFormData('schedule_config.contact_hours.end', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Modal Actions */}
          <div className="flex items-center justify-end space-x-4 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {submitting ? 'Creating...' : 'Create Campaign'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Campaign Status Modal Component
const CampaignStatusModal = ({ isOpen, onClose, campaign }) => {
  if (!isOpen || !campaign) return null;

  const statusData = campaign.statusData || {};
  const leadStats = statusData.lead_processing_stats || {};
  const recentInteractions = statusData.recent_interactions || [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">{campaign.name} - Status</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Campaign Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-600">Total Leads</p>
                <p className="text-2xl font-bold text-blue-900">{leadStats.total || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center">
              <Target className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-600">Contacted</p>
                <p className="text-2xl font-bold text-green-900">{leadStats.contacted || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center">
              <MessageSquare className="h-8 w-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-purple-600">Responded</p>
                <p className="text-2xl font-bold text-purple-900">{leadStats.responded || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-orange-50 rounded-lg p-4">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-orange-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-orange-600">In Progress</p>
                <p className="text-2xl font-bold text-orange-900">{statusData.is_processing ? 'Yes' : 'No'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Lead Processing Breakdown */}
        <div className="mb-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Lead Processing Status</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-600">Queued</div>
                <div className="text-2xl font-bold text-blue-600">{leadStats.queued || 0}</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-600">Processing</div>
                <div className="text-2xl font-bold text-yellow-600">{leadStats.processing || 0}</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-gray-600">Failed</div>
                <div className="text-2xl font-bold text-red-600">{leadStats.failed || 0}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Interactions */}
        {recentInteractions.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Interactions</h3>
            <div className="bg-white border border-gray-200 rounded-lg">
              <div className="divide-y divide-gray-200">
                {recentInteractions.map((interaction, index) => (
                  <div key={index} className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{interaction.lead_name}</p>
                        <p className="text-sm text-gray-600">
                          {interaction.contact_method} • {interaction.attempts} attempt(s)
                        </p>
                      </div>
                      <div className="text-right">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          interaction.status === 'contacted' ? 'bg-green-100 text-green-800' :
                          interaction.status === 'responded' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {interaction.status}
                        </span>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(interaction.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Modal Actions */}
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default Campaigns;