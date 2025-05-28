import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Conversations = ({ currentOrg }) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [actionLoading, setActionLoading] = useState({});
  const [viewConversation, setViewConversation] = useState(null);
  
  useEffect(() => {
    loadConversations();
  }, [currentOrg]);
  
  const loadConversations = async () => {
    try {
      setLoading(true);
      
      // Try to fetch real data from API
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/conversations?org_id=${currentOrg?.id || 'production_org_123'}`);
      
      if (response.data.success && response.data.conversations.length > 0) {
        setConversations(response.data.conversations);
      } else {
        // Fallback to mock data if no real conversations
        const mockConversations = [
          {
            id: '1',
            lead: {
              id: '1',
              name: 'John Smith',
              email: 'john.smith@example.com'
            },
            channel: 'voice',
            agent_type: 'qualifier',
            duration_seconds: 384,
            sentiment_analysis: {
              overall: 'positive',
              changes: [
                {time: 120, sentiment: 'neutral'},
                {time: 240, sentiment: 'positive'}
              ]
            },
            created_at: '2023-03-15T10:30:00Z',
            effectiveness_score: 0.85
          },
          {
            id: '2',
            lead: {
              id: '2',
              name: 'Sarah Johnson',
              email: 'sarah.j@example.com'
            },
            channel: 'email',
            agent_type: 'nurturer',
            duration_seconds: null,
            sentiment_analysis: {
              overall: 'neutral'
            },
            created_at: '2023-03-14T14:45:00Z',
            effectiveness_score: 0.65
          },
          {
            id: '3',
            lead: {
              id: '3',
              name: 'Michael Brown',
              email: 'michael.b@example.com'
            },
            channel: 'sms',
            agent_type: 'initial_contact',
            duration_seconds: null,
            sentiment_analysis: {
              overall: 'positive'
            },
            created_at: '2023-03-13T09:15:00Z',
            effectiveness_score: 0.75
          },
          {
            id: '4',
            lead: {
              id: '4',
              name: 'Emily Davis',
              email: 'emily.d@example.com'
            },
            channel: 'voice',
            agent_type: 'closer',
            duration_seconds: 612,
            sentiment_analysis: {
              overall: 'very_positive',
              changes: [
                {time: 180, sentiment: 'neutral'},
                {time: 360, sentiment: 'positive'},
                {time: 540, sentiment: 'very_positive'}
              ]
            },
            created_at: '2023-03-12T16:20:00Z',
            effectiveness_score: 0.95
          },
          {
            id: '5',
            lead: {
              id: '5',
              name: 'Robert Wilson',
              email: 'robert.w@example.com'
            },
            channel: 'sms',
            agent_type: 'objection_handler',
            duration_seconds: null,
            sentiment_analysis: {
              overall: 'neutral'
            },
            created_at: '2023-03-11T11:10:00Z',
            effectiveness_score: 0.70
          },
          {
            id: '6',
            lead: {
              id: '1',
              name: 'John Smith',
              email: 'john.smith@example.com'
            },
            channel: 'email',
            agent_type: 'nurturer',
            duration_seconds: null,
            sentiment_analysis: {
              overall: 'positive'
            },
            created_at: '2023-03-10T13:50:00Z',
            effectiveness_score: 0.80
          }
        ];
        
        setConversations(mockConversations);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading conversations:', error);
      // Fallback to mock data on error
      const mockConversations = [
        {
          id: '1',
          lead: {
            id: '1',
            name: 'John Smith',
            email: 'john.smith@example.com'
          },
          channel: 'voice',
          agent_type: 'qualifier',
          created_at: '2023-03-15T10:30:00Z',
          effectiveness_score: 0.85
        }
      ];
      setConversations(mockConversations);
      setLoading(false);
    }
  };
  
  // Action handlers
  const handleNewCall = async () => {
    try {
      setActionLoading(prev => ({ ...prev, 'new_call': true }));
      
      // For now, we'll show a selection dialog or redirect to leads
      alert('New Call: Please select a lead from the Leads page to initiate a call, or this could open a lead selection modal.');
      
    } catch (error) {
      console.error('Error with new call:', error);
      alert('Error: Unable to initiate new call');
    } finally {
      setActionLoading(prev => ({ ...prev, 'new_call': false }));
    }
  };
  
  const handleNewMessage = async () => {
    try {
      setActionLoading(prev => ({ ...prev, 'new_message': true }));
      
      // For now, we'll show a selection dialog or redirect to leads
      alert('New Message: Please select a lead from the Leads page to send a message, or this could open a lead selection modal.');
      
    } catch (error) {
      console.error('Error with new message:', error);
      alert('Error: Unable to send new message');
    } finally {
      setActionLoading(prev => ({ ...prev, 'new_message': false }));
    }
  };
  
  const handleViewDetails = async (conversationId, leadId) => {
    try {
      setActionLoading(prev => ({ ...prev, [`view_${conversationId}`]: true }));
      
      // Get detailed conversation information
      // For now, we'll use the lead view endpoint to get lead details
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/actions/view-lead`, {
        lead_id: leadId
      });
      
      if (response.data.success) {
        // Find the specific conversation
        const conversation = conversations.find(c => c.id === conversationId);
        setViewConversation({
          ...response.data,
          conversation: conversation
        });
      } else {
        alert('Failed to load conversation details. Please try again.');
      }
    } catch (error) {
      console.error('Error viewing conversation details:', error);
      let errorMessage = 'Unknown error occurred';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.message) {
        errorMessage = error.message;
      }
      alert(`Error loading conversation details: ${errorMessage}`);
    } finally {
      setActionLoading(prev => ({ ...prev, [`view_${conversationId}`]: false }));
    }
  };
  
  const filteredConversations = conversations.filter(convo => {
    if (filter === 'all') return true;
    return convo.channel === filter;
  });
  
  const renderChannelBadge = (channel) => {
    const channelStyles = {
      'voice': 'bg-blue-100 text-blue-800',
      'sms': 'bg-green-100 text-green-800',
      'email': 'bg-yellow-100 text-yellow-800',
      'chat': 'bg-purple-100 text-purple-800'
    };
    
    const channelIcons = {
      'voice': (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
        </svg>
      ),
      'sms': (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      ),
      'email': (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      'chat': (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
        </svg>
      )
    };
    
    return (
      <span className={`px-2 py-1 inline-flex items-center text-xs leading-5 font-semibold rounded-full ${channelStyles[channel] || 'bg-gray-100 text-gray-800'}`}>
        {channelIcons[channel]}
        {channel.charAt(0).toUpperCase() + channel.slice(1)}
      </span>
    );
  };
  
  const renderAgentBadge = (agentType) => {
    const agentStyles = {
      'initial_contact': 'bg-gray-100 text-gray-800',
      'qualifier': 'bg-indigo-100 text-indigo-800',
      'nurturer': 'bg-yellow-100 text-yellow-800',
      'objection_handler': 'bg-red-100 text-red-800',
      'closer': 'bg-green-100 text-green-800',
      'appointment_setter': 'bg-purple-100 text-purple-800'
    };
    
    const agentLabels = {
      'initial_contact': 'Initial Contact',
      'qualifier': 'Qualifier',
      'nurturer': 'Nurturer',
      'objection_handler': 'Objection Handler',
      'closer': 'Closer',
      'appointment_setter': 'Appointment Setter'
    };
    
    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${agentStyles[agentType] || 'bg-gray-100 text-gray-800'}`}>
        {agentLabels[agentType] || agentType}
      </span>
    );
  };
  
  const renderSentimentIndicator = (sentiment) => {
    const sentimentColors = {
      'very_negative': 'bg-red-500',
      'negative': 'bg-red-400',
      'neutral': 'bg-gray-400',
      'positive': 'bg-green-400',
      'very_positive': 'bg-green-500'
    };
    
    return (
      <div className="flex items-center">
        <div className={`h-3 w-3 rounded-full ${sentimentColors[sentiment] || 'bg-gray-400'} mr-2`}></div>
        <span className="text-sm text-gray-600">
          {sentiment.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
        </span>
      </div>
    );
  };
  
  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric'
    }).format(date);
  };
  
  return (
    <div>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Conversations</h1>
        <div className="flex space-x-2">
          <button 
            onClick={handleNewCall}
            disabled={actionLoading['new_call']}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {actionLoading['new_call'] ? (
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
            )}
            {actionLoading['new_call'] ? 'Loading...' : 'New Call'}
          </button>
          <button 
            onClick={handleNewMessage}
            disabled={actionLoading['new_message']}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {actionLoading['new_message'] ? (
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            )}
            {actionLoading['new_message'] ? 'Loading...' : 'New Message'}
          </button>
        </div>
      </div>
      
      {/* Filters */}
      <div className="mt-4 flex space-x-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-3 py-2 text-sm font-medium rounded-md ${
            filter === 'all'
              ? 'bg-indigo-100 text-indigo-700'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilter('voice')}
          className={`px-3 py-2 text-sm font-medium rounded-md ${
            filter === 'voice'
              ? 'bg-indigo-100 text-indigo-700'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Voice
        </button>
        <button
          onClick={() => setFilter('sms')}
          className={`px-3 py-2 text-sm font-medium rounded-md ${
            filter === 'sms'
              ? 'bg-indigo-100 text-indigo-700'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          SMS
        </button>
        <button
          onClick={() => setFilter('email')}
          className={`px-3 py-2 text-sm font-medium rounded-md ${
            filter === 'email'
              ? 'bg-indigo-100 text-indigo-700'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Email
        </button>
      </div>
      
      {/* Conversations List */}
      <div className="mt-4 grid gap-5 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          <div className="col-span-3 text-center py-10">
            <p className="text-gray-500">Loading conversations...</p>
          </div>
        ) : filteredConversations.length === 0 ? (
          <div className="col-span-3 text-center py-10">
            <p className="text-gray-500">No conversations found</p>
          </div>
        ) : (
          filteredConversations.map((conversation) => (
            <div key={conversation.id} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-indigo-100 text-indigo-800 font-semibold">
                        {conversation.lead.name.charAt(0)}
                      </div>
                      <div className="ml-3">
                        <h3 className="text-sm font-medium text-gray-900">{conversation.lead.name}</h3>
                        <p className="text-xs text-gray-500">{conversation.lead.email}</p>
                      </div>
                    </div>
                    
                    <div className="mt-3">
                      <div className="flex justify-between mb-2">
                        <div>{renderChannelBadge(conversation.channel)}</div>
                        <div className="text-xs text-gray-500">{formatDate(conversation.created_at)}</div>
                      </div>
                      
                      <div className="mt-2">
                        <div className="text-xs text-gray-500 mb-1">Agent Type:</div>
                        <div>{renderAgentBadge(conversation.agent_type)}</div>
                      </div>
                      
                      <div className="mt-3">
                        <div className="text-xs text-gray-500 mb-1">Sentiment:</div>
                        <div>{renderSentimentIndicator(conversation.sentiment_analysis.overall)}</div>
                      </div>
                      
                      {conversation.channel === 'voice' && (
                        <div className="mt-3">
                          <div className="text-xs text-gray-500 mb-1">Duration:</div>
                          <div className="text-sm text-gray-900">{formatDuration(conversation.duration_seconds)}</div>
                        </div>
                      )}
                      
                      <div className="mt-3">
                        <div className="text-xs text-gray-500 mb-1">Effectiveness:</div>
                        <div className="flex items-center">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div className={`h-2 rounded-full ${
                              conversation.effectiveness_score >= 0.8 ? 'bg-green-500' :
                              conversation.effectiveness_score >= 0.6 ? 'bg-yellow-500' :
                              'bg-red-500'
                            }`} style={{ width: `${conversation.effectiveness_score * 100}%` }}></div>
                          </div>
                          <span className="ml-2 text-xs text-gray-500">{Math.round(conversation.effectiveness_score * 100)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-4 flex justify-end">
                  <button 
                    onClick={() => handleViewDetails(conversation.id, conversation.lead.id)}
                    disabled={actionLoading[`view_${conversation.id}`]}
                    className="text-indigo-600 hover:text-indigo-900 text-sm font-medium disabled:opacity-50"
                  >
                    {actionLoading[`view_${conversation.id}`] ? 'Loading...' : 'View Details'}
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      
      {/* View Conversation Details Modal */}
      {viewConversation && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-medium text-gray-900">Conversation Details</h3>
                <button
                  onClick={() => setViewConversation(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Conversation Information */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-md font-medium text-gray-900 mb-3">Conversation Information</h4>
                  <div className="space-y-2">
                    <p><span className="font-medium">Channel:</span> {viewConversation.conversation?.channel}</p>
                    <p><span className="font-medium">Agent Type:</span> {viewConversation.conversation?.agent_type}</p>
                    {viewConversation.conversation?.duration_seconds && (
                      <p><span className="font-medium">Duration:</span> {formatDuration(viewConversation.conversation.duration_seconds)}</p>
                    )}
                    <p><span className="font-medium">Date:</span> {formatDate(viewConversation.conversation?.created_at)}</p>
                    {viewConversation.conversation?.effectiveness_score && (
                      <p><span className="font-medium">Effectiveness:</span> {Math.round(viewConversation.conversation.effectiveness_score * 100)}%</p>
                    )}
                  </div>
                </div>
                
                {/* Lead Information */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-md font-medium text-gray-900 mb-3">Lead Information</h4>
                  <div className="space-y-2">
                    <p><span className="font-medium">Name:</span> {viewConversation.lead?.name}</p>
                    <p><span className="font-medium">Email:</span> {viewConversation.lead?.email}</p>
                    <p><span className="font-medium">Phone:</span> {viewConversation.lead?.phone}</p>
                    <p><span className="font-medium">Status:</span> {viewConversation.lead?.status}</p>
                    <p><span className="font-medium">Trust Level:</span> {Math.round((viewConversation.lead?.trust_level || 0) * 100)}%</p>
                  </div>
                </div>
                
                {/* Sentiment Analysis */}
                {viewConversation.conversation?.sentiment_analysis && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="text-md font-medium text-gray-900 mb-3">Sentiment Analysis</h4>
                    <div className="space-y-2">
                      <p><span className="font-medium">Overall Sentiment:</span> {renderSentimentIndicator(viewConversation.conversation.sentiment_analysis.overall)}</p>
                      {viewConversation.conversation.sentiment_analysis.changes && (
                        <div>
                          <p className="font-medium mb-2">Sentiment Changes:</p>
                          <div className="space-y-1 max-h-32 overflow-y-auto">
                            {viewConversation.conversation.sentiment_analysis.changes.map((change, index) => (
                              <div key={index} className="text-sm bg-white p-2 rounded">
                                <span className="font-medium">Time {Math.floor(change.time / 60)}:{(change.time % 60).toString().padStart(2, '0')}:</span> {renderSentimentIndicator(change.sentiment)}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {/* AI Memory Context */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="text-md font-medium text-gray-900 mb-3">AI Memory Context</h4>
                  {viewConversation.memory_context && Object.keys(viewConversation.memory_context).length > 0 ? (
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {Object.entries(viewConversation.memory_context).map(([key, value], index) => (
                        <div key={index} className="text-sm">
                          <span className="font-medium">{key}:</span> {typeof value === 'object' ? JSON.stringify(value) : value}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">No memory context available</p>
                  )}
                </div>
              </div>
              
              <div className="flex justify-end mt-6">
                <button
                  onClick={() => setViewConversation(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md shadow-sm hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Conversations;