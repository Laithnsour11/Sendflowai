import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Play, 
  Square, 
  Eye, 
  BarChart3, 
  Zap, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  XCircle,
  AlertCircle,
  Plus,
  Settings,
  Activity
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const AITraining = ({ currentOrg }) => {
  const [fineTuningJobs, setFineTuningJobs] = useState([]);
  const [rlhfAnalytics, setRlhfAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [showJobModal, setShowJobModal] = useState(false);
  const [activeTab, setActiveTab] = useState('jobs');

  const orgId = currentOrg?.id || 'production_org_123';

  useEffect(() => {
    fetchData();
  }, [orgId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchFineTuningJobs(),
        fetchRLHFAnalytics()
      ]);
      setError(null);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchFineTuningJobs = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/fine-tuning/jobs?org_id=${orgId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch fine-tuning jobs: ${response.status}`);
      }
      
      const data = await response.json();
      setFineTuningJobs(data.jobs || []);
    } catch (err) {
      console.error('Error fetching fine-tuning jobs:', err);
      throw err;
    }
  };

  const fetchRLHFAnalytics = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/rlhf/analytics?org_id=${orgId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch RLHF analytics: ${response.status}`);
      }
      
      const data = await response.json();
      setRlhfAnalytics(data);
    } catch (err) {
      console.error('Error fetching RLHF analytics:', err);
      throw err;
    }
  };

  const handleStartJob = async (jobId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/fine-tuning/${jobId}/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ org_id: orgId })
      });

      if (!response.ok) {
        throw new Error(`Failed to start fine-tuning job: ${response.status}`);
      }

      await fetchFineTuningJobs(); // Refresh jobs list
    } catch (err) {
      console.error('Error starting fine-tuning job:', err);
      setError(`Failed to start fine-tuning job: ${err.message}`);
    }
  };

  const handleCancelJob = async (jobId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/fine-tuning/${jobId}/cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ org_id: orgId })
      });

      if (!response.ok) {
        throw new Error(`Failed to cancel fine-tuning job: ${response.status}`);
      }

      await fetchFineTuningJobs(); // Refresh jobs list
    } catch (err) {
      console.error('Error cancelling fine-tuning job:', err);
      setError(`Failed to cancel fine-tuning job: ${err.message}`);
    }
  };

  const handleViewJob = async (job) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/fine-tuning/${job._id}/status?org_id=${orgId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch job status: ${response.status}`);
      }
      
      const statusData = await response.json();
      setSelectedJob({ ...job, statusData });
      setShowJobModal(true);
    } catch (err) {
      console.error('Error fetching job status:', err);
      setError(`Failed to fetch job status: ${err.message}`);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'training':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'preparing_data':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'training':
        return <Activity className="h-4 w-4" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      case 'failed':
        return <XCircle className="h-4 w-4" />;
      case 'cancelled':
        return <Square className="h-4 w-4" />;
      case 'preparing_data':
        return <Clock className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  const renderRLHFAnalytics = () => {
    if (!rlhfAnalytics) return null;

    const { analytics } = rlhfAnalytics;
    if (!analytics) return null;

    // Prepare chart data for feedback types
    const feedbackTypeData = Object.entries(analytics.average_scores_by_feedback_type || {}).map(([type, score]) => ({
      name: type.replace('_', ' '),
      score: score
    }));

    // Prepare chart data for agent types
    const agentTypeData = Object.entries(analytics.average_scores_by_agent_type || {}).map(([type, score]) => ({
      name: type.replace('_', ' '),
      score: score
    }));

    return (
      <div className="space-y-6">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Overall Score</p>
                <p className="text-2xl font-bold text-gray-900">
                  {(analytics.overall_average_score || 0).toFixed(2)}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center">
              <BarChart3 className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Total Feedback</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics.total_feedback_items || 0}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Feedback Types</p>
                <p className="text-2xl font-bold text-gray-900">
                  {Object.keys(analytics.average_scores_by_feedback_type || {}).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Feedback Type Performance */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Performance by Feedback Type</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={feedbackTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis domain={[0, 5]} />
                <Tooltip />
                <Bar dataKey="score" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Agent Type Performance */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Performance by Agent Type</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={agentTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis domain={[0, 5]} />
                <Tooltip />
                <Bar dataKey="score" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recommendations */}
        {rlhfAnalytics.recommendations && rlhfAnalytics.recommendations.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-blue-900 mb-4">Training Recommendations</h3>
            <ul className="space-y-2">
              {rlhfAnalytics.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <Zap className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <span className="text-blue-800">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const renderFineTuningJobs = () => {
    if (fineTuningJobs.length === 0) {
      return (
        <div className="text-center py-12">
          <Brain className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No fine-tuning jobs yet</h3>
          <p className="text-gray-600 mb-6">Create your first AI fine-tuning job to start improving your agents based on RLHF feedback.</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 mx-auto"
          >
            <Plus className="h-5 w-5" />
            <span>Create Fine-Tuning Job</span>
          </button>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {fineTuningJobs.map((job) => (
          <div key={job._id} className="bg-white rounded-lg p-6 shadow hover:shadow-lg transition-shadow">
            {/* Job Header */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{job.job_name}</h3>
                <p className="text-sm text-gray-600">{job.model_config?.base_model}</p>
              </div>
              <span className={`px-2 py-1 text-xs rounded-full border capitalize flex items-center space-x-1 ${getStatusColor(job.status)}`}>
                {getStatusIcon(job.status)}
                <span>{job.status.replace('_', ' ')}</span>
              </span>
            </div>

            {/* Progress */}
            {job.status === 'training' && job.training_progress && (
              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Training Progress</span>
                  <span>{job.training_progress.current_epoch}/{job.training_progress.total_epochs} epochs</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ 
                      width: `${(job.training_progress.current_epoch / job.training_progress.total_epochs) * 100}%` 
                    }}
                  ></div>
                </div>
              </div>
            )}

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="text-center">
                <div className="text-lg font-bold text-blue-600">
                  {job.data_processing?.processed_training_examples || 0}
                </div>
                <div className="text-xs text-gray-500">Training Examples</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-green-600">
                  {((job.data_processing?.data_quality_score || 0) * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-gray-500">Data Quality</div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleViewJob(job)}
                className="flex-1 bg-gray-100 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-200 transition-colors flex items-center justify-center space-x-1"
              >
                <Eye className="h-4 w-4" />
                <span>Details</span>
              </button>

              {job.status === 'pending' ? (
                <button
                  onClick={() => handleStartJob(job._id)}
                  className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 transition-colors flex items-center justify-center space-x-1"
                >
                  <Play className="h-4 w-4" />
                  <span>Start</span>
                </button>
              ) : (job.status === 'training' || job.status === 'preparing_data') ? (
                <button
                  onClick={() => handleCancelJob(job._id)}
                  className="flex-1 bg-red-600 text-white px-3 py-2 rounded text-sm hover:bg-red-700 transition-colors flex items-center justify-center space-x-1"
                >
                  <Square className="h-4 w-4" />
                  <span>Cancel</span>
                </button>
              ) : null}
            </div>
          </div>
        ))}
      </div>
    );
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
          <h3 className="text-red-800 font-medium">Error Loading AI Training Data</h3>
          <p className="text-red-600 mt-1">{error}</p>
          <button 
            onClick={fetchData}
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
          <h1 className="text-3xl font-bold text-gray-900">AI Training</h1>
          <p className="text-gray-600">Fine-tune your AI agents using RLHF feedback data</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>New Training Job</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('jobs')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'jobs'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Brain className="h-4 w-4" />
              <span>Training Jobs</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'analytics'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>RLHF Analytics</span>
            </div>
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'jobs' ? renderFineTuningJobs() : renderRLHFAnalytics()}

      {/* Create Job Modal */}
      {showCreateModal && (
        <CreateFineTuningModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={fetchFineTuningJobs}
          orgId={orgId}
        />
      )}

      {/* Job Details Modal */}
      {showJobModal && selectedJob && (
        <JobDetailsModal
          isOpen={showJobModal}
          onClose={() => setShowJobModal(false)}
          job={selectedJob}
        />
      )}
    </div>
  );
};

// Create Fine-Tuning Job Modal Component
const CreateFineTuningModal = ({ isOpen, onClose, onSuccess, orgId }) => {
  const [formData, setFormData] = useState({
    job_name: '',
    description: '',
    model_config: {
      base_model: 'gpt-4o',
      provider: 'openai',
      agent_type: 'all',
      target_capabilities: []
    },
    training_config: {
      feedback_date_range: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
        end: new Date().toISOString().split('T')[0] // today
      },
      feedback_types: [],
      minimum_feedback_score: 3,
      include_conversation_context: true,
      training_epochs: 3,
      learning_rate: 0.0001
    }
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/fine-tuning/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          org_id: orgId,
          job_config: formData
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to create fine-tuning job: ${response.status}`);
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error creating fine-tuning job:', err);
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
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Fine-Tuning Job</h2>
        
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
                <label className="block text-sm font-medium text-gray-700 mb-2">Job Name</label>
                <input
                  type="text"
                  value={formData.job_name}
                  onChange={(e) => updateFormData('job_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter job name"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => updateFormData('description', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe the training objective"
                  rows={3}
                />
              </div>
            </div>
          </div>

          {/* Model Configuration */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Model Configuration</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Base Model</label>
                <select
                  value={formData.model_config.base_model}
                  onChange={(e) => updateFormData('model_config.base_model', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="claude-3">Claude 3</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Provider</label>
                <select
                  value={formData.model_config.provider}
                  onChange={(e) => updateFormData('model_config.provider', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="openai">OpenAI</option>
                  <option value="openrouter">OpenRouter</option>
                  <option value="anthropic">Anthropic</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Agent Type</label>
                <select
                  value={formData.model_config.agent_type}
                  onChange={(e) => updateFormData('model_config.agent_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Agents</option>
                  <option value="initial_contact">Initial Contact</option>
                  <option value="qualifier">Qualifier</option>
                  <option value="nurturer">Nurturer</option>
                  <option value="objection_handler">Objection Handler</option>
                  <option value="appointment_setter">Appointment Setter</option>
                  <option value="closer">Closer</option>
                </select>
              </div>
            </div>
          </div>

          {/* Training Configuration */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Training Configuration</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                <input
                  type="date"
                  value={formData.training_config.feedback_date_range.start}
                  onChange={(e) => updateFormData('training_config.feedback_date_range.start', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                <input
                  type="date"
                  value={formData.training_config.feedback_date_range.end}
                  onChange={(e) => updateFormData('training_config.feedback_date_range.end', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Training Epochs</label>
                <input
                  type="number"
                  value={formData.training_config.training_epochs}
                  onChange={(e) => updateFormData('training_config.training_epochs', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="1"
                  max="10"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Minimum Feedback Score</label>
                <input
                  type="number"
                  value={formData.training_config.minimum_feedback_score}
                  onChange={(e) => updateFormData('training_config.minimum_feedback_score', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="1"
                  max="5"
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
              {submitting ? 'Creating...' : 'Create Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Job Details Modal Component
const JobDetailsModal = ({ isOpen, onClose, job }) => {
  if (!isOpen || !job) return null;

  const statusData = job.statusData || {};
  const sampleExamples = statusData.sample_training_examples || [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">{job.job_name} - Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Job Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-600">Training Examples</p>
                <p className="text-2xl font-bold text-blue-900">{job.data_processing?.processed_training_examples || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-600">Data Quality</p>
                <p className="text-2xl font-bold text-green-900">{((job.data_processing?.data_quality_score || 0) * 100).toFixed(0)}%</p>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-purple-600">Status</p>
                <p className="text-2xl font-bold text-purple-900 capitalize">{job.status.replace('_', ' ')}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Training Progress */}
        {job.status === 'training' && job.training_progress && (
          <div className="mb-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Training Progress</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Epoch {job.training_progress.current_epoch} of {job.training_progress.total_epochs}</span>
                <span>{((job.training_progress.current_epoch / job.training_progress.total_epochs) * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300" 
                  style={{ 
                    width: `${(job.training_progress.current_epoch / job.training_progress.total_epochs) * 100}%` 
                  }}
                ></div>
              </div>
              {job.training_progress.loss && (
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Training Loss:</span>
                    <span className="ml-2 font-medium">{job.training_progress.loss.toFixed(4)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Validation Loss:</span>
                    <span className="ml-2 font-medium">{job.training_progress.validation_loss?.toFixed(4) || 'N/A'}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Sample Training Examples */}
        {sampleExamples.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Sample Training Examples</h3>
            <div className="space-y-4">
              {sampleExamples.slice(0, 3).map((example, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Input</h4>
                      <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                        {example.input || 'No input data'}
                      </p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Expected Output</h4>
                      <p className="text-sm text-gray-600 bg-white p-3 rounded border">
                        {example.output || 'No output data'}
                      </p>
                    </div>
                  </div>
                  <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                    <span>Score: {example.score}/5</span>
                    <span>Type: {example.feedback_type?.replace('_', ' ')}</span>
                  </div>
                </div>
              ))}
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

export default AITraining;