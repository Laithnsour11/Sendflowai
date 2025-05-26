import React, { useState, useEffect } from 'react';
import axios from 'axios';

const KnowledgeBase = ({ currentOrg }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedType, setSelectedType] = useState('all');
  const [newDocument, setNewDocument] = useState({
    title: '',
    content: '',
    document_type: 'sop',
    metadata: {}
  });
  const [showAddForm, setShowAddForm] = useState(false);
  
  const documentTypes = [
    { value: 'sop', label: 'Standard Operating Procedure' },
    { value: 'script', label: 'Sales Script' },
    { value: 'training', label: 'Training Material' },
    { value: 'faq', label: 'FAQ' },
    { value: 'objection', label: 'Objection Handler' }
  ];
  
  useEffect(() => {
    // Simulated data loading for demo
    const loadDocuments = async () => {
      try {
        setLoading(true);
        
        // In a real app, we would fetch this data from the API
        // const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/knowledge/documents?org_id=${currentOrg.id}`);
        
        // Mock data for demo
        setTimeout(() => {
          const mockDocuments = [
            {
              id: '1',
              title: 'Luxury Property Sales Guide',
              document_type: 'sop',
              content: 'This comprehensive guide covers strategies for marketing and selling luxury properties to high-net-worth individuals. Focus on unique selling points, exclusivity, and personalized service.',
              metadata: { author: 'Marketing Team', version: '1.2' },
              created_at: '2023-01-15T10:30:00Z'
            },
            {
              id: '2',
              title: 'First-Time Buyer FAQ',
              document_type: 'faq',
              content: 'Common questions from first-time homebuyers: 1. What is a down payment? 2. How much do I need for a down payment? 3. What is the difference between pre-qualification and pre-approval?',
              metadata: { updated_by: 'Sarah Johnson', effectiveness: 0.85 },
              created_at: '2023-02-05T14:45:00Z'
            },
            {
              id: '3',
              title: 'Price Objection Handler',
              document_type: 'objection',
              content: 'When clients object to the price: Acknowledge their concern, explain the value proposition, provide market comparisons, and discuss financing options that might make it more affordable.',
              metadata: { success_rate: 0.72 },
              created_at: '2023-01-28T09:15:00Z'
            },
            {
              id: '4',
              title: 'Downtown Market Report 2023',
              document_type: 'training',
              content: 'Analysis of the downtown real estate market trends for 2023, including price changes, inventory levels, average days on market, and buyer demographics.',
              metadata: { region: 'Downtown', year: 2023 },
              created_at: '2023-03-10T16:20:00Z'
            },
            {
              id: '5',
              title: 'Initial Qualification Call Script',
              document_type: 'script',
              content: 'Script for initial qualification calls: Introduction, rapport building, needs assessment, budget discussion, timeline exploration, and next steps.',
              metadata: { conversion_rate: 0.65, call_duration: '15 minutes' },
              created_at: '2023-02-15T11:10:00Z'
            }
          ];
          
          setDocuments(mockDocuments);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error loading documents:', error);
        setLoading(false);
      }
    };
    
    loadDocuments();
  }, [currentOrg]);
  
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    
    try {
      // In a real app, we would fetch this data from the API
      // const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/knowledge/search`, {
      //   org_id: currentOrg.id,
      //   query: searchQuery,
      //   document_type: selectedType !== 'all' ? selectedType : null
      // });
      
      // Mock search functionality
      const results = documents.filter(doc => 
        (selectedType === 'all' || doc.document_type === selectedType) &&
        (doc.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
         doc.content.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      
      // Add mock similarity scores
      const resultsWithScores = results.map(doc => ({
        ...doc,
        similarity: Math.random() * 0.5 + 0.5 // Random score between 0.5 and 1.0
      }));
      
      // Sort by similarity
      resultsWithScores.sort((a, b) => b.similarity - a.similarity);
      
      setSearchResults(resultsWithScores);
    } catch (error) {
      console.error('Error searching knowledge base:', error);
    } finally {
      setIsSearching(false);
    }
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewDocument({
      ...newDocument,
      [name]: value
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // In a real app, we would post this data to the API
      // const response = await axios.post(`${process.env.REACT_APP_BACKEND_URL}/api/knowledge/documents`, {
      //   org_id: currentOrg.id,
      //   title: newDocument.title,
      //   content: newDocument.content,
      //   document_type: newDocument.document_type,
      //   metadata: newDocument.metadata
      // });
      
      // Mock adding a document
      const newDoc = {
        id: String(documents.length + 1),
        title: newDocument.title,
        content: newDocument.content,
        document_type: newDocument.document_type,
        metadata: newDocument.metadata,
        created_at: new Date().toISOString()
      };
      
      setDocuments([...documents, newDoc]);
      
      // Reset form
      setNewDocument({
        title: '',
        content: '',
        document_type: 'sop',
        metadata: {}
      });
      
      setShowAddForm(false);
    } catch (error) {
      console.error('Error adding document:', error);
    }
  };
  
  const filteredDocuments = selectedType === 'all' 
    ? documents 
    : documents.filter(doc => doc.document_type === selectedType);
  
  return (
    <div>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Knowledge Base</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            {showAddForm ? 'Cancel' : 'Add Document'}
          </button>
        </div>
      </div>
      
      {/* Add Document Form */}
      {showAddForm && (
        <div className="mt-6 bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h2 className="text-lg leading-6 font-medium text-gray-900">Add New Document</h2>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">Add a new document to the knowledge base.</p>
          </div>
          <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title</label>
                <input
                  type="text"
                  name="title"
                  id="title"
                  value={newDocument.title}
                  onChange={handleInputChange}
                  required
                  className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                />
              </div>
              
              <div>
                <label htmlFor="document_type" className="block text-sm font-medium text-gray-700">Document Type</label>
                <select
                  name="document_type"
                  id="document_type"
                  value={newDocument.document_type}
                  onChange={handleInputChange}
                  className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                >
                  {documentTypes.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label htmlFor="content" className="block text-sm font-medium text-gray-700">Content</label>
                <textarea
                  name="content"
                  id="content"
                  rows={6}
                  value={newDocument.content}
                  onChange={handleInputChange}
                  required
                  className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                />
              </div>
              
              <div className="flex justify-end">
                <button
                  type="submit"
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Save Document
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Search and Filter */}
      <div className="mt-6 flex flex-col sm:flex-row items-center gap-4">
        <div className="relative flex-1">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search knowledge base..."
            className="block w-full shadow-sm sm:text-sm border-gray-300 rounded-md pr-10"
          />
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
            </svg>
          </div>
        </div>
        
        <div className="flex items-center">
          <label htmlFor="documentType" className="block text-sm font-medium text-gray-700 mr-2">
            Type:
          </label>
          <select
            id="documentType"
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="shadow-sm sm:text-sm border-gray-300 rounded-md"
          >
            <option value="all">All Types</option>
            {documentTypes.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
        </div>
        
        <button
          onClick={handleSearch}
          disabled={isSearching || !searchQuery.trim()}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>
      
      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-medium text-gray-900">Search Results</h2>
          <div className="mt-2 grid gap-5 grid-cols-1 sm:grid-cols-2">
            {searchResults.map(doc => (
              <div key={doc.id} className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex justify-between">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">{doc.title}</h3>
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      doc.similarity > 0.8 ? 'bg-green-100 text-green-800' :
                      doc.similarity > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {Math.round(doc.similarity * 100)}% match
                    </span>
                  </div>
                  <p className="mt-1 max-w-2xl text-sm text-gray-500">
                    {documentTypes.find(t => t.value === doc.document_type)?.label || doc.document_type}
                  </p>
                  <div className="mt-3">
                    <p className="text-sm text-gray-500">{doc.content.substring(0, 200)}...</p>
                  </div>
                </div>
                <div className="bg-gray-50 px-4 py-4 sm:px-6">
                  <div className="text-sm">
                    <a href="#" className="font-medium text-indigo-600 hover:text-indigo-500">
                      View full document
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Document List */}
      <div className="mt-6">
        <h2 className="text-lg font-medium text-gray-900">All Documents</h2>
        {loading ? (
          <div className="text-center py-10">
            <p className="text-gray-500">Loading documents...</p>
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="text-center py-10">
            <p className="text-gray-500">No documents found</p>
          </div>
        ) : (
          <div className="mt-2 bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {filteredDocuments.map(doc => (
                <li key={doc.id}>
                  <div className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 flex items-center justify-center rounded-md bg-indigo-100 text-indigo-800">
                            {doc.document_type === 'sop' && (
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                            )}
                            {doc.document_type === 'script' && (
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                              </svg>
                            )}
                            {doc.document_type === 'training' && (
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path d="M12 14l9-5-9-5-9 5 9 5z" />
                                <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
                              </svg>
                            )}
                            {doc.document_type === 'faq' && (
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            )}
                            {doc.document_type === 'objection' && (
                              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                              </svg>
                            )}
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{doc.title}</div>
                          <div className="text-sm text-gray-500">
                            {documentTypes.find(t => t.value === doc.document_type)?.label || doc.document_type}
                          </div>
                        </div>
                      </div>
                      <div className="ml-2 flex-shrink-0 flex">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <div className="mt-2 sm:flex sm:justify-between">
                      <div className="sm:flex">
                        <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                          {doc.content.substring(0, 150)}...
                        </p>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                        <a href="#" className="font-medium text-indigo-600 hover:text-indigo-500">
                          View
                        </a>
                        <span className="mx-2">•</span>
                        <a href="#" className="font-medium text-indigo-600 hover:text-indigo-500">
                          Edit
                        </a>
                        <span className="mx-2">•</span>
                        <a href="#" className="font-medium text-red-600 hover:text-red-500">
                          Delete
                        </a>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default KnowledgeBase;