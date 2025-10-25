import React from 'react';
import SandboxPage from './SandboxPage';

const SandboxLoanRequestsPage = ({ onShowSnackbar }) => {
  return (
    <SandboxPage 
      onShowSnackbar={onShowSnackbar}
      dataType="loan_requests"
      title="Loan Request"
    />
  );
};

export default SandboxLoanRequestsPage;

