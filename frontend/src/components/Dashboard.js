import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FeedbackButton } from './FeedbackButton';
import { Users, MessageSquare, TrendingUp, Clock, BarChart3, Activity } from 'lucide-react';

const Dashboard = ({ currentOrg }) => {
  const [realtimeData, setRealtimeData] = useState(null);
  const [recentLeads, setRecentLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const orgId = currentOrg?.id || 'production_org_123';

  useEffect(() => {
    fetchRealtimeData();
    
    // Set up real-time updates every 30 seconds
    const interval = setInterval(fetchRealtimeData, 30000);
    return () => clearInterval(interval);
  }, [orgId]);

  const fetchRealtimeData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/dashboard/real-time?org_id=${orgId}`);
      
      if (!response.ok) {
        throw new Error(`Dashboard API error: ${response.status}`);
      }
      
      const data = await response.json();
      setRealtimeData(data);
      setError(null);
      
      // Mock some recent leads data
      setRecentLeads([
        {
          id: '1',
          name: 'John Smith',
          email: 'john.smith@example.com',
          status: 'Qualified',
          lastContact: '2 hours ago',
          conversionProbability: 75,
          conversationId: 'conv_001'
        },
        {
          id: '2',
          name: 'Sarah Johnson', 
          email: 'sarah.j@example.com',
          status: 'Nurturing',
          lastContact: '1 day ago',
          conversionProbability: 55,
          conversationId: 'conv_002'
        },
        {
          id: '3',
          name: 'Mike Davis',
          email: 'mike.d@example.com',
          status: 'Initial Contact',
          lastContact: '3 hours ago',
          conversionProbability: 30,
          conversationId: 'conv_003'
        }
      ]);
      
    } catch (err) {
      console.error('Error fetching realtime data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSystemHealthColor = (health) => {
    switch (health) {
      case 'excellent': return 'text-green-600 bg-green-100';
      case 'good': return 'text-blue-600 bg-blue-100';
      case 'fair': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getAgentStatusColor = (active) => {
    return active ? 'text-green-600 bg-green-100' : 'text-gray-400 bg-gray-100';
  };

  if (loading && !realtimeData) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-white rounded-lg p-6 shadow">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Error Loading Dashboard</h3>
          <p className="text-red-600 mt-1">{error}</p>
          <button 
            onClick={fetchRealtimeData}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Real-time AI agent performance overview</p>
        </div>
        <div className="flex items-center space-x-4">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSystemHealthColor(realtimeData?.kpi_overview?.system_health)}`}>
            System: {realtimeData?.kpi_overview?.system_health || 'Unknown'}
          </span>
          <Link 
            to="/analytics" 
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <BarChart3 className="h-4 w-4" />
            <span>View Analytics</span>
          </Link>
        </div>
      </div>

      {/* Real-time KPI Cards */}
      {realtimeData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg p-6 shadow hover:shadow-lg transition-shadow">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <MessageSquare className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Conversations</p>
                <p className="text-2xl font-bold text-gray-900">{realtimeData.kpi_overview.active_conversations}</p>
                <p className="text-xs text-gray-500">Live interactions</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow hover:shadow-lg transition-shadow">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <Users className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Leads Today</p>
                <p className="text-2xl font-bold text-gray-900">{realtimeData.kpi_overview.leads_today}</p>
                <p className="text-xs text-gray-500">New prospects</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow hover:shadow-lg transition-shadow">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                <p className="text-2xl font-bold text-gray-900">{realtimeData.kpi_overview.avg_response_time}s</p>
                <p className="text-xs text-gray-500">All agents</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow hover:shadow-lg transition-shadow">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Responses Sent</p>
                <p className="text-2xl font-bold text-gray-900">{realtimeData.kpi_overview.responses_sent}</p>
                <p className="text-xs text-gray-500">Today's total</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Agents Status */}
        {realtimeData && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <Activity className="h-5 w-5 mr-2" />
                Active Agents
              </h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {Object.entries(realtimeData.active_agents).map(([agentType, data]) => (
                  <div key={agentType} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className={`w-3 h-3 rounded-full mr-3 ${getAgentStatusColor(data.active)}`}></span>
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {agentType.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-sm text-gray-600">{data.current_conversations} active</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Recent Activity */}
        {realtimeData && realtimeData.recent_activity.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {realtimeData.recent_activity.map((activity, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">{activity.summary}</p>
                      <p className="text-xs text-gray-500">
                        {activity.agent} • {new Date(activity.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Recent Leads with RLHF Feedback */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Leads</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentLeads.map((lead) => (
                <div key={lead.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-gray-900">{lead.name}</h4>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      lead.status === 'Qualified' ? 'bg-green-100 text-green-800' :
                      lead.status === 'Nurturing' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {lead.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mb-2">{lead.email}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">Last contact: {lead.lastContact}</span>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500">{lead.conversionProbability}% likely</span>
                      <FeedbackButton 
                        conversationId={lead.conversationId} 
                        variant="small"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;