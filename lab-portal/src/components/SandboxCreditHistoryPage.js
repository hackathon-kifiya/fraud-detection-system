import React from 'react';
import SandboxPage from './SandboxPage';

const SandboxCreditHistoryPage = ({ onShowSnackbar }) => {
  return (
    <SandboxPage 
      onShowSnackbar={onShowSnackbar}
      dataType="credit_history"
      title="Credit History"
    />
  );
};

export default SandboxCreditHistoryPage;

