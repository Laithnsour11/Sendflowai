import React from 'react';
import AdvancedAnalytics from './AdvancedAnalytics';

const Analytics = ({ currentOrg }) => {
  // For Phase C.3, we're using the new AdvancedAnalytics component
  // which includes comprehensive dashboard, campaign intelligence, and agent intelligence
  return <AdvancedAnalytics currentOrg={currentOrg} />;
};

export default Analytics;