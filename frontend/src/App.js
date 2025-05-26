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

// Layouts
import AppLayout from './layouts/AppLayout';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentOrg, setCurrentOrg] = useState(null);
  
  // Simple mock authentication for demo
  const handleLogin = () => {
    setIsAuthenticated(true);
    setCurrentOrg({
      id: '12345',
      name: 'ABC Realty',
      subscription_tier: 'starter'
    });
  };
  
  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentOrg(null);
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
        <Route path="/" element={
          isAuthenticated 
            ? <AppLayout currentOrg={currentOrg} onLogout={handleLogout} /> 
            : <Navigate to="/" replace />
        }>
          <Route path="/dashboard" element={<Dashboard currentOrg={currentOrg} />} />
          <Route path="/leads" element={<LeadsList currentOrg={currentOrg} />} />
          <Route path="/conversations" element={<Conversations currentOrg={currentOrg} />} />
          <Route path="/knowledge" element={<KnowledgeBase currentOrg={currentOrg} />} />
          <Route path="/agent-training" element={<AgentTraining currentOrg={currentOrg} />} />
          <Route path="/settings" element={<Settings currentOrg={currentOrg} />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;