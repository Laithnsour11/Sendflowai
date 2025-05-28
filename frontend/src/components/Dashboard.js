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
  
  useEffect(() => {
    // Simulated data loading for demo
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        
        // In a real app, we would fetch this data from the API
        // const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/dashboard?org_id=${currentOrg.id}`);
        
        // Mock data for demo
        setTimeout(() => {
          setStats({
            totalLeads: 87,
            activeConversations: 24,
            convertedLeads: 35,
            avgResponseTime: 2.4
          });
          
          setRecentLeads([
            {
              id: '1',
              name: 'John Smith',
              email: 'john.smith@example.com',
              status: 'Qualified',
              lastContact: '2 hours ago',
              conversionProbability: 75
            },
            {
              id: '2',
              name: 'Sarah Johnson',
              email: 'sarah.j@example.com',
              status: 'Nurturing',
              lastContact: '1 day ago',
              conversionProbability: 55
            },
            {
              id: '3',
              name: 'Michael Brown',
              email: 'michael.b@example.com',
              status: 'Initial Contact',
              lastContact: '3 hours ago',
              conversionProbability: 30
            },
            {
              id: '4',
              name: 'Emily Davis',
              email: 'emily.d@example.com',
              status: 'Closing',
              lastContact: '5 hours ago',
              conversionProbability: 90
            }
          ]);
          
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error loading dashboard data:', error);
        setLoading(false);
      }
    };
    
    loadDashboardData();
  }, [currentOrg]);
  
  return (
    <div>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <div className="flex space-x-2">
          <button className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            <svg xmlns="http://www.w3.org/2000/svg" className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            New Campaign
          </button>
        </div>
      </div>
      
      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Leads */}
        <div className="animate-fade-in bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Leads</dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {loading ? '...' : stats.totalLeads}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        {/* Active Conversations */}
        <div className="animate-fade-in delay-100 bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Conversations</dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {loading ? '...' : stats.activeConversations}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        {/* Converted Leads */}
        <div className="animate-fade-in delay-200 bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Converted Leads</dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {loading ? '...' : stats.convertedLeads}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        
        {/* Avg Response Time */}
        <div className="animate-fade-in delay-300 bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-indigo-500 rounded-md p-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg Response Time</dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {loading ? '...' : `${stats.avgResponseTime} min`}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Recent Leads */}
      <div className="mt-8">
        <div className="flex items-center justify-between">
          <h2 className="text-lg leading-6 font-medium text-gray-900">Recent Leads</h2>
          <a href="#" className="text-sm font-medium text-indigo-600 hover:text-indigo-500">View all</a>
        </div>
        <div className="mt-4 flex flex-col">
          <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
            <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
              <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Last Contact
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Conversion Probability
                      </th>
                      <th scope="col" className="relative px-6 py-3">
                        <span className="sr-only">Actions</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {loading ? (
                      <tr>
                        <td colSpan="5" className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-500">
                          Loading...
                        </td>
                      </tr>
                    ) : (
                      recentLeads.map((lead) => (
                        <tr key={lead.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-indigo-100 text-indigo-800 font-semibold">
                                {lead.name.charAt(0)}
                              </div>
                              <div className="ml-4">
                                <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                                <div className="text-sm text-gray-500">{lead.email}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                              ${lead.status === 'Qualified' ? 'bg-green-100 text-green-800' : 
                                lead.status === 'Nurturing' ? 'bg-yellow-100 text-yellow-800' :
                                lead.status === 'Closing' ? 'bg-indigo-100 text-indigo-800' :
                                'bg-gray-100 text-gray-800'}`}>
                              {lead.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {lead.lastContact}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="w-full bg-gray-200 rounded-full h-2.5">
                                <div className={`h-2.5 rounded-full ${
                                  lead.conversionProbability >= 70 ? 'bg-green-500' :
                                  lead.conversionProbability >= 40 ? 'bg-yellow-500' :
                                  'bg-red-500'
                                }`} style={{ width: `${lead.conversionProbability}%` }}></div>
                              </div>
                              <span className="ml-2 text-sm text-gray-500">{lead.conversionProbability}%</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <a href="#" className="text-indigo-600 hover:text-indigo-900">Details</a>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* AI Insights */}
      <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">AI Insights</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">Latest insights from the AI system.</p>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
          <dl className="sm:divide-y sm:divide-gray-200">
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Best performing agent</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">Closer Agent (85% effectiveness)</dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Top objection detected</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">"Property is outside our budget" (23% of conversations)</dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Common buying signals</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">Questions about financing options, specific property details</dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Recommended next action</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">Create content addressing price objections for nurturing campaigns</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;