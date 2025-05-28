import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Users, MessageSquare, Clock, Target } from 'lucide-react';

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [realtimeData, setRealtimeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timePeriod, setTimePeriod] = useState('30_days');
  const [error, setError] = useState(null);

  const orgId = 'production_org_123'; // In real app, get from auth context

  useEffect(() => {
    fetchAnalyticsData();
    fetchRealtimeData();
    
    // Set up real-time updates every 30 seconds
    const interval = setInterval(fetchRealtimeData, 30000);
    return () => clearInterval(interval);
  }, [timePeriod]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analytics/agent-performance?org_id=${orgId}&time_period=${timePeriod}`);
      
      if (!response.ok) {
        throw new Error(`Analytics API error: ${response.status}`);
      }
      
      const data = await response.json();
      setAnalyticsData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchRealtimeData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/dashboard/real-time?org_id=${orgId}`);
      
      if (!response.ok) {
        throw new Error(`Dashboard API error: ${response.status}`);
      }
      
      const data = await response.json();
      setRealtimeData(data);
    } catch (err) {
      console.error('Error fetching realtime data:', err);
    }
  };

  const formatPercentage = (value) => `${(value * 100).toFixed(1)}%`;
  const formatTime = (value) => `${value}s`;

  // Prepare chart data
  const agentPerformanceData = analyticsData ? Object.entries(analyticsData.agent_breakdown).map(([agent, data]) => ({
    agent: agent.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    success_rate: data.success_rate * 100,
    avg_response_time: data.avg_response_time,
    interactions: data.interactions
  })) : [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading && !analyticsData) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
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
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Error Loading Analytics</h3>
          <p className="text-red-600 mt-1">{error}</p>
          <button 
            onClick={fetchAnalyticsData}
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
        <h1 className="text-3xl font-bold text-gray-900">AI Agent Analytics</h1>
        <div className="flex items-center space-x-4">
          <select 
            value={timePeriod} 
            onChange={(e) => setTimePeriod(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="7_days">Last 7 Days</option>
            <option value="30_days">Last 30 Days</option>
            <option value="90_days">Last 90 Days</option>
          </select>
        </div>
      </div>

      {/* Real-time KPIs */}
      {realtimeData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <MessageSquare className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Conversations</p>
                <p className="text-2xl font-bold text-gray-900">{realtimeData.kpi_overview.active_conversations}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <Users className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Leads Today</p>
                <p className="text-2xl font-bold text-gray-900">{realtimeData.kpi_overview.leads_today}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                <p className="text-2xl font-bold text-gray-900">{realtimeData.kpi_overview.avg_response_time}s</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Target className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">System Health</p>
                <p className="text-2xl font-bold text-gray-900 capitalize">{realtimeData.kpi_overview.system_health}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Overview Stats */}
      {analyticsData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Total Interactions</h3>
            <p className="text-3xl font-bold text-blue-600">{analyticsData.overview.total_interactions.toLocaleString()}</p>
            <p className="text-sm text-gray-600 mt-1">Across all agents</p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Overall Success Rate</h3>
            <p className="text-3xl font-bold text-green-600">{formatPercentage(analyticsData.overview.overall_success_rate)}</p>
            <p className="text-sm text-gray-600 mt-1">Lead progression average</p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Avg Response Time</h3>
            <p className="text-3xl font-bold text-purple-600">{formatTime(analyticsData.overview.average_response_time)}</p>
            <p className="text-sm text-gray-600 mt-1">Across all interactions</p>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Agent Performance Bar Chart */}
        <div className="bg-white rounded-lg p-6 shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Success Rates</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={agentPerformanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="agent" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Success Rate']} />
              <Bar dataKey="success_rate" fill="#0088FE" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Response Time Chart */}
        <div className="bg-white rounded-lg p-6 shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Agent Response Times</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={agentPerformanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="agent" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}s`, 'Response Time']} />
              <Bar dataKey="avg_response_time" fill="#00C49F" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Agent Breakdown Table */}
      {analyticsData && (
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Detailed Agent Performance</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agent</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Interactions</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Success Rate</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Response Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Progression Rate</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(analyticsData.agent_breakdown).map(([agentType, data]) => (
                  <tr key={agentType}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 capitalize">
                      {agentType.replace('_', ' ')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {data.interactions}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        data.success_rate > 0.8 ? 'bg-green-100 text-green-800' :
                        data.success_rate > 0.7 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {formatPercentage(data.success_rate)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatTime(data.avg_response_time)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatPercentage(data.lead_progression_rate || 0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Improvement Recommendations */}
      {analyticsData && analyticsData.improvement_recommendations.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Improvement Recommendations</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {analyticsData.improvement_recommendations.map((rec, index) => (
                <div key={index} className={`p-4 border-l-4 ${
                  rec.priority === 'high' ? 'border-red-400 bg-red-50' :
                  rec.priority === 'medium' ? 'border-yellow-400 bg-yellow-50' :
                  'border-blue-400 bg-blue-50'
                }`}>
                  <div className="flex">
                    <div className="flex-shrink-0">
                      {rec.priority === 'high' ? (
                        <TrendingDown className="h-5 w-5 text-red-400" />
                      ) : (
                        <TrendingUp className="h-5 w-5 text-yellow-400" />
                      )}
                    </div>
                    <div className="ml-3">
                      <h3 className={`text-sm font-medium ${
                        rec.priority === 'high' ? 'text-red-800' :
                        rec.priority === 'medium' ? 'text-yellow-800' :
                        'text-blue-800'
                      }`}>
                        {rec.agent.charAt(0).toUpperCase() + rec.agent.slice(1)} - {rec.metric}
                      </h3>
                      <p className={`mt-1 text-sm ${
                        rec.priority === 'high' ? 'text-red-700' :
                        rec.priority === 'medium' ? 'text-yellow-700' :
                        'text-blue-700'
                      }`}>
                        {rec.recommendation}
                      </p>
                      <p className="mt-1 text-xs text-gray-600">
                        Current: {rec.current_value} | Target: {rec.target_value}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;