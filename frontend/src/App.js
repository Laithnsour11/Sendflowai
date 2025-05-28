import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import './App.css';

// Components
import Dashboard from './components/Dashboard';
import LeadsList from './components/LeadsList';
import Conversations from './components/Conversations';
import Settings from './components/Settings';
import LandingPage from './components/LandingPage';
import KnowledgeBase from './components/KnowledgeBase';
import AgentTraining from './components/AgentTraining';
import Analytics from './components/Analytics';
import Campaigns from './components/Campaigns';

// Layouts
import AppLayout from './layouts/AppLayout';

function App() {
  // Initialize authentication state from localStorage
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('ai_closer_authenticated') === 'true';
  });
  
  const [currentOrg, setCurrentOrg] = useState(() => {
    const savedOrg = localStorage.getItem('ai_closer_org');
    return savedOrg ? JSON.parse(savedOrg) : null;
  });
  
  // Simple mock authentication for demo
  const handleLogin = () => {
    setIsAuthenticated(true);
    const orgData = {
      id: '12345',
      name: 'ABC Realty',
      subscription_tier: 'starter'
    };
    setCurrentOrg(orgData);
    
    // Persist authentication state
    localStorage.setItem('ai_closer_authenticated', 'true');
    localStorage.setItem('ai_closer_org', JSON.stringify(orgData));
  };
  
  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentOrg(null);
    
    // Clear persisted authentication state
    localStorage.removeItem('ai_closer_authenticated');
    localStorage.removeItem('ai_closer_org');
  };
  
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={
          isAuthenticated 
            ? <Navigate to="/dashboard" replace /> 
            : <LandingPage onLogin={handleLogin} />
        } />
        
        {/* Protected routes */}
        {isAuthenticated ? (
          <Route path="/" element={<AppLayout currentOrg={currentOrg} onLogout={handleLogout} />}>
            <Route path="dashboard" element={<Dashboard currentOrg={currentOrg} />} />
            <Route path="leads" element={<LeadsList currentOrg={currentOrg} />} />
            <Route path="conversations" element={<Conversations currentOrg={currentOrg} />} />
            <Route path="analytics" element={<Analytics currentOrg={currentOrg} />} />
            <Route path="campaigns" element={<Campaigns currentOrg={currentOrg} />} />
            <Route path="knowledge" element={<KnowledgeBase currentOrg={currentOrg} />} />
            <Route path="agents" element={<AgentTraining currentOrg={currentOrg} />} />
            <Route path="settings" element={<Settings currentOrg={currentOrg} />} />
          </Route>
        ) : (
          <Route path="*" element={<Navigate to="/" replace />} />
        )}
      </Routes>
    </Router>
  );
}

export default App;