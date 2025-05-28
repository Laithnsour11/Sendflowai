import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Download, 
  Filter, 
  Calendar,
  Target,
  Users,
  MessageSquare,
  Zap,
  Brain,
  Activity,
  CheckCircle,
  ArrowUp,
  ArrowDown,
  Minus,
  Settings,
  Eye,
  RefreshCw
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  BarChart, 
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';

const AdvancedAnalytics = ({ currentOrg }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [campaignReport, setCampaignReport] = useState(null);
  const [agentReport, setAgentReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [timePeriod, setTimePeriod] = useState('30d');
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const orgId = currentOrg?.id || 'production_org_123';

  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 30 seconds if enabled
    let refreshInterval;
    if (autoRefresh) {
      refreshInterval = setInterval(() => {
        fetchData();
      }, 30000);
    }
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [orgId, timePeriod, autoRefresh]);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchDashboardData(),
        fetchCampaignReport(),
        fetchAgentReport()
      ]);
      setError(null);
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/analytics/comprehensive-dashboard?org_id=${orgId}&time_period=${timePeriod}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch dashboard data: ${response.status}`);
      }
      
      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      throw err;
    }
  };

  const fetchCampaignReport = async () => {
    try {
      const campaignParam = selectedCampaign ? `&campaign_id=${selectedCampaign}` : '';
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/analytics/campaign-performance-report?org_id=${orgId}&time_period=${timePeriod}${campaignParam}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch campaign report: ${response.status}`);
      }
      
      const data = await response.json();
      setCampaignReport(data);
    } catch (err) {
      console.error('Error fetching campaign report:', err);
      throw err;
    }
  };

  const fetchAgentReport = async () => {
    try {
      const agentParam = selectedAgent ? `&agent_type=${selectedAgent}` : '';
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/analytics/agent-intelligence-report?org_id=${orgId}&time_period=${timePeriod}${agentParam}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch agent report: ${response.status}`);
      }
      
      const data = await response.json();
      setAgentReport(data);
    } catch (err) {
      console.error('Error fetching agent report:', err);
      throw err;
    }
  };

  const handleExportReport = async (reportType, formatType = 'json') => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/analytics/export-report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          org_id: orgId,
          report_type: reportType,
          time_period: timePeriod,
          format_type: formatType
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to export report: ${response.status}`);
      }

      const result = await response.json();
      
      if (formatType === 'json') {
        // For JSON, show the data in a new window
        const newWindow = window.open();
        newWindow.document.write(`<pre>${JSON.stringify(result.data, null, 2)}</pre>`);
      } else {
        // For other formats, would trigger download
        alert('Report export initiated. Download would be available in production.');
      }
    } catch (err) {
      console.error('Error exporting report:', err);
      setError(`Failed to export report: ${err.message}`);
    }
  };

  const renderMetricCard = (title, value, change, IconComponent, color = 'blue') => {
    const isPositive = change > 0;
    const isNeutral = change === 0;
    
    return (
      <div className="bg-white rounded-lg p-6 shadow hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
            {change !== undefined && (
              <div className={`flex items-center mt-2 text-sm ${
                isPositive ? 'text-green-600' : isNeutral ? 'text-gray-600' : 'text-red-600'
              }`}>
                {isPositive ? <ArrowUp className="h-4 w-4 mr-1" /> : 
                 isNeutral ? <Minus className="h-4 w-4 mr-1" /> : 
                 <ArrowDown className="h-4 w-4 mr-1" />}
                <span>{Math.abs(change * 100).toFixed(1)}%</span>
              </div>
            )}
          </div>
          <IconComponent className={`h-8 w-8 text-${color}-600`} />
        </div>
      </div>
    );
  };

  const renderDashboard = () => {
    if (!dashboardData) return null;

    const { overview_metrics, campaign_analytics, agent_performance, trends_and_insights, performance_recommendations } = dashboardData;

    // Prepare chart data
    const agentPerformanceData = agent_performance?.agent_metrics?.map(agent => ({
      name: agent.agent_type.replace('_', ' '),
      quality: agent.avg_response_quality,
      success: agent.conversation_success_rate * 100,
      interactions: agent.total_interactions,
      improvement: agent.improvement_trend * 100
    })) || [];

    const trendData = agent_performance?.performance_trends?.response_quality_trend?.map((value, index) => ({
      day: `Day ${index + 1}`,
      quality: value,
      success: agent_performance.performance_trends.success_rate_trend[index] * 100,
      efficiency: agent_performance.performance_trends.efficiency_trend[index]
    })) || [];

    // Channel performance data
    const channelData = campaign_analytics?.channel_breakdown ? Object.entries(campaign_analytics.channel_breakdown).map(([channel, data]) => ({
      name: channel.toUpperCase(),
      leads: data.leads,
      response_rate: data.response_rate * 100,
      conversion_rate: data.conversion_rate * 100
    })) : [];

    return (
      <div className="space-y-6">
        {/* Overview Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {renderMetricCard("Total Leads", overview_metrics?.total_leads?.toLocaleString() || '0', 0.12, Users, 'blue')}
          {renderMetricCard("Response Rate", `${((overview_metrics?.response_rate || 0) * 100).toFixed(1)}%`, 0.08, Target, 'green')}
          {renderMetricCard("Conversion Rate", `${((overview_metrics?.conversion_rate || 0) * 100).toFixed(1)}%`, 0.15, CheckCircle, 'purple')}
          {renderMetricCard("Avg Response Time", `${overview_metrics?.average_response_time || 0}s`, -0.05, Activity, 'orange')}
        </div>

        {/* Secondary Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {renderMetricCard("Total Campaigns", overview_metrics?.total_campaigns?.toLocaleString() || '0', null, Target, 'indigo')}
          {renderMetricCard("Active Agents", overview_metrics?.active_agents?.toLocaleString() || '0', null, Brain, 'pink')}
          {renderMetricCard("RLHF Feedback", overview_metrics?.rlhf_feedback_items?.toLocaleString() || '0', null, MessageSquare, 'cyan')}
          {renderMetricCard("Data Quality", `${((overview_metrics?.data_quality_score || 0) * 100).toFixed(0)}%`, null, CheckCircle, 'emerald')}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Agent Performance Chart */}
          <div className="bg-white rounded-lg p-6 shadow">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Agent Performance Overview</h3>
              <button 
                onClick={() => setActiveTab('agents')}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center space-x-1"
              >
                <Eye className="h-4 w-4" />
                <span>View Details</span>
              </button>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={agentPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="quality" fill="#3B82F6" name="Quality Score" />
                <Bar dataKey="success" fill="#10B981" name="Success Rate %" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Performance Trends */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Trends</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="quality" stroke="#3B82F6" name="Quality Score" strokeWidth={2} />
                <Line type="monotone" dataKey="success" stroke="#10B981" name="Success Rate %" strokeWidth={2} />
                <Line type="monotone" dataKey="efficiency" stroke="#F59E0B" name="Efficiency" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Channel Performance */}
        <div className="bg-white rounded-lg p-6 shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Channel Performance Analysis</h3>
            <button 
              onClick={() => setActiveTab('campaigns')}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center space-x-1"
            >
              <Eye className="h-4 w-4" />
              <span>View Campaign Details</span>
            </button>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={channelData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="response_rate" fill="#3B82F6" name="Response Rate %" />
              </BarChart>
            </ResponsiveContainer>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={channelData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="conversion_rate" fill="#10B981" name="Conversion Rate %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Campaign Analytics */}
        <div className="bg-white rounded-lg p-6 shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Campaign Performance Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{campaign_analytics?.total_campaigns || 0}</div>
              <div className="text-sm text-gray-600">Total Campaigns</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{campaign_analytics?.active_campaigns || 0}</div>
              <div className="text-sm text-gray-600">Active Campaigns</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{campaign_analytics?.completed_campaigns || 0}</div>
              <div className="text-sm text-gray-600">Completed Campaigns</div>
            </div>
          </div>
          
          {/* Campaign Performance Table */}
          {campaign_analytics?.campaign_performance && (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Campaign</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contacted</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Response Rate</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Conversion Rate</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ROI</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {campaign_analytics.campaign_performance.map((campaign, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{campaign.name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{campaign.leads_contacted}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{(campaign.response_rate * 100).toFixed(1)}%</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{(campaign.conversion_rate * 100).toFixed(1)}%</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">{campaign.roi.toFixed(1)}x</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Insights and Recommendations */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Key Trends */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Key Trends & Insights</h3>
            <div className="space-y-4">
              {trends_and_insights?.key_trends?.map((trend, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <TrendingUp className={`h-5 w-5 mt-0.5 ${trend.change > 0 ? 'text-green-600' : 'text-red-600'}`} />
                  <div>
                    <p className="font-medium text-gray-900">{trend.trend}</p>
                    <p className="text-sm text-gray-600">
                      {trend.change > 0 ? '+' : ''}{(trend.change * 100).toFixed(1)}% over {trend.period}
                    </p>
                    <span className={`inline-block px-2 py-1 text-xs rounded-full mt-1 ${
                      trend.significance === 'high' ? 'bg-red-100 text-red-800' :
                      trend.significance === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {trend.significance} impact
                    </span>
                  </div>
                </div>
              )) || []}
            </div>
          </div>

          {/* Performance Recommendations */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">AI-Driven Recommendations</h3>
            <div className="space-y-4">
              {performance_recommendations?.slice(0, 4).map((rec, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    rec.priority === 'high' ? 'bg-red-500' : 
                    rec.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                  }`} />
                  <div>
                    <p className="font-medium text-gray-900">{rec.recommendation}</p>
                    <p className="text-sm text-gray-600">{rec.expected_impact}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                        rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                        rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {rec.priority} priority
                      </span>
                      <span className="text-xs text-gray-500">Effort: {rec.effort}</span>
                    </div>
                  </div>
                </div>
              )) || []}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderCampaignReport = () => {
    if (!campaignReport) return null;

    const { campaign_overview, lead_funnel_analysis, channel_performance, temporal_analysis, roi_analysis } = campaignReport;

    // Prepare funnel chart data
    const funnelData = lead_funnel_analysis?.funnel_stages?.map(stage => ({
      name: stage.stage,
      count: stage.count,
      percentage: stage.percentage
    })) || [];

    // Prepare temporal data
    const temporalData = temporal_analysis?.daily_performance ? Object.entries(temporal_analysis.daily_performance).map(([day, data]) => ({
      name: day,
      contacts: data.contacts,
      response_rate: data.response_rate * 100
    })) : [];

    return (
      <div className="space-y-6">
        {/* Campaign Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {renderMetricCard("Leads Targeted", campaign_overview?.total_leads_targeted?.toLocaleString() || '0', null, Target, 'blue')}
          {renderMetricCard("Leads Contacted", campaign_overview?.total_leads_contacted?.toLocaleString() || '0', null, Users, 'green')}
          {renderMetricCard("Total Responses", campaign_overview?.total_responses?.toLocaleString() || '0', null, MessageSquare, 'purple')}
          {renderMetricCard("Conversions", campaign_overview?.total_conversions?.toLocaleString() || '0', null, CheckCircle, 'orange')}
        </div>

        {/* ROI Metrics */}
        <div className="bg-white rounded-lg p-6 shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">ROI Analysis</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">${roi_analysis?.total_revenue?.toLocaleString() || '0'}</div>
              <div className="text-sm text-gray-600">Total Revenue</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{roi_analysis?.roi_percentage?.toFixed(1) || '0'}%</div>
              <div className="text-sm text-gray-600">ROI</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">${roi_analysis?.cost_per_conversion?.toFixed(2) || '0'}</div>
              <div className="text-sm text-gray-600">Cost per Conversion</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{roi_analysis?.payback_period_days || '0'} days</div>
              <div className="text-sm text-gray-600">Payback Period</div>
            </div>
          </div>
        </div>

        {/* Lead Funnel */}
        <div className="bg-white rounded-lg p-6 shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Lead Conversion Funnel</h3>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={funnelData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value, name) => [value.toLocaleString(), name]} />
              <Area type="monotone" dataKey="count" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
          
          {/* Funnel Analysis */}
          {lead_funnel_analysis?.drop_off_analysis && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h4 className="font-medium text-yellow-800">Optimization Opportunity</h4>
              <p className="text-yellow-700 text-sm mt-1">
                Highest drop-off: {lead_funnel_analysis.drop_off_analysis.highest_drop} 
                ({lead_funnel_analysis.drop_off_analysis.drop_percentage}% loss)
              </p>
              <p className="text-yellow-600 text-sm mt-1">
                {lead_funnel_analysis.drop_off_analysis.improvement_opportunity}
              </p>
            </div>
          )}
        </div>

        {/* Temporal Analysis */}
        <div className="bg-white rounded-lg p-6 shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance by Day</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={temporalData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="contacts" stroke="#3B82F6" name="Contacts" strokeWidth={2} />
              <Line type="monotone" dataKey="response_rate" stroke="#10B981" name="Response Rate %" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Channel Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">SMS Performance</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Leads Contacted:</span>
                <span className="font-medium">{channel_performance?.sms_performance?.leads_contacted?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Response Rate:</span>
                <span className="font-medium">{((channel_performance?.sms_performance?.response_rate || 0) * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Conversion Rate:</span>
                <span className="font-medium">{((channel_performance?.sms_performance?.conversion_rate || 0) * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Cost per Lead:</span>
                <span className="font-medium">${channel_performance?.sms_performance?.avg_cost_per_lead?.toFixed(2) || '0.00'}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Voice Performance</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Leads Contacted:</span>
                <span className="font-medium">{channel_performance?.voice_performance?.leads_contacted?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Response Rate:</span>
                <span className="font-medium">{((channel_performance?.voice_performance?.response_rate || 0) * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Conversion Rate:</span>
                <span className="font-medium">{((channel_performance?.voice_performance?.conversion_rate || 0) * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Cost per Lead:</span>
                <span className="font-medium">${channel_performance?.voice_performance?.avg_cost_per_lead?.toFixed(2) || '0.00'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Channel Recommendations */}
        {channel_performance?.channel_recommendations && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-blue-900 mb-4">Channel Optimization Insights</h3>
            <ul className="space-y-2">
              {channel_performance.channel_recommendations.map((rec, index) => (
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

  const renderAgentReport = () => {
    if (!agentReport) return null;

    const { agent_performance_metrics, learning_progress, conversation_quality, fine_tuning_impact } = agentReport;

    // Prepare quality metrics chart
    const qualityData = conversation_quality?.quality_dimensions ? Object.entries(conversation_quality.quality_dimensions).map(([key, value]) => ({
      name: key.replace(/_/g, ' '),
      value: value
    })) : [];

    // Prepare radar chart data for performance metrics
    const radarData = agent_performance_metrics?.performance_scores ? Object.entries(agent_performance_metrics.performance_scores).map(([key, value]) => ({
      metric: key.replace(/_/g, ' '),
      value: value,
      fullMark: 5
    })) : [];

    return (
      <div className="space-y-6">
        {/* Agent Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {renderMetricCard(
            "Response Quality", 
            agent_performance_metrics?.performance_scores?.response_quality?.toFixed(1) || '0.0', 
            null, 
            Brain, 
            'blue'
          )}
          {renderMetricCard(
            "Conversation Flow", 
            agent_performance_metrics?.performance_scores?.conversation_flow?.toFixed(1) || '0.0', 
            null, 
            MessageSquare, 
            'green'
          )}
          {renderMetricCard(
            "Goal Achievement", 
            agent_performance_metrics?.performance_scores?.goal_achievement?.toFixed(1) || '0.0', 
            null, 
            Target, 
            'purple'
          )}
          {renderMetricCard(
            "User Satisfaction", 
            agent_performance_metrics?.performance_scores?.user_satisfaction?.toFixed(1) || '0.0', 
            null, 
            CheckCircle, 
            'orange'
          )}
        </div>

        {/* Performance Radar Chart */}
        <div className="bg-white rounded-lg p-6 shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Performance Profile</h3>
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={30} domain={[0, 5]} />
              <Radar name="Performance" dataKey="value" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Learning Progress & Fine-tuning Impact */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Learning Progress */}
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Learning Progress</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {learning_progress?.learning_curve?.current_performance?.toFixed(1) || '0.0'}
                </div>
                <div className="text-sm text-gray-600">Current Performance</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {((learning_progress?.learning_curve?.improvement_rate || 0) * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-gray-600">Improvement Rate</div>
              </div>
            </div>
            <div className="mt-4 text-center">
              <div className="text-2xl font-bold text-purple-600">
                {learning_progress?.learning_curve?.learning_velocity || 'N/A'}
              </div>
              <div className="text-sm text-gray-600">Learning Velocity</div>
            </div>
          </div>

          {/* Fine-tuning Impact */}
          {fine_tuning_impact && (
            <div className="bg-white rounded-lg p-6 shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Fine-tuning Impact</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Performance Score:</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-500">{fine_tuning_impact.pre_fine_tuning?.avg_score?.toFixed(1)}</span>
                    <ArrowUp className="h-4 w-4 text-green-600" />
                    <span className="font-medium text-green-600">{fine_tuning_impact.post_fine_tuning?.avg_score?.toFixed(1)}</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Success Rate:</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-500">{(fine_tuning_impact.pre_fine_tuning?.success_rate * 100)?.toFixed(1)}%</span>
                    <ArrowUp className="h-4 w-4 text-green-600" />
                    <span className="font-medium text-green-600">{(fine_tuning_impact.post_fine_tuning?.success_rate * 100)?.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">User Satisfaction:</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-500">{fine_tuning_impact.pre_fine_tuning?.user_satisfaction?.toFixed(1)}</span>
                    <ArrowUp className="h-4 w-4 text-green-600" />
                    <span className="font-medium text-green-600">{fine_tuning_impact.post_fine_tuning?.user_satisfaction?.toFixed(1)}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Conversation Quality */}
        <div className="bg-white rounded-lg p-6 shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Conversation Quality Dimensions</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={qualityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 5]} />
              <Tooltip />
              <Bar dataKey="value" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Knowledge Areas */}
        {learning_progress?.knowledge_areas && (
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Knowledge Areas Performance</h3>
            <div className="space-y-4">
              {learning_progress.knowledge_areas.map((area, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{area.area.replace(/_/g, ' ')}</p>
                    <p className="text-sm text-gray-600 capitalize flex items-center space-x-1">
                      <span>{area.trend}</span>
                      {area.trend === 'improving' && <ArrowUp className="h-3 w-3 text-green-600" />}
                      {area.trend === 'stable' && <Minus className="h-3 w-3 text-gray-600" />}
                      {area.trend === 'declining' && <ArrowDown className="h-3 w-3 text-red-600" />}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${area.proficiency * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {(area.proficiency * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-white rounded-lg p-6 shadow">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="h-6 bg-gray-200 rounded w-1/4"></div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[1, 2].map(i => (
              <div key={i} className="bg-white rounded-lg p-6 shadow">
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="h-64 bg-gray-200 rounded"></div>
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
          <h3 className="text-red-800 font-medium">Error Loading Advanced Analytics</h3>
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
          <h1 className="text-3xl font-bold text-gray-900">Advanced Analytics</h1>
          <p className="text-gray-600">Comprehensive performance insights and intelligence</p>
        </div>
        <div className="flex items-center space-x-4">
          {/* Auto-refresh toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg border ${
              autoRefresh 
                ? 'bg-green-50 border-green-200 text-green-700' 
                : 'bg-gray-50 border-gray-200 text-gray-700'
            }`}
          >
            <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            <span className="text-sm">Auto-refresh</span>
          </button>

          {/* Manual refresh */}
          <button
            onClick={fetchData}
            className="px-3 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center space-x-2"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh</span>
          </button>

          {/* Time Period Selector */}
          <select
            value={timePeriod}
            onChange={(e) => setTimePeriod(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>

          {/* Export Button */}
          <div className="relative">
            <button 
              onClick={() => handleExportReport(activeTab)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Export Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'dashboard'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4" />
              <span>Comprehensive Dashboard</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('campaigns')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'campaigns'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Target className="h-4 w-4" />
              <span>Campaign Intelligence</span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('agents')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'agents'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Brain className="h-4 w-4" />
              <span>Agent Intelligence</span>
            </div>
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'dashboard' && renderDashboard()}
      {activeTab === 'campaigns' && renderCampaignReport()}
      {activeTab === 'agents' && renderAgentReport()}
    </div>
  );
};

export default AdvancedAnalytics;