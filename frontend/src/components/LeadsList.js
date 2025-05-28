import React, { useState, useEffect } from 'react';
import axios from 'axios';

const LeadsList = ({ currentOrg }) => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [actionLoading, setActionLoading] = useState({});
  const [showAddModal, setShowAddModal] = useState(false);
  const [viewLead, setViewLead] = useState(null);
  
  // Add Lead form state
  const [newLead, setNewLead] = useState({
    name: '',
    email: '',
    phone: '',
    status: 'Initial Contact'
  });
  
  useEffect(() => {
    loadLeads();
  }, [currentOrg]);
  
  const loadLeads = async () => {
    try {
      setLoading(true);
      
      // Try to fetch real data from API
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/leads?org_id=${currentOrg?.id || 'production_org_123'}`);
      
      if (response.data.success && response.data.leads.length > 0) {
        setLeads(response.data.leads);
      } else {
        // Fallback to mock data if no real leads
        const mockLeads = [
          {
            id: '1',
            name: 'John Smith',
            email: 'john.smith@example.com',
            phone: '(555) 123-4567',
            status: 'Qualified',
            relationship_stage: 'qualification',
            personality_type: 'analytical',
            trust_level: 0.75,
            conversion_probability: 0.75,
            created_at: '2023-01-15T10:30:00Z'
          },
          {
            id: '2',
            name: 'Sarah Johnson',
            email: 'sarah.j@example.com',
            phone: '(555) 234-5678',
            status: 'Nurturing',
            relationship_stage: 'nurturing',
            personality_type: 'expressive',
            trust_level: 0.55,
            conversion_probability: 0.55,
            created_at: '2023-02-20T14:45:00Z'
          },
          {
            id: '3',
            name: 'Michael Brown',
            email: 'michael.b@example.com',
            phone: '(555) 345-6789',
            status: 'Initial Contact',
            relationship_stage: 'initial_contact',
            personality_type: 'driver',
            trust_level: 0.30,
            conversion_probability: 0.30,
            created_at: '2023-03-05T09:15:00Z'
          },
          {
            id: '4',
            name: 'Emily Davis',
            email: 'emily.d@example.com',
            phone: '(555) 456-7890',
            status: 'Closing',
            relationship_stage: 'closing',
            personality_type: 'amiable',
            trust_level: 0.90,
            conversion_probability: 0.90,
            created_at: '2023-01-10T16:20:00Z'
          },
          {
            id: '5',
            name: 'Robert Wilson',
            email: 'robert.w@example.com',
            phone: '(555) 567-8901',
            status: 'Qualified',
            relationship_stage: 'qualification',
            personality_type: 'analytical',
            trust_level: 0.65,
            conversion_probability: 0.65,
            created_at: '2023-02-28T11:10:00Z'
          },
          {
            id: '6',
            name: 'Jennifer Lee',
            email: 'jennifer.l@example.com',
            phone: '(555) 678-9012',
            status: 'Nurturing',
            relationship_stage: 'nurturing',
            personality_type: 'expressive',
            trust_level: 0.40,
            conversion_probability: 0.40,
            created_at: '2023-03-15T13:50:00Z'
          },
          {
            id: '7',
            name: 'William Taylor',
            email: 'william.t@example.com',
            phone: '(555) 789-0123',
            status: 'Initial Contact',
            relationship_stage: 'initial_contact',
            personality_type: 'driver',
            trust_level: 0.25,
            conversion_probability: 0.25,
            created_at: '2023-03-20T10:05:00Z'
          },
          {
            id: '8',
            name: 'Olivia Martin',
            email: 'olivia.m@example.com',
            phone: '(555) 890-1234',
            status: 'Closing',
            relationship_stage: 'closing',
            personality_type: 'amiable',
            trust_level: 0.85,
            conversion_probability: 0.85,
            created_at: '2023-01-25T15:30:00Z'
          }
        ];
        setLeads(mockLeads);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading leads:', error);
      // Fallback to mock data on error
      const mockLeads = [
        {
          id: '1',
          name: 'John Smith',
          email: 'john.smith@example.com',
          phone: '(555) 123-4567',
          status: 'Qualified',
          relationship_stage: 'qualification',
          personality_type: 'analytical',
          trust_level: 0.75,
          conversion_probability: 0.75,
          created_at: '2023-01-15T10:30:00Z'
        }
      ];
      setLeads(mockLeads);
      setLoading(false);
    }
  };
  
  // Action handlers
  const handleSendMessage = async (leadId, leadName) => {
    try {
      setActionLoading(prev => ({ ...prev, [`message_${leadId}`]: true }));
      
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/actions/send-message`, {
        lead_id: leadId,
        org_id: currentOrg?.id || 'production_org_123'
      });
      
      if (response.data.success) {
        alert(`Message sent successfully to ${leadName}!\n\nAI Agent: ${response.data.agent_type}\nConversation ID: ${response.data.conversation_id}`);
      } else {
        alert('Failed to send message. Please try again.');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error sending message: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(prev => ({ ...prev, [`message_${leadId}`]: false }));
    }
  };
  
  const handleInitiateCall = async (leadId, leadName) => {
    try {
      setActionLoading(prev => ({ ...prev, [`call_${leadId}`]: true }));
      
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/actions/initiate-call`, {
        lead_id: leadId,
        org_id: currentOrg?.id || 'production_org_123'
      });
      
      if (response.data.success) {
        alert(`Call initiated successfully to ${leadName}!\n\nCall ID: ${response.data.call_id}\nAgent: ${response.data.agent_type}\nStatus: ${response.data.status}`);
      } else {
        alert('Failed to initiate call. Please try again.');
      }
    } catch (error) {
      console.error('Error initiating call:', error);
      alert('Error initiating call: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(prev => ({ ...prev, [`call_${leadId}`]: false }));
    }
  };
  
  const handleViewLead = async (leadId) => {
    try {
      setActionLoading(prev => ({ ...prev, [`view_${leadId}`]: true }));
      
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/actions/view-lead`, {
        lead_id: leadId
      });
      
      if (response.data.success) {
        setViewLead(response.data);
      } else {
        alert('Failed to load lead details. Please try again.');
      }
    } catch (error) {
      console.error('Error viewing lead:', error);
      alert('Error loading lead details: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(prev => ({ ...prev, [`view_${leadId}`]: false }));
    }
  };
  
  const handleAddLead = async (e) => {
    e.preventDefault();
    try {
      setActionLoading(prev => ({ ...prev, 'add_lead': true }));
      
      const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/actions/add-lead`, {
        org_id: currentOrg?.id || 'production_org_123',
        name: newLead.name,
        email: newLead.email,
        phone: newLead.phone,
        status: newLead.status
      });
      
      if (response.data.success) {
        alert(`Lead "${newLead.name}" added successfully!`);
        setShowAddModal(false);
        setNewLead({ name: '', email: '', phone: '', status: 'Initial Contact' });
        loadLeads(); // Refresh the list
      } else {
        alert('Failed to add lead. Please try again.');
      }
    } catch (error) {
      console.error('Error adding lead:', error);
      alert('Error adding lead: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(prev => ({ ...prev, 'add_lead': false }));
    }
  };
  
  const filteredLeads = leads.filter(lead => {
    if (filter === 'all') return true;
    return lead.relationship_stage === filter;
  });
  
  const renderLeadStatus = (status) => {
    const statusStyles = {
      'Qualified': 'bg-green-100 text-green-800',
      'Nurturing': 'bg-yellow-100 text-yellow-800',
      'Initial Contact': 'bg-gray-100 text-gray-800',
      'Closing': 'bg-indigo-100 text-indigo-800'
    };
    
    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };
  
  const renderPersonalityBadge = (type) => {
    const typeStyles = {
      'analytical': 'bg-blue-100 text-blue-800',
      'driver': 'bg-red-100 text-red-800',
      'expressive': 'bg-purple-100 text-purple-800',
      'amiable': 'bg-green-100 text-green-800'
    };
    
    const typeLabels = {
      'analytical': 'Analytical',
      'driver': 'Driver',
      'expressive': 'Expressive',
      'amiable': 'Amiable'
    };
    
    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${typeStyles[type] || 'bg-gray-100 text-gray-800'}`}>
        {typeLabels[type] || type}
      </span>
    );
  };
  
  return (
    <div>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Leads</h1>
        <div className="flex space-x-2">
          <button 
            onClick={() => setShowAddModal(true)}
            disabled={actionLoading['add_lead']}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {actionLoading['add_lead'] ? (
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            )}
            {actionLoading['add_lead'] ? 'Adding...' : 'Add Lead'}
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
          onClick={() => setFilter('initial_contact')}
          className={`px-3 py-2 text-sm font-medium rounded-md ${
            filter === 'initial_contact'
              ? 'bg-indigo-100 text-indigo-700'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Initial Contact
        </button>
        <button
          onClick={() => setFilter('qualification')}
          className={`px-3 py-2 text-sm font-medium rounded-md ${
            filter === 'qualification'
              ? 'bg-indigo-100 text-indigo-700'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Qualification
        </button>
        <button
          onClick={() => setFilter('nurturing')}
          className={`px-3 py-2 text-sm font-medium rounded-md ${
            filter === 'nurturing'
              ? 'bg-indigo-100 text-indigo-700'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Nurturing
        </button>
        <button
          onClick={() => setFilter('closing')}
          className={`px-3 py-2 text-sm font-medium rounded-md ${
            filter === 'closing'
              ? 'bg-indigo-100 text-indigo-700'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Closing
        </button>
      </div>
      
      {/* Leads Table */}
      <div className="mt-4 flex flex-col">
        <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Lead
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Personality
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Trust Level
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Conversion
                    </th>
                    <th scope="col" className="relative px-6 py-3">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-500">
                        Loading...
                      </td>
                    </tr>
                  ) : filteredLeads.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-500">
                        No leads found
                      </td>
                    </tr>
                  ) : (
                    filteredLeads.map((lead) => (
                      <tr key={lead.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-indigo-100 text-indigo-800 font-semibold">
                              {lead.name.charAt(0)}
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                              <div className="text-sm text-gray-500">{lead.email}</div>
                              <div className="text-sm text-gray-500">{lead.phone}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {renderLeadStatus(lead.status)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {renderPersonalityBadge(lead.personality_type)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                              <div className={`h-2.5 rounded-full ${
                                lead.trust_level >= 0.7 ? 'bg-green-500' :
                                lead.trust_level >= 0.4 ? 'bg-yellow-500' :
                                'bg-red-500'
                              }`} style={{ width: `${lead.trust_level * 100}%` }}></div>
                            </div>
                            <span className="ml-2 text-sm text-gray-500">{Math.round(lead.trust_level * 100)}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="w-full bg-gray-200 rounded-full h-2.5">
                              <div className={`h-2.5 rounded-full ${
                                lead.conversion_probability >= 0.7 ? 'bg-green-500' :
                                lead.conversion_probability >= 0.4 ? 'bg-yellow-500' :
                                'bg-red-500'
                              }`} style={{ width: `${lead.conversion_probability * 100}%` }}></div>
                            </div>
                            <span className="ml-2 text-sm text-gray-500">{Math.round(lead.conversion_probability * 100)}%</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex space-x-2">
                          <button 
                            onClick={() => handleSendMessage(lead.id, lead.name)}
                            disabled={actionLoading[`message_${lead.id}`]}
                            className="text-blue-600 hover:text-blue-900 text-sm font-medium disabled:opacity-50"
                          >
                            {actionLoading[`message_${lead.id}`] ? 'Sending...' : 'Message'}
                          </button>
                          <span className="text-gray-300">|</span>
                          <button 
                            onClick={() => handleInitiateCall(lead.id, lead.name)}
                            disabled={actionLoading[`call_${lead.id}`]}
                            className="text-green-600 hover:text-green-900 text-sm font-medium disabled:opacity-50"
                          >
                            {actionLoading[`call_${lead.id}`] ? 'Calling...' : 'Call'}
                          </button>
                          <span className="text-gray-300">|</span>
                          <button 
                            onClick={() => handleViewLead(lead.id)}
                            disabled={actionLoading[`view_${lead.id}`]}
                            className="text-indigo-600 hover:text-indigo-900 text-sm font-medium disabled:opacity-50"
                          >
                            {actionLoading[`view_${lead.id}`] ? 'Loading...' : 'View'}
                          </button>
                        </div>
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
    
    {/* Add Lead Modal */}
    {showAddModal && (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
          <div className="mt-3">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Lead</h3>
            <form onSubmit={handleAddLead}>
              <div className="mb-4">
                <label htmlFor="name" className="block text-sm font-medium text-gray-700">Name *</label>
                <input
                  type="text"
                  id="name"
                  required
                  value={newLead.name}
                  onChange={(e) => setNewLead(prev => ({ ...prev, name: e.target.value }))}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email *</label>
                <input
                  type="email"
                  id="email"
                  required
                  value={newLead.email}
                  onChange={(e) => setNewLead(prev => ({ ...prev, email: e.target.value }))}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">Phone</label>
                <input
                  type="tel"
                  id="phone"
                  value={newLead.phone}
                  onChange={(e) => setNewLead(prev => ({ ...prev, phone: e.target.value }))}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
              <div className="mb-4">
                <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
                <select
                  id="status"
                  value={newLead.status}
                  onChange={(e) => setNewLead(prev => ({ ...prev, status: e.target.value }))}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
                  <option value="Initial Contact">Initial Contact</option>
                  <option value="Qualified">Qualified</option>
                  <option value="Nurturing">Nurturing</option>
                  <option value="Closing">Closing</option>
                </select>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md shadow-sm hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading['add_lead']}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {actionLoading['add_lead'] ? 'Adding...' : 'Add Lead'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    )}
    
    {/* View Lead Modal */}
    {viewLead && (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div className="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
          <div className="mt-3">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-medium text-gray-900">Lead Details</h3>
              <button
                onClick={() => setViewLead(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Lead Information */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-medium text-gray-900 mb-3">Lead Information</h4>
                <div className="space-y-2">
                  <p><span className="font-medium">Name:</span> {viewLead.lead?.name}</p>
                  <p><span className="font-medium">Email:</span> {viewLead.lead?.email}</p>
                  <p><span className="font-medium">Phone:</span> {viewLead.lead?.phone}</p>
                  <p><span className="font-medium">Status:</span> {viewLead.lead?.status}</p>
                  <p><span className="font-medium">Trust Level:</span> {Math.round((viewLead.lead?.trust_level || 0) * 100)}%</p>
                  <p><span className="font-medium">Conversion Probability:</span> {Math.round((viewLead.lead?.conversion_probability || 0) * 100)}%</p>
                </div>
              </div>
              
              {/* Recent Conversations */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-medium text-gray-900 mb-3">Recent Conversations</h4>
                {viewLead.recent_conversations?.length > 0 ? (
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {viewLead.recent_conversations.map((conv, index) => (
                      <div key={index} className="text-sm bg-white p-2 rounded">
                        <p><span className="font-medium">Channel:</span> {conv.channel}</p>
                        <p><span className="font-medium">Agent:</span> {conv.agent_type}</p>
                        <p><span className="font-medium">Date:</span> {new Date(conv.created_at).toLocaleDateString()}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No conversations yet</p>
                )}
              </div>
              
              {/* Memory Context */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-medium text-gray-900 mb-3">AI Memory Context</h4>
                {viewLead.memory_context && Object.keys(viewLead.memory_context).length > 0 ? (
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {Object.entries(viewLead.memory_context).map(([key, value], index) => (
                      <div key={index} className="text-sm">
                        <span className="font-medium">{key}:</span> {typeof value === 'object' ? JSON.stringify(value) : value}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No memory context available</p>
                )}
              </div>
              
              {/* Recent Agent Interactions */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="text-md font-medium text-gray-900 mb-3">Recent AI Interactions</h4>
                {viewLead.recent_interactions?.length > 0 ? (
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {viewLead.recent_interactions.map((interaction, index) => (
                      <div key={index} className="text-sm bg-white p-2 rounded">
                        <p><span className="font-medium">Agent:</span> {interaction.agent_type}</p>
                        <p><span className="font-medium">Confidence:</span> {Math.round((interaction.confidence_score || 0) * 100)}%</p>
                        <p><span className="font-medium">Date:</span> {new Date(interaction.created_at).toLocaleDateString()}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No recent interactions</p>
                )}
              </div>
            </div>
            
            <div className="flex justify-end mt-6">
              <button
                onClick={() => setViewLead(null)}
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

export default LeadsList;