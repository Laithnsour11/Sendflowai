import React from 'react';
import AITraining from './AITraining';

const AgentTraining = ({ currentOrg }) => {
  // For Phase C.2, we're using the new AITraining component
  // which includes fine-tuning capabilities based on RLHF data
  return <AITraining currentOrg={currentOrg} />;
};

export default AgentTraining;